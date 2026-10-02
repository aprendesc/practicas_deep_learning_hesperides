#!/usr/bin/env python3
"""Fail-closed personal PR policy; read event and policy from trusted base checkout."""
import argparse
import json
import os
import re
import subprocess
import sys

OWNERS = {'aprendesc', 'pantagruel-alpha'}
NUMBERED = re.compile(r'^(?:[a-z][a-z0-9_-]*/)*(?:issue-)?[0-9]+-[a-zA-Z0-9][a-zA-Z0-9._/-]*$')
RELEASE = re.compile(r'^release/(?:issue-)?[0-9]+-[a-zA-Z0-9][a-zA-Z0-9._/-]*$')


def git(*args, env=None):
    result = subprocess.run(['git', *args], capture_output=True, env=env)
    if result.returncode:
        raise ValueError('Git verification failed')
    return result.stdout


def private(path):
    parts = path.split('/')
    return (parts[0] in {'context', 'skills', '.agents', '.codex', '.claude', '.githooks', '.worktreelink'}
            or any(p in {'AGENTS.md', 'CLAUDE.md', 'SKILL.md'} for p in parts)
            or path == '.github/skills' or path.startswith('.github/skills/')
            or any(path == p or path.startswith(p + '/') for p in
                   ('scripts/promote-to-upstream', 'scripts/prepare-upstream-branch')))


def paths(data):
    return [p.decode('utf-8', errors='surrogateescape') for p in data.split(b'\0') if p]


def validate(event, policy, event_name=None):
    if policy.get('role') not in {'origin', 'upstream', 'combined'}:
        raise ValueError('Unknown policy role')
    repo = event['repository']['full_name']
    if repo != policy['repository'] or repo.split('/')[0] not in OWNERS:
        raise ValueError('Repository is outside personal policy')
    if policy['role'] == 'origin' and repo.split('/')[0] != 'aprendesc':
        raise ValueError('Origin must belong to aprendesc')
    event_name = event_name or ('pull_request' if 'pull_request' in event else 'push')
    if event_name in {'push', 'workflow_dispatch'}:
        ref = event.get('ref') or os.getenv('GITHUB_REF')
        if ref not in {'refs/heads/develop', 'refs/heads/main'}:
            raise ValueError('Unsupported branch event')
        sha = event.get('after') if event_name == 'push' else os.getenv('GITHUB_SHA')
        if not sha or not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', sha):
            raise ValueError('Invalid event commit identifier')
        git('cat-file', '-e', sha + '^{commit}')
        if policy['role'] == 'upstream' and any(private(p) for p in paths(git('ls-tree', '-r', '--name-only', '-z', sha))):
            raise ValueError('Private paths remain in upstream event tree')
        return 'integration' if policy['role'] == 'upstream' or ref == 'refs/heads/main' else 'fast'
    if event_name not in {'pull_request', 'pull_request_target'}:
        raise ValueError('Unsupported event type')
    pr = event['pull_request']
    if pr['base']['repo']['full_name'] != repo or pr['head']['repo']['full_name'] != repo:
        raise ValueError('PR must originate in the destination repository')
    base, head = pr['base']['ref'], pr['head']['ref']
    if base == 'develop':
        if not NUMBERED.fullmatch(head):
            raise ValueError('Develop requires a numbered branch')
    elif base == 'main':
        if head != 'develop' and not RELEASE.fullmatch(head):
            raise ValueError('Main requires develop or a numbered release branch')
    else:
        raise ValueError('Unsupported PR destination')
    for side in ('base', 'head'):
        sha = pr[side]['sha']
        if not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', sha):
            raise ValueError('Invalid commit identifier')
        git('cat-file', '-e', sha + '^{commit}')
    if policy['role'] == 'upstream':
        if any(private(p) for p in paths(git('ls-tree', '-r', '--name-only', '-z', pr['head']['sha']))):
            raise ValueError('Private paths remain in proposed upstream tree')
        # Check every incoming commit against every parent, including merge parents.
        commits = git('rev-list', pr['base']['sha'] + '..' + pr['head']['sha']).decode().splitlines()
        for commit in commits:
            changed = git('diff-tree', '--root', '-m', '--no-commit-id', '-r', '--name-only', '-z',
                          '--diff-filter=ACMRT', commit)
            if any(private(p) for p in paths(changed)):
                raise ValueError('Private paths occur in incoming upstream history')
    return 'integration' if policy['role'] == 'upstream' or base == 'main' else 'fast'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--event', default=os.getenv('GITHUB_EVENT_PATH'))
    p.add_argument('--policy', required=True)
    args = p.parse_args()
    try:
        if os.getenv('GITHUB_EVENT_NAME') not in (None, 'pull_request', 'pull_request_target', 'push', 'workflow_dispatch'):
            raise ValueError('Unsupported event type')
        if not args.event:
            raise ValueError('PR event is required')
        stage = validate(json.load(open(args.event)), json.load(open(args.policy)), os.getenv('GITHUB_EVENT_NAME'))
        print('Policy passed: ' + stage)
        if os.getenv('GITHUB_OUTPUT'):
            with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
                output.write('stage=' + stage + '\n')
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError):
        print('Policy rejected: event, repository, branch, or private-path verification failed', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
