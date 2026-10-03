#!/usr/bin/env python3
"""Share declared local state and prepare environments in a linked worktree."""
import argparse
import glob
import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib


def git(root, *args):
    env = os.environ.copy()
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR"):
        env.pop(key, None)
    return subprocess.check_output(["git", "-C", str(root), *args], env=env).decode().strip()


def is_link(path):
    return path.is_symlink() or getattr(path, "is_junction", lambda: False)()


def remove_link(path):
    if getattr(path, "is_junction", lambda: False)():
        path.rmdir()
    else:
        path.unlink()


def local_excludes(root, paths):
    filename = Path(git(root, "rev-parse", "--git-path", "info/exclude"))
    if not filename.is_absolute():
        filename = root / filename
    begin, end = "# BEGIN worktree-setup", "# END worktree-setup"
    content = filename.read_text() if filename.exists() else ""
    if begin in content:
        before, rest = content.split(begin, 1)
        if end not in rest:
            raise ValueError("The worktree exclude block is incomplete.")
        content = before + rest.split(end, 1)[1].lstrip("\n")
    block = begin + "\n" + "\n".join("/" + p.rstrip("/") for p in sorted(set(paths))) + "\n" + end + "\n"
    filename.parent.mkdir(parents=True, exist_ok=True)
    filename.write_text(content.rstrip("\n") + "\n\n" + block)


def repair_links(main, current, patterns):
    target_files = set(git(current, "ls-files", "-z").split("\0"))
    source_files = set(git(main, "ls-files", "-z").split("\0"))
    tracked = target_files | source_files
    parents = {str(parent) for name in tracked if name for parent in Path(name).parents}
    errors = []

    def link(source, relative):
        target = current / relative
        if relative in tracked:
            return
        if not source.exists():
            errors.append(f"Missing canonical source: {relative}")
            return
        if relative in parents and source.is_dir():
            # Keep versioned placeholders and link only the local children.
            for child in source.iterdir():
                if child.name not in {".git", ".venv", "node_modules"}:
                    link(child, str(Path(relative) / child.name))
            return
        for parent in target.parents:
            if parent == current:
                break
            if is_link(parent):
                canonical = main / parent.relative_to(current)
                if parent.resolve() == canonical.resolve():
                    return
                errors.append(f"Cannot write through an unrelated link: {parent.relative_to(current)}")
                return
        if is_link(target):
            if target.resolve() == source.resolve() and target.exists():
                return
            remove_link(target)
        elif target.exists():
            if target.is_dir() and not any(target.iterdir()):
                target.rmdir()
            else:
                errors.append(f"Preserved existing local data: {relative}")
                return
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            target.symlink_to(source, target_is_directory=source.is_dir())
        except OSError:
            if os.name != "nt" or not source.is_dir():
                raise
            # A junction does not require Windows Developer Mode.
            subprocess.run(["cmd", "/c", "mklink", "/J", str(target), str(source)], check=True)
        print(f"worktree: linked {relative}", file=sys.stderr)

    for pattern in patterns:
        managed = pattern.endswith("/")
        pattern = pattern.rstrip("/")
        if Path(pattern).is_absolute() or any(p in {"..", ".git", ".venv", "venv", "node_modules"} for p in Path(pattern).parts):
            raise ValueError(f"Unsafe shared path: {pattern}")
        if managed and not glob.has_magic(pattern) and not (main / pattern).exists():
            if is_link(main / pattern):
                errors.append(f"Broken canonical source: {pattern}")
                continue
            (main / pattern).mkdir(parents=True, exist_ok=True)
        for source_name in glob.glob(str(main / pattern)):
            source = Path(source_name)
            if source.exists():
                link(source, str(source.relative_to(main)))
            else:
                errors.append(f"Missing canonical source: {source.relative_to(main)}")
    return errors


def prepare_environments(main, current, config):
    env = os.environ.copy()
    for key in ("VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT", "PYTHONPATH", "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR"):
        env.pop(key, None)
    def project_path(relative):
        project = current / relative
        if Path(relative).is_absolute() or not project.resolve().is_relative_to(current):
            raise ValueError("The environment must stay inside this worktree.")
        return project
    for relative in config.get("python_projects", []):
        project = project_path(relative)
        if not (project / "pyproject.toml").is_file():
            continue  # This branch does not contain the configured project.
        venv = project / ".venv"
        if is_link(venv):
            remove_link(venv)  # Remove the link only; keep the shared environment.
        settings = tomllib.loads((project / "pyproject.toml").read_text())
        sources = settings.get("tool", {}).get("uv", {}).get("sources", {})
        external = {}
        for name, source in sources.items():
            if isinstance(source, dict) and "path" in source:
                source_path = (project / source["path"]).resolve()
                if not source_path.is_relative_to(current):
                    canonical = (main / relative / source["path"]).resolve()
                    if not canonical.exists():
                        raise ValueError(f"Missing local dependency: {name}")
                    external[name] = canonical
        command = ["uv", "sync"]
        if (project / "uv.lock").is_file():
            command.append("--frozen")
        for name in external:
            command.extend(["--no-install-package", name])
        python_env = dict(env, UV_PROJECT_ENVIRONMENT=str(venv))
        subprocess.run(command, cwd=project, env=python_env, check=True)
        for name, source in external.items():
            interpreter = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            subprocess.run(["uv", "pip", "install", "--python", str(interpreter), "--no-deps", "--editable", str(source)], cwd=project, env=python_env, check=True)
    for relative in config.get("python_standalone", []):
        project = project_path(relative["directory"])
        if not project.is_dir():
            continue
        venv = project / ".venv"
        if is_link(venv):
            remove_link(venv)
        subprocess.run(["uv", "venv", "--allow-existing", "--python", relative["python"], str(venv)], cwd=project, env=env, check=True)
        requirements = project / relative.get("requirements", "requirements.lock")
        if requirements.is_file():
            interpreter = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            subprocess.run(["uv", "pip", "install", "--python", str(interpreter), "-r", str(requirements)], cwd=project, env=env, check=True)
    for spec in config.get("node_projects", []):
        project = project_path(spec["directory"])
        if not (project / "package.json").is_file():
            continue
        if is_link(project / "node_modules"):
            remove_link(project / "node_modules")
        subprocess.run(spec["command"], cwd=project, env=env, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--links-only", action="store_true")
    args = parser.parse_args()
    current = Path(git(Path.cwd(), "rev-parse", "--show-toplevel")).resolve()
    principal = Path(git(current, "worktree", "list", "--porcelain").splitlines()[0].removeprefix("worktree ")).resolve()
    if current == principal:
        return 0
    cache = Path(git(current, "rev-parse", "--path-format=absolute", "--git-common-dir")) / "worktree-setup"
    manifest = principal / ".worktreelink"
    if not manifest.is_file():
        manifest = cache / ".worktreelink"
    patterns = [line.split("#", 1)[0].strip() for line in manifest.read_text().splitlines()]
    patterns = [p for p in patterns if p]
    config_path = principal / ".githooks/worktree-setup.json"
    if not config_path.is_file():
        config_path = cache / "worktree-setup.json"
    config = json.loads(config_path.read_text())
    excludes = patterns + [str(Path(p) / ".venv") for p in config.get("python_projects", [])]
    excludes += [str(Path(p["directory"]) / ".venv") for p in config.get("python_standalone", [])]
    excludes += [str(Path(p["directory"]) / "node_modules") for p in config.get("node_projects", [])]
    for p in config.get("python_projects", []):
        lock = str(Path(p) / "uv.lock")
        if not git(current, "ls-files", "--", lock):
            excludes.append(lock)
    local_excludes(current, excludes)
    errors = repair_links(principal, current, patterns)
    if not args.links_only and os.environ.get("WORKTREELINK_SKIP_SYNC") != "1":
        prepare_environments(principal, current, config)
    for error in errors:
        print("worktree: " + error, file=sys.stderr)
    return bool(errors)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        sys.exit(f"Worktree setup failed; rerun python3 {Path(__file__).absolute()}: {error}")
