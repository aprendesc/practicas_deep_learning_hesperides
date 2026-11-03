#!/usr/bin/env python3
"""Enforce the downstream/upstream development methodology in local Git hooks.

pre-commit                  develop/main stay private-only; task branches keep a contract;
                            Worker workspaces hold only clones; content repos reject residue.
pre-push REMOTE URL         protected branches, develop provenance and task branch readiness
                            (refs on stdin). Only the issue state is queried, through gh.
post-merge | post-commit    warn when a merge drops private methodology content and refresh
                            the installed hooks when the versioned baseline changed.
"""
from collections import Counter
import json
import os
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HOOKS = Path(__file__).resolve().parent
sys.path.insert(0, str(HOOKS))
from publication import clean_ignore, identity, private  # noqa: E402  (shared publication rules)

PROTECTED = {'develop', 'main', 'master'}
TASK = re.compile(r'[a-z][a-z0-9-]*/([1-9]\d*)-[a-z0-9]+(?:-[a-z0-9]+)*')
ISSUE = re.compile(r'[1-9]\d*-[a-z0-9]+(?:-[a-z0-9]+)*')
LINK = re.compile(r'\[Local Contract\]\(([^\n)]+)\)')
PERSONAL_OWNERS = {'aprendesc', 'pantagruel-alpha'}
RESIDUE = re.compile(r'(^\.playwright-mcp/|^tmp/|^out/|\.DS_Store$|__pycache__/|\.ipynb_checkpoints/|^wandb/'
                     r'|\.(aux|fls|fdb_latexmk|synctex\.gz|nav|snm|bbl|blg|vrb|toc)$)')
WORKSPACE_EXTRAS = {'.claude', '.DS_Store'}
DOWNSTREAM_CI = ('.github/personal-ci/', '.github/workflows/personal-')  # Personal CI never reaches a corporate upstream.


def git(*args, check=True):
    result = subprocess.run(['git', '--no-optional-locks', *args], capture_output=True, text=True)
    if check and result.returncode:
        raise RuntimeError('git ' + args[0] + ' failed: ' + result.stderr.strip()[:200])
    return result.stdout.strip() if result.returncode == 0 else ''


def stop(message):
    sys.exit('Methodology guard: ' + message)


def zero(oid):
    return set(oid) == {'0'}


def policy():
    path = HOOKS / 'clone-policy.json'
    if not path.is_file():
        path = HOOKS.parent / 'clone-setup.json'
    return json.loads(path.read_text())


def root():
    return Path(git('rev-parse', '--show-toplevel'))


def owner(slug):
    parts = slug.split('/')
    return parts[1] if len(parts) > 2 else ''


def mirrors_upstream(rules):
    """An Inditex develop mirrors its upstream base branch plus private files."""
    downstream, upstream = identity(rules['downstream_url']), identity(rules['upstream_url'])
    return upstream != downstream and owner(upstream) == 'inditex'


def allowed_on_develop(path, rules, mirrors=False):
    return private(path) or path in rules.get('develop_paths', []) or (mirrors and path.startswith(DOWNSTREAM_CI))


def contract_format(text):
    """Return a problem description, or None when the contract follows the standard layout."""
    headings = [line.strip() for line in text.splitlines() if line.startswith('## ')]
    if not headings or headings[0] != '## Execution plan':
        return 'the contract must start with "## Execution plan"'
    if '## Context' not in headings or '### Applicable skills' not in text:
        return 'the contract needs "## Context" and "### Applicable skills"'
    return None


def linked_contract(repo, agents_text, number):
    """A companion clone declares the canonical contract of a sibling repository."""
    for link in LINK.findall(agents_text or ''):
        target = (repo / link.strip('<>')).resolve()
        if (ISSUE.fullmatch(target.parent.name) and target.parent.name.startswith(number + '-')
                and target.name == target.parent.name + '.md' and target.is_file()):
            return target
    return None


def resolve_contract(repo, number, names, read):
    """Find the task contract in a tree (names/read) or through the declared link.

    Returns (contract_text, issue_repository_slug, problem).
    """
    folders = {name.split('/')[2] for name in names
               if name.startswith('context/issues/' + number + '-') and name.count('/') >= 3}
    if len(folders) > 1:
        return None, None, 'several issue folders match #' + number + ': ' + ', '.join(sorted(folders))
    if folders:
        folder = folders.pop()
        if not ISSUE.fullmatch(folder):
            return None, None, 'issue folder must be <number>-<kebab-case-title>: ' + folder
        contract = 'context/issues/' + folder + '/' + folder + '.md'
        if contract not in names:
            return None, None, 'issue folder lacks its contract ' + contract
        return read(contract), identity(policy()['downstream_url']), None
    target = linked_contract(repo, read('AGENTS.md') if 'AGENTS.md' in names else '', number)
    if target is None:
        return None, None, 'no contract for #' + number + ' (context/issues/' + number + '-<title>/ or a [Local Contract] link in AGENTS.md)'
    sibling = git('-C', str(target.parents[3]), 'remote', 'get-url', 'downstream', check=False)
    if not sibling:
        return None, None, 'the linked contract repository has no downstream remote'
    return target.read_text(), identity(sibling), None


def issue_state(slug, number):
    states = os.environ.get('APC_HOOKS_ISSUE_STATES')  # Isolated tests only.
    if states:
        return json.loads(states).get(slug + '#' + number, 'MISSING')
    repository = slug.split('/', 1)[1]
    try:
        result = subprocess.run(['gh', 'issue', 'view', number, '-R', repository, '--json', 'state', '-q', '.state'],
                                capture_output=True, text=True, timeout=25)
    except (OSError, subprocess.TimeoutExpired):
        return 'UNVERIFIED'
    return result.stdout.strip() if result.returncode == 0 else 'UNVERIFIED'


# ----- pre-commit -----

def workspace_clean(repo):
    workspace = repo.parent
    if workspace.parent.name != 'workspaces' or not re.fullmatch(r'w[1-9]\d*', workspace.name):
        return
    extra = [entry.name for entry in workspace.iterdir()
             if entry.name not in WORKSPACE_EXTRAS
             and not (entry.is_dir() and not entry.is_symlink() and (entry / '.git').exists())]
    if extra:
        stop('Worker workspace ' + workspace.name + ' must contain only repository clones; remove: ' + ', '.join(sorted(extra)))


def pre_commit():
    rules, repo = policy(), root()
    workspace_clean(repo)
    staged = [p for p in git('diff', '--cached', '--name-only', '-z').split('\0') if p]
    if rules.get('residue_guard'):
        residue = [p for p in staged if RESIDUE.search(p)]
        if residue:
            stop('working residue staged (unstage it and ignore it): ' + ', '.join(residue[:8]))
    branch = git('symbolic-ref', '--quiet', '--short', 'HEAD', check=False)
    if branch in PROTECTED:
        if git('rev-parse', '-q', '--verify', 'MERGE_HEAD', check=False):
            return
        if branch != 'develop':
            stop(branch + ' only changes through reviewed pull requests.')
        public = [p for p in staged if not allowed_on_develop(p, rules, mirrors_upstream(rules))]
        if public:
            stop('develop only accepts private methodology files; move these to a task branch: ' + ', '.join(public[:8]))
        return
    match = TASK.fullmatch(branch)
    if match:
        names = set(git('ls-files', '-co', '--exclude-standard', '-z', '--', 'context/issues', 'AGENTS.md').split('\0'))
        read = lambda path: (repo / path).read_text() if (repo / path).is_file() else ''
        _, _, problem = resolve_contract(repo, match[1], names, read)
        if problem:
            stop(problem)


# ----- pre-push -----

def tree_names(commit):
    return {p for p in git('ls-tree', '-r', '--name-only', '-z', commit).split('\0') if p}


def public_tree(commit):
    entries = {}
    for record in git('ls-tree', '-r', '-z', commit).split('\0'):
        if record:
            meta, name = record.split('\t', 1)
            if not private(name) and not name.startswith(DOWNSTREAM_CI):
                entries[name] = meta
    return entries


def ancestor(older, newer):
    return subprocess.run(['git', 'merge-base', '--is-ancestor', older, newer], capture_output=True).returncode == 0


def known(oid):
    return subprocess.run(['git', 'cat-file', '-e', oid + '^{commit}'], capture_output=True).returncode == 0


def base_refs():
    """Upstream integration branches available locally; develop first, main when upstream has no develop."""
    return [ref for ref in ('refs/remotes/upstream/develop', 'refs/remotes/upstream/main') if git('rev-parse', '-q', '--verify', ref, check=False)]


def check_develop(local, remote, rules, mirrors):
    bases = base_refs()
    excluded = ['^' + ref for ref in bases] + (['^' + remote] if remote else [])
    for line in git('rev-list', '--parents', local, *excluded).splitlines():
        commit, *parents = line.split()
        if len(parents) > 1:
            foreign = [p for p in parents[1:] if not any(ancestor(p, ref) for ref in bases)]
            if foreign:
                stop('develop has a local merge (' + commit[:9] + '); integrate task branches through pull requests.')
            continue
        changed = [p for p in git('diff-tree', '--root', '--no-commit-id', '--name-only', '-r', '-z', commit).split('\0') if p]
        public = [p for p in changed if not allowed_on_develop(p, rules, mirrors)]
        if public:
            stop('commit ' + commit[:9] + ' changes public files on develop (' + ', '.join(public[:5]) + '); use a task branch and a pull request.')
    if mirrors:
        if not bases:
            stop('fetch upstream first: develop must be verified against its upstream base branch.')
        if not ancestor(bases[0], local):
            stop('integrate ' + bases[0][len('refs/remotes/'):] + ' into develop first; downstream develop stays synchronized with upstream.')
        # Divergence from upstream only enters through downstream PRs merged on GitHub and pending upstream;
        # a push never adds its own.
        mine, theirs = public_tree(local), public_tree(bases[0])
        accepted = public_tree(remote) if remote else {}
        introduced = sorted(p for p in set(mine) | set(theirs)
                            if mine.get(p) != theirs.get(p) and mine.get(p) != accepted.get(p))
        if introduced:
            stop('develop must equal ' + bases[0][len('refs/remotes/'):] + ' plus private files and downstream PRs pending upstream;'
                 ' this push adds: ' + ', '.join(introduced[:8]))


def check_task(local, number, slug_hint=None):
    repo = root()
    names = tree_names(local)
    read = lambda path: git('cat-file', 'blob', local + ':' + path) if path in names else ''
    text, slug, problem = resolve_contract(repo, number, names, read)
    if problem:
        stop(problem)
    problem = contract_format(text)
    if problem:
        stop(problem)
    if 'context/project-map.md' not in names:
        stop('task branches require context/project-map.md.')
    state = issue_state(slug, number)
    if state != 'OPEN':
        stop('issue ' + slug.split('/', 1)[1] + '#' + number + ' is ' + state.lower() + '; task branches need an open issue.')


def publishable(commit):
    """Public tree as publication prepares it: private paths out, private .gitignore lines filtered."""
    entries = public_tree(commit)
    for name, meta in entries.items():
        if Path(name).name == '.gitignore':
            mode, kind, oid = meta.split()
            data = subprocess.run(['git', 'cat-file', 'blob', oid], capture_output=True, check=True).stdout
            clean = subprocess.run(['git', 'hash-object', '--stdin'], input=clean_ignore(data), capture_output=True, check=True).stdout
            entries[name] = ' '.join((mode, kind, clean.decode().strip()))
    return entries


def lines(ref, path):
    data = subprocess.run(['git', 'cat-file', 'blob', ref + ':' + path], capture_output=True).stdout
    return Counter(data.decode('utf-8', 'surrogateescape').splitlines())


def check_integrated(source, name):
    """The downstream PR comes first: every line the branch adds is in downstream develop, and every line it removes is gone.

    Line containment keeps the check valid when another task touches or creates the same file.
    """
    develop = 'refs/remotes/downstream/develop'
    if not git('rev-parse', '-q', '--verify', develop, check=False):
        stop('fetch downstream first: upstream publication needs downstream/develop.')
    base = git('merge-base', source, develop)
    changed = [p for p in git('diff', '--name-only', '-z', base, source).split('\0')
               if p and not private(p) and not p.startswith(DOWNSTREAM_CI)]
    branch, integrated = public_tree(source), public_tree(develop)
    pending = []
    for path in changed:
        if branch.get(path) == integrated.get(path):
            continue
        if (path in branch) != (path in integrated):  # Added or deleted by the branch, not by develop.
            pending.append(path)
            continue
        before, after, merged = lines(base, path), lines(source, path), lines(develop, path)
        added_missing = (after - before) - merged
        removed_kept = (before - after) - (before - merged)
        if added_missing or removed_kept:
            pending.append(path)
    if pending:
        stop('downstream/' + name + ' is not integrated in downstream develop; merge its downstream PR first'
             ' (or update the branch from develop). Pending: ' + ', '.join(sorted(pending)[:8]))


def check_orthogonal(source, name):
    """A task reaches upstream alone: its branch carries no other downstream PR still pending upstream."""
    develop = 'refs/remotes/downstream/develop'
    pending = git('rev-list', '--first-parent', '--merges', '--format=%H %P %s', develop, '--not', *base_refs())
    for line in pending.splitlines():
        if line.startswith('commit '):
            continue
        commit, *rest = line.split(' ')
        parents = [p for p in rest if re.fullmatch(r'[0-9a-f]{40}', p)]
        subject = ' '.join(rest[len(parents):])
        merged = re.search(r'Merge pull request #\d+ from [^/\s]+/(\S+)', subject)
        if not merged or merged[1] == name or len(parents) < 2:
            continue
        if ancestor(commit, source) or ancestor(parents[1], source):
            stop('downstream/' + name + ' contains ' + merged[1] + ', another downstream PR pending upstream;'
                 ' tasks reach upstream independently. Rebuild the branch from the upstream base.')


def check_upstream_branch(local, name, mirrors):
    """A distinct upstream only receives the public content of the homonymous downstream branch."""
    source = 'refs/remotes/downstream/' + name
    if not git('rev-parse', '-q', '--verify', source, check=False):
        stop('upstream branch ' + name + ' needs the homonymous downstream branch; push it to downstream and fetch first.')
    mine, theirs = publishable(local), publishable(source)
    differing = sorted(p for p in set(mine) | set(theirs) if mine.get(p) != theirs.get(p))
    if differing:
        stop('upstream ' + name + ' must carry exactly the public content of downstream/' + name + '; differs in: ' + ', '.join(differing[:8]))
    check_integrated(source, name)
    check_orthogonal(source, name)
    if mirrors:
        leaked = [p for p in tree_names(local) if p.startswith(DOWNSTREAM_CI)]
        for commit in git('rev-list', local, '--not', '--remotes=upstream').splitlines():
            leaked += [p for p in git('diff-tree', '--root', '-m', '--no-commit-id', '--name-only', '-r', '-z', commit).split('\0')
                       if p.startswith(DOWNSTREAM_CI)]
        if leaked:
            stop('downstream personal CI cannot reach a corporate upstream: ' + ', '.join(sorted(set(leaked))[:5]))


def pre_push(remote, url, lines):
    rules = policy()
    downstream, upstream, destination = identity(rules['downstream_url']), identity(rules['upstream_url']), identity(url)
    shared, mirrors = upstream != downstream, mirrors_upstream(rules)
    if remote == 'upstream' and destination != upstream:
        stop('upstream destination differs from the verified repository.')
    for line in lines:
        local_ref, local, remote_ref, previous = line.split()
        if not remote_ref.startswith('refs/heads/'):
            continue
        name = remote_ref[len('refs/heads/'):]
        if name in PROTECTED:
            if zero(local):
                stop(name + ' cannot be deleted.')
            if not zero(previous) and not (known(previous) and ancestor(previous, local)):
                stop('non-fast-forward update of ' + name + ' refused; fetch and integrate instead of forcing.')
            if shared and destination == upstream:
                stop('base branches of a distinct upstream change only through reviewed pull requests.')
            if destination == downstream and name == 'develop':
                check_develop(local, None if zero(previous) else previous, rules, mirrors)
            continue
        if zero(local):
            continue
        match = TASK.fullmatch(name)
        if destination == downstream or (destination == upstream and owner(upstream) in PERSONAL_OWNERS):
            if not match:
                stop('branch ' + name + ' must be named <type>/<issue>-<kebab-case-title>.')
        if destination == downstream and match:
            check_task(local, match[1])
        if shared and destination == upstream:
            check_upstream_branch(local, name, mirrors)


# ----- post-merge / post-commit -----

def private_snapshot(commit):
    names = {p for p in tree_names(commit) if private(p) and not p.startswith('.githooks/')}  # Hooks follow their baseline.
    agents = git('cat-file', 'blob', commit + ':AGENTS.md', check=False) if 'AGENTS.md' in names else ''
    return names, set(LINK.findall(agents))


def warn_lost(before, after):
    names_before, links_before = private_snapshot(before)
    names_after, links_after = private_snapshot(after)
    lost = sorted(names_before - names_after)
    links = sorted(links_before - links_after)
    if lost or links:
        print('Methodology guard WARNING: this merge removed private methodology content.', file=sys.stderr)
        for path in lost[:12]:
            print('  - ' + path, file=sys.stderr)
        for link in links:
            print('  - [Local Contract](' + link + ') in AGENTS.md', file=sys.stderr)
        print('Restore it from ' + before[:9] + ' if the removal was not intended.', file=sys.stderr)


def refresh_hooks():
    """Install a newer versioned baseline after a merge brings it in."""
    repo = root()
    source, setup = repo / '.githooks/clone-hooks', repo / '.githooks/clone-setup.py'
    if not (source / 'methodology-guard.py').is_file() or not setup.is_file():
        return
    current = (repo / '.githooks/clone-setup.json').read_bytes() == (HOOKS / 'clone-policy.json').read_bytes() and all(
        (HOOKS / f.name).is_file() and (HOOKS / f.name).read_bytes() == f.read_bytes() for f in source.iterdir() if f.is_file())
    if not current:
        result = subprocess.run([sys.executable, '-B', str(setup)], capture_output=True, text=True, cwd=repo)
        print('Methodology guard: hooks refreshed from the versioned baseline.' if result.returncode == 0
              else 'Methodology guard WARNING: hook refresh failed; run python3 .githooks/clone-setup.py', file=sys.stderr)


def post_merge():
    if git('rev-parse', '-q', '--verify', 'ORIG_HEAD', check=False):
        warn_lost('ORIG_HEAD', 'HEAD')
    refresh_hooks()


def post_commit():
    parents = git('rev-list', '--parents', '-n', '1', 'HEAD').split()[1:]
    if len(parents) > 1:
        warn_lost(parents[0], 'HEAD')
        refresh_hooks()


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else ''
    try:
        if command == 'pre-commit':
            pre_commit()
        elif command == 'pre-push' and len(sys.argv) == 4:
            pre_push(sys.argv[2], sys.argv[3], sys.stdin.read().splitlines())
        elif command in ('post-merge', 'post-commit'):
            try:
                post_merge() if command == 'post-merge' else post_commit()
            except (OSError, ValueError, RuntimeError) as error:
                print('Methodology guard WARNING: post-' + command[5:] + ' check skipped: ' + str(error), file=sys.stderr)
        else:
            stop(__doc__)
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        stop('cannot verify the methodology: ' + str(error))


if __name__ == '__main__':
    main()
