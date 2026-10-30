#!/usr/bin/env python3
"""Verify local publication identity and keep environment files outside Git."""
import json, re, subprocess, sys
from pathlib import Path
from urllib.parse import urlsplit
policy=json.loads((Path(__file__).parent/'clone-policy.json').read_text())
def identity(url):
    if '://' in url:
        p=urlsplit(url);host,path=p.hostname or '',p.path
    else:host,_,path=url.split('@')[-1].partition(':')
    host=re.sub(r'^github\.com-.*$', 'github.com',host.lower())
    return host+'/'+path.strip('/').removesuffix('.git').lower()
if sys.argv[1:] == ['--staged']:
    files=subprocess.check_output(['git','diff','--cached','--name-only','--diff-filter=ACMR','-z']).decode().split('\0')
    names=set(policy['local_env_files'])|{'.env','code/.env','.env.local','code/.env.local'}
    if any(f in names for f in files):sys.exit('Commit blocked: local environment configuration must remain outside Git.')
elif len(sys.argv)>2 and sys.argv[1]=='downstream' and identity(sys.argv[2])!=identity(policy['downstream_url']):
    sys.exit('Push blocked: downstream destination differs from the verified repository.')
