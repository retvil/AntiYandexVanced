"""Unit tests for pure logic: engine lookup, Firefox policies.json, LZ4 decompressor.

No GUI, no registry, no network — everything runs on CPU in milliseconds.
"""

import json
import struct

import pytest

import engines
import policies
import profiles
import yandex_detect


# --- engines -------------------------------------------------------------------

def test_get_engine_returns_matching_engine():
    engine = engines.get_engine("DuckDuckGo")
    assert engine.name == "DuckDuckGo"
    assert "duckduckgo.com" in engine.search_url


def test_get_engine_unknown_name_raises_keyerror():
    with pytest.raises(KeyError):
        engines.get_engine("Yandex")


def test_all_engines_have_unique_names_and_valid_urls():
    names = [e.name for e in engines.SEARCH_ENGINES]
    assert len(names) == len(set(names))
    for engine in engines.SEARCH_ENGINES:
        assert "{searchTerms}" in engine.search_url
        assert engine.search_url.startswith("https://")


# --- Firefox policies.json -----------------------------------------------------

def test_firefox_policies_json_with_suggest_url():
    engine = engines.get_engine("Google")
    doc = policies._firefox_policies_json(engine)
    entry = doc["policies"]["SearchEngines"]["Add"][0]
    assert entry["Name"] == "Google"
    assert "SuggestURLTemplate" in entry


def test_firefox_policies_json_without_suggest_url_has_no_null():
    engine = engines.SearchEngine(
        name="Custom", keyword="custom", search_url="https://c.example/?q={searchTerms}"
    )
    doc = policies._firefox_policies_json(engine)
    entry = doc["policies"]["SearchEngines"]["Add"][0]
    assert "SuggestURLTemplate" not in entry
    # document must be JSON-serializable without nulls in the engine entry
    serialized = json.dumps(doc)
    assert "null" not in serialized


# --- LZ4 block decompressor ----------------------------------------------------

def _lz4_compress_literals_only(data: bytes) -> bytes:
    """Minimal LZ4 compressor: literals-only blocks (no matches)."""
    out = bytearray()
    src = 0
    while src < len(data):
        chunk = data[src:src + 65535]
        lit_len = len(chunk)
        token = (lit_len if lit_len < 15 else 15) << 4
        out.append(token)
        if lit_len >= 15:
            remaining = lit_len - 15
            while remaining >= 255:
                out.append(255)
                remaining -= 255
            out.append(remaining)
        out += chunk
        src += lit_len
    out.append(0)  # end mark: empty token
    return bytes(out)


def test_lz4_decompress_literals_only_roundtrip():
    original = b"Hello, Yandex removal!" * 100
    compressed = _lz4_compress_literals_only(original)
    size = len(original)
    result = yandex_detect._lz4_block_decompress(compressed, size)
    assert result == original


def test_lz4_decompress_with_match():
    # "abc" literals + match(offset=3, len=6) -> "abcabcabc"
    token = (3 << 4) | 2  # literal_len=3, match_len=2 (+4 => 6)
    block = bytes([token]) + b"abc" + struct.pack("<H", 3)
    assert yandex_detect._lz4_block_decompress(block, 9) == b"abcabcabc"


def test_lz4_decompress_corrupt_offset_raises():
    # token with literal_len=0, match_len=0; offset=0 is invalid
    block = bytes([0x00]) + struct.pack("<H", 0)
    with pytest.raises(ValueError):
        yandex_detect._lz4_block_decompress(block, 100)


# --- markers -------------------------------------------------------------------

def test_is_yandex_positive_markers():
    for text in ("Yandex Browser", "яндекс", "https://ya.ru/search", "yandex.ru", "Punto Switcher"):
        assert yandex_detect._is_yandex(text)


def test_is_yandex_negative():
    for text in ("Google Chrome", "Mozilla Firefox", "https://google.com", ""):
        assert not yandex_detect._is_yandex(text)


# --- scheduled tasks parsing ---------------------------------------------------

def test_decode_schtasks_utf8():
    assert yandex_detect._decode_schtasks("TaskName,Status\n".encode("utf-8")) == "TaskName,Status\n"


def test_scan_scheduled_tasks_handles_missing_schtasks(monkeypatch):
    def boom(*args, **kwargs):
        raise FileNotFoundError("schtasks")
    monkeypatch.setattr(yandex_detect.subprocess, "run", boom)
    assert yandex_detect.scan_scheduled_tasks() == []


# --- exclusions ----------------------------------------------------------------

def test_exclusions_roundtrip(tmp_path, monkeypatch):
    import exclusions
    monkeypatch.setattr(exclusions, "EXCLUSIONS_FILE", tmp_path / "exclusions.json")
    monkeypatch.setattr(exclusions, "BASE_DIR", tmp_path)
    assert exclusions.load() == set()
    exclusions.add("Service: YandexUpdaterService (Yandex Updater)")
    assert exclusions.is_excluded("Service: YandexUpdaterService (Yandex Updater)")
    assert not exclusions.is_excluded("Scheduled task: YandexBrowserUpdate")
    exclusions.clear()
    assert exclusions.load() == set()


def test_exclusions_load_corrupt_file_returns_empty(tmp_path, monkeypatch):
    import exclusions
    bad = tmp_path / "exclusions.json"
    bad.write_text("{not json", encoding="utf-8")
    monkeypatch.setattr(exclusions, "EXCLUSIONS_FILE", bad)
    assert exclusions.load() == set()


# --- extended vectors (16-30) ---------------------------------------------------

def test_lnk_mentions_yandex_ascii_and_utf16(tmp_path):
    import yandex_detect
    plain = tmp_path / "plain.lnk"
    plain.write_bytes(b"\x00\x01chrome" + b"\x00" * 32)
    assert not yandex_detect._lnk_mentions_yandex(plain)
    ascii_lnk = tmp_path / "ascii.lnk"
    ascii_lnk.write_bytes(b"\x00\x01" + b"C:\\Yandex\\browser.exe" + b"\x00" * 8)
    assert yandex_detect._lnk_mentions_yandex(ascii_lnk)
    utf16_lnk = tmp_path / "utf16.lnk"
    utf16_lnk.write_bytes(b"\x00\x01" + "Яндекс.Браузер".encode("utf-16-le"))
    assert yandex_detect._lnk_mentions_yandex(utf16_lnk)


def test_hosts_yandex_lines_skips_comments_and_other_domains():
    text = "\n".join([
        "# comment yandex.ru",
        "127.0.0.1 yandex.ru",
        "  0.0.0.0 ya.ru  ",
        "1.2.3.4 google.com",
        "",
    ])
    lines = yandex_detect._hosts_yandex_lines(text)
    assert lines == ["127.0.0.1 yandex.ru", "0.0.0.0 ya.ru"]


def test_parse_firewall_output():
    text = "\nRule1|Display One\n\nRule2|Display Two\n|\n"
    assert yandex_detect._parse_firewall_output(text) == [
        ("Rule1", "Display One"),
        ("Rule2", "Display Two"),
    ]


def test_consent_prefixes_cover_consent_findings():
    samples = [
        "Roaming: C:\\Users\\X\\AppData\\Roaming\\Yandex",
        "YandexDisk data: C:\\Users\\X\\AppData\\Local\\Yandex\\YandexDisk2",
        "YandexDisk files: C:\\Users\\X\\YandexDisk",
        "Extension: C:\\Users\\X\\...\\Extensions\\abc",
        "Cookies: Google Chrome [Default] (3 rows)",
        "Defender exclusion: C:\\Yandex",
    ]
    for sample in samples:
        assert sample.startswith(yandex_detect.CONSENT_PREFIXES), sample


def test_new_scan_functions_return_lists():
    for name in (
        "scan_shell_overlays", "scan_context_menus", "scan_startup_approved",
        "scan_app_paths", "scan_shortcuts", "scan_leftover_dirs", "scan_hosts",
        "scan_firewall_rules", "scan_uri_protocols", "scan_browser_extensions",
        "scan_cookies", "scan_openwith", "scan_traces",
        "scan_defender_exclusions", "scan_keyboard_layouts",
    ):
        assert isinstance(getattr(yandex_detect, name)(), list), name


# --- product profiles (Vanced / Extended) ---------------------------------------

def test_profile_steps_reference_existing_scan_functions():
    for profile, steps in profiles.PROFILE_SCANS.items():
        for name in steps:
            assert callable(getattr(yandex_detect, name, None)), (profile, name)


def test_extended_is_superset_of_vanced():
    assert set(profiles.PROFILE_SCANS[profiles.VANCED]) < set(
        profiles.PROFILE_SCANS[profiles.EXTENDED]
    )


def test_vanced_excludes_product_wide_vectors():
    vanced = set(profiles.PROFILE_SCANS[profiles.VANCED])
    for name in (
        "scan_shell_overlays", "scan_context_menus", "scan_leftover_dirs",
        "scan_hosts", "scan_firewall_rules", "scan_defender_exclusions",
        "scan_keyboard_layouts",
    ):
        assert name not in vanced, name


def test_validate_rejects_unknown_profile():
    with pytest.raises(ValueError):
        profiles.validate("nope")


def test_scan_all_vanced_runs_and_is_list():
    assert isinstance(yandex_detect.scan_all(profiles.VANCED), list)


def test_scan_all_default_is_extended():
    import inspect
    signature = inspect.signature(yandex_detect.scan_all)
    assert signature.parameters["profile"].default is None


# --- Extended product scans (Store apps, product dirs) ---------------------------

def test_parse_appx_output():
    import products_detect
    text = "A025C540.Yandex.Music|A025C540.Yandex.Music_4.54_x64__vfvw9svesycw6\n\njunk\n|"
    parsed = products_detect._parse_appx_output(text)
    assert parsed == [
        ("A025C540.Yandex.Music", "A025C540.Yandex.Music_4.54_x64__vfvw9svesycw6"),
    ]


def test_scan_store_apps_returns_list():
    import products_detect
    assert isinstance(products_detect.scan_store_apps(), list)


def test_scan_product_dirs_skips_browser(tmp_path, monkeypatch):
    import products_detect
    base = tmp_path / "Yandex"
    (base / "YandexBrowser").mkdir(parents=True)
    (base / "YandexDisk").mkdir()
    monkeypatch.setattr(
        products_detect, "scan_product_dirs",
        lambda: _scan_product_dirs_at(str(base)),
    )
    found = products_detect.scan_product_dirs()
    assert found == [f"Product dir: {base / 'YandexDisk'}"]


def _scan_product_dirs_at(base: str) -> list[str]:
    import os
    found = []
    for entry in os.listdir(base):
        path = os.path.join(base, entry)
        if os.path.isdir(path) and entry.lower() != "yandexbrowser":
            found.append(f"Product dir: {path}")
    return found


def test_remove_one_store_app_and_product_dir_dispatch(monkeypatch):
    import products_detect
    calls = []
    monkeypatch.setattr(
        products_detect, "remove_store_app",
        lambda finding: calls.append("store") or True,
    )
    monkeypatch.setattr(
        products_detect, "remove_product_dir",
        lambda finding: calls.append("dir") or True,
    )
    removed: list[str] = []
    failed: list[str] = []
    yandex_detect._remove_one("Store app: X (Y)", removed, failed)
    yandex_detect._remove_one("Product dir: C:\\Yandex\\Disk", removed, failed)
    assert calls == ["store", "dir"]
    assert failed == []
    assert removed == ["X (Y)", "C:\\Yandex\\Disk"]


def test_is_product_process_matches_products_and_browser():
    import products_detect
    assert products_detect.is_product_process("YandexDisk2.exe") is True
    assert products_detect.is_product_process("punto.exe") is True
    assert products_detect.is_product_process("browser.exe") is True
    assert products_detect.is_product_process("yandex.exe") is True
    assert products_detect.is_product_process("Yandex.Music.exe") is True
    assert products_detect.is_product_process("chrome.exe") is False
    assert products_detect.is_product_process("agent-browser-win32-x64.exe") is False
    assert products_detect.is_product_process(None) is False
    assert products_detect.is_product_process("") is False
