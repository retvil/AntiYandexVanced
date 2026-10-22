# Journal des modifications

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> La source de référence est le [CHANGELOG.md](CHANGELOG.md) anglais ; cette traduction peut légèrement prendre du retard.

## [2.8.0] - 2026-10-22

### Ajouté
- **Scan de la zone IE (zone map)** — détecte les entrées zone-map pour les
  domaines Yandex (résidus de « sites approuvés ») ; la suppression efface
  le sous-arbre du domaine (exporté d'abord)
- **Scan RegisteredApplications** — détecte les entrées Yandex dans les
  métadonnées des applications par défaut ; la suppression efface la
  valeur (exportée d'abord)
- **Scan MUICache** — détecte les traces d'exécution des exécutables
  Yandex ; la suppression efface la valeur du cache (exportée d'abord)
- **Traces d'installateurs dans %TEMP%** — scan_traces signale désormais
  aussi les installateurs Yandex laissés dans le dossier temporaire de
  l'utilisateur
- **Répertoires de produits per-user** — scan_product_dirs couvre désormais
  aussi `%LOCALAPPDATA%\Programs\Yandex*` (installations legacy de Yandex
  Music / Messenger / Translate), le dossier du navigateur est exclu
- **Kill de processus par chemin (Vanced)** — le kill côté navigateur
  détecte désormais aussi les processus dont l'exécutable se trouve sous un
  chemin YandexBrowser (crashpad, updater), et pas seulement la liste
  étroite browser.exe/yandex.exe
- **Scan de détournement des URL de démarrage** — détecte les URL Yandex
  dans les politiques d'entreprise `RestoreOnStartupURLs` (Edge, Chrome,
  Chromium, Brave, Vivaldi, Opera, Yandex Browser) ; la suppression purge
  les valeurs Yandex
- **Scan de détournement de la page d'accueil Firefox** — détecte
  `browser.startup.homepage` pointant vers Yandex dans le `prefs.js` de
  Firefox/Waterfox ; la suppression réécrit le fichier (sauvegarde d'abord)

## [2.7.0] - 2026-10-21

### Ajouté
- **Scan Yandex.DNS** (Extended) — détecte les adaptateurs réseau configurés
  avec les serveurs DNS Yandex (77.88.8.x basic/safe/family) ; la
  suppression remet l'adaptateur en DNS automatique ; avec confirmation
- **Scan de détournement de la page de démarrage** — détecte la page de
  démarrage IE legacy (`HKCU\...\Internet Explorer\Main\Start Page`)
  pointant vers Yandex/ya.ru ; la suppression restaure la valeur par
  défaut (les deux éditions)

## [2.6.0] - 2026-10-21

### Ajouté
- **Édition Extended** : scan des applications Store (Appx) — détecte
  Yandex Music, Alice, Messenger et les autres applications Store Yandex,
  les supprime via `Remove-AppxPackage`
- **Édition Extended** : scan des répertoires de produits non-navigateur
  sous `Program Files\Yandex\` (Yandex Disk, Punto Switcher, IME, ...) avec
  sauvegarde avant suppression
- **Édition Extended** : scan des données locales non-navigateur sous
  `%LOCALAPPDATA%\Yandex\` (données locales Punto Switcher, updater de
  Yandex Disk, builds Beta) — avec confirmation, sauvegarde avant
  suppression
- **Édition Extended** : « Kill Processes » termine désormais les processus
  de tous les produits Yandex (Yandex Disk, Punto Switcher, applications
  Store), pas seulement le navigateur

## [2.5.0] - 2026-10-21

### Ajouté
- Deux éditions depuis une même base de code : **AntiYandexVanced**
  (suppression de Yandex Browser + Yandex Search) et **AntiYandexExtended**
  (tous les produits Yandex) — les profils de produits dans `profiles.py`
  choisissent le périmètre du scan, GUI partagé dans `app.py`, points
  d'entrée minces `main.py` / `main_extended.py`
- `build.bat` construit désormais les deux EXE

## [2.4.0] - 2026-10-21

### Ajouté
- 16e–30e vecteurs de détournement : intégration shell de Yandex Disk
  (overlays d'icônes + gestionnaires de menu contextuel), autostart
  désactivé (`StartupApproved`), `App Paths`, raccourcis (Bureau / Menu
  Démarrer / barre des tâches), répertoires résiduels (ProgramData,
  Roaming, données Yandex Disk et fichiers synchronisés), entrées `hosts`,
  règles du pare-feu Windows, gestionnaires de protocoles URI, extensions
  de navigateur (manifestes Chromium + `.xpi` Firefox), cookies yandex.ru
  (Chromium + Firefox), associations `OpenWithProgids`/`OpenWithList`,
  traces Prefetch / CrashDumps / WER, exclusions Windows Defender,
  dispositions clavier personnalisées (Yandex IME)
- Confirmation de consentement : les détections touchant les données
  utilisateur (fichiers Yandex Disk, historique Punto Switcher,
  extensions, cookies, exclusions Defender) exigent une confirmation
  supplémentaire explicite avant suppression
- Tests unitaires pour la détection d'octets `.lnk`, le filtrage des
  lignes hosts, l'analyse de la sortie du pare-feu et la couverture des
  préfixes de consentement

## [2.3.0] - 2026-10-20

### Ajouté
- 13e–15e vecteurs de détournement : services Windows (scan via le
  registre, suppression via `sc stop` + `sc delete`), Punto Switcher
  (détection via le marqueur `punto`), associations de fichiers (scan +
  suppression du ProgId dans `FileExts\<ext>\UserChoice`)
- Boîte de dialogue de sélection après le scan : choisir exactement quelles
  détections supprimer au lieu de « tout ou rien »
- Exclusions : les détections décochées peuvent être enregistrées dans
  `%APPDATA%\AntiYandexVanced\exclusions.json` — les scans futurs les
  désélectionnent automatiquement, mais elles restent sélectionnables dans
  la boîte de dialogue ; les exclusions peuvent être réinitialisées depuis
  la boîte de dialogue
- Tests unitaires pour la persistance des exclusions et le marqueur Punto
  Switcher

## [2.2.0] - 2026-10-20

### Ajouté
- Sauvegarde avant suppression : chaque clé de registre / fichier de profil
  touché est exporté vers
  `%APPDATA%\AntiYandexVanced\backup\<timestamp>\` avant suppression
- Journal des opérations : `%APPDATA%\AntiYandexVanced\antiyandex.log`
- 12e vecteur de détournement : entrées du Planificateur de tâches Windows
  (tâches de l'updater Yandex)
- Scan/nettoyage des politiques Chromium HKCU (politiques par utilisateur,
  auparavant HKLM uniquement)
- Vérification des droits administrateur au démarrage avec avertissement
  dans la barre d'état
- Invite à fermer les navigateurs en cours avant la suppression des
  détournements (évite « database locked »)
- Proposition « ouvrir le dossier du rapport » lorsque certains éléments
  de détournement n'ont pas pu être supprimés
- Tests unitaires de la logique pure (recherche de moteur, Firefox
  policies.json, décompresseur LZ4)

### Corrigé
- Toutes les mises à jour de l'UI depuis les threads d'arrière-plan sont
  désormais marshalées vers le thread principal via `root.after`
  (tkinter n'est pas thread-safe)
- Les clauses `except:` nues remplacées par `except OSError`
- Le nettoyage de Web Data supprime désormais exactement les lignes
  détectées (par `rowid`), pas par sous-chaîne d'URL — détection et
  suppression sont cohérentes
- Les connexions SQLite sont fermées sur les chemins d'erreur (`finally`)
- Firefox `policies.json` ne contient plus de `SuggestURLTemplate` `null`
- Les politiques Firefox ne sont plus écrites dans des dossiers
  d'installation inexistants
- La chaîne d'erreur admin codée en dur en russe remplacée par une clé
  traduisible dans les 10 langues de l'UI
- `shutil.rmtree` signale désormais quels fichiers sont verrouillés au
  lieu d'une erreur générique
- Les blocs LZ4 corrompus avec des offsets de correspondance invalides
  lèvent une exception au lieu de renvoyer des données corrompues

## [2.1.2] - 2026-10-20

### Modifié
- Titre de l'application raccourci en « Удаление Яндекс » / « Remove
  Yandex » (ru/en/uk)
- Pied de page fixé en bas à droite : auteur, version et lien GitHub
  cliquable
- Lien du dépôt défini sur `https://github.com/retvil/AntiYandexVanced`

## [2.1.0] - 2026-10-20

### Ajouté
- Disposition verticale de la fenêtre (560×700) : pile d'actions centrée,
  cartes de sections pleine largeur
- Thème UI clair sur **ttkbootstrap** (thème `flatly`) — CustomTkinter
  remplacé par une pile ttk plus légère
- Pied de page avec auteur, version et lien cliquable vers le dépôt GitHub

### Modifié
- Migration de la bibliothèque UI : tkinter → CustomTkinter → ttkbootstrap
- Sélecteur de langue déplacé dans le coin supérieur droit

## [2.0.0] - 2026-10-20

Fork de [TheCawa/AntiYandex](https://github.com/TheCawa/AntiYandex) 1.3.

### Ajouté
- **Scanner de détournement de recherche** — détecte les 11 vecteurs par
  lesquels Yandex s'installe comme recherche/navigateur par défaut :
  - répertoires d'installation sur le disque
  - entrées Uninstall du registre (HKLM, WOW6432Node, HKCU)
  - association navigateur par défaut de Windows (ProgId `UserChoice` pour
    http/https)
  - enregistrements de clients navigateurs `StartMenuInternet`
  - arbres de clés `Software\Yandex` autonomes (HKCU/HKLM/WOW6432Node)
  - détournement via les politiques d'entreprise `DefaultSearchProvider*`
    (la manière « dure » dont Yandex s'impose)
  - JSON `Preferences` par profil de Chromium (Chrome, Edge, Brave,
    Vivaldi, Yandex Browser)
  - lignes de mots-clés des moteurs de recherche dans les bases SQLite
    `Web Data` de Chromium
  - Firefox/Waterfox `search.json.mozlz4` (avec un décompresseur de blocs
    LZ4 pure-Python intégré)
  - entrées `SearchScopes` legacy IE/Windows
  - entrées d'autostart (`Run`/`RunOnce`)
- **Suppression des détournements** — suppression en un clic de chaque
  vecteur détecté, avec un remover par vecteur : suppression récursive des
  clés de registre, réinitialisation `UserChoice`, nettoyage `Preferences`,
  `DELETE FROM keywords` dans Web Data, réinitialisation
  `search.json.mozlz4` (Firefox reconstruit les valeurs par défaut),
  suppression des valeurs d'autostart. Les bases/fichiers verrouillés
  (navigateur en cours) sont signalés, sans crash.
- **Politique stricte de recherche par défaut** — impose l'un des 10
  moteurs (Google, Bing, DuckDuckGo, Brave Search, Startpage, Mojeek,
  Qwant, Ecosia, Yahoo, SearXNG) :
  - famille Chromium via les valeurs HKLM `SOFTWARE\Policies\...`
    `DefaultSearchProvider*` (Chrome, Edge, Brave, Vivaldi, Opera,
    Yandex Browser)
  - Firefox/Waterfox via `distribution\policies.json` (`SearchEngines` +
    `LockDefaultSearchEngine` + `PreventSearchEngineInstall`)
- Bouton **« Supprimer les politiques Yandex »** — purge les valeurs de
  politique `DefaultSearchProvider*` de Yandex du registre
- **10 langues d'UI** (ru, en, uk, kk, de, fr, es, pl, tr, zh) dans un
  module dédié `translations.py` ; langue du système détectée
  automatiquement via l'API Windows UI language
  (`GetUserDefaultUILanguage`), repli sur l'anglais
- Liste déroulante de changement de langue dans l'UI

### Modifié
- Code divisé en modules : `engines.py`, `yandex_detect.py`, `policies.py`,
  `translations.py`, `main.py`

## [1.3.0] - upstream

Base de [TheCawa/AntiYandex](https://github.com/TheCawa/AntiYandex) :
- Terminaison des processus de Yandex Browser (`browser.exe`, `yandex.exe`)
- Recherche des chemins d'installation
- Nettoyage des entrées Uninstall du registre
- Suppression du dossier du navigateur
- Bascule d'interface RU/EN

[Unreleased]: https://github.com/retvil/AntiYandexVanced/compare/v2.1.2...HEAD
[2.1.2]: https://github.com/retvil/AntiYandexVanced/compare/v2.1.0...v2.1.2
[2.1.0]: https://github.com/retvil/AntiYandexVanced/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/retvil/AntiYandexVanced/compare/v1.3.0...v2.0.0
