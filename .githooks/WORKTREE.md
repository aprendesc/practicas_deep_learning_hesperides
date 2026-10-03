# Worktree setup

The principal checkout owns the shared local state. `.worktreelink` declares its
project-specific paths. `.githooks/worktree-setup.json` declares the Python and
Node projects that need independent environments.

Install once after cloning, from the principal checkout:

```sh
python3 .githooks/install-worktree-setup.py
```

Git then runs setup when Codex creates a worktree or checks out a branch. The
dispatcher reads the configuration from the principal checkout. The checked-out
branch does not need to contain these private files.

Setup repairs missing, broken, and incorrectly targeted links. It preserves
tracked files, local data, and existing publication guards. Shared directories
with tracked placeholders retain those files and link only their local children.
Python `.venv` and Node `node_modules` remain inside each worktree. Python setup
uses `uv` and the branch's lockfile; Node setup uses the configured package manager.
Missing tools, dependencies, credentials, or conflicting local data produce an
explicit failure. Windows directory links use junctions when symlinks are unavailable.

Run setup again from a worktree to repair it:

```sh
python3 /absolute/path/to/principal/.githooks/worktree-setup.py
```

Use `--links-only` to repair state without installing dependencies. For temporary
Git inspections, `WORKTREELINK_SKIP_SYNC=1` skips dependency installation.

Version `.githooks/` and `.worktreelink` only in `origin`. The installer adds a
pre-push guard and preserves the previous one. Upstream promotion must remove
these paths from both the publication tree and incoming commits. Remotes that
point to the same repository provide no physical separation between destinations.
Git hooks are local safeguards; bypassing them can bypass their checks.
