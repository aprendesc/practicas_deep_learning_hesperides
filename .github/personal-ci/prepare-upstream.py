#!/usr/bin/env python3
"""Create one sanitized local commit; never checkout, fetch, or push."""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from gate import OWNERS, NUMBERED, git, paths, private


def remote(name):
    identities = set()
    urls = (git('remote', 'get-url', '--all', name).decode().splitlines()
            + git('remote', 'get-url', '--push', '--all', name).decode().splitlines())
    for url in urls:
        m = re.fullmatch(r'(?:https://github\.com/|ssh://git@github\.com(?:-aprendesc|-pantagruel)?/|git@github\.com(?:-aprendesc|-pantagruel)?:)([\w.-]+/[\w.-]+?)(?:\.git)?/?', url)
        if not m or m[1].split('/')[0] not in OWNERS:
            raise ValueError('Remote must belong to a personal allowlisted GitHub owner')
        identities.add(m[1].lower())
    if len(identities) != 1:
        raise ValueError('Remote fetch and push destinations must agree')
    return identities.pop()


def prepare(branch, source, base):
    if not NUMBERED.fullmatch(branch):
        raise ValueError('Branch must be numbered')
    git('check-ref-format', 'refs/heads/' + branch)
    if source != 'origin/develop' or base != 'upstream/develop':
        raise ValueError('Source and base must be origin/develop and upstream/develop')
    if remote('origin') == remote('upstream'):
        raise ValueError('Aliases require the combined-repository flow')
    source_sha = git('rev-parse', '--verify', source + '^{commit}').decode().strip()
    base_sha = git('rev-parse', '--verify', base + '^{commit}').decode().strip()
    ancestor = git('merge-base', source_sha, base_sha).decode().strip()
    managed = ('.github/personal-ci/policy.json', '.github/workflows/ci.yml',
               '.github/workflows/personal-integration.yml', '.github/workflows/portability.yml')
    baseline_files = set(paths(git('ls-tree', '-r', '--name-only', '-z', base_sha)))
    if managed[0] not in baseline_files:
        raise ValueError('Upstream managed CI policy is missing; configure upstream separately first')
    try:
        upstream_policy = json.loads(git('show', base_sha + ':' + managed[0]))
    except (ValueError, TypeError):
        raise ValueError('Upstream managed CI policy is invalid') from None
    if upstream_policy.get('role') != 'upstream' or upstream_policy.get('repository', '').lower() != remote('upstream'):
        raise ValueError('Upstream managed CI policy must identify the upstream repository and role')
    # Sanitize all three trees before merging. Private differences cannot conflict.
    def clean_tree(ref):
        with tempfile.TemporaryDirectory(prefix='personal-ci-index-') as directory:
            env = dict(os.environ, GIT_INDEX_FILE=os.path.join(directory, 'index'))
            git('read-tree', ref, env=env)
            excluded = [p for p in paths(git('ls-tree', '-r', '--name-only', '-z', ref)) if private(p)]
            if excluded:
                result = subprocess.run(['git', 'update-index', '--force-remove', '-z', '--stdin'],
                                        input=b'\0'.join(os.fsencode(p) for p in excluded) + b'\0',
                                        capture_output=True, env=env)
                if result.returncode:
                    raise ValueError('Tree sanitation failed')
            if ref == source_sha:
                # Routing belongs to upstream. Deliberate CI changes require a separate
                # upstream configuration PR, never origin promotion.
                for path in managed:
                    if path in baseline_files:
                        entry = git('ls-tree', '-z', base_sha, '--', path).split(b'\t', 1)[0].decode().split()
                        git('update-index', '--add', '--cacheinfo', entry[0], entry[2], path, env=env)
                    else:
                        git('update-index', '--force-remove', '--', path, env=env)
            return git('write-tree', env=env).decode().strip()
    ancestor_tree, source_tree, base_tree = map(clean_tree, (ancestor, source_sha, base_sha))
    ancestor_commit = git('commit-tree', ancestor_tree, '-m', 'Temporary public merge base').decode().strip()
    left = git('commit-tree', base_tree, '-p', ancestor_commit, '-m', 'Temporary upstream public tree').decode().strip()
    right = git('commit-tree', source_tree, '-p', ancestor_commit, '-m', 'Temporary origin public tree').decode().strip()
    tree = git('merge-tree', '--write-tree', left, right).decode().splitlines()[0]
    if any(private(p) for p in paths(git('ls-tree', '-r', '--name-only', '-z', tree))):
        raise ValueError('Sanitized tree contains private paths')
    commit = git('commit-tree', tree, '-p', base_sha, '-m', 'Prepare public contribution ' + branch).decode().strip()
    # Empty expected old object means create only; preserves other refs/worktrees.
    git('update-ref', 'refs/heads/' + branch, commit, '0' * len(commit))
    return commit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--branch', required=True)
    parser.add_argument('--source', default='origin/develop')
    parser.add_argument('--base', default='upstream/develop')
    args = parser.parse_args()
    try:
        print('Created local branch ' + args.branch + ' at ' + prepare(args.branch, args.source, args.base))
    except (ValueError, OSError) as error:
        print('Preparation rejected: ' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
