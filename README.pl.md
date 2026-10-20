# AntiYandex Vanced

[![Release](https://img.shields.io/github/v/release/retvil/AntiYandexVanced?sort=date)](https://github.com/retvil/AntiYandexVanced/releases) [![Platform Windows](https://img.shields.io/badge/platform-Windows-blue)](https://github.com/retvil/AntiYandexVanced/releases) [![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

**Kompletne usunięcie Yandex Browser i twarde zabezpieczenie wyszukiwarki domyślnej przed przejęciem — 15 wektorów detekcji, 10 wyszukiwarek, 10 języków interfejsu.**

[🇬🇧 English](README.md) | [🇷🇺 Русский](README.ru.md) | [🇺🇦 Українська](README.uk.md) | [🇰🇿 Қазақша](README.kk.md) | [🇩🇪 Deutsch](README.de.md) | [🇫🇷 Français](README.fr.md) | [🇪🇸 Español](README.es.md) | **🇵🇱 Polski** | [🇹🇷 Türkçe](README.tr.md) | [🇨🇳 中文](README.zh.md)

## Co to jest?

Yandex nie instaluje tylko przeglądarki — po cichu rejestruje się jako domyślna wyszukiwarka i przeglądarka przez kilkanaście różnych mechanizmów systemu: asocjacje w rejestrze, polityki enterprise, ustawienia profili przeglądarek, a nawet bazy wyszukiwarek wewnątrz profili Chromium. Samo usunięcie przeglądarki tego nie cofa.

**AntiYandex Vanced** (fork [TheCawa/AntiYandex](https://github.com/TheCawa/AntiYandex)) znajduje **wszystkie 15 wektorów przejęcia**, usuwa je jednym kliknięciem, a następnie **twardo blokuje wyszukiwarkę domyślną** na wybranej przez Ciebie wyszukiwarce przez polityki enterprise Windows — żeby nic nie mogło po cichu przywrócić starych ustawień.

## Funkcje

- **Skaner przejęć** — wykrywa 15 wektorów: ścieżki instalacji, wpisy Uninstall w rejestrze, asocjacja `UserChoice`, rejestracje `StartMenuInternet`, drzewa kluczy `Software\Yandex`, przejęcie przez polityki `DefaultSearchProvider*`, `Preferences` profili Chromium, słowa kluczowe w `Web Data` (SQLite), `search.json.mozlz4` Firefox, legacy `SearchScopes`, wpisy autostartu, zaplanowane zadania, usługi Windows, Punto Switcher, skojarzenia plików
- **Usuwanie jednym kliknięciem** — każdy wektor ma własny remover; zablokowane bazy są uczciwie raportowane, bez crashy
- **Twarda polityka wyszukiwania** — blokuje wyszukiwarkę domyślną na jednej z 10 wyszukiwarek (Google, Bing, DuckDuckGo, Brave Search, Startpage, Mojeek, Qwant, Ecosia, Yahoo, SearXNG) przez polityki HKLM dla Chrome, Edge, Brave, Vivaldi, Opera i Yandex Browser + `policies.json` dla Firefox/Waterfox
- **Czyszczenie polityk** — usuwa wartości `DefaultSearchProvider*` Yandexa z rejestru
- **10 języków interfejsu** — ru, en, uk, kk, de, fr, es, pl, tr, zh; język systemu wykrywany automatycznie
- **Lekki interfejs** — ttkbootstrap, układ pionowy, przypięty pasek statusu i stopka

## Zrzut ekranu

<details>
<summary>Okno główne</summary>

![Okno główne AntiYandexVanced](docs/screenshot.png)

</details>

## Gotowe buildy

Pobierz z [Releases](https://github.com/retvil/AntiYandexVanced/releases):

- **Windows** — `AntiYandexVanced.exe` (portable, jeden plik, ~35 MB)

Uruchom **jako administrator** — polityki HKLM i czyszczenie rejestru wymagają podwyższonych uprawnień.

## Instalacja ze źródeł

Wymagany Python 3.10+ ([python.org](https://python.org)).

```bash
git clone https://github.com/retvil/AntiYandexVanced.git
cd AntiYandexVanced
pip install psutil ttkbootstrap
python main.py
```

Budowa własnego EXE: uruchom `build.bat` (PyInstaller, wynik w `dist/`).

## Użycie

1. **Zakończ procesy** → **Szukaj Yandexa** → **Usuń Yandexa** — usuwamy samą przeglądarkę.
2. **Skanuj przejęcia wyszukiwania** — pokaże wszystkie sposoby, jakimi Yandex zapuścił korzenie w systemie.
3. **Usuń przejęcia** — najpierw zamknij wszystkie przeglądarki, potem usuń wszystko znalezione.
4. Wybierz wyszukiwarkę → **Zastosuj politykę** — wyszukiwarka domyślna zablokowana na poziomie systemu.

## FAQ

- **Po co administrator?** Polityki wyszukiwania mieszkają w HKLM, czyszczenie dotyka rejestru systemowego — potrzebne podwyższone uprawnienia.
- **„Database locked" w wynikach?** Podczas czyszczenia działała przeglądarka Chromium. Zamknij wszystkie przeglądarki i powtórz usuwanie.
- **Jak zdjąć politykę wyszukiwania?** Przycisk **Usuń polityki Yandexa** czyści wartości polityk; w Firefoxie można też usunąć plik `distribution\policies.json`.

## Autor i wsparcie

**Nod33Eset** — fork [TheCawa/AntiYandex](https://github.com/TheCawa/AntiYandex). Issues i PR mile widziane.

Jeśli narzędzie uwolniło Cię od Yandexa — możesz wesprzeć rozwój:

**Krypto:**

- BTC: `bc1qunld3rsp37qf5gg69aune50y0qqkd0eugg7j97`
- TON: `UQDmvr4SKOxSION3Yky6aOgzAnCDXySPuAbG4EKJa5JUT7tC`
- USDT (TRC20): `TBPJSSLu1mUcX54g9UyxUohYGf2fuRvbwd`
- USDT (ERC20): `0x25CAED3776Ef5b18E03392bC5b254Bbd78E8180C`
- USDT (SOL): `3qgN5z291CEcj2FUi2Zza5DioxKgNw72kC7P52pCcTrG`

## Licencja

MIT — zob. [LICENSE](LICENSE).
