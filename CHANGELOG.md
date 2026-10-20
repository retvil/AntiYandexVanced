# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.1.2] - 2026-10-20

### Changed
- App title shortened to "Удаление Яндекс" / "Remove Yandex" (ru/en/uk)
- Footer pinned to the bottom-right corner: author, version and clickable GitHub link
- Repository link set to `https://github.com/retvil/AntiYandexVanced`

## [2.1.0] - 2026-10-20

### Added
- Vertical window layout (560×700): centered action stack, full-width section cards
- Light theme UI on **ttkbootstrap** (`flatly` theme) — replaced CustomTkinter for a lighter ttk-based stack
- Footer with author, version and clickable GitHub repository link

### Changed
- Migrated UI library: tkinter → CustomTkinter → ttkbootstrap
- Language selector moved to the top-right corner

## [2.0.0] - 2026-10-20

Fork of [TheCawa/AntiYandex](https://github.com/TheCawa/AntiYandex) 1.3.

### Added
- **Search hijack scanner** — detects 11 vectors Yandex uses to install itself as default search/browser:
  - installation directories on disk
  - uninstall registry entries (HKLM, WOW6432Node, HKCU)
  - Windows default-browser association (`UserChoice` ProgId for http/https)
  - `StartMenuInternet` browser client registrations
  - standalone `Software\Yandex` key trees (HKCU/HKLM/WOW6432Node)
  - enterprise-policy hijack via `DefaultSearchProvider*` registry values (the "hard" way Yandex enforces itself)
  - per-profile Chromium `Preferences` JSON (Chrome, Edge, Brave, Vivaldi, Yandex Browser)
  - search-engine keyword rows in Chromium `Web Data` SQLite databases
  - Firefox/Waterfox `search.json.mozlz4` (with a built-in pure-Python LZ4 block decompressor)
  - legacy IE/Windows `SearchScopes` entries
  - autostart entries (`Run`/`RunOnce`)
- **Hijack removal** — one-click removal of every detected vector, with per-vector removers:
  recursive registry key deletion, `UserChoice` reset, `Preferences` cleanup,
  `DELETE FROM keywords` in Web Data, `search.json.mozlz4` reset (Firefox rebuilds defaults),
  autostart value deletion. Locked databases/files (browser running) are reported, never crash.
- **Hard default-search policy** — enforces one of 10 search engines
  (Google, Bing, DuckDuckGo, Brave Search, Startpage, Mojeek, Qwant, Ecosia, Yahoo, SearXNG):
  - Chromium family via HKLM `SOFTWARE\Policies\...` `DefaultSearchProvider*` values
    (Chrome, Edge, Brave, Vivaldi, Opera, Yandex Browser)
  - Firefox/Waterfox via `distribution\policies.json`
    (`SearchEngines` + `LockDefaultSearchEngine` + `PreventSearchEngineInstall`)
- **Remove Yandex policies** button — strips Yandex `DefaultSearchProvider*` policy values from the registry
- **10 UI languages** (ru, en, uk, kk, de, fr, es, pl, tr, zh) in a dedicated `translations.py` module;
  system language auto-detected via Windows UI language API (`GetUserDefaultUILanguage`),
  English fallback when no match
- Language switcher dropdown in the UI

### Changed
- Code split into modules: `engines.py`, `yandex_detect.py`, `policies.py`, `translations.py`, `main.py`

## [1.3.0] - upstream

Baseline from [TheCawa/AntiYandex](https://github.com/TheCawa/AntiYandex):
- Yandex Browser process termination (`browser.exe`, `yandex.exe`)
- Installation path search
- Uninstall registry entry cleanup
- Browser folder deletion
- RU/EN interface toggle

[Unreleased]: https://github.com/retvil/AntiYandexVanced/compare/v2.1.2...HEAD
[2.1.2]: https://github.com/retvil/AntiYandexVanced/compare/v2.1.0...v2.1.2
[2.1.0]: https://github.com/retvil/AntiYandexVanced/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/retvil/AntiYandexVanced/compare/v1.3.0...v2.0.0
