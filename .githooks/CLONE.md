# Independent clone setup

Run `python3 .githooks/clone-setup.py` from this checkout to install its versioned Git safeguards. The installer copies the canonical APC Harness hook suite, removes any other file from the hook directory and verifies repository identities. Local hooks do not govern GitHub API operations; downstream rulesets protect `develop` and `main` on the server.

For a Worker clone, add `--source-base /absolute/path/to/this/repository` to recover missing local environment files from its verified base. Existing environment files are preserved. Credentials remain ignored and are never printed or committed.

Run `python3 .githooks/clone-setup.py --check` to verify the installed safeguards, required local env files and repository structure. Prepare dependencies using this repository's manifests and lockfiles, then verify its runtime separately. A successful hook/configuration check alone does not certify application readiness.

Keep contracts, their functional scripts and issue documentation in `context/issues/<issue>/<issue>.md` and the same issue folder. Keep meeting summaries in `context/sessions/`. Neutral standby uses the local `develop` branch, clean and synchronized with `downstream/develop`.

## Publication boundary

Version all context and agent instructions in downstream. Ignore rules must not
exclude these files or contain exceptions for them. Secrets remain ignored.
For a distinct upstream, `scripts/promote-to-upstream <existing-upstream-branch> [source-ref]`
prepares a filtered local commit from committed source, without changing the checkout
or pushing. It removes private methodology paths and their mentions in `.gitignore`
files. Review `publish/<existing-upstream-branch>` before any authorized publication.
The pre-push hook checks the proposed tree and incoming history and rejects private
paths or ignore traces. It does not rewrite commits. Existing publication branches
and conflicts require review; the preparer does not overwrite them.

## Methodology guards

`methodology-guard.py` enforces the development methodology:

- **Commits.** `develop` accepts only private methodology files, merges in progress and paths in `develop_paths`; `main` accepts none. A task branch `<type>/<issue>-<title>` needs its contract or a `[Local Contract]` link in `AGENTS.md`. A Worker workspace holds only repository clones. With `residue_guard`, working residue is rejected.
- **Pushes.** `develop` and `main` are never deleted or rewritten. On downstream, new `develop` commits are private-only, or integrate `upstream/develop`; an Inditex `develop` equals `upstream/develop` plus private files. Task branches need an open issue, `context/issues/<issue>/<issue>.md` with `## Execution plan` first, `## Context` and `### Applicable skills`, and `context/project-map.md`. Unnumbered branches are rejected on downstream.
- **Merges.** A merge that drops private methodology content or a contract link prints a warning. A merge that brings a newer versioned hook baseline reinstalls it.

APC Harness owns the canonical suite in `.githooks/clone-hooks/`; `scripts/sync_git_hooks.py` distributes it. Edit it there, never in a single repository.
