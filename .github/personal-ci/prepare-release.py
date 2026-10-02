#!/usr/bin/env python3
"""Prepare a local numbered release without importing legacy develop history."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from gate import RELEASE, git, paths, private, validate

_spec = importlib.util.spec_from_file_location('personal_promotion', Path(__file__).with_name('prepare-upstream.py'))
_promotion = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_promotion)
remote_identity = _promotion.remote


def prepare(branch, remote=None):
    if not RELEASE.fullmatch(branch):
        raise ValueError('Use release/<number>-<title>')
    git('check-ref-format', 'refs/heads/' + branch)
    origin = remote_identity('origin')
    if remote is None:
        available = git('remote').decode().splitlines()
        remote = 'upstream' if 'upstream' in available and remote_identity('upstream') != origin else 'origin'
    if remote not in {'origin', 'upstream'}:
        raise ValueError('Only origin or upstream release destinations are supported')
    destination = remote_identity(remote)
    source = git('rev-parse', '--verify', remote + '/develop^{commit}').decode().strip()
    base = git('rev-parse', '--verify', remote + '/main^{commit}').decode().strip()
    policy = json.loads(git('show', source + ':.github/personal-ci/policy.json'))
    if policy.get('repository', '').lower() != destination or policy.get('role') not in {'upstream', 'combined'}:
        raise ValueError('Develop must contain the matching upstream or combined release policy')
    if policy['role'] == 'upstream' and (remote != 'upstream' or destination == origin):
        raise ValueError('Distinct upstream releases must use upstream/develop')
    if policy['role'] == 'combined' and destination != origin:
        raise ValueError('Combined releases must use the origin repository')
    ancestor = git('merge-base', source, base).decode().strip()

    def clean_tree(ref):
        if policy['role'] == 'combined':
            return git('rev-parse', ref + '^{tree}').decode().strip()
        with tempfile.TemporaryDirectory(prefix='personal-release-index-') as directory:
            env = dict(os.environ, GIT_INDEX_FILE=os.path.join(directory, 'index'))
            git('read-tree', ref, env=env)
            excluded = [p for p in paths(git('ls-tree', '-r', '--name-only', '-z', ref)) if private(p)]
            if excluded:
                result = subprocess.run(['git', 'update-index', '--force-remove', '-z', '--stdin'],
                                        input=b'\0'.join(os.fsencode(p) for p in excluded) + b'\0',
                                        capture_output=True, env=env)
                if result.returncode:
                    raise ValueError('Release sanitation failed')
            return git('write-tree', env=env).decode().strip()

    ancestor_tree, source_tree, base_tree = map(clean_tree, (ancestor, source, base))
    parent = git('commit-tree', ancestor_tree, '-m', 'Temporary release merge base').decode().strip()
    left = git('commit-tree', base_tree, '-p', parent, '-m', 'Temporary main tree').decode().strip()
    right = git('commit-tree', source_tree, '-p', parent, '-m', 'Temporary develop tree').decode().strip()
    tree = git('merge-tree', '--write-tree', left, right).decode().splitlines()[0]
    commit = git('commit-tree', tree, '-p', base, '-m', 'Prepare release ' + branch).decode().strip()
    repo = {'full_name': destination}
    event = {'repository': repo, 'pull_request': {
        'base': {'repo': repo, 'ref': 'main', 'sha': base},
        'head': {'repo': repo, 'ref': branch, 'sha': commit}}}
    validate(event, policy, 'pull_request')
    git('update-ref', 'refs/heads/' + branch, commit, '0' * len(commit))
    return commit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--branch', required=True)
    parser.add_argument('--remote', choices=('origin', 'upstream'))
    args = parser.parse_args()
    try:
        print('Created local release branch ' + args.branch + ' at ' + prepare(args.branch, args.remote))
    except (ValueError, OSError, KeyError, TypeError) as error:
        print('Release preparation rejected: ' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
