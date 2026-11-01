#!/usr/bin/env python3
"""Install worktree automation without replacing existing publication guards."""
from pathlib import Path
import shutil
import subprocess


def git(*args):
    return subprocess.check_output(["git", *args]).decode().strip()


root = Path(git("rev-parse", "--show-toplevel")).resolve()
principal = Path(git("worktree", "list", "--porcelain").splitlines()[0].removeprefix("worktree ")).resolve()
if root != principal:
    raise SystemExit("Install from the principal checkout.")
common = Path(git("rev-parse", "--path-format=absolute", "--git-common-dir"))
cache = common / "worktree-setup"
cache.mkdir(parents=True, exist_ok=True)
for name in ("worktree-setup.py", "worktree-publication-guard.py", "worktree-setup.json"):
    shutil.copyfile(root / ".githooks" / name, cache / name)
shutil.copyfile(root / ".worktreelink", cache / ".worktreelink")
configured = subprocess.run(["git", "config", "--get", "core.hooksPath"], capture_output=True, text=True).stdout.strip()
hooks = Path(configured) if configured else Path(git("rev-parse", "--git-common-dir")) / "hooks"
if not hooks.is_absolute():
    hooks = root / hooks
hooks.mkdir(parents=True, exist_ok=True)
marker = "# worktree-setup dispatcher"
post = hooks / "post-checkout"
if post.exists() and marker not in post.read_text() and "enlazar_estado_local" not in post.read_text():
    backup = hooks / "post-checkout.before-worktree-setup"
    if backup.exists():
        raise SystemExit("An existing post-checkout backup requires review.")
    post.rename(backup)
post.write_text((root / ".githooks/post-checkout").read_text())
post.chmod(0o755)
push = hooks / "pre-push"
if push.exists() and marker not in push.read_text():
    backup = hooks / "pre-push.before-worktree-setup"
    if backup.exists():
        raise SystemExit("An existing pre-push backup requires review.")
    push.rename(backup)
push.write_text('''#!/usr/bin/env bash
set -euo pipefail
# worktree-setup dispatcher
hook_dir="$(cd "$(dirname "$0")" && pwd)"
principal="$(git worktree list --porcelain | sed -n '1s/^worktree //p')"
refs="$(mktemp)"
trap 'rm -f "$refs"' EXIT
cat > "$refs"
guard="$principal/.githooks/worktree-publication-guard.py"
if [ ! -f "$guard" ]; then
    common="$(git rev-parse --path-format=absolute --git-common-dir)"
    guard="$common/worktree-setup/worktree-publication-guard.py"
fi
python3 "$guard" "$@" < "$refs"
if [ -x "$hook_dir/pre-push.before-worktree-setup" ]; then
    "$hook_dir/pre-push.before-worktree-setup" "$@" < "$refs"
elif git config --get filter.lfs.clean >/dev/null 2>&1; then
    git lfs pre-push "$@" < "$refs"
fi
''')
push.chmod(0o755)
print("Installed worktree setup and publication guard in " + str(hooks))
