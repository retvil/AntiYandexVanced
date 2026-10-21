"""Detection of every known way Yandex installs itself as default search / browser.

Scan returns a list of human-readable findings. Each check is independent;
a failing check is skipped silently (missing keys/profiles are normal).
"""

import csv
import io
import json
import os
import shutil
import sqlite3
import struct
import subprocess
import winreg
import zipfile
from pathlib import Path

import backup

YANDEX_MARKERS: tuple[str, ...] = ("yandex", "яндекс", "ya.ru", "yandex.ru", "punto")

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

# Chromium policy registry roots: (hive, subkey). Both HKLM (machine-wide)
# and HKCU (per-user) variants are scanned — hijackers use either.
_CHROMIUM_POLICY_SUBKEYS: tuple[str, ...] = (
    r"SOFTWARE\Policies\Google\Chrome",
    r"SOFTWARE\Policies\Microsoft\Edge",
    r"SOFTWARE\Policies\BraveSoftware\Brave",
    r"SOFTWARE\Policies\Vivaldi",
    r"SOFTWARE\Policies\OperaSoftware\Opera",
    r"SOFTWARE\Policies\Yandex\YandexBrowser",
)
CHROMIUM_POLICY_KEYS: tuple[tuple[int, str], ...] = tuple(
    (hive, f"{prefix}{subkey}")
    for hive, prefix in (
        (winreg.HKEY_LOCAL_MACHINE, ""),
        (winreg.HKEY_CURRENT_USER, ""),
    )
    for subkey in _CHROMIUM_POLICY_SUBKEYS
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


def _reg_enum_value_names(hive: int, path: str) -> list[str]:
    """Value names of any type (unlike _reg_enum_values, which keeps strings only)."""
    try:
        with winreg.OpenKey(hive, path, 0, winreg.KEY_READ) as key:
            names = []
            i = 0
            while True:
                try:
                    names.append(winreg.EnumValue(key, i)[0])
                    i += 1
                except OSError:
                    break
            return names
    except OSError:
        return []


def _ps_run(script: str) -> str:
    """Run a PowerShell snippet and return its stdout decoded as UTF-8."""
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True,
            timeout=120,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return proc.stdout.decode("utf-8", errors="replace")


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
        if offset == 0 or offset > len(out):
            raise ValueError("corrupt LZ4 block: invalid match offset")
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


def _decode_schtasks(raw: bytes) -> str:
    """Decode schtasks CSV output (OEM codepage on most systems)."""
    for encoding in ("utf-8", "cp866", "cp1251"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def scan_scheduled_tasks() -> list[str]:
    """Windows Task Scheduler entries referencing Yandex (updater tasks etc.)."""
    try:
        proc = subprocess.run(
            ["schtasks", "/query", "/fo", "csv", "/nh"],
            capture_output=True,
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    text = _decode_schtasks(proc.stdout)
    found = []
    for row in csv.reader(io.StringIO(text)):
        if not row:
            continue
        task_name = row[0]
        haystack = task_name + " " + (row[1] if len(row) > 1 else "")
        if _is_yandex(haystack):
            found.append(f"Scheduled task: {task_name}")
    return found


SERVICES_KEY = r"SYSTEM\CurrentControlSet\Services"


def scan_services() -> list[str]:
    """Windows services whose name, display name or binary path mentions Yandex.

    Reads the registry directly (fast, no subprocess per service).
    """
    found = []
    for service_name in _reg_enum_subkey_names(winreg.HKEY_LOCAL_MACHINE, SERVICES_KEY):
        key_path = f"{SERVICES_KEY}\\{service_name}"
        display = _reg_get_string(winreg.HKEY_LOCAL_MACHINE, key_path, "DisplayName") or ""
        image_path = _reg_get_string(winreg.HKEY_LOCAL_MACHINE, key_path, "ImagePath") or ""
        if _is_yandex(f"{service_name} {display} {image_path}"):
            found.append(f"Service: {service_name} ({display or service_name})")
    return found


def remove_service(service_name: str) -> bool:
    """Stop and delete a Windows service (registry key exported first)."""
    backup.export_key(winreg.HKEY_LOCAL_MACHINE, f"{SERVICES_KEY}\\{service_name}")
    try:
        subprocess.run(["sc", "stop", service_name], capture_output=True, timeout=60)
        proc = subprocess.run(
            ["sc", "delete", service_name], capture_output=True, timeout=60
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return proc.returncode == 0


FILE_EXTS_KEY = r"Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts"


def scan_file_associations() -> list[str]:
    """File extensions whose default app (UserChoice ProgId) is Yandex Browser."""
    found = []
    for ext in _reg_enum_subkey_names(winreg.HKEY_CURRENT_USER, FILE_EXTS_KEY):
        prog_id = _reg_get_string(
            winreg.HKEY_CURRENT_USER, f"{FILE_EXTS_KEY}\\{ext}\\UserChoice", "ProgId"
        )
        if prog_id and _is_yandex(prog_id):
            found.append(f"File association: {ext} -> {prog_id}")
    return found


def remove_file_association(ext: str) -> bool:
    """Delete the UserChoice key for one extension (exported first)."""
    user_choice = f"{FILE_EXTS_KEY}\\{ext}\\UserChoice"
    backup.export_key(winreg.HKEY_CURRENT_USER, user_choice)
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, user_choice)
        return True
    except OSError:
        return False


# --- Extended vectors (16-30) ---------------------------------------------------
# Findings with a prefix from CONSENT_PREFIXES touch user data (files, history,
# cookies, extensions, antivirus settings) — the GUI asks for extra confirmation.

CONSENT_PREFIXES: tuple[str, ...] = (
    "Roaming: ",
    "YandexDisk data: ",
    "YandexDisk files: ",
    "Extension: ",
    "Cookies: ",
    "Defender exclusion: ",
)

SHELL_OVERLAY_KEY = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\ShellIconOverlayIdentifiers"

_CONTEXT_MENU_PARENTS: tuple[str, ...] = (
    r"*\shellex\ContextMenuHandlers",
    r"AllFilesystemObjects\shellex\ContextMenuHandlers",
    r"Directory\shellex\ContextMenuHandlers",
    r"Directory\Background\shellex\ContextMenuHandlers",
    r"Folder\shellex\ContextMenuHandlers",
)


def scan_shell_overlays() -> list[str]:
    """Explorer icon-overlay handlers registered by Yandex Disk."""
    found = []
    for hive in _HIVES:
        for name in _reg_enum_subkey_names(hive, SHELL_OVERLAY_KEY):
            if _is_yandex(name):
                found.append(f"Shell overlay: {SHELL_OVERLAY_KEY}\\{name}")
    return found


def scan_context_menus() -> list[str]:
    """Explorer context-menu handlers registered by Yandex Disk."""
    found = []
    for parent in _CONTEXT_MENU_PARENTS:
        rel_parent = f"SOFTWARE\\Classes\\{parent}"
        for hive in _HIVES:
            for name in _reg_enum_subkey_names(hive, rel_parent):
                clsid = _reg_get_string(hive, f"{rel_parent}\\{name}", "") or ""
                if _is_yandex(f"{name} {clsid}"):
                    found.append(f"Context menu: {rel_parent}\\{name}")
    return found


STARTUP_APPROVED_KEYS: tuple[str, ...] = (
    r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
    r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run32",
    r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\StartupFolder",
)


def scan_startup_approved() -> list[str]:
    """Autostart entries that are disabled but still registered."""
    found = []
    for hive in _HIVES:
        for path in STARTUP_APPROVED_KEYS:
            for name in _reg_enum_value_names(hive, path):
                if _is_yandex(name):
                    found.append(f"StartupApproved: {path}\\{name}")
    return found


def scan_app_paths() -> list[str]:
    """App Paths registrations letting Yandex binaries launch by name."""
    found = []
    base = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"
    for hive in _HIVES:
        for subkey in _reg_enum_subkey_names(hive, base):
            default = _reg_get_string(hive, f"{base}\\{subkey}", "") or ""
            if _is_yandex(f"{subkey} {default}"):
                found.append(f"App Paths: {base}\\{subkey}")
    return found


def _shortcut_dirs() -> list[Path]:
    return [
        Path(os.environ.get("USERPROFILE", "")) / "Desktop",
        Path(os.environ.get("APPDATA", "")) / r"Microsoft\Windows\Start Menu",
        Path(r"C:\ProgramData\Microsoft\Windows\Start Menu"),
        Path(os.environ.get("APPDATA", ""))
        / r"Microsoft\Internet Explorer\Quick Launch\User Pinned\TaskBar",
    ]


def _lnk_mentions_yandex(path: Path) -> bool:
    """True if .lnk bytes mention Yandex (ASCII or UTF-16 target string)."""
    try:
        data = path.read_bytes()
    except OSError:
        return False
    if b"yandex" in data.lower():
        return True
    return any(
        word.encode("utf-16-le") in data
        for word in ("yandex", "Yandex", "яндекс", "Яндекс")
    )


def scan_shortcuts() -> list[str]:
    """Shortcuts to Yandex apps on Desktop, Start Menu and taskbar."""
    found = []
    for directory in _shortcut_dirs():
        if not directory.is_dir():
            continue
        for lnk in directory.rglob("*.lnk"):
            if _is_yandex(lnk.stem) or _lnk_mentions_yandex(lnk):
                found.append(f"Shortcut: {lnk}")
    return found


def scan_leftover_dirs() -> list[str]:
    """Leftover Yandex data directories (ProgramData, Roaming, Yandex Disk).

    Roaming/Yandex holds Punto Switcher history and diary; YandexDisk holds
    the user's synced files — both require explicit consent before removal.
    """
    found = []
    programdata = os.environ.get("ProgramData", r"C:\ProgramData")
    for entry in Path(programdata).glob("Yandex*"):
        if entry.is_dir():
            found.append(f"ProgramData: {entry}")
    roaming = Path(os.environ.get("APPDATA", "")) / "Yandex"
    if roaming.is_dir():
        found.append(f"Roaming: {roaming}")
    disk_cache = Path(os.environ.get("LOCALAPPDATA", "")) / "Yandex" / "YandexDisk2"
    if disk_cache.is_dir():
        found.append(f"YandexDisk data: {disk_cache}")
    disk_files = Path(os.environ.get("USERPROFILE", "")) / "YandexDisk"
    if disk_files.is_dir():
        found.append(f"YandexDisk files: {disk_files}")
    return found


HOSTS_FILE = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "drivers" / "etc" / "hosts"


def _hosts_yandex_lines(text: str) -> list[str]:
    """Non-comment hosts lines mentioning Yandex (pure function, testable)."""
    result = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and _is_yandex(stripped):
            result.append(stripped)
    return result


def scan_hosts() -> list[str]:
    """hosts-file entries redirecting or blocking Yandex domains."""
    try:
        text = HOSTS_FILE.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            text = HOSTS_FILE.read_text(encoding="cp1251")
        except OSError:
            return []
    except OSError:
        return []
    return [f"Hosts: {line}" for line in _hosts_yandex_lines(text)]


def _parse_firewall_output(text: str) -> list[tuple[str, str]]:
    """Parse 'name|display' lines produced by the firewall scan script."""
    result = []
    for line in text.splitlines():
        line = line.strip()
        if "|" in line and line != "|":
            name, _, display = line.partition("|")
            result.append((name, display))
    return result


_FIREWALL_SCAN_PS = (
    "[Console]::OutputEncoding=[Text.Encoding]::UTF8;"
    "Get-NetFirewallRule | ForEach-Object {"
    " $n=$_.Name; $d=$_.DisplayName;"
    " if (($n + ' ' + $d) -match 'yandex|яндекс') { \"$n|$d\" } }"
)


def scan_firewall_rules() -> list[str]:
    """Windows Firewall rules created for Yandex components."""
    text = _ps_run(_FIREWALL_SCAN_PS)
    return [
        f"Firewall rule: {name} ({display})"
        for name, display in _parse_firewall_output(text)
    ]


def scan_uri_protocols() -> list[str]:
    """URI protocol handlers registered by Yandex (yandexdisk://, ya://, ProgIDs)."""
    found = []
    for name in _reg_enum_subkey_names(winreg.HKEY_CLASSES_ROOT, ""):
        if _is_yandex(name) or name.lower() == "ya":
            found.append(f"Protocol: SOFTWARE\\Classes\\{name}")
    return found


def _chromium_profile_dirs() -> list[tuple[str, Path]]:
    """(browser, profile_dir) pairs for every existing Chromium profile."""
    result = []
    local = os.environ.get("LOCALAPPDATA", "")
    for browser, rel in CHROMIUM_BROWSERS.items():
        user_data = Path(local) / rel
        if not user_data.is_dir():
            continue
        for profile_dir in user_data.iterdir():
            if profile_dir.is_dir():
                result.append((browser, profile_dir))
    return result


def _firefox_profile_dirs() -> list[Path]:
    result = []
    for root in (
        Path(os.environ.get("APPDATA", "")) / "Mozilla" / "Firefox" / "Profiles",
        Path(os.environ.get("APPDATA", "")) / "Waterfox" / "Profiles",
    ):
        if root.is_dir():
            for profile_dir in root.iterdir():
                if profile_dir.is_dir():
                    result.append(profile_dir)
    return result


def scan_browser_extensions() -> list[str]:
    """Browser extensions whose manifest mentions Yandex (consent required)."""
    found = []
    for _browser, profile_dir in _chromium_profile_dirs():
        extensions_dir = profile_dir / "Extensions"
        if not extensions_dir.is_dir():
            continue
        for ext_dir in extensions_dir.iterdir():
            if not ext_dir.is_dir():
                continue
            for version_dir in ext_dir.iterdir():
                manifest = version_dir / "manifest.json"
                if not manifest.is_file():
                    continue
                try:
                    manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if _is_yandex(str(manifest_data.get("name", ""))):
                    found.append(f"Extension: {ext_dir}")
                    break
    for profile_dir in _firefox_profile_dirs():
        extensions_dir = profile_dir / "extensions"
        if not extensions_dir.is_dir():
            continue
        for xpi in extensions_dir.glob("*.xpi"):
            try:
                with zipfile.ZipFile(xpi) as archive:
                    manifest_data = json.loads(archive.read("manifest.json"))
            except (OSError, zipfile.BadZipFile, KeyError, json.JSONDecodeError):
                continue
            if _is_yandex(str(manifest_data.get("name", ""))):
                found.append(f"Extension: {xpi}")
    return found


_COOKIE_HOSTS: tuple[str, str] = ("%yandex%", "%ya.ru%")


def scan_cookies() -> list[str]:
    """Cookies for yandex.ru domains in browser profiles (consent required)."""
    found = []
    for browser, profile_dir in _chromium_profile_dirs():
        cookies_db = profile_dir / "Network" / "Cookies"
        if not cookies_db.is_file():
            cookies_db = profile_dir / "Cookies"
        if not cookies_db.is_file():
            continue
        try:
            conn = sqlite3.connect(f"file:{cookies_db}?immutable=1", uri=True)
            count = conn.execute(
                "SELECT COUNT(*) FROM cookies WHERE host_key LIKE ? OR host_key LIKE ?",
                _COOKIE_HOSTS,
            ).fetchone()[0]
            conn.close()
        except sqlite3.Error:
            continue
        if count:
            found.append(f"Cookies: {browser} [{profile_dir.name}] ({count} rows)")
    for profile_dir in _firefox_profile_dirs():
        cookies_db = profile_dir / "cookies.sqlite"
        if not cookies_db.is_file():
            continue
        try:
            conn = sqlite3.connect(f"file:{cookies_db}?immutable=1", uri=True)
            count = conn.execute(
                "SELECT COUNT(*) FROM moz_cookies WHERE host LIKE ? OR host LIKE ?",
                _COOKIE_HOSTS,
            ).fetchone()[0]
            conn.close()
        except sqlite3.Error:
            continue
        if count:
            found.append(f"Cookies: Firefox [{profile_dir.name}] ({count} rows)")
    return found


def _cookies_db_path(browser: str, profile_name: str) -> Path | None:
    """Locate the cookies database for one browser profile."""
    if browser == "Firefox":
        for profile_dir in _firefox_profile_dirs():
            if profile_dir.name == profile_name:
                return profile_dir / "cookies.sqlite"
        return None
    rel = CHROMIUM_BROWSERS.get(browser)
    if rel is None:
        return None
    profile_dir = Path(os.environ.get("LOCALAPPDATA", "")) / rel / profile_name
    db = profile_dir / "Network" / "Cookies"
    if db.is_file():
        return db
    db = profile_dir / "Cookies"
    return db if db.is_file() else None


def scan_openwith() -> list[str]:
    """'Open with' associations offering Yandex apps."""
    found = []
    for ext in _reg_enum_subkey_names(winreg.HKEY_CURRENT_USER, FILE_EXTS_KEY):
        ext_path = f"{FILE_EXTS_KEY}\\{ext}"
        progids_path = f"{ext_path}\\OpenWithProgids"
        for name in _reg_enum_value_names(winreg.HKEY_CURRENT_USER, progids_path):
            if _is_yandex(name):
                found.append(f"OpenWith: {progids_path}\\{name}")
        list_path = f"{ext_path}\\OpenWithList"
        for name, value in _reg_enum_values(winreg.HKEY_CURRENT_USER, list_path):
            if _is_yandex(value):
                found.append(f"OpenWith: {list_path}\\{name} = {value}")
    return found


def scan_traces() -> list[str]:
    """Harmless leftover traces: Prefetch, crash dumps, WER reports."""
    found = []
    prefetch = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "Prefetch"
    if prefetch.is_dir():
        for pf in prefetch.glob("*.pf"):
            if _is_yandex(pf.stem):
                found.append(f"Trace: {pf}")
    crash_dumps = Path(os.environ.get("LOCALAPPDATA", "")) / "CrashDumps"
    if crash_dumps.is_dir():
        for entry in crash_dumps.iterdir():
            if _is_yandex(entry.stem):
                found.append(f"Trace: {entry}")
    wer_root = Path(os.environ.get("LOCALAPPDATA", "")) / r"Microsoft\Windows\WER"
    for sub in ("ReportArchive", "ReportQueue"):
        directory = wer_root / sub
        if not directory.is_dir():
            continue
        for entry in directory.iterdir():
            if _is_yandex(entry.name):
                found.append(f"Trace: {entry}")
    return found


_DEFENDER_SCAN_PS = (
    "[Console]::OutputEncoding=[Text.Encoding]::UTF8;"
    "$p = Get-MpPreference;"
    "($p.ExclusionPath + $p.ExclusionProcess + $p.ExclusionExtension)"
    " | Where-Object { $_ -and ($_ -match 'yandex|яндекс') }"
)


def scan_defender_exclusions() -> list[str]:
    """Windows Defender exclusions added for Yandex (consent required)."""
    text = _ps_run(_DEFENDER_SCAN_PS)
    seen: set[str] = set()
    found = []
    for line in text.splitlines():
        item = line.strip()
        if item and item not in seen:
            seen.add(item)
            found.append(f"Defender exclusion: {item}")
    return found


KEYBOARD_LAYOUTS_KEY = r"SYSTEM\CurrentControlSet\Control\Keyboard Layouts"


def scan_keyboard_layouts() -> list[str]:
    """Custom keyboard layouts registered by Yandex IME."""
    found = []
    for klid in _reg_enum_subkey_names(winreg.HKEY_LOCAL_MACHINE, KEYBOARD_LAYOUTS_KEY):
        layout_path = f"{KEYBOARD_LAYOUTS_KEY}\\{klid}"
        layout_text = (
            _reg_get_string(winreg.HKEY_LOCAL_MACHINE, layout_path, "Layout Text")
            or _reg_get_string(winreg.HKEY_LOCAL_MACHINE, layout_path, "Layout Display Name")
            or ""
        )
        layout_file = _reg_get_string(winreg.HKEY_LOCAL_MACHINE, layout_path, "Layout File") or ""
        if _is_yandex(f"{layout_text} {layout_file}"):
            found.append(f"Keyboard layout: {klid} ({layout_text or layout_file})")
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
    findings += scan_scheduled_tasks()
    findings += scan_services()
    findings += scan_file_associations()
    findings += scan_shell_overlays()
    findings += scan_context_menus()
    findings += scan_startup_approved()
    findings += scan_app_paths()
    findings += scan_shortcuts()
    findings += scan_leftover_dirs()
    findings += scan_hosts()
    findings += scan_firewall_rules()
    findings += scan_uri_protocols()
    findings += scan_browser_extensions()
    findings += scan_cookies()
    findings += scan_openwith()
    findings += scan_traces()
    findings += scan_defender_exclusions()
    findings += scan_keyboard_layouts()
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
                backup.export_key(hive, f"{path}\\{subkey}")
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
            backup.export_key(winreg.HKEY_CURRENT_USER, user_choice)
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
                backup.export_key(hive, f"{path}\\{subkey}")
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
        backup.export_key(hive, path)
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
            backup.export_key(hive, path)
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
            backup.copy_file(prefs_file)
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
            except sqlite3.Error:
                failed.append(f"{browser} [{profile_dir.name}] (database locked)")
                continue
            try:
                rows = conn.execute(
                    "SELECT rowid, short_name, url FROM keywords"
                ).fetchall()
                yandex_rowids = [
                    rowid for rowid, short_name, url in rows
                    if _is_yandex(f"{short_name} {url}")
                ]
                if not yandex_rowids:
                    continue
                backup.copy_file(web_data)
                conn.executemany(
                    "DELETE FROM keywords WHERE rowid = ?",
                    [(rowid,) for rowid in yandex_rowids],
                )
                conn.commit()
                removed.append(
                    f"{browser} [{profile_dir.name}] ({len(yandex_rowids)} rows)"
                )
            except sqlite3.Error:
                failed.append(f"{browser} [{profile_dir.name}] (database locked)")
            finally:
                conn.close()
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
            backup.copy_file(mozlz4)
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
            backup.export_key(winreg.HKEY_CURRENT_USER, f"{path}\\{subkey}")
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
            backup.export_key(hive, path)
            try:
                with winreg.OpenKey(hive, path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, name)
                removed.append(f"{path}\\{name}")
            except OSError:
                failed.append(f"{path}\\{name}")
    return removed, failed


def remove_scheduled_tasks() -> tuple[list[str], list[str]]:
    """Delete Yandex-related scheduled tasks (definition saved as XML first)."""
    removed: list[str] = []
    failed: list[str] = []
    for finding in scan_scheduled_tasks():
        task_name = finding.split("Scheduled task: ", 1)[1]
        backup.save_task_xml(task_name)
        try:
            proc = subprocess.run(
                ["schtasks", "/delete", "/tn", task_name, "/f"],
                capture_output=True,
                timeout=60,
            )
        except (OSError, subprocess.SubprocessError):
            failed.append(task_name)
            continue
        if proc.returncode == 0:
            removed.append(task_name)
        else:
            failed.append(task_name)
    return removed, failed


def remove_all_hijacks() -> tuple[list[str], list[str]]:
    """Remove every detected Yandex hijack vector.

    A backup session is opened first; every key/file touched is exported
    into it before deletion.

    Returns:
        (removed, failed) combined lists across all vectors.
    """
    return remove_selected(scan_all())


# --- Per-item removal (selection dialog) ----------------------------------------
# Every finding string from scan_all() can be removed individually.

_HIVES = (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER)


def _delete_tree_any_hive(rel_path: str) -> bool:
    """Delete a registry key tree from whichever hive contains it."""
    for hive in _HIVES:
        try:
            winreg.OpenKey(hive, rel_path, 0, winreg.KEY_READ)
        except OSError:
            continue
        backup.export_key(hive, rel_path)
        _reg_delete_tree(hive, rel_path)
        return True
    return False


def _delete_value_any_hive(rel_path: str, value_name: str) -> bool:
    """Delete one registry value from whichever hive contains the key."""
    for hive in _HIVES:
        try:
            winreg.OpenKey(hive, rel_path, 0, winreg.KEY_READ)
        except OSError:
            continue
        backup.export_key(hive, rel_path)
        try:
            with winreg.OpenKey(hive, rel_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, value_name)
            return True
        except OSError:
            return False
    return False


def _clean_profile_preferences(browser: str, rel: str, profile_name: str) -> str:
    """Strip Yandex default-search data from one Chromium profile.

    Raises:
        OSError: if the Preferences file cannot be rewritten (browser running).
    """
    prefs_file = Path(os.environ.get("LOCALAPPDATA", "")) / rel / profile_name / "Preferences"
    prefs = json.loads(prefs_file.read_text(encoding="utf-8"))
    data = prefs.get("default_search_provider_data", {}).get("template_url_data", {})
    haystack = f"{data.get('short_name', '')} {data.get('url', '')} {data.get('keyword', '')}"
    if not _is_yandex(haystack):
        return ""
    backup.copy_file(prefs_file)
    del prefs["default_search_provider_data"]
    prefs_file.write_text(json.dumps(prefs), encoding="utf-8")
    return f"{browser} [{profile_name}]"


def _clean_profile_web_data(browser: str, rel: str, profile_name: str) -> str:
    """Delete Yandex keyword rows from one Chromium profile's Web Data.

    Raises:
        sqlite3.Error: if the database is locked (browser running).
    """
    web_data = Path(os.environ.get("LOCALAPPDATA", "")) / rel / profile_name / "Web Data"
    conn = sqlite3.connect(web_data)
    try:
        rows = conn.execute("SELECT rowid, short_name, url FROM keywords").fetchall()
        yandex_rowids = [
            rowid for rowid, short_name, url in rows if _is_yandex(f"{short_name} {url}")
        ]
        if not yandex_rowids:
            return ""
        backup.copy_file(web_data)
        conn.executemany(
            "DELETE FROM keywords WHERE rowid = ?", [(rowid,) for rowid in yandex_rowids]
        )
        conn.commit()
        return f"{browser} [{profile_name}] ({len(yandex_rowids)} rows)"
    finally:
        conn.close()


def _remove_firefox_profile(profile_name: str) -> str:
    """Delete search.json.mozlz4 in one Firefox/Waterfox profile.

    Raises:
        OSError: if the file cannot be deleted (browser running).
    """
    for profiles_root in (
        Path(os.environ.get("APPDATA", "")) / "Mozilla" / "Firefox" / "Profiles",
        Path(os.environ.get("APPDATA", "")) / "Waterfox" / "Profiles",
    ):
        mozlz4 = profiles_root / profile_name / "search.json.mozlz4"
        if mozlz4.is_file():
            backup.copy_file(mozlz4)
            mozlz4.unlink()
            return f"Firefox [{profile_name}]"
    return ""


def _remove_keyboard_layout(klid: str) -> bool:
    """Unregister one keyboard layout: Preload/Substitutes values + layout key."""
    ok = True
    for path in (r"Keyboard Layout\Preload", r"Keyboard Layout\Substitutes"):
        for name, value in _reg_enum_values(winreg.HKEY_CURRENT_USER, path):
            if value == klid and not _delete_value_any_hive(path, name):
                ok = False
    backup.export_key(winreg.HKEY_LOCAL_MACHINE, f"{KEYBOARD_LAYOUTS_KEY}\\{klid}")
    try:
        _reg_delete_tree(winreg.HKEY_LOCAL_MACHINE, f"{KEYBOARD_LAYOUTS_KEY}\\{klid}")
    except OSError:
        ok = False
    return ok


def _remove_one(finding: str, removed: list[str], failed: list[str]) -> None:
    """Remove a single finding; append a description to removed or failed."""
    if finding.startswith("Install path: "):
        target = finding[len("Install path: "):]
        try:
            shutil.rmtree(target, ignore_errors=False)
            removed.append(target)
        except OSError:
            failed.append(f"{target} (locked?)")
        return

    if finding.startswith(("Shell overlay: ", "Context menu: ", "App Paths: ", "Protocol: ")):
        rel_path = finding.split(": ", 1)[1]
        if _delete_tree_any_hive(rel_path):
            removed.append(rel_path)
        else:
            failed.append(rel_path)
        return

    if finding.startswith("StartupApproved: "):
        left = finding[len("StartupApproved: "):]
        rel_path, value_name = left.rsplit("\\", 1)
        if _delete_value_any_hive(rel_path, value_name):
            removed.append(left)
        else:
            failed.append(left)
        return

    if finding.startswith("Shortcut: "):
        target = Path(finding.split(": ", 1)[1])
        backup.copy_file(target)
        try:
            target.unlink()
            removed.append(str(target))
        except OSError:
            failed.append(f"{target} (locked?)")
        return

    if finding.startswith(("ProgramData: ", "Roaming: ", "YandexDisk data: ", "YandexDisk files: ")):
        target = Path(finding.split(": ", 1)[1])
        try:
            shutil.rmtree(target, ignore_errors=False)
            removed.append(str(target))
        except OSError:
            failed.append(f"{target} (locked?)")
        return

    if finding.startswith("Hosts: "):
        line = finding[len("Hosts: "):]
        try:
            try:
                text = HOSTS_FILE.read_text(encoding="utf-8")
                encoding = "utf-8"
            except UnicodeDecodeError:
                text = HOSTS_FILE.read_text(encoding="cp1251")
                encoding = "cp1251"
            backup.copy_file(HOSTS_FILE)
            drop = set(_hosts_yandex_lines(text))
            kept = [l for l in text.splitlines() if l.strip() not in drop]
            HOSTS_FILE.write_text("\n".join(kept) + "\n", encoding=encoding)
            removed.append(line)
        except OSError:
            failed.append(f"{line} (admin required?)")
        return

    if finding.startswith("Firewall rule: "):
        name = finding[len("Firewall rule: "):].rsplit(" (", 1)[0]
        escaped = name.replace("'", "''")
        script = (
            "[Console]::OutputEncoding=[Text.Encoding]::UTF8;"
            f"Remove-NetFirewallRule -Name '{escaped}'"
        )
        try:
            proc = subprocess.run(
                ["powershell", "-NoProfile", "-Command", script],
                capture_output=True, timeout=120,
            )
        except (OSError, subprocess.SubprocessError):
            failed.append(f"{name} (admin required?)")
            return
        (removed if proc.returncode == 0 else failed).append(name)
        return

    if finding.startswith("Extension: "):
        target = Path(finding[len("Extension: "):])
        try:
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
            removed.append(str(target))
        except OSError:
            failed.append(f"{target} (browser running?)")
        return

    if finding.startswith("Cookies: "):
        left = finding[len("Cookies: "):]
        browser, rest = left.split(" [", 1)
        profile_name = rest.split("]", 1)[0]
        db = _cookies_db_path(browser, profile_name)
        if db is None:
            failed.append(finding)
            return
        try:
            backup.copy_file(db)
            conn = sqlite3.connect(db)
            try:
                if browser == "Firefox":
                    conn.execute(
                        "DELETE FROM moz_cookies WHERE host LIKE ? OR host LIKE ?",
                        _COOKIE_HOSTS,
                    )
                else:
                    conn.execute(
                        "DELETE FROM cookies WHERE host_key LIKE ? OR host_key LIKE ?",
                        _COOKIE_HOSTS,
                    )
                conn.commit()
            finally:
                conn.close()
            removed.append(left)
        except (OSError, sqlite3.Error):
            failed.append(f"{left} (browser running?)")
        return

    if finding.startswith("OpenWith: "):
        left = finding[len("OpenWith: "):].split(" = ", 1)[0]
        rel_path, value_name = left.rsplit("\\", 1)
        if _delete_value_any_hive(rel_path, value_name):
            removed.append(left)
        else:
            failed.append(left)
        return

    if finding.startswith("Trace: "):
        target = Path(finding.split(": ", 1)[1])
        try:
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
            removed.append(str(target))
        except OSError:
            failed.append(f"{target} (locked?)")
        return

    if finding.startswith("Defender exclusion: "):
        item = finding[len("Defender exclusion: "):]
        escaped = item.replace("'", "''")
        script = (
            "[Console]::OutputEncoding=[Text.Encoding]::UTF8;"
            f"Remove-MpPreference -ExclusionPath '{escaped}'"
            f" -ExclusionProcess '{escaped}' -ExclusionExtension '{escaped}'"
            " -ErrorAction SilentlyContinue"
        )
        try:
            proc = subprocess.run(
                ["powershell", "-NoProfile", "-Command", script],
                capture_output=True, timeout=120,
            )
        except (OSError, subprocess.SubprocessError):
            failed.append(f"{item} (admin required?)")
            return
        (removed if proc.returncode == 0 else failed).append(item)
        return

    if finding.startswith("Keyboard layout: "):
        klid = finding[len("Keyboard layout: "):].split(" (", 1)[0]
        if _remove_keyboard_layout(klid):
            removed.append(klid)
        else:
            failed.append(klid)
        return

    if finding.startswith("Service: "):
        service_name = finding[len("Service: "):].split(" (", 1)[0]
        if remove_service(service_name):
            removed.append(service_name)
        else:
            failed.append(f"{service_name} (admin required?)")
        return

    if finding.startswith("File association: "):
        ext = finding[len("File association: "):].split(" -> ", 1)[0]
        if remove_file_association(ext):
            removed.append(ext)
        else:
            failed.append(ext)
        return

    if finding.startswith("Scheduled task: "):
        task_name = finding[len("Scheduled task: "):]
        backup.save_task_xml(task_name)
        try:
            proc = subprocess.run(
                ["schtasks", "/delete", "/tn", task_name, "/f"],
                capture_output=True, timeout=60,
            )
        except (OSError, subprocess.SubprocessError):
            failed.append(task_name)
            return
        (removed if proc.returncode == 0 else failed).append(task_name)
        return

    if finding.startswith("Default browser ("):
        protocol = finding.split("(", 1)[1].split(")", 1)[0]
        user_choice = (
            r"Software\Microsoft\Windows\Shell\Associations"
            f"\\UrlAssociations\\{protocol}\\UserChoice"
        )
        if _delete_tree_any_hive(user_choice):
            removed.append(f"{protocol} UserChoice")
        else:
            failed.append(f"{protocol} UserChoice")
        return

    if finding.startswith("Policy hijack: "):
        left = finding[len("Policy hijack: "):].split(" = ", 1)[0]
        rel_path, value_name = left.rsplit("\\", 1)
        if _delete_value_any_hive(rel_path, value_name):
            removed.append(left)
        else:
            failed.append(left)
        return

    if finding.startswith("SearchScopes\\"):
        subkey = finding.split("SearchScopes\\", 1)[1].split(" -> ", 1)[0]
        rel_path = r"Software\Microsoft\Internet Explorer\SearchScopes"
        try:
            backup.export_key(winreg.HKEY_CURRENT_USER, f"{rel_path}\\{subkey}")
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, f"{rel_path}\\{subkey}")
            removed.append(f"SearchScopes\\{subkey}")
        except OSError:
            failed.append(f"SearchScopes\\{subkey}")
        return

    if " [" in finding and "]: " in finding:
        # Chromium profile findings: "<browser> [<profile>]: <detail>"
        browser, rest = finding.split(" [", 1)
        profile_name, detail = rest.split("]: ", 1)
        rel = CHROMIUM_BROWSERS.get(browser)
        try:
            if rel is not None:
                if detail.startswith("keyword"):
                    result = _clean_profile_web_data(browser, rel, profile_name)
                else:
                    result = _clean_profile_preferences(browser, rel, profile_name)
            else:
                result = _remove_firefox_profile(profile_name)
            if result:
                removed.append(result)
            else:
                failed.append(finding)
        except (OSError, sqlite3.Error, json.JSONDecodeError, KeyError):
            failed.append(f"{finding} (browser running?)")
        return

    if " (DisplayName=" in finding:
        # Uninstall entries: "<reg path>\\<subkey> (DisplayName=...)"
        rel_path = finding.split(" (DisplayName=", 1)[0]
        if _delete_tree_any_hive(rel_path):
            removed.append(rel_path)
        else:
            failed.append(rel_path)
        return

    if " = " in finding:
        # Autostart Run/RunOnce values: "<reg path>\\<name> = <value>"
        left = finding.split(" = ", 1)[0]
        rel_path, value_name = left.rsplit("\\", 1)
        if _delete_value_any_hive(rel_path, value_name):
            removed.append(left)
        else:
            failed.append(left)
        return

    # Plain registry paths: StartMenuInternet clients, Software\Yandex trees
    if _delete_tree_any_hive(finding):
        removed.append(finding)
    else:
        failed.append(finding)


def remove_selected(selected: list[str]) -> tuple[list[str], list[str]]:
    """Remove exactly the findings the user selected in the dialog.

    A backup session is opened first; every key/file touched is exported
    into it before deletion.

    Returns:
        (removed, failed) lists of human-readable descriptions.
    """
    backup.start_session()
    removed: list[str] = []
    failed: list[str] = []
    for finding in selected:
        _remove_one(finding, removed, failed)
    backup.log_action(
        f"remove_selected: {len(selected)} selected, removed={len(removed)} failed={len(failed)}"
    )
    return removed, failed
