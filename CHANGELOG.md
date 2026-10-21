# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Two editions from one codebase: **AntiYandexVanced** (Yandex Browser +
  Yandex Search removal) and **AntiYandexExtended** (every Yandex product) —
  product profiles in `profiles.py` select the scan scope, shared GUI in
  `app.py`, thin entry points `main.py` / `main_extended.py`
- `build.bat` now builds both EXEs

## [2.4.0] - 2026-10-21

### Added
- 16th–30th hijack vectors: Yandex Disk shell integration (icon overlays +
  context-menu handlers), disabled autostart (`StartupApproved`), `App Paths`,
  shortcuts (Desktop / Start Menu / taskbar), leftover directories
  (ProgramData, Roaming, Yandex Disk data and synced files), `hosts` entries,
  Windows Firewall rules, URI protocol handlers, browser extensions
  (Chromium manifests + Firefox `.xpi`), yandex.ru cookies (Chromium +
  Firefox), `OpenWithProgids`/`OpenWithList` associations, Prefetch /
  CrashDumps / WER traces, Windows Defender exclusions, custom keyboard
  layouts (Yandex IME)
- Consent confirmation: findings that touch user data (Yandex Disk files,
  Punto Switcher history, extensions, cookies, Defender exclusions) require
  an explicit extra confirmation before removal
- Unit tests for `.lnk` byte detection, hosts-line filtering, firewall output
  parsing and consent-prefix coverage

## [2.3.0] - 2026-10-20

### Added
- 13th–15th hijack vectors: Windows services (registry-based scan, `sc stop` +
  `sc delete` removal), Punto Switcher (detection via the `punto` marker),
  file associations (`FileExts\<ext>\UserChoice` ProgId scan + removal)
- Selection dialog after scan: pick exactly which findings to remove instead
  of all-or-nothing removal
- Exclusions: unchecked findings can be saved to
  `%APPDATA%\AntiYandexVanced\exclusions.json` — future scans deselect them
  automatically, but they stay selectable in the dialog; exclusions can be
  reset from the dialog
- Unit tests for exclusions persistence and the Punto Switcher marker

## [2.2.0] - 2026-10-20

### Added
- Backup before removal: every registry key / profile file touched is exported
  to `%APPDATA%\AntiYandexVanced\backup\<timestamp>\` before deletion
- Operation log: `%APPDATA%\AntiYandexVanced\antiyandex.log`
- 12th hijack vector: Windows Task Scheduler entries (Yandex updater tasks)
- HKCU Chromium policy scan/cleanup (per-user policies, previously HKLM only)
- Administrator-rights check at startup with a warning in the status bar
- Prompt to close running browsers before hijack removal (prevents "database locked")
- "Open report folder" offer when some hijack items fail to be removed
- Unit tests for pure logic (engine lookup, Firefox policies.json, LZ4 decompressor)

### Fixed
- All UI updates from background threads are now marshaled to the main thread
  via `root.after` (tkinter is not thread-safe)
- Bare `except:` clauses replaced with `except OSError`
- Web Data cleanup now deletes exactly the detected rows (by `rowid`), not by
  URL substring — detection and deletion are consistent
- SQLite connections are closed on error paths (`finally`)
- Firefox `policies.json` no longer contains a `null` `SuggestURLTemplate`
- Firefox policies are no longer written into non-existent install folders
- Hardcoded Russian admin-error string replaced with a translated key in all
  10 UI languages
- `shutil.rmtree` now reports which files are locked instead of a generic error
- Corrupt LZ4 blocks with invalid match offsets raise instead of returning garbage

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
