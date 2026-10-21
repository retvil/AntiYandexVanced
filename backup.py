"""Backup and operation log for destructive actions.

Every registry key / file about to be modified or deleted is first exported
into a per-session backup folder under %APPDATA%\\AntiYandexVanced\\backup\\.
All actions are appended to a plain-text log for support purposes.

All functions are best-effort: a backup failure never blocks the removal.
"""

import os
import shutil
import subprocess
import winreg
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(os.environ.get("APPDATA", "")) / "AntiYandexVanced"
LOG_FILE = BASE_DIR / "antiyandex.log"

_HIVE_NAMES = {
    winreg.HKEY_LOCAL_MACHINE: "HKLM",
    winreg.HKEY_CURRENT_USER: "HKCU",
}

_session_dir: Path | None = None


def start_session() -> Path:
    """Open a new backup session folder (one per removal run)."""
    global _session_dir
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    _session_dir = BASE_DIR / "backup" / stamp
    return _session_dir


def _ensure_session() -> Path:
    global _session_dir
    if _session_dir is None:
        start_session()
    assert _session_dir is not None
    return _session_dir


def log_action(message: str) -> None:
    """Append a timestamped line to the operation log (best-effort)."""
    try:
        BASE_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as fh:
            fh.write(f"{datetime.now():%Y-%m-%d %H:%M:%S}  {message}\n")
    except OSError:
        pass


def export_key(hive: int, path: str) -> None:
    """Export a registry key (with subkeys) to a .reg file (best-effort)."""
    try:
        dest = _ensure_session()
        dest.mkdir(parents=True, exist_ok=True)
        hive_name = _HIVE_NAMES.get(hive, "HKU")
        safe = path.replace("\\", "_")
        out = dest / f"{hive_name}_{safe}.reg"
        subprocess.run(
            ["reg", "export", f"{hive_name}\\{path}", str(out), "/y"],
            capture_output=True,
            check=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        pass


def copy_file(path: str | os.PathLike) -> None:
    """Copy a file into the backup session folder (best-effort)."""
    try:
        src = Path(path)
        if not src.is_file():
            return
        dest = _ensure_session() / "files"
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest / src.name)
    except OSError:
        pass


def export_dir(path: str | os.PathLike) -> None:
    """Copy every file under a directory into the backup session folder (best-effort).

    Relative structure is preserved under files/<dir name>/ so name
    collisions between subdirectories cannot overwrite each other.
    """
    try:
        src_root = Path(path)
        if not src_root.is_dir():
            return
        dest_root = _ensure_session() / "files" / src_root.name
        for src in src_root.rglob("*"):
            if src.is_file():
                dest = dest_root / src.relative_to(src_root)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
    except OSError:
        pass


def save_task_xml(task_name: str) -> None:
    """Save a scheduled task definition as XML before deleting it."""
    try:
        dest = _ensure_session()
        dest.mkdir(parents=True, exist_ok=True)
        safe = task_name.strip("\\").replace("\\", "_").replace("/", "_")
        out = dest / f"task_{safe}.xml"
        proc = subprocess.run(
            ["schtasks", "/query", "/tn", task_name, "/xml"],
            capture_output=True,
            timeout=30,
        )
        if proc.returncode == 0:
            out.write_bytes(proc.stdout)
    except (OSError, subprocess.SubprocessError):
        pass
