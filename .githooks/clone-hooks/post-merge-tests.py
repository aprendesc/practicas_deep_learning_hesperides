#!/usr/bin/env python3
"""Opt-in local functional battery after downstream/develop integration."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


def git(*args):
    return subprocess.check_output(['git', '--no-optional-locks', *args], stderr=subprocess.DEVNULL).decode().strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--force', action='store_true', help='Repeat a previously passed commit/configuration')
    args = parser.parse_args()
    root = Path(git('rev-parse', '--show-toplevel'))
    config = root / '.githooks/post-merge-tests.json'
    if not config.exists():
        return 0
    raw = config.read_bytes()
    cfg = json.loads(raw)
    if cfg.get('enabled') is not True:
        return 0
    if git('branch', '--show-current') != 'develop':
        return 0
    sha = git('rev-parse', 'HEAD')
    if sha != git('rev-parse', 'refs/remotes/downstream/develop'):
        raise ValueError('HEAD must match the freshly synchronized downstream/develop')
    if git('status', '--porcelain', '--untracked-files=no'):
        raise ValueError('Tracked changes present; preserve them and validate in a clean checkout')
    runner = cfg.get('runner')
    if not isinstance(runner, list) or not runner or not all(isinstance(x, str) and x for x in runner):
        raise ValueError('Configure runner as an argument array, e.g. [".venv/bin/python"]')
    timeout = cfg.get('timeout_seconds', 1800)
    if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0:
        raise ValueError('timeout_seconds must be a positive integer')
    scripts = sorted((root / 'context/tests').rglob('*_functional_test.py'))
    if not scripts:
        raise ValueError('No functional scripts found in context/tests')
    tracked = set(git('ls-files', 'context/tests').splitlines())
    if any(p.relative_to(root).as_posix() not in tracked or p.is_symlink() for p in scripts):
        raise ValueError('Battery must contain tracked regular scripts only')
    state = Path(git('rev-parse', '--absolute-git-dir')) / 'post-merge-tests'
    state.mkdir(exist_ok=True)
    key = sha + ':' + hashlib.sha256(raw).hexdigest()
    report = state / 'latest.json'
    if report.exists():
        previous = json.loads(report.read_text())
        if not args.force and previous.get('key') == key and previous.get('status') == 'passed':
            print('Post-merge functional tests: already passed for this commit/configuration')
            return 0
    lock = state / 'running'
    try:
        lock.mkdir()
    except FileExistsError:
        raise ValueError('Battery already running (inspect Git-local post-merge-tests/running)')
    result = {'key': key, 'commit': sha, 'started_at': time.time(), 'status': 'running', 'tests': []}
    try:
        report.write_text(json.dumps(result, indent=2))
        for i, script in enumerate(scripts):
            relative = script.relative_to(root).as_posix()
            log = state / f'{i:03d}.log'
            with log.open('wb') as output:
                try:
                    run = subprocess.run([*runner, relative], cwd=root, stdout=output, stderr=subprocess.STDOUT, timeout=timeout)
                    code = run.returncode
                except subprocess.TimeoutExpired:
                    code = 124
            result['tests'].append({'script': relative, 'exit_code': code, 'log': str(log)})
            report.write_text(json.dumps(result, indent=2))
            if code:
                result['status'] = 'failed'
                break
        else:
            result['status'] = 'passed'
        if git('rev-parse', 'HEAD') != sha or git('status', '--porcelain', '--untracked-files=no'):
            result['status'] = 'failed'
            result['reason'] = 'Checkout changed during validation; inspect and preserve changes'
        result['finished_at'] = time.time()
        report.write_text(json.dumps(result, indent=2))
        print('Post-merge functional tests: ' + result['status'] + '; ' + str(report))
        return 0 if result['status'] == 'passed' else 1
    except BaseException:
        result['status'] = 'error'
        report.write_text(json.dumps(result, indent=2))
        raise
    finally:
        lock.rmdir()


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print('Post-merge functional tests: ERROR: ' + str(exc), file=sys.stderr)
        sys.exit(1)
