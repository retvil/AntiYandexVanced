"""Extended-edition scans: whole Yandex products beyond the browser.

Covers Store (Appx) applications — Yandex Music, Alice, Messenger, etc. —
and product install directories under Program Files\\Yandex that are not
the browser itself.
"""

import os
import shutil
import subprocess

import backup

_STORE_APPS_PS = (
    "[Console]::OutputEncoding=[Text.Encoding]::UTF8;"
    "Get-AppxPackage | Where-Object { $_.Name -match 'yandex' }"
    " | ForEach-Object { \"$($_.Name)|$($_.PackageFullName)\" }"
)


def _parse_appx_output(text: str) -> list[tuple[str, str]]:
    """Parse 'Name|PackageFullName' lines produced by the Appx scan script."""
    result = []
    for line in text.splitlines():
        line = line.strip()
        if "|" in line and line != "|":
            name, _, full_name = line.partition("|")
            if name and full_name:
                result.append((name, full_name))
    return result


def scan_store_apps() -> list[str]:
    """Yandex Store (Appx) applications installed for the current user."""
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-Command", _STORE_APPS_PS],
            capture_output=True, timeout=120,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    text = proc.stdout.decode("utf-8", errors="replace")
    return [
        f"Store app: {name} ({full_name})"
        for name, full_name in _parse_appx_output(text)
    ]


def remove_store_app(finding: str) -> bool:
    """Uninstall one Store app by its package full name.

    Args:
        finding: a "Store app: Name (PackageFullName)" finding string.

    Returns:
        True if Remove-AppxPackage reported success.
    """
    full_name = finding[len("Store app: "):].rsplit(" (", 1)[0].rstrip(")")
    escaped = full_name.replace("'", "''")
    script = (
        "[Console]::OutputEncoding=[Text.Encoding]::UTF8;"
        f"Remove-AppxPackage -Package '{escaped}'"
    )
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True, timeout=180,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return proc.returncode == 0


def scan_product_dirs() -> list[str]:
    """Non-browser Yandex product directories in Program Files.

    The browser install path is reported by scan_install_paths as
    "Install path: ..."; everything else under Yandex\\ (Yandex Disk,
    Punto Switcher, IME, ...) is reported here.
    """
    found = []
    for base in (
        r"C:\Program Files\Yandex",
        r"C:\Program Files (x86)\Yandex",
    ):
        if not os.path.isdir(base):
            continue
        for entry in os.listdir(base):
            path = os.path.join(base, entry)
            if os.path.isdir(path) and entry.lower() != "yandexbrowser":
                found.append(f"Product dir: {path}")
    return found


def remove_product_dir(finding: str) -> bool:
    """Delete one non-browser product directory (exported to backup first)."""
    target = finding[len("Product dir: "):]
    backup.export_dir(target)
    try:
        shutil.rmtree(target, ignore_errors=False)
        return True
    except OSError:
        return False
