#!/usr/bin/env python3
"""Prepare filtered upstream commits and reject private content at pre-push.

prepare SOURCE UPSTREAM_BRANCH: create publish/UPSTREAM_BRANCH locally from
committed SOURCE and an existing upstream tracking branch. No fetch/push/checkout.
check REMOTE URL: inspect pre-push refs on stdin, without contacting a server.
"""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit

ROOTS = {'context', '.githooks', '.worktreelink', '.agents', '.codex', '.claude', 'skills'}
NAMES = {'AGENTS.md', 'CLAUDE.md', 'OPENCODE.md', 'SKILL.md', 'opencode.json', 'opencode.jsonc'}
SCRIPTS = {'scripts/promote-to-upstream', 'scripts/prepare-upstream-branch'}
TRACE = re.compile(r'(?i)(\bcontext\b|\bagents\.md\b|\bclaude\b|\bcodex\b|\bopencode\b|\bskills?\b|\bgithooks\b|\bworktreelink\b|promote-to-upstream|prepare-upstream-branch|\.github/agents)')


def git(*args, env=None, data=None):
    result = subprocess.run(['git', '--no-optional-locks', *args], input=data,
                            capture_output=True, env=env)
    if result.returncode:
        raise RuntimeError('Git operation failed: ' + args[0])
    return result.stdout


def identity(url):
    if '://' in url:
        parsed = urlsplit(url)
        host, path = parsed.hostname or '', parsed.path
    else:
        host, _, path = url.split('@')[-1].partition(':')
    return re.sub(r'^github\.com-.*$', 'github.com', host.lower()) + '/' + path.strip('/').removesuffix('.git').lower()


def private(name):
    parts = name.split('/')
    return (parts[0] in ROOTS or any(part in NAMES for part in parts)
            or name in SCRIPTS or name.startswith(('.github/skills/', '.github/agents/')))


def entries(tree):
    for record in git('ls-tree', '-r', '-z', tree).split(b'\0'):
        if record:
            meta, name = record.split(b'\t', 1)
            mode, kind, oid = meta.decode().split()
            yield mode, kind, oid, name.decode('utf-8', 'surrogateescape')


def clean_ignore(data):
    return b''.join(line for line in data.splitlines(keepends=True)
                    if not TRACE.search(line.decode('utf-8', 'replace')))


def validate_tree(tree):
    for mode, kind, oid, name in entries(tree):
        if private(name):
            raise RuntimeError('Upstream contains private path: ' + name)
        if Path(name).name == '.gitignore' and kind == 'blob':
            if mode == '120000':
                raise RuntimeError('Cannot certify a symlinked .gitignore: ' + name)
            data = git('cat-file', 'blob', oid)
            if clean_ignore(data) != data:
                raise RuntimeError('Upstream ignore file mentions private methodology: ' + name)


def prepare(source, target):
    downstream = identity(git('remote', 'get-url', '--push', 'downstream').decode().strip())
    upstream = identity(git('remote', 'get-url', 'upstream').decode().strip())
    if downstream == upstream:
        raise RuntimeError('Same destination: use the ordinary downstream contribution flow')
    git('check-ref-format', 'refs/heads/' + target)
    destination = git('rev-parse', '--verify', 'refs/remotes/upstream/' + target + '^{commit}').decode().strip()
    source_oid = git('rev-parse', '--verify', source + '^{commit}').decode().strip()
    base = git('merge-base', source_oid, destination).decode().strip()
    branch = 'refs/heads/publish/' + target
    if ('branch ' + branch + '\n').encode() in git('worktree', 'list', '--porcelain'):
        raise RuntimeError('Publication branch is checked out; preserve that work')
    existing = subprocess.run(['git', 'show-ref', '--verify', '--quiet', branch]).returncode == 0
    if existing:
        raise RuntimeError('Publication branch already exists; preserve it and select another target')
    validate_tree(destination)
    with tempfile.TemporaryDirectory(prefix='upstream-filter-') as directory:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(directory) / 'index'))
        git('read-tree', source_oid, env=env)
        for mode, kind, oid, name in entries(source_oid):
            if private(name):
                git('update-index', '--force-remove', '--', name, env=env)
            elif Path(name).name == '.gitignore' and kind == 'blob':
                if mode == '120000':
                    raise RuntimeError('Cannot filter symlinked .gitignore')
                blob = git('hash-object', '-w', '--stdin', data=clean_ignore(git('cat-file', 'blob', oid))).decode().strip()
                git('update-index', '--cacheinfo', mode, blob, name, env=env)
        filtered = git('write-tree', env=env).decode().strip()
        git('read-tree', '-m', base, destination, filtered, env=env)
        if git('ls-files', '-u', env=env):
            raise RuntimeError('Publication conflicts with upstream; manual review required')
        tree = git('write-tree', env=env).decode().strip()
        validate_tree(tree)
        if tree == git('rev-parse', destination + '^{tree}').decode().strip():
            raise RuntimeError('No public changes to publish')
        commit = git('commit-tree', tree, '-p', destination, data=b'chore: prepare upstream contribution\n').decode().strip()
        git('diff', '--check', destination, commit)
        git('update-ref', branch, commit, '0' * len(commit))
        print(json.dumps(dict(branch=branch, commit=commit, target=target, pushed=False)))


def check(url):
    policy_path = Path(__file__).with_name('clone-policy.json')
    if not policy_path.exists():
        policy_path = Path(__file__).parents[1] / 'clone-setup.json'
    policy = json.loads(policy_path.read_text())
    if identity(url) == identity(policy['downstream_url']):
        return
    for line in sys.stdin:
        local_ref, new, remote_ref, old = line.split()
        if set(new) == {'0'}:
            continue
        validate_tree(new)
        args = ('rev-list', new, '^' + old) if set(old) != {'0'} else ('rev-list', new, '--not', '--remotes=upstream')
        for commit in git(*args).decode().splitlines():
            validate_tree(commit)


def main():
    try:
        if len(sys.argv) == 4 and sys.argv[1] == 'prepare':
            prepare(sys.argv[2], sys.argv[3])
        elif len(sys.argv) == 4 and sys.argv[1] == 'check':
            check(sys.argv[3])
        else:
            raise RuntimeError(__doc__)
    except (OSError, ValueError, RuntimeError, KeyError) as error:
        sys.exit('Publication blocked: ' + str(error))


if __name__ == '__main__':
    main()
