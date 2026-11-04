# Independent clone setup

Run `python3 .githooks/clone-setup.py` from this checkout to install its versioned Git safeguards. The installer copies the canonical APC Harness hook suite, removes any other file from the hook directory and verifies repository identities. Local hooks do not govern GitHub API operations; downstream rulesets protect `develop` and `main` on the server.

For a Worker clone, add `--source-base /absolute/path/to/this/repository` to recover missing local environment files from its verified base. Existing environment files are preserved. Credentials remain ignored and are never printed or committed.

Run `python3 .githooks/clone-setup.py --check` to verify the installed safeguards, required local env files and repository structure. Prepare dependencies using this repository's manifests and lockfiles, then verify its runtime separately. A successful hook/configuration check alone does not certify application readiness.

Keep contracts, their functional scripts and issue documentation in `context/issues/<issue>/<issue>.md` and the same issue folder. Keep meeting summaries in `context/sessions/`. Neutral standby uses the local `develop` branch, clean and synchronized with `downstream/develop`.

## Publication boundary

The APC Harness recovery trees also classify their skill Markdown, skill `agents/openai.yaml` and host `PROJECTS.md` as private methodology metadata. This does not whitelist runtime code or arbitrary YAML under those trees.

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
- **Pushes.** `develop` and `main` are never deleted or rewritten. On downstream, new `develop` commits are private-only, or integrate `upstream/develop`; an Inditex `develop` integrates its upstream base branch and equals it plus private files and downstream PRs already merged and pending upstream; a push never adds its own divergence. Task branches need an open issue, `context/issues/<issue>/<issue>.md` with the current coding contract blocks (Context, Diff, Test Profiling, Persistence, Execution plan and Results and reporting). Context contains Descripción and Specialized skills. Empty initial scaffolding is accepted; populated Test Profiling declares tracked issue/global validation scripts with unique executable cell IDs registered in the contract. Documentary contracts use Context, Reglas de redacción y construcción, Índice and Documento: the first three blocks carry delta timestamps, while Documento remains undated. General contracts require only a level-one title, Descripción and Persistencia; their optional blocks do not inherit coding checks. Explicit legacy documentary forms remain readable. No project-map or worktreelink is required. Unnumbered branches are rejected on downstream. A distinct upstream only receives a branch whose homonymous `downstream/<branch>` exists and whose public content, after filtering private paths and private `.gitignore` lines, is exactly that of the downstream branch; downstream personal CI never reaches a corporate upstream, in the tree or in incoming history. The downstream PR comes first: merging the branch into `downstream/develop` must change nothing, file by file (merge or squash, even when another task touches the same file; a file the branch creates must have all its lines in develop). Tasks reach upstream independently: the branch cannot contain another downstream PR still pending upstream; update task branches from the upstream base, not from a `develop` that carries other pending tasks.
- **Merges.** A merge that drops private methodology content or a contract link prints a warning. A merge that brings a newer versioned hook baseline reinstalls it.

APC Harness owns the canonical suite in `.githooks/clone-hooks/`; the private `.githooks/sync-base-hooks.py` in APC Harness distributes it only to the direct base repositories and the three declared Hespérides teaching bases, excluding recovery checkouts and Worker clones. Edit it there, never in a single repository.
