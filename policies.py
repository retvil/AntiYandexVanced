"""Hard enforcement of default search engine via browser enterprise policies.

Chromium family: HKLM\\SOFTWARE\\Policies\\<vendor>\\<browser> DefaultSearchProvider*
registry values (machine-wide, survives profile resets and Yandex re-hijacks).
Firefox: distribution\\policies.json with SearchEngines + DefaultSearchEngine.

Writing HKLM requires administrator rights; failures are reported per browser.
"""

import json
import os
import winreg

from engines import SearchEngine

# Chromium policy registry paths: display name -> HKLM subkey
CHROMIUM_POLICY_PATHS: dict[str, str] = {
    "Google Chrome": r"SOFTWARE\Policies\Google\Chrome",
    "Microsoft Edge": r"SOFTWARE\Policies\Microsoft\Edge",
    "Brave": r"SOFTWARE\Policies\BraveSoftware\Brave",
    "Vivaldi": r"SOFTWARE\Policies\Vivaldi",
    "Opera": r"SOFTWARE\Policies\OperaSoftware\Opera",
    "Yandex Browser": r"SOFTWARE\Policies\Yandex\YandexBrowser",
}

# Firefox install roots to place distribution\policies.json into
FIREFOX_INSTALL_ROOTS: tuple[str, ...] = (
    r"C:\Program Files\Mozilla Firefox",
    r"C:\Program Files (x86)\Mozilla Firefox",
    r"C:\Program Files\Waterfox",
)

POLICY_VALUE_NAMES: tuple[str, ...] = (
    "DefaultSearchProviderEnabled",
    "DefaultSearchProviderName",
    "DefaultSearchProviderSearchURL",
    "DefaultSearchProviderKeyword",
    "DefaultSearchProviderSuggestURL",
)


def _set_policy_values(policy_path: str, engine: SearchEngine) -> None:
    """Write DefaultSearchProvider* values under one Chromium policy key."""
    values = {
        "DefaultSearchProviderEnabled": 1,
        "DefaultSearchProviderName": engine.name,
        "DefaultSearchProviderSearchURL": engine.search_url,
        "DefaultSearchProviderKeyword": engine.keyword,
    }
    if engine.suggest_url:
        values["DefaultSearchProviderSuggestURL"] = engine.suggest_url
    with winreg.CreateKeyEx(
        winreg.HKEY_LOCAL_MACHINE, policy_path, 0, winreg.KEY_SET_VALUE
    ) as key:
        for name, value in values.items():
            if isinstance(value, int):
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
            else:
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)


def apply_chromium(engine: SearchEngine, browsers: list[str]) -> tuple[list[str], list[str]]:
    """Apply default-search policy to selected Chromium browsers.

    Args:
        engine: Engine to enforce.
        browsers: Display names from CHROMIUM_POLICY_PATHS.

    Returns:
        (applied, failed) lists of browser display names.
    """
    applied: list[str] = []
    failed: list[str] = []
    for browser in browsers:
        policy_path = CHROMIUM_POLICY_PATHS.get(browser)
        if not policy_path:
            continue
        try:
            _set_policy_values(policy_path, engine)
            applied.append(browser)
        except OSError:
            failed.append(browser)
    return applied, failed


def _firefox_policies_json(engine: SearchEngine) -> dict:
    """Build a Firefox policies.json document for the engine."""
    engine_entry: dict = {
        "Name": engine.name,
        "Alias": engine.keyword,
        "URLTemplate": engine.search_url,
    }
    if engine.suggest_url:
        engine_entry["SuggestURLTemplate"] = engine.suggest_url
    return {
        "policies": {
            "SearchEngines": {
                "Default": engine.name,
                "PreventSearchEngineInstall": True,
                "LockDefaultSearchEngine": True,
                "Add": [engine_entry],
            },
            "DisableTelemetry": True,
        }
    }


def apply_firefox(engine: SearchEngine) -> tuple[list[str], list[str]]:
    """Write policies.json into every found Firefox/Waterfox install.

    Returns:
        (applied, failed) lists of install paths.
    """
    applied: list[str] = []
    failed: list[str] = []
    document = _firefox_policies_json(engine)
    for root in FIREFOX_INSTALL_ROOTS:
        if not os.path.isdir(root):
            continue  # browser not installed — don't litter Program Files
        dist_dir = os.path.join(root, "distribution")
        policies_file = os.path.join(dist_dir, "policies.json")
        try:
            os.makedirs(dist_dir, exist_ok=True)
            with open(policies_file, "w", encoding="utf-8") as fh:
                json.dump(document, fh, indent=2, ensure_ascii=False)
            applied.append(root)
        except OSError:
            failed.append(root)
    return applied, failed


def remove_yandex_search_policies() -> list[str]:
    """Delete DefaultSearchProvider* policy values that point to Yandex.

    Checks both HKLM (machine) and HKCU (per-user) policy keys.

    Returns:
        List of cleaned policy paths (hive-prefixed).
    """
    cleaned: list[str] = []
    for hive, hive_name in (
        (winreg.HKEY_LOCAL_MACHINE, "HKLM"),
        (winreg.HKEY_CURRENT_USER, "HKCU"),
    ):
        for policy_path in CHROMIUM_POLICY_PATHS.values():
            try:
                with winreg.OpenKey(
                    hive, policy_path, 0, winreg.KEY_ALL_ACCESS
                ) as key:
                    names_to_delete = []
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            i += 1
                            if name.startswith("DefaultSearchProvider") and isinstance(value, str):
                                lowered = value.lower()
                                if "yandex" in lowered or "ya.ru" in lowered:
                                    names_to_delete.append(name)
                        except OSError:
                            break
                if not names_to_delete:
                    continue
                with winreg.OpenKey(
                    hive, policy_path, 0, winreg.KEY_SET_VALUE
                ) as key:
                    for name in names_to_delete:
                        winreg.DeleteValue(key, name)
                cleaned.append(f"{hive_name}\\{policy_path}")
            except OSError:
                continue
    return cleaned
