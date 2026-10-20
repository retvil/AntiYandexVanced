"""User exclusions for scan findings, persisted across sessions.

Excluded findings are deselected by default in future scans, but the user
can still pick them in the selection dialog.
"""

import json
import os
from pathlib import Path

BASE_DIR = Path(os.environ.get("APPDATA", "")) / "AntiYandexVanced"
EXCLUSIONS_FILE = BASE_DIR / "exclusions.json"


def load() -> set[str]:
    """Load the exclusion set; empty set on missing or corrupt file."""
    try:
        data = json.loads(EXCLUSIONS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    if not isinstance(data, list):
        return set()
    return {item for item in data if isinstance(item, str)}


def save(items: set[str]) -> None:
    """Persist the exclusion set (best effort, never raises)."""
    try:
        BASE_DIR.mkdir(parents=True, exist_ok=True)
        EXCLUSIONS_FILE.write_text(
            json.dumps(sorted(items), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError:
        pass


def is_excluded(finding: str, items: set[str] | None = None) -> bool:
    """True if the finding is in the exclusion set."""
    if items is None:
        items = load()
    return finding in items


def add(finding: str) -> None:
    """Add one finding to the exclusion set."""
    items = load()
    items.add(finding)
    save(items)


def clear() -> None:
    """Remove all exclusions."""
    save(set())
