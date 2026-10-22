# AntiYandex Vanced

[![Release](https://img.shields.io/github/v/release/retvil/AntiYandexVanced?sort=date)](https://github.com/retvil/AntiYandexVanced/releases) [![Platform Windows](https://img.shields.io/badge/platform-Windows-blue)](https://github.com/retvil/AntiYandexVanced/releases) [![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

**Supprime complètement Yandex Browser et verrouille ta recherche par défaut contre le détournement — 40 vecteurs de détection, 10 moteurs de recherche, 10 langues d'interface.**

[🇬🇧 English](README.md) | [🇷🇺 Русский](README.ru.md) | [🇺🇦 Українська](README.uk.md) | [🇰🇿 Қазақша](README.kk.md) | [🇩🇪 Deutsch](README.de.md) | **🇫🇷 Français** | [🇪🇸 Español](README.es.md) | [🇵🇱 Polski](README.pl.md) | [🇹🇷 Türkçe](README.tr.md) | [🇨🇳 中文](README.zh.md)

## Qu'est-ce que c'est ?

Yandex n'installe pas qu'un navigateur — il s'enregistre silencieusement comme recherche et navigateur par défaut via quarante mécanismes système : associations dans le registre, politiques d'entreprise, paramètres de profils de navigateurs, même les bases de données de moteurs de recherche dans les profils Chromium. Supprimer le navigateur seul ne suffit pas.

**AntiYandex Vanced** (un fork de [TheCawa/AntiYandex](https://github.com/TheCawa/AntiYandex)) trouve **les 40 vecteurs de détournement**, les supprime en un clic, puis **verrouille ta recherche par défaut** sur le moteur de ton choix via les politiques d'entreprise Windows — pour que rien ne puisse la reprendre silencieusement.

## Fonctionnalités

- **Scanner de détournements** — détecte 40 vecteurs : chemins d'installation, entrées Uninstall du registre, association `UserChoice`, enregistrements `StartMenuInternet`, arbres de clés `Software\Yandex`, détournement via les politiques `DefaultSearchProvider*`, `Preferences` des profils Chromium, mots-clés dans `Web Data` (SQLite), `search.json.mozlz4` Firefox, `SearchScopes` legacy, entrées d'autostart, tâches planifiées, services Windows, Punto Switcher, associations de fichiers, intégration shell de Yandex Disk, autostart désactivé, App Paths, raccourcis, restes ProgramData/Roaming, entrées hosts, règles de pare-feu, protocoles URI, extensions de navigateur, cookies yandex.ru, associations « Ouvrir avec », traces Prefetch/WER, exclusions Defender, dispositions clavier, détournement de la page de démarrage IE, politiques d'URL de démarrage (`RestoreOnStartupURLs`), page d'accueil Firefox, zone map IE, entrées RegisteredApplications, traces MUICache, programmes d'installation dans %TEMP%, applications Store (Yandex Music, Alice), répertoires de produits, répertoires de données locales, Yandex.DNS
- **Suppression en un clic** — chaque vecteur a son propre remover ; les bases verrouillées sont signalées honnêtement, sans crash
- **Politique stricte de recherche** — verrouille la recherche par défaut sur l'un des 10 moteurs (Google, Bing, DuckDuckGo, Brave Search, Startpage, Mojeek, Qwant, Ecosia, Yahoo, SearXNG) via les politiques HKLM pour Chrome, Edge, Brave, Vivaldi, Opera et Yandex Browser + `policies.json` pour Firefox/Waterfox
- **Nettoyage des politiques** — purge les valeurs `DefaultSearchProvider*` de Yandex du registre
- **10 langues d'interface** — ru, en, uk, kk, de, fr, es, pl, tr, zh ; langue du système détectée automatiquement
- **Interface légère** — ttkbootstrap, disposition verticale, barre d'état et pied de page fixés

## Capture d'écran

<details>
<summary>Fenêtre principale</summary>

![Fenêtre principale d'AntiYandexVanced](docs/screenshot.png)

</details>

## Builds prêts à l'emploi

Téléchargez depuis [Releases](https://github.com/retvil/AntiYandexVanced/releases) :

- **Windows** — `AntiYandexVanced.exe` (portable, fichier unique, ~35 Mo) — supprime Yandex Browser et Yandex Search
- **Windows** — `AntiYandexExtended.exe` (portable, fichier unique, ~35 Mo) — suppression de tous les produits Yandex (Yandex Disk, historique Punto Switcher, traces système, applications Store, Yandex.DNS)

Lancez-le **en tant qu'administrateur** — les politiques HKLM et le nettoyage du registre exigent des droits élevés.

## Installation depuis les sources

Python 3.10+ requis ([python.org](https://python.org)).

```bash
git clone https://github.com/retvil/AntiYandexVanced.git
cd AntiYandexVanced
pip install psutil ttkbootstrap
python main.py
```

Compiler votre propre EXE : lancez `build.bat` (PyInstaller, résultat dans `dist/`).

## Utilisation

1. **Terminer les processus** → **Rechercher Yandex** → **Supprimer Yandex** — on retire le navigateur lui-même.
2. **Scanner les détournements** — liste toutes les façons dont Yandex s'est enraciné dans le système.
3. **Supprimer les détournements** — fermez d'abord tous les navigateurs, puis retirez tout ce qui est trouvé.
4. Choisissez un moteur → **Appliquer la politique** — la recherche par défaut est verrouillée au niveau du système.

## FAQ

- **Pourquoi administrateur ?** Les politiques de recherche vivent dans HKLM, le nettoyage touche le registre système — droits élevés requis.
- **« Database locked » dans les résultats ?** Un navigateur Chromium tournait pendant le nettoyage. Fermez tous les navigateurs et relancez la suppression.
- **Comment retirer la politique de recherche ?** Le bouton **Supprimer les politiques Yandex** purge les valeurs ; dans Firefox, vous pouvez aussi supprimer le fichier `distribution\policies.json`.

## Auteur & support

**Nod33Eset** — fork de [TheCawa/AntiYandex](https://github.com/TheCawa/AntiYandex). Issues et PR bienvenues.

Si l'outil t'a débarrassé de Yandex, tu peux soutenir le développement :

**Crypto :**

- BTC : `bc1qunld3rsp37qf5gg69aune50y0qqkd0eugg7j97`
- TON : `UQDmvr4SKOxSION3Yky6aOgzAnCDXySPuAbG4EKJa5JUT7tC`
- USDT (TRC20) : `TBPJSSLu1mUcX54g9UyxUohYGf2fuRvbwd`
- USDT (ERC20) : `0x25CAED3776Ef5b18E03392bC5b254Bbd78E8180C`
- USDT (SOL) : `3qgN5z291CEcj2FUi2Zza5DioxKgNw72kC7P52pCcTrG`

## Licence

MIT — voir [LICENSE](LICENSE).
