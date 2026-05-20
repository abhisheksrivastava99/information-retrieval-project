"""Dataset download helpers for Git LFS-backed CSV files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
import tempfile

DATA_REPO_URL = "https://github.com/abhisheksrivastava99/information-retrieval-project.git"
CODE_BRANCH = "main"
DATA_BRANCH = "dataset-lfs"
TARGET_DIRECTORY = "data"
EXPECTED_DATA_FILES = ("businesses_CA(Sheet1).csv", "reviews_CA(Sheet1).csv")
_POINTER_HEADER = "version https://git-lfs.github.com/spec/v1"


class DatasetFetchError(RuntimeError):
    """Raised when the GitHub/LFS dataset download flow cannot complete."""


@dataclass(frozen=True)
class FetchResult:
    paths: tuple[Path, ...]
    reused_existing: bool


def expected_dataset_paths(project_dir: str | Path | None = None) -> tuple[Path, ...]:
    base_dir = Path(project_dir) if project_dir else Path.cwd()
    data_dir = base_dir / TARGET_DIRECTORY
    return tuple(data_dir / filename for filename in EXPECTED_DATA_FILES)


def fetch_dataset(
    force: bool = False,
    project_dir: str | Path | None = None,
) -> FetchResult:
    base_dir = Path(project_dir) if project_dir else Path.cwd()
    target_paths = expected_dataset_paths(base_dir)

    if not force and all(path.exists() for path in target_paths):
        return FetchResult(paths=target_paths, reused_existing=True)

    ensure_git_tools()

    with tempfile.TemporaryDirectory(prefix="business_review_dataset_") as temp_dir:
        clone_dir = Path(temp_dir) / "dataset-source"
        clone_dataset_branch(clone_dir)

        source_paths = tuple(resolve_source_file(clone_dir, filename) for filename in EXPECTED_DATA_FILES)
        for path in source_paths:
            if is_lfs_pointer_file(path):
                raise DatasetFetchError(
                    f"{path.name} is still a Git LFS pointer file. "
                    "Run `git lfs install`, then retry `python app.py fetch-data`."
                )

        target_dir = base_dir / TARGET_DIRECTORY
        target_dir.mkdir(parents=True, exist_ok=True)
        for source_path, target_path in zip(source_paths, target_paths):
            shutil.copy2(source_path, target_path)

    return FetchResult(paths=target_paths, reused_existing=False)


def ensure_git_tools() -> None:
    run_command(["git", "--version"], error_prefix="Git is required")
    run_command(["git", "lfs", "version"], error_prefix="Git LFS is required")


def clone_dataset_branch(destination: Path) -> None:
    run_command(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "--single-branch",
            "--branch",
            DATA_BRANCH,
            DATA_REPO_URL,
            str(destination),
        ],
        error_prefix=f"Failed to clone dataset branch `{DATA_BRANCH}`",
    )
    run_command(
        ["git", "lfs", "pull"],
        cwd=destination,
        error_prefix=f"Failed to download Git LFS objects from `{DATA_BRANCH}`",
    )


def resolve_source_file(clone_dir: Path, filename: str) -> Path:
    candidate_paths = (
        clone_dir / TARGET_DIRECTORY / filename,
        clone_dir / filename,
    )
    for path in candidate_paths:
        if path.exists():
            return path
    locations = ", ".join(str(path.relative_to(clone_dir)) for path in candidate_paths)
    raise DatasetFetchError(
        f"Could not find `{filename}` in the `{DATA_BRANCH}` branch. "
        f"Expected one of: {locations}."
    )


def is_lfs_pointer_file(path: str | Path) -> bool:
    file_path = Path(path)
    with file_path.open("rb") as handle:
        preview = handle.read(256).decode("utf-8", errors="ignore")
    lines = [line.strip() for line in preview.splitlines() if line.strip()]
    if not lines:
        return False
    return (
        lines[0] == _POINTER_HEADER
        and any(line.startswith("oid sha256:") for line in lines[1:])
        and any(line.startswith("size ") for line in lines[1:])
    )


def run_command(
    command: list[str],
    cwd: str | Path | None = None,
    error_prefix: str = "Command failed",
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError as exc:
        raise DatasetFetchError(
            f"{error_prefix}: `{command[0]}` is not installed or not available on PATH."
        ) from exc
    except subprocess.CalledProcessError as exc:
        details = (exc.stderr or exc.stdout or "").strip()
        if details:
            raise DatasetFetchError(f"{error_prefix}: {details}") from exc
        raise DatasetFetchError(
            f"{error_prefix}: `{subprocess.list2cmdline(command)}` exited with code {exc.returncode}."
        ) from exc
