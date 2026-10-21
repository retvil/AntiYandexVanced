# AntiYandex Vanced

[![Release](https://img.shields.io/github/v/release/retvil/AntiYandexVanced?sort=date)](https://github.com/retvil/AntiYandexVanced/releases) [![Platform Windows](https://img.shields.io/badge/platform-Windows-blue)](https://github.com/retvil/AntiYandexVanced/releases) [![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

**Yandex Browser vollständig entfernen und die Standardsuche hart gegen Entführung sichern — 30 Erkennungsvektoren, 10 Suchmaschinen, 10 UI-Sprachen.**

[🇬🇧 English](README.md) | [🇷🇺 Русский](README.ru.md) | [🇺🇦 Українська](README.uk.md) | [🇰🇿 Қазақша](README.kk.md) | **🇩🇪 Deutsch** | [🇫🇷 Français](README.fr.md) | [🇪🇸 Español](README.es.md) | [🇵🇱 Polski](README.pl.md) | [🇹🇷 Türkçe](README.tr.md) | [🇨🇳 中文](README.zh.md)

## Was ist das?

Yandex installiert nicht nur einen Browser — es trägt sich still über dreißig Systemmechanismen als Standardsuche und Standardbrowser ein: Registry-Assoziationen, Enterprise-Richtlinien, Profileinstellungen von Browsern, sogar Suchmaschinen-Datenbanken in Chromium-Profilen. Allein das Entfernen des Browsers macht das nicht rückgängig.

**AntiYandex Vanced** (ein Fork von [TheCawa/AntiYandex](https://github.com/TheCawa/AntiYandex)) findet **alle 30 Hijack-Vektoren**, entfernt sie mit einem Klick und **verriegelt dann Ihre Standardsuche** hart auf eine von Ihnen gewählte Suchmaschine über Windows-Enterprise-Richtlinien — damit nichts sie laut zurückholen kann.

## Funktionen

- **Hijack-Scanner** — erkennt 30 Vektoren: Installationspfade, Uninstall-Registry-Einträge, `UserChoice`-Assoziation, `StartMenuInternet`-Registrierungen, `Software\Yandex`-Schlüsselbäume, Hijack über `DefaultSearchProvider*`-Richtlinien, Chromium-Profil-`Preferences`, Schlüsselwörter in `Web Data` (SQLite), Firefox `search.json.mozlz4`, Legacy-`SearchScopes`, Autostart-Einträge, geplante Aufgaben, Windows-Dienste, Punto Switcher, Dateizuordnungen, Yandex-Disk-Shell-Integration, deaktivierter Autostart, App Paths, Verknüpfungen, ProgramData/Roaming-Reste, hosts-Einträge, Firewall-Regeln, URI-Protokolle, Browser-Erweiterungen, yandex.ru-Cookies, „Öffnen mit“-Zuordnungen, Prefetch/WER-Spuren, Defender-Ausschlüsse, Tastaturlayouts
- **Entfernung mit einem Klick** — jeder Vektor hat seinen eigenen Remover; gesperrte Datenbanken werden ehrlich gemeldet, ohne Abstürze
- **Harte Suchrichtlinie** — verriegelt die Standardsuche auf eine von 10 Suchmaschinen (Google, Bing, DuckDuckGo, Brave Search, Startpage, Mojeek, Qwant, Ecosia, Yahoo, SearXNG) über HKLM-Richtlinien für Chrome, Edge, Brave, Vivaldi, Opera und Yandex Browser + `policies.json` für Firefox/Waterfox
- **Richtlinien-Bereinigung** — entfernt Yandex-`DefaultSearchProvider*`-Werte aus der Registry
- **10 UI-Sprachen** — ru, en, uk, kk, de, fr, es, pl, tr, zh; Systemsprache wird automatisch erkannt
- **Leichtes UI** — ttkbootstrap, vertikales Layout, fixierte Statusleiste und Fußzeile

## Screenshot

<details>
<summary>Hauptfenster</summary>

![AntiYandexVanced Hauptfenster](docs/screenshot.png)

</details>

## Fertige Builds

Download von [Releases](https://github.com/retvil/AntiYandexVanced/releases):

- **Windows** — `AntiYandexVanced.exe` (portabel, eine Datei, ~35 MB) — entfernt Yandex Browser und die Yandex-Suche
- **Windows** — `AntiYandexExtended.exe` (portabel, eine Datei, ~35 MB) — Entfernung aller Yandex-Produkte (Yandex Disk, Punto-Switcher-Verlauf, systemweite Spuren)

Als **Administrator ausführen** — HKLM-Richtlinien und Registry-Bereinigung erfordern erhöhte Rechte.

## Installation aus dem Quellcode

Python 3.10+ erforderlich ([python.org](https://python.org)).

```bash
git clone https://github.com/retvil/AntiYandexVanced.git
cd AntiYandexVanced
pip install psutil ttkbootstrap
python main.py
```

Eigenes EXE bauen: `build.bat` ausführen (PyInstaller, Ergebnis in `dist/`).

## Verwendung

1. **Prozesse beenden** → **Yandex suchen** → **Yandex löschen** — den Browser selbst entfernen.
2. **Such-Hijacks scannen** — zeigt alle Wege, wie Yandex sich ins System eingegraben hat.
3. **Hijacks entfernen** — zuerst alle Browser schließen, dann alles Gefundene entfernen.
4. Suchmaschine wählen → **Richtlinie anwenden** — die Standardsuche ist auf Systemebene verriegelt.

## FAQ

- **Warum Administrator?** Suchrichtlinien liegen in HKLM, die Hijack-Bereinigung berührt die System-Registry — erhöhte Rechte nötig.
- **„Database locked" in den Ergebnissen?** Während der Bereinigung lief ein Chromium-Browser. Alle Browser schließen und die Entfernung wiederholen.
- **Wie entferne ich die Suchrichtlinie?** Die Schaltfläche **Yandex-Richtlinien entfernen** räumt die Richtlinienwerte weg; in Firefox kann man zusätzlich die Datei `distribution\policies.json` löschen.

## Autor & Support

**Nod33Eset** — Fork von [TheCawa/AntiYandex](https://github.com/TheCawa/AntiYandex). Issues und PRs sind willkommen.

Wenn dich das Tool von Yandex befreit hat, kannst du die Entwicklung unterstützen:

**Krypto:**

- BTC: `bc1qunld3rsp37qf5gg69aune50y0qqkd0eugg7j97`
- TON: `UQDmvr4SKOxSION3Yky6aOgzAnCDXySPuAbG4EKJa5JUT7tC`
- USDT (TRC20): `TBPJSSLu1mUcX54g9UyxUohYGf2fuRvbwd`
- USDT (ERC20): `0x25CAED3776Ef5b18E03392bC5b254Bbd78E8180C`
- USDT (SOL): `3qgN5z291CEcj2FUi2Zza5DioxKgNw72kC7P52pCcTrG`

## Lizenz

MIT — siehe [LICENSE](LICENSE).
