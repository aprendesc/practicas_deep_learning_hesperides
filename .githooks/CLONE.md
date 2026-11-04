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

## Optional local post-merge functional battery

Disabled by default in every repository. Missing `.githooks/post-merge-tests.json` or `"enabled": false` means no tests and no report writes. Configure each repository independently; never enable it during setup or synchronization without authorization. Example configuration:

```json
{"enabled": false, "runner": [".venv/bin/python"], "timeout_seconds": 1800}
```

To opt in, agree the global scenarios and prepared runtime, set `runner` to an argument array (for example `["uv", "run", "python"]`) and version `"enabled": true` through the normal contribution workflow. Set it back to `false` to disable it. Synchronization preserves existing settings and never enables a repository.

After a downstream PR merge, fetch the verified downstream remote and synchronize a clean local `develop` to `downstream/develop`, preserving pending work. The installed `post-merge` hook invokes the runner on local merges, including fast-forward updates. A GitHub merge alone cannot trigger a local hook: the executing agent must synchronize locally and invoke `python3 -B .githooks/clone-hooks/post-merge-tests.py`, including when synchronization used checkout/reset or no merge event occurred. Do not run this as a standby timer.

When enabled, the runner requires local `develop`, HEAD equal to the freshly fetched downstream tracking ref, and no tracked changes. It runs all tracked `context/tests/**/*_functional_test.py` scripts sequentially in the local repository environment, stopping at the first failure or timeout (per script). No matching scripts is a configuration error. The runner does not fetch, merge, install dependencies or execute issue scripts automatically. A script may invoke Databricks if its agreed validation requires it; a local launcher does not make that workload local.

Results and stdout/stderr remain in `<git-dir>/post-merge-tests/latest.json` and numbered logs. A successful commit/configuration is deduplicated; use `--force` for an intentional rerun after runtime/data changes. A running lock prevents concurrent batteries in the checkout; remove a stale lock only after verifying no execution remains. Timeouts do not guarantee cancellation of remote jobs started by a script.

A failure is reported and leaves closure pending; record it in the contract and resolve it before claiming successful validation. The merge is already applied and is never rolled back by this hook. Disabled execution is not evidence of passing tests and does not waive issue validation.

## Shared repository publication branches

When upstream and downstream identify the same repository, contracts use upstream `main`/`master`, downstream `develop`, and `publish/<issue-branch>` for publication. Prepare a filtered snapshot with `python3 -B .githooks/clone-hooks/publication.py prepare-mapped refs/remotes/downstream/<issue-branch> main publish/<issue-branch>` after fetching the verified source and base. It creates one local commit parented by the upstream base, removes private paths and ignore traces, and preserves the checkout. Existing publication branches are never overwritten. Publication guards check filtered content and new history even for shared destinations; mapped branches must equal their downstream issue's public content. Existing upstream ancestry is preserved, not scrubbed. Publishing or merging requires the user's applicable authorization; preparing a branch does not approve its PR merge.
