#!/usr/bin/env python3
"""Validate local personal CI pushes. Read refs once; do not contact a server."""
import json,os,pathlib,re,subprocess,sys
policy=json.load(open(pathlib.Path(__file__).with_name('personal-policy.json')))
def git(*args):return subprocess.check_output(['git',*args],stderr=subprocess.PIPE).decode().strip()
def identity(url):
 m=re.search(r'(?:github\.com(?:-[^/:]+)?[/:])([^/]+)/([^/]+)',url)
 return (m[1]+'/'+m[2].removesuffix('.git')).lower() if m else None
def private(path):
 parts=path.split('/')
 return parts[0] in {'context','skills','.agents','.codex','.claude','.githooks','.worktreelink'} or any(p in {'AGENTS.md','CLAUDE.md','SKILL.md'} for p in parts) or path.startswith('.github/skills/') or path in {'scripts/promote-to-upstream','scripts/prepare-upstream-branch'}
def stop(message):sys.exit('Personal CI push blocked: '+message)
try:
 destination=identity(sys.argv[2]);origin=policy['origin'];upstream=policy.get('upstream');same=origin==upstream
 # Corporate destinations retain their previous hook and policy.
 if destination not in {origin,upstream} or (destination!=origin and destination.split('/')[0] not in {'aprendesc','pantagruel-alpha'}):sys.exit(0)
 shared=destination==upstream and not same and upstream!=origin
 for line in sys.stdin.read().splitlines():
  local_ref,local_oid,remote_ref,remote_oid=line.split();deleted=set(local_oid)=={'0'}
  if remote_ref in {'refs/heads/main','refs/heads/master'} or (shared and remote_ref=='refs/heads/develop'):
   stop('base branches require a reviewed PR; origin/develop remains fast.')
  if deleted:continue
  if remote_ref.startswith('refs/heads/') and remote_ref!='refs/heads/develop':
   branch=remote_ref[len('refs/heads/'):]
   if (shared or set(remote_oid)=={'0'}) and not re.fullmatch(r'[a-z][a-z0-9_-]*/[0-9]+-[a-zA-Z0-9][a-zA-Z0-9._/-]*',branch):stop('new contribution branches must contain an issue number.')
  if shared:
   if any(private(p) for p in git('ls-tree','-r','--name-only',local_oid).splitlines()):stop('private paths remain in the proposed tree.')
   if set(remote_oid)=={'0'}:
    # For a new branch, exclude history already fetched from the shared develop.
    base=git('rev-parse','refs/remotes/upstream/develop');revision=base+'..'+local_oid
   else:revision=remote_oid+'..'+local_oid
   for commit in git('rev-list',revision).splitlines():
    changed=git('diff-tree','--root','-m','--diff-filter=ACMRT','--no-commit-id','--name-only','-r',commit).splitlines()
    if any(private(p) for p in changed):stop('incoming history contains private content.')
except (OSError,ValueError,IndexError,subprocess.CalledProcessError):stop('the destination or proposed history cannot be verified.')
