#!/usr/bin/env python3
"""Keep the worktree mechanism out of upstream trees and incoming history."""
import re
import subprocess
import sys
from urllib.parse import urlsplit


def git(*args):
    return subprocess.check_output(["git", *args], stderr=subprocess.PIPE).decode().strip()


def identity(url):
    if "://" in url:
        parsed = urlsplit(url)
        host, path = parsed.hostname or "", parsed.path
    else:
        host, _, path = url.split("@")[-1].partition(":")
    host = re.sub(r"^github\.com-.*$", "github.com", host.lower())
    return host + "/" + path.strip("/").removesuffix(".git").lower()


def main():
    refs = sys.stdin.read().splitlines()
    origin = identity(git("remote", "get-url", "--push", "origin"))
    upstream = subprocess.run(["git", "remote", "get-url", "--push", "--all", "upstream"], capture_output=True, text=True)
    destinations = {identity(x) for x in upstream.stdout.splitlines()}
    applies = sys.argv[1] == "upstream" or (identity(sys.argv[2]) in destinations and identity(sys.argv[2]) != origin)
    if not applies:
        return
    paths = [".githooks", ".worktreelink"]
    for line in refs:
        local_ref, local_oid, remote_ref, remote_oid = line.split()
        if set(local_oid) == {"0"}:
            continue
        if git("ls-tree", "-r", "--name-only", local_oid, "--", *paths):
            sys.exit("Push blocked: the worktree mechanism belongs only in origin.")
        revision = local_oid if set(remote_oid) == {"0"} else remote_oid + ".." + local_oid
        for commit in git("rev-list", revision).splitlines():
            if git("diff-tree", "--root", "-m", "--no-commit-id", "--name-only", "-r", commit, "--", *paths):
                sys.exit("Push blocked: incoming upstream history contains the worktree mechanism.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        sys.exit("Push blocked: cannot verify the worktree publication boundary: " + str(error))
