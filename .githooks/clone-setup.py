#!/usr/bin/env python3
"""Install this repository's local Git safeguards and optional local env copies."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from urllib.parse import urlsplit

def git(root, *args, check=True):
    r = subprocess.run(['git', '--no-optional-locks', '-C', str(root), *args], capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError('Git configuration could not be verified: ' + args[0])
    return r.stdout.strip()

def identity(url):
    if '://' in url:
        parsed = urlsplit(url)
        host, path = parsed.hostname or '', parsed.path
    else:
        host, _, path = url.split('@')[-1].partition(':')
    if host.startswith('github.com-'):
        host = 'github.com'
    return host.lower() + '/' + path.strip('/').removesuffix('.git').lower()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--source-base', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    policy = json.loads((root / '.githooks/clone-setup.json').read_text())
    expected = identity(policy['downstream_url'])
    if identity(git(root, 'remote', 'get-url', '--push', 'downstream')) != expected:
        raise RuntimeError('Downstream does not match this repository; no changes made')
    upstream = git(root, 'remote', 'get-url', 'upstream', check=False)
    if upstream and identity(upstream) != identity(policy['upstream_url']):
        raise RuntimeError('Upstream differs from the verified repository configuration')
    target = Path(git(root, 'rev-parse', '--path-format=absolute', '--git-path', 'organization-hooks'))
    source = root / '.githooks/clone-hooks'
    if not args.check:
        if not upstream:
            git(root, 'remote', 'add', 'upstream', policy['upstream_url'])
            git(root, 'remote', 'set-url', '--push', 'upstream', 'no_push')
        previous = git(root, 'config', '--get', 'core.hooksPath', check=False)
        if previous and Path(previous).resolve() != target.resolve():
            old = Path(previous) if Path(previous).is_absolute() else root / previous
            saved = target.parent / 'organization-hooks-before'
            if old.is_dir() and not saved.exists():
                shutil.copytree(old, saved, symlinks=True)
        target.mkdir(parents=True, exist_ok=True)
        for f in source.iterdir():
            if f.is_file():
                shutil.copy2(f, target / f.name)
                if f.name.startswith(('pre-', 'post-')):
                    (target / f.name).chmod(0o755)
        shutil.copy2(root / '.githooks/clone-setup.json', target / 'clone-policy.json')
        git(root, 'config', 'core.hooksPath', str(target))
        if args.source_base:
            base = args.source_base.resolve()
            if identity(git(base, 'remote', 'get-url', '--push', 'downstream')) != expected:
                raise RuntimeError('Env source does not belong to this downstream')
            for name in policy['local_env_files']:
                src, dest = base / name, root / name
                if not src.is_file():
                    raise RuntimeError('Required local env source is unavailable: ' + name)
                if dest.is_file():
                    continue
                if dest.is_symlink():
                    raise RuntimeError('Broken env link requires explicit repair: ' + name)
                text = src.read_text().replace(str(base), str(root))
                dest.parent.mkdir(parents=True, exist_ok=True)
                with dest.open('x') as stream:
                    stream.write(text)
                dest.chmod(0o600)
    configured = git(root, 'config', '--get', 'core.hooksPath', check=False)
    effective = Path(configured) if configured else root / '.git/hooks'
    if not effective.is_absolute():
        effective = root / effective
    problems = []
    for f in source.iterdir():
        installed = effective / f.name
        if not installed.is_file() or installed.read_bytes() != f.read_bytes():
            problems.append('Hook payload missing or outdated: ' + f.name)
    for hook in ['pre-commit', 'pre-push']:
        if not os.access(effective / hook, os.X_OK):
            problems.append('Hook is not executable: ' + hook)
    if not git(root, 'remote', 'get-url', 'upstream', check=False):
        problems.append('Upstream identity is absent')
    for name in policy['local_env_files']:
        if not (root / name).is_file():
            problems.append('Required local env file absent: ' + name)
        elif not git(root, 'check-ignore', '--', name, check=False):
            problems.append('Local env file is not excluded from Git: ' + name)
    for name in ['AGENTS.md', 'context/issues', 'context/sessions']:
        if not (root / name).exists():
            problems.append('Repository structure missing: ' + name)
    print(json.dumps({'repository': policy['repository'], 'local_configuration_ready': not problems, 'problems': problems}))
    return bool(problems)

if __name__ == '__main__':
    raise SystemExit(main())
