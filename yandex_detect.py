"""Detection of every known way Yandex installs itself as default search / browser.

Scan returns a list of human-readable findings. Each check is independent;
a failing check is skipped silently (missing keys/profiles are normal).
"""

import json
import os
import shutil
import sqlite3
import struct
import winreg
from pathlib import Path

YANDEX_MARKERS: tuple[str, ...] = ("yandex", "яндекс", "ya.ru", "yandex.ru")

YANDEX_PATHS: tuple[str, ...] = (
    r"C:\Program Files (x86)\Yandex\YandexBrowser",
    r"C:\Program Files\Yandex\YandexBrowser",
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Yandex", "YandexBrowser"),
    os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "Local", "Yandex", "YandexBrowser"),
)

# Chromium-family browsers: display name -> "User Data" directory under LOCALAPPDATA
CHROMIUM_BROWSERS: dict[str, str] = {
    "Google Chrome": r"Google\Chrome\User Data",
    "Microsoft Edge": r"Microsoft\Edge\User Data",
    "Brave": r"BraveSoftware\Brave-Browser\User Data",
    "Vivaldi": r"Vivaldi\User Data",
    "Yandex Browser": r"Yandex\YandexBrowser\User Data",
}

# Chromium policy registry roots: (hive, subkey)
CHROMIUM_POLICY_KEYS: tuple[tuple[int, str], ...] = (
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Google\Chrome"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Edge"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\BraveSoftware\Brave"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Vivaldi"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\OperaSoftware\Opera"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Yandex\YandexBrowser"),
)

UNINSTALL_PATHS: tuple[tuple[int, str], ...] = (
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
)

RUN_KEYS: tuple[tuple[int, str], ...] = (
    (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
    (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
)


def _is_yandex(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in YANDEX_MARKERS)


def _reg_enum_values(hive: int, path: str) -> list[tuple[str, str]]:
    """Return (name, value) string pairs; empty list on any error."""
    try:
        with winreg.OpenKey(hive, path, 0, winreg.KEY_READ) as key:
            result = []
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    if isinstance(value, str):
                        result.append((name, value))
                    i += 1
                except OSError:
                    break
            return result
    except OSError:
        return []


def _reg_enum_subkey_names(hive: int, path: str) -> list[str]:
    try:
        with winreg.OpenKey(hive, path, 0, winreg.KEY_READ) as key:
            names = []
            i = 0
            while True:
                try:
                    names.append(winreg.EnumKey(key, i))
                    i += 1
                except OSError:
                    break
            return names
    except OSError:
        return []


def _reg_get_string(hive: int, path: str, value_name: str) -> str | None:
    try:
        with winreg.OpenKey(hive, path, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, value_name)
            return value if isinstance(value, str) else None
    except OSError:
        return None


def scan_install_paths() -> list[str]:
    """Yandex Browser installation directories on disk."""
    return [p for p in YANDEX_PATHS if os.path.exists(p)]


def scan_uninstall_entries() -> list[str]:
    """Uninstall registry entries referencing Yandex."""
    found = []
    for hive, path in UNINSTALL_PATHS:
        for subkey in _reg_enum_subkey_names(hive, path):
            display = _reg_get_string(hive, f"{path}\\{subkey}", "DisplayName")
            if display and _is_yandex(display):
                found.append(f"{path}\\{subkey} (DisplayName={display})")
    return found


def scan_default_browser() -> list[str]:
    """Windows default browser association (UserChoice ProgId) pointing to Yandex."""
    found = []
    base = r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations"
    for protocol in ("http", "https"):
        prog_id = _reg_get_string(
            winreg.HKEY_CURRENT_USER, f"{base}\\{protocol}\\UserChoice", "ProgId"
        )
        if prog_id and _is_yandex(prog_id):
            found.append(f"Default browser ({protocol}): {prog_id}")
    return found


def scan_start_menu_internet() -> list[str]:
    """Registered browser clients (StartMenuInternet) referencing Yandex."""
    found = []
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        path = r"SOFTWARE\Clients\StartMenuInternet"
        for subkey in _reg_enum_subkey_names(hive, path):
            display = _reg_get_string(hive, f"{path}\\{subkey}", "")
            if (display and _is_yandex(display)) or _is_yandex(subkey):
                found.append(f"{path}\\{subkey}")
    return found


def scan_yandex_software_keys() -> list[str]:
    """Standalone Yandex software keys (settings, updates, telemetry)."""
    found = []
    paths = (
        (winreg.HKEY_CURRENT_USER, r"Software\Yandex"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Yandex"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Yandex"),
    )
    for hive, path in paths:
        try:
            winreg.OpenKey(hive, path)
            found.append(path)
        except OSError:
            continue
    return found


def scan_policy_hijack() -> list[str]:
    """Yandex enforcing itself via enterprise policies (the 'hard' way).

    Covers both Yandex's own policy key and any Chromium DefaultSearchProvider*
    policy whose URL/name points to Yandex.
    """
    found = []
    for hive, path in CHROMIUM_POLICY_KEYS:
        for name, value in _reg_enum_values(hive, path):
            if _is_yandex(str(value)):
                found.append(f"Policy hijack: {path}\\{name} = {value}")
    return found


def scan_chromium_profiles() -> list[str]:
    """Per-profile Chromium Preferences with Yandex as default search engine."""
    found = []
    local = os.environ.get("LOCALAPPDATA", "")
    for browser, rel in CHROMIUM_BROWSERS.items():
        user_data = Path(local) / rel
        if not user_data.is_dir():
            continue
        for profile_dir in user_data.iterdir():
            prefs_file = profile_dir / "Preferences"
            if not prefs_file.is_file():
                continue
            try:
                prefs = json.loads(prefs_file.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            data = (
                prefs.get("default_search_provider_data", {}).get("template_url_data", {})
            )
            haystack = f"{data.get('short_name', '')} {data.get('url', '')} {data.get('keyword', '')}"
            if _is_yandex(haystack):
                found.append(f"{browser} [{profile_dir.name}]: default search = Yandex")
    return found


def scan_web_data_keywords() -> list[str]:
    """Chromium 'Web Data' SQLite keyword table entries pointing to Yandex."""
    found = []
    local = os.environ.get("LOCALAPPDATA", "")
    for browser, rel in CHROMIUM_BROWSERS.items():
        user_data = Path(local) / rel
        if not user_data.is_dir():
            continue
        for profile_dir in user_data.iterdir():
            web_data = profile_dir / "Web Data"
            if not web_data.is_file():
                continue
            try:
                conn = sqlite3.connect(f"file:{web_data}?immutable=1", uri=True)
                rows = conn.execute(
                    "SELECT short_name, url FROM keywords"
                ).fetchall()
                conn.close()
            except sqlite3.Error:
                continue
            for short_name, url in rows:
                if _is_yandex(f"{short_name} {url}"):
                    found.append(f"{browser} [{profile_dir.name}]: keyword '{short_name}' -> {url}")
    return found


def _lz4_block_decompress(data: bytes, uncompressed_size: int) -> bytes:
    """Minimal LZ4 block decompressor (enough for Firefox mozlz4 files)."""
    out = bytearray()
    src = 0
    while len(out) < uncompressed_size and src < len(data):
        token = data[src]
        src += 1
        literal_len = token >> 4
        if literal_len == 15:
            while True:
                extra = data[src]
                src += 1
                literal_len += extra
                if extra != 255:
                    break
        out += data[src:src + literal_len]
        src += literal_len
        if src >= len(data) or len(out) >= uncompressed_size:
            break
        offset = struct.unpack_from("<H", data, src)[0]
        src += 2
        match_len = token & 0x0F
        if match_len == 15:
            while True:
                extra = data[src]
                src += 1
                match_len += extra
                if extra != 255:
                    break
        match_len += 4
        match_start = len(out) - offset
        for i in range(match_len):
            out.append(out[match_start + i])
    return bytes(out)


def scan_firefox_search() -> list[str]:
    """Firefox search.json.mozlz4 containing Yandex engine entries."""
    found = []
    candidates = [
        Path(os.environ.get("APPDATA", "")) / "Mozilla" / "Firefox" / "Profiles",
        Path(os.environ.get("APPDATA", "")) / "Waterfox" / "Profiles",
    ]
    for profiles_root in candidates:
        if not profiles_root.is_dir():
            continue
        for profile_dir in profiles_root.iterdir():
            mozlz4 = profile_dir / "search.json.mozlz4"
            if not mozlz4.is_file():
                continue
            try:
                raw = mozlz4.read_bytes()
                if not raw.startswith(b"mozLz40\0"):
                    continue
                size = struct.unpack_from("<I", raw, 8)[0]
                text = _lz4_block_decompress(raw[12:], size).decode("utf-8", errors="ignore")
            except (OSError, struct.error, IndexError):
                continue
            if _is_yandex(text):
                found.append(f"Firefox [{profile_dir.name}]: Yandex in search.json.mozlz4")
    return found


def scan_search_scopes() -> list[str]:
    """Legacy IE/Windows SearchScopes entries pointing to Yandex."""
    found = []
    path = r"Software\Microsoft\Internet Explorer\SearchScopes"
    for subkey in _reg_enum_subkey_names(winreg.HKEY_CURRENT_USER, path):
        url = _reg_get_string(winreg.HKEY_CURRENT_USER, f"{path}\\{subkey}", "URL")
        if url and _is_yandex(url):
            found.append(f"SearchScopes\\{subkey} -> {url}")
    return found


def scan_autostart() -> list[str]:
    """Run/RunOnce autostart entries launching Yandex components."""
    found = []
    for hive, path in RUN_KEYS:
        for name, value in _reg_enum_values(hive, path):
            if _is_yandex(name) or _is_yandex(value):
                found.append(f"{path}\\{name} = {value}")
    return found


def scan_all() -> list[str]:
    """Run every detection vector and return combined findings."""
    findings: list[str] = []
    findings += [f"Install path: {p}" for p in scan_install_paths()]
    findings += scan_uninstall_entries()
    findings += scan_default_browser()
    findings += scan_start_menu_internet()
    findings += scan_yandex_software_keys()
    findings += scan_policy_hijack()
    findings += scan_chromium_profiles()
    findings += scan_web_data_keywords()
    findings += scan_firefox_search()
    findings += scan_search_scopes()
    findings += scan_autostart()
    return findings


# --- Removal of hijack vectors -------------------------------------------------
# Every remover returns (removed, failed) lists of human-readable descriptions.


def _reg_delete_tree(hive: int, path: str) -> None:
    """Recursively delete a registry key with all its subkeys."""
    try:
        with winreg.OpenKey(hive, path, 0, winreg.KEY_ALL_ACCESS) as key:
            while True:
                try:
                    subkey = winreg.EnumKey(key, 0)
                except OSError:
                    break
                _reg_delete_tree(hive, f"{path}\\{subkey}")
        winreg.DeleteKey(hive, path)
    except OSError as exc:
        raise OSError(f"{path}: {exc}") from exc


def remove_install_paths() -> tuple[list[str], list[str]]:
    """Delete Yandex Browser installation directories from disk."""
    removed: list[str] = []
    failed: list[str] = []
    for path in scan_install_paths():
        try:
            shutil.rmtree(path, ignore_errors=False)
            removed.append(path)
        except OSError:
            failed.append(path)
    return removed, failed


def remove_uninstall_entries() -> tuple[list[str], list[str]]:
    """Delete Yandex uninstall registry entries."""
    removed: list[str] = []
    failed: list[str] = []
    for hive, path in UNINSTALL_PATHS:
        for subkey in _reg_enum_subkey_names(hive, path):
            display = _reg_get_string(hive, f"{path}\\{subkey}", "DisplayName")
            if display and _is_yandex(display):
                try:
                    _reg_delete_tree(hive, f"{path}\\{subkey}")
                    removed.append(f"{path}\\{subkey}")
                except OSError:
                    failed.append(f"{path}\\{subkey}")
    return removed, failed


def remove_default_browser_assoc() -> tuple[list[str], list[str]]:
    """Reset Windows default-browser association if it points to Yandex.

    Deleting the UserChoice key makes Windows fall back to its default
    selection (the user may be asked to pick a browser again).
    """
    removed: list[str] = []
    failed: list[str] = []
    base = r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations"
    for protocol in ("http", "https"):
        user_choice = f"{base}\\{protocol}\\UserChoice"
        prog_id = _reg_get_string(winreg.HKEY_CURRENT_USER, user_choice, "ProgId")
        if prog_id and _is_yandex(prog_id):
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, user_choice)
                removed.append(f"{protocol} UserChoice ({prog_id})")
            except OSError:
                failed.append(f"{protocol} UserChoice")
    return removed, failed


def remove_start_menu_internet() -> tuple[list[str], list[str]]:
    """Delete Yandex browser client registrations (StartMenuInternet)."""
    removed: list[str] = []
    failed: list[str] = []
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        path = r"SOFTWARE\Clients\StartMenuInternet"
        for subkey in _reg_enum_subkey_names(hive, path):
            display = _reg_get_string(hive, f"{path}\\{subkey}", "")
            if (display and _is_yandex(display)) or _is_yandex(subkey):
                try:
                    _reg_delete_tree(hive, f"{path}\\{subkey}")
                    removed.append(f"{path}\\{subkey}")
                except OSError:
                    failed.append(f"{path}\\{subkey}")
    return removed, failed


def remove_yandex_software_keys() -> tuple[list[str], list[str]]:
    """Delete standalone Yandex software key trees."""
    removed: list[str] = []
    failed: list[str] = []
    paths = (
        (winreg.HKEY_CURRENT_USER, r"Software\Yandex"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Yandex"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Yandex"),
    )
    for hive, path in paths:
        try:
            winreg.OpenKey(hive, path)
        except OSError:
            continue
        try:
            _reg_delete_tree(hive, path)
            removed.append(path)
        except OSError:
            failed.append(path)
    return removed, failed


def remove_policy_hijack() -> tuple[list[str], list[str]]:
    """Delete policy values that force Yandex as default search."""
    removed: list[str] = []
    failed: list[str] = []
    for hive, path in CHROMIUM_POLICY_KEYS:
        for name, value in _reg_enum_values(hive, path):
            if not _is_yandex(str(value)):
                continue
            try:
                with winreg.OpenKey(hive, path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, name)
                removed.append(f"{path}\\{name}")
            except OSError:
                failed.append(f"{path}\\{name}")
    return removed, failed


def remove_chromium_profile_search() -> tuple[list[str], list[str]]:
    """Strip Yandex default-search data from Chromium profile Preferences.

    Browsers must be closed; locked files are reported as failed.
    """
    removed: list[str] = []
    failed: list[str] = []
    local = os.environ.get("LOCALAPPDATA", "")
    for browser, rel in CHROMIUM_BROWSERS.items():
        user_data = Path(local) / rel
        if not user_data.is_dir():
            continue
        for profile_dir in user_data.iterdir():
            prefs_file = profile_dir / "Preferences"
            if not prefs_file.is_file():
                continue
            try:
                prefs = json.loads(prefs_file.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            data = prefs.get("default_search_provider_data", {}).get("template_url_data", {})
            haystack = f"{data.get('short_name', '')} {data.get('url', '')} {data.get('keyword', '')}"
            if not _is_yandex(haystack):
                continue
            try:
                del prefs["default_search_provider_data"]
                prefs_file.write_text(json.dumps(prefs), encoding="utf-8")
                removed.append(f"{browser} [{profile_dir.name}]")
            except OSError:
                failed.append(f"{browser} [{profile_dir.name}] (browser running?)")
    return removed, failed


def remove_web_data_keywords() -> tuple[list[str], list[str]]:
    """Delete Yandex keyword rows from Chromium 'Web Data' SQLite databases.

    Browsers must be closed; locked databases are reported as failed.
    """
    removed: list[str] = []
    failed: list[str] = []
    local = os.environ.get("LOCALAPPDATA", "")
    for browser, rel in CHROMIUM_BROWSERS.items():
        user_data = Path(local) / rel
        if not user_data.is_dir():
            continue
        for profile_dir in user_data.iterdir():
            web_data = profile_dir / "Web Data"
            if not web_data.is_file():
                continue
            try:
                conn = sqlite3.connect(web_data)
                rows = conn.execute(
                    "SELECT short_name, url FROM keywords"
                ).fetchall()
                yandex_rows = [r for r in rows if _is_yandex(f"{r[0]} {r[1]}")]
                if not yandex_rows:
                    conn.close()
                    continue
                conn.execute(
                    "DELETE FROM keywords WHERE url LIKE '%yandex%' OR url LIKE '%ya.ru%'"
                )
                conn.commit()
                conn.close()
                removed.append(f"{browser} [{profile_dir.name}] ({len(yandex_rows)} rows)")
            except sqlite3.Error:
                failed.append(f"{browser} [{profile_dir.name}] (database locked)")
    return removed, failed


def remove_firefox_yandex() -> tuple[list[str], list[str]]:
    """Reset Firefox search engine config by deleting search.json.mozlz4.

    Firefox rebuilds the file with default engines on next start.
    """
    removed: list[str] = []
    failed: list[str] = []
    candidates = [
        Path(os.environ.get("APPDATA", "")) / "Mozilla" / "Firefox" / "Profiles",
        Path(os.environ.get("APPDATA", "")) / "Waterfox" / "Profiles",
    ]
    for profiles_root in candidates:
        if not profiles_root.is_dir():
            continue
        for profile_dir in profiles_root.iterdir():
            mozlz4 = profile_dir / "search.json.mozlz4"
            if not mozlz4.is_file():
                continue
            try:
                raw = mozlz4.read_bytes()
                if not raw.startswith(b"mozLz40\0"):
                    continue
                size = struct.unpack_from("<I", raw, 8)[0]
                text = _lz4_block_decompress(raw[12:], size).decode("utf-8", errors="ignore")
            except (OSError, struct.error, IndexError):
                continue
            if not _is_yandex(text):
                continue
            try:
                mozlz4.unlink()
                removed.append(f"Firefox [{profile_dir.name}]")
            except OSError:
                failed.append(f"Firefox [{profile_dir.name}] (browser running?)")
    return removed, failed


def remove_search_scopes() -> tuple[list[str], list[str]]:
    """Delete legacy SearchScopes entries pointing to Yandex."""
    removed: list[str] = []
    failed: list[str] = []
    path = r"Software\Microsoft\Internet Explorer\SearchScopes"
    for subkey in _reg_enum_subkey_names(winreg.HKEY_CURRENT_USER, path):
        url = _reg_get_string(winreg.HKEY_CURRENT_USER, f"{path}\\{subkey}", "URL")
        if url and _is_yandex(url):
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, f"{path}\\{subkey}")
                removed.append(f"SearchScopes\\{subkey}")
            except OSError:
                failed.append(f"SearchScopes\\{subkey}")
    return removed, failed


def remove_autostart() -> tuple[list[str], list[str]]:
    """Delete Run/RunOnce autostart values launching Yandex components."""
    removed: list[str] = []
    failed: list[str] = []
    for hive, path in RUN_KEYS:
        for name, value in _reg_enum_values(hive, path):
            if not (_is_yandex(name) or _is_yandex(value)):
                continue
            try:
                with winreg.OpenKey(hive, path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, name)
                removed.append(f"{path}\\{name}")
            except OSError:
                failed.append(f"{path}\\{name}")
    return removed, failed


def remove_all_hijacks() -> tuple[list[str], list[str]]:
    """Remove every detected Yandex hijack vector.

    Returns:
        (removed, failed) combined lists across all vectors.
    """
    removed: list[str] = []
    failed: list[str] = []
    for remover in (
        remove_uninstall_entries,
        remove_default_browser_assoc,
        remove_start_menu_internet,
        remove_yandex_software_keys,
        remove_policy_hijack,
        remove_chromium_profile_search,
        remove_web_data_keywords,
        remove_firefox_yandex,
        remove_search_scopes,
        remove_autostart,
    ):
        part_removed, part_failed = remover()
        removed += part_removed
        failed += part_failed
    return removed, failed
