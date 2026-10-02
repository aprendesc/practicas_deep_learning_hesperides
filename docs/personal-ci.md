# Personal continuous integration

Use `<type>/<issue-number>-<title>` for contribution branches.

## Development

Start from `origin/develop`. Integrate into `origin/develop` without required unit or integration tests. Keep private context and agent instructions in origin.

## Publication

When the repositories differ, prepare a clean numbered branch from `upstream/develop`. Use `.github/personal-ci/prepare-upstream.py`. Transfer public changes without private history. Open a same-repository PR into `upstream/develop`. Run the privacy gate before push and merge. Unit tests are not required for this stage; existing integration validations run in the publication repository.

When origin and upstream identify the same repository, use one develop branch. Keep develop fast. Run validation on the release PR into main. Private development files can remain in this repository; this does not create a separate public destination.

## Release

Use a reviewed PR from develop into main. Require Personal policy and Integration where the GitHub plan supports required checks. Release only the validated main commit. Keep the repository's existing artifacts and deployments. Do not publish a release from a development fork.

## Installation and limitations

Local hooks are installed in the common Git directory and shared by existing worktrees. In each new clone, run `python3 .github/personal-ci/install-hooks.py` before publication. Fetch upstream develop before preparing a publication branch. A local hook cannot protect pushes made by another machine or a GitHub API client. Private repository rules need a GitHub plan that supports them. GitHub workflows report results even when that plan cannot make them mandatory.

This policy applies only to aprendesc origin repositories and aprendesc or pantagruel-alpha publication destinations. Do not alter corporate upstream CI.
