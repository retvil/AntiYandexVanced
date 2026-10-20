"""Unit tests for pure logic: engine lookup, Firefox policies.json, LZ4 decompressor.

No GUI, no registry, no network — everything runs on CPU in milliseconds.
"""

import json
import struct

import pytest

import engines
import policies
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
