# AntiYandex Vanced

[RU](#русский) | [EN](#english) | [UK](#українська) | [KK](#қазақша) | [DE](#deutsch) | [FR](#français) | [ES](#español) | [PL](#polski) | [TR](#türkçe) | [ZH](#中文)

Fork of [TheCawa/AntiYandex](https://github.com/TheCawa/AntiYandex) — a Windows utility that removes Yandex Browser and hardens the system against search hijacking.

![AntiYandexVanced screenshot](docs/screenshot.png)

---

## Русский

Утилита для полного удаления Яндекс.Браузера и защиты от повторного захвата поиска и браузера по умолчанию.

### Возможности
- Завершение процессов (`browser.exe`, `yandex.exe`), поиск и удаление Яндекс.Браузера, очистка реестра
- **Сканирование захвата поиска** — детект 11 способов, которыми Яндекс прописывается поиском/браузером по умолчанию:
  - каталоги установки на диске
  - записи Uninstall в реестре (HKLM, WOW6432Node, HKCU)
  - ассоциации браузера по умолчанию (`UserChoice` для http/https)
  - регистрация `StartMenuInternet`
  - ключи `Software\Yandex` (HKCU/HKLM/WOW6432Node)
  - hijack через enterprise-политики `DefaultSearchProvider*` (Яндекс сам так прописывается)
  - `Preferences` профилей Chromium (Chrome, Edge, Brave, Vivaldi)
  - записи поисковиков в `Web Data` (SQLite keywords)
  - `search.json.mozlz4` Firefox/Waterfox
  - SearchScopes (IE/legacy), автозапуск (Run/RunOnce)
- **Удаление захвата** — снятие всех найденных векторов одной кнопкой (с подтверждением)
- **Жёсткая политика поиска по умолчанию** — принудительная пропись одного из 10 поисковиков (Google, Bing, DuckDuckGo, Brave Search, Startpage, Mojeek, Qwant, Ecosia, Yahoo, SearXNG):
  - Chromium-браузеры: HKLM `SOFTWARE\Policies\...` `DefaultSearchProvider*` (Chrome, Edge, Brave, Vivaldi, Opera, Yandex Browser)
  - Firefox/Waterfox: `distribution\policies.json` (`SearchEngines` + `LockDefaultSearchEngine`)
  - кнопка «Снять политику Яндекса» удаляет Yandex-значения из реестра
- **10 языков интерфейса** (ru, en, uk, kk, de, fr, es, pl, tr, zh) — язык системы определяется автоматически, при отсутствии совпадения — английский
- Светлый интерфейс на ttkbootstrap, вертикальная компоновка

### Установка

**Вариант 1 — готовый EXE:** скачайте `AntiYandexVanced.exe` со страницы [Releases](https://github.com/retvil/AntiYandexVanced/releases) и запустите от имени администратора.

**Вариант 2 — из исходников:**

```bash
git clone https://github.com/retvil/AntiYandexVanced.git
cd AntiYandexVanced
pip install psutil ttkbootstrap
python main.py
```

---

### Требования
- Windows 10/11
- Python 3.10+ и `pip install psutil ttkbootstrap` (или собранный EXE)

### Использование
1. Запустите **от имени администратора** (нужно для HKLM-политик и удаления записей реестра).
2. «Завершить процессы» → «Поиск Яндекса» → «Удалить Яндекс».
3. «Сканировать захват поиска» — покажет все найденные способы захвата.
4. «Удалить захват» — уберёт их (закройте браузеры перед этим).
5. Выберите поисковик → «Применить политику» — поиск будет закреплён во всех браузерах.

### Сборка EXE
Запустите `build.bat` — соберёт однофайловый EXE в `dist/` через PyInstaller.

---

## English

A Windows utility that completely removes Yandex Browser and hardens the system against default-search and default-browser hijacking.

### Features
- Process termination (`browser.exe`, `yandex.exe`), Yandex Browser search/removal, registry cleanup
- **Search hijack scanner** — detects 11 vectors Yandex uses to set itself as default search/browser:
  - installation directories on disk
  - uninstall registry entries (HKLM, WOW6432Node, HKCU)
  - default-browser association (`UserChoice` for http/https)
  - `StartMenuInternet` client registrations
  - `Software\Yandex` key trees (HKCU/HKLM/WOW6432Node)
  - enterprise-policy hijack via `DefaultSearchProvider*` values (how Yandex hard-enforces itself)
  - per-profile Chromium `Preferences` JSON (Chrome, Edge, Brave, Vivaldi)
  - search-engine keyword rows in Chromium `Web Data` (SQLite)
  - Firefox/Waterfox `search.json.mozlz4`
  - SearchScopes (IE/legacy), autostart (Run/RunOnce)
- **Hijack removal** — removes every detected vector with one click (with confirmation)
- **Hard default-search policy** — enforces one of 10 engines (Google, Bing, DuckDuckGo, Brave Search, Startpage, Mojeek, Qwant, Ecosia, Yahoo, SearXNG):
  - Chromium browsers: HKLM `SOFTWARE\Policies\...` `DefaultSearchProvider*` (Chrome, Edge, Brave, Vivaldi, Opera, Yandex Browser)
  - Firefox/Waterfox: `distribution\policies.json` (`SearchEngines` + `LockDefaultSearchEngine`)
  - "Remove Yandex Policies" button strips Yandex values from the registry
- **10 UI languages** (ru, en, uk, kk, de, fr, es, pl, tr, zh) — system language auto-detected, English fallback
- Light ttkbootstrap UI, vertical layout

### Installation

**Option 1 — prebuilt EXE:** download `AntiYandexVanced.exe` from the [Releases](https://github.com/retvil/AntiYandexVanced/releases) page and run it as administrator.

**Option 2 — from source:**

```bash
git clone https://github.com/retvil/AntiYandexVanced.git
cd AntiYandexVanced
pip install psutil ttkbootstrap
python main.py
```

---

### Requirements
- Windows 10/11
- Python 3.10+ with `pip install psutil ttkbootstrap` (or a prebuilt EXE)

### Usage
1. Run **as administrator** (required for HKLM policies and registry cleanup).
2. "Kill Processes" → "Search Yandex" → "Delete Yandex".
3. "Scan Search Hijacks" — lists every detected hijack vector.
4. "Remove Hijacks" — removes them (close all browsers first).
5. Pick a search engine → "Apply Policy" — the default search is locked in all browsers.

### Building the EXE
Run `build.bat` — produces a one-file EXE in `dist/` via PyInstaller.

---

## Українська

Утиліта для повного видалення Яндекс.Браузера та захисту від повторного захоплення пошуку й браузера за замовчуванням.

### Можливості
- Завершення процесів (`browser.exe`, `yandex.exe`), пошук і видалення Яндекс.Браузера, очищення реєстру
- **Сканування захоплення пошуку** — виявлення 11 способів, якими Яндекс прописується пошуком/браузером за замовчуванням (шляхи встановлення, Uninstall-реєстр, UserChoice, StartMenuInternet, ключі `Software\Yandex`, hijack через політики `DefaultSearchProvider*`, `Preferences` профілів Chromium, `Web Data` SQLite, `search.json.mozlz4` Firefox, SearchScopes, автозапуск)
- **Видалення захоплення** — зняття всіх знайдених векторів однією кнопкою
- **Жорстка політика пошуку** — примусове закріплення одного з 10 пошуковиків (Google, Bing, DuckDuckGo, Brave Search, Startpage, Mojeek, Qwant, Ecosia, Yahoo, SearXNG) через HKLM-політики Chromium та `policies.json` Firefox
- **10 мов інтерфейсу** — мова системи визначається автоматично, за відсутності збігу — англійська

### Встановлення

**Варіант 1 — готовий EXE:** завантажте `AntiYandexVanced.exe` зі сторінки [Releases](https://github.com/retvil/AntiYandexVanced/releases) і запустіть від імені адміністратора.

**Варіант 2 — з джерел:**

```bash
git clone https://github.com/retvil/AntiYandexVanced.git
cd AntiYandexVanced
pip install psutil ttkbootstrap
python main.py
```

---

### Використання
1. Запустіть **від імені адміністратора**.
2. «Завершити процеси» → «Пошук Яндекса» → «Видалити Яндекс».
3. «Сканувати захоплення пошуку» → «Видалити захоплення» (закрийте браузери).
4. Виберіть пошуковик → «Застосувати політику».

---

## Қазақша

Yandex Browser-ді толық жою және әдепкі іздеу/браузерді қайта ұрлаудан қорғау утилитасы.

### Мүмкіндіктер
- Проcestерді тоқтату (`browser.exe`, `yandex.exe`), Yandex Browser іздеу/жою, реестрді тазарту
- **Іздеу ұрлауын сканерлеу** — Яндекстің әдепкі іздеу/браузер болып тіркелуінің 11 тәсілін анықтау (орнату жолдары, Uninstall-реестр, UserChoice, StartMenuInternet, `Software\Yandex` кілттері, `DefaultSearchProvider*` саясаттары арқылы ұрлау, Chromium `Preferences`, `Web Data` SQLite, Firefox `search.json.mozlz4`, SearchScopes, автозапуск)
- **Ұрлауды жою** — табылған барлық векторды бір батырмамен алып тастау
- **Қатаң іздеу саясаты** — 10 іздеу жүйесінің біреуін (Google, Bing, DuckDuckGo, Brave Search, Startpage, Mojeek, Qwant, Ecosia, Yahoo, SearXNG) Chromium HKLM-саясаттары және Firefox `policies.json` арқылы бекіту
- **10 интерфейс тілі** — жүйе тілі автоматты анықталады, сәйкестік болмаса — ағылшынша

### Орнату

**1-нұсқа — дайын EXE:** [Releases](https://github.com/retvil/AntiYandexVanced/releases) бетінен `AntiYandexVanced.exe` жүктеп алып, әкімші ретінде іске қосыңыз.

**2-нұсқа — бастапқы кодтан:**

```bash
git clone https://github.com/retvil/AntiYandexVanced.git
cd AntiYandexVanced
pip install psutil ttkbootstrap
python main.py
```

---

### Пайдалану
1. **Әкімші ретінде** іске қосыңыз.
2. «Проcestерді тоқтату» → «Яндексті іздеу» → «Яндексті жою».
3. «Іздеу ұрлауын сканерлеу» → «Ұрлауды жою» (браузерлерді жабыңыз).
4. Іздеу жүйесін таңдаңыз → «Саясатты қолдану».

---

## Deutsch

Ein Windows-Dienstprogramm, das Yandex Browser vollständig entfernt und das System vor der Entführung von Standardsuche und Standardbrowser schützt.

### Funktionen
- Prozessbeendigung (`browser.exe`, `yandex.exe`), Yandex-Browser-Suche/-Entfernung, Registry-Bereinigung
- **Such-Hijack-Scanner** — erkennt 11 Vektoren, mit denen Yandex sich als Standardsuche/Standardbrowser einträgt (Installationspfade, Uninstall-Registry, UserChoice, StartMenuInternet, `Software\Yandex`-Schlüssel, Hijack über `DefaultSearchProvider*`-Richtlinien, Chromium-`Preferences`, `Web Data`-SQLite, Firefox-`search.json.mozlz4`, SearchScopes, Autostart)
- **Hijacks entfernen** — alle erkannten Vektoren mit einem Klick entfernen
- **Harte Standardsuche-Richtlinie** — erzwingt eine von 10 Suchmaschinen (Google, Bing, DuckDuckGo, Brave Search, Startpage, Mojeek, Qwant, Ecosia, Yahoo, SearXNG) über HKLM-Richtlinien für Chromium und `policies.json` für Firefox
- **10 UI-Sprachen** — Systemsprache wird automatisch erkannt, sonst Englisch

### Installation

**Option 1 — fertige EXE:** laden Sie `AntiYandexVanced.exe` von der [Releases](https://github.com/retvil/AntiYandexVanced/releases)-Seite herunter und führen Sie es als Administrator aus.

**Option 2 — aus dem Quellcode:**

```bash
git clone https://github.com/retvil/AntiYandexVanced.git
cd AntiYandexVanced
pip install psutil ttkbootstrap
python main.py
```

---

### Verwendung
1. **Als Administrator** ausführen.
2. „Prozesse beenden“ → „Yandex suchen“ → „Yandex löschen“.
3. „Such-Hijacks scannen“ → „Hijacks entfernen“ (Browser vorher schließen).
4. Suchmaschine wählen → „Richtlinie anwenden“.

---

## Français

Un utilitaire Windows qui supprime complètement Yandex Browser et protège le système contre le détournement de la recherche et du navigateur par défaut.

### Fonctionnalités
- Terminaison des processus (`browser.exe`, `yandex.exe`), recherche/suppression de Yandex Browser, nettoyage du registre
- **Scanner les détournements** — détecte 11 vecteurs utilisés par Yandex pour s'imposer comme recherche/navigateur par défaut (chemins d'installation, registre Uninstall, UserChoice, StartMenuInternet, clés `Software\Yandex`, hijack via les politiques `DefaultSearchProvider*`, `Preferences` Chromium, `Web Data` SQLite, `search.json.mozlz4` Firefox, SearchScopes, démarrage automatique)
- **Supprimer les détournements** — retire tous les vecteurs détectés en un clic
- **Politique stricte de recherche par défaut** — impose l'un des 10 moteurs (Google, Bing, DuckDuckGo, Brave Search, Startpage, Mojeek, Qwant, Ecosia, Yahoo, SearXNG) via les politiques HKLM Chromium et `policies.json` Firefox
- **10 langues d'interface** — langue du système détectée automatiquement, sinon anglais

### Installation

**Option 1 — EXE prêt à l'emploi :** téléchargez `AntiYandexVanced.exe` depuis la page [Releases](https://github.com/retvil/AntiYandexVanced/releases) et lancez-le en tant qu'administrateur.

**Option 2 — depuis les sources :**

```bash
git clone https://github.com/retvil/AntiYandexVanced.git
cd AntiYandexVanced
pip install psutil ttkbootstrap
python main.py
```

---

### Utilisation
1. Lancer **en tant qu'administrateur**.
2. « Terminer les processus » → « Rechercher Yandex » → « Supprimer Yandex ».
3. « Scanner les détournements » → « Supprimer les détournements » (fermez les navigateurs).
4. Choisir un moteur → « Appliquer la politique ».

---

## Español

Una utilidad de Windows que elimina completamente Yandex Browser y protege el sistema contra el secuestro del buscador y navegador predeterminados.

### Características
- Terminación de procesos (`browser.exe`, `yandex.exe`), búsqueda/eliminación de Yandex Browser, limpieza del registro
- **Escanear secuestros de búsqueda** — detecta 11 vectores que Yandex usa para establecerse como buscador/navegador predeterminado (rutas de instalación, registro Uninstall, UserChoice, StartMenuInternet, claves `Software\Yandex`, secuestro vía políticas `DefaultSearchProvider*`, `Preferences` de Chromium, `Web Data` SQLite, `search.json.mozlz4` de Firefox, SearchScopes, inicio automático)
- **Eliminar secuestros** — quita todos los vectores detectados con un clic
- **Política estricta de búsqueda predeterminada** — impone uno de los 10 buscadores (Google, Bing, DuckDuckGo, Brave Search, Startpage, Mojeek, Qwant, Ecosia, Yahoo, SearXNG) vía políticas HKLM de Chromium y `policies.json` de Firefox
- **10 idiomas de interfaz** — idioma del sistema detectado automáticamente, si no hay coincidencia, inglés

### Instalación

**Opción 1 — EXE listo:** descargue `AntiYandexVanced.exe` desde la página de [Releases](https://github.com/retvil/AntiYandexVanced/releases) y ejecútelo como administrador.

**Opción 2 — desde el código fuente:**

```bash
git clone https://github.com/retvil/AntiYandexVanced.git
cd AntiYandexVanced
pip install psutil ttkbootstrap
python main.py
```

---

### Uso
1. Ejecutar **como administrador**.
2. «Terminar procesos» → «Buscar Yandex» → «Eliminar Yandex».
3. «Escanear secuestros de búsqueda» → «Eliminar secuestros» (cierre los navegadores).
4. Elija un buscador → «Aplicar política».

---

## Polski

Narzędzie dla Windows, które całkowicie usuwa Yandex Browser i chroni system przed przejęciem domyślnej wyszukiwarki i przeglądarki.

### Funkcje
- Zakończenie procesów (`browser.exe`, `yandex.exe`), wyszukiwanie/usuwanie Yandex Browser, czyszczenie rejestru
- **Skanowanie przejęć wyszukiwania** — wykrywa 11 wektorów, którymi Yandex wpisuje się jako domyślna wyszukiwarka/przeglądarka (ścieżki instalacji, rejestr Uninstall, UserChoice, StartMenuInternet, klucze `Software\Yandex`, przejęcie przez polityki `DefaultSearchProvider*`, `Preferences` Chromium, `Web Data` SQLite, `search.json.mozlz4` Firefox, SearchScopes, autostart)
- **Usuwanie przejęć** — usuwa wszystkie wykryte wektory jednym kliknięciem
- **Twarda polityka wyszukiwania domyślnego** — wymusza jedną z 10 wyszukiwarek (Google, Bing, DuckDuckGo, Brave Search, Startpage, Mojeek, Qwant, Ecosia, Yahoo, SearXNG) przez polityki HKLM Chromium i `policies.json` Firefox
- **10 języków interfejsu** — język systemu wykrywany automatycznie, w razie braku dopasowania — angielski

### Instalacja

**Opcja 1 — gotowy EXE:** pobierz `AntiYandexVanced.exe` ze strony [Releases](https://github.com/retvil/AntiYandexVanced/releases) i uruchom jako administrator.

**Opcja 2 — z kodu źródłowego:**

```bash
git clone https://github.com/retvil/AntiYandexVanced.git
cd AntiYandexVanced
pip install psutil ttkbootstrap
python main.py
```

---

### Użycie
1. Uruchom **jako administrator**.
2. „Zakończ procesy” → „Szukaj Yandex” → „Usuń Yandex”.
3. „Skanuj przejęcia wyszukiwania” → „Usuń przejęcia” (zamknij przeglądarki).
4. Wybierz wyszukiwarkę → „Zastosuj politykę”.

---

## Türkçe

Yandex Browser'ı tamamen kaldıran ve sistemi varsayılan arama/tarayıcı ele geçirmelerine karşı koruyan bir Windows yardımcı programı.

### Özellikler
- İşlem sonlandırma (`browser.exe`, `yandex.exe`), Yandex Browser arama/kaldırma, kayıt defteri temizliği
- **Arama ele geçirme tarayıcısı** — Yandex'in varsayılan arama/tarayıcı olarak kendini yerleştirmek için kullandığı 11 vektörü tespit eder (kurulum yolları, Uninstall kayıt defteri, UserChoice, StartMenuInternet, `Software\Yandex` anahtarları, `DefaultSearchProvider*` ilkeleri üzerinden ele geçirme, Chromium `Preferences`, `Web Data` SQLite, Firefox `search.json.mozlz4`, SearchScopes, otomatik başlatma)
- **Ele geçirmeleri kaldır** — tespit edilen tüm vektörleri tek tıkla kaldırır
- **Katı varsayılan arama ilkesi** — 10 arama motorundan birini (Google, Bing, DuckDuckGo, Brave Search, Startpage, Mojeek, Qwant, Ecosia, Yahoo, SearXNG) Chromium HKLM ilkeleri ve Firefox `policies.json` ile zorunlu kılar
- **10 arayüz dili** — sistem dili otomatik algılanır, eşleşme yoksa İngilizce

### Kurulum

**Seçenek 1 — hazır EXE:** [Releases](https://github.com/retvil/AntiYandexVanced/releases) sayfasından `AntiYandexVanced.exe` indirin ve yönetici olarak çalıştırın.

**Seçenek 2 — kaynaktan:**

```bash
git clone https://github.com/retvil/AntiYandexVanced.git
cd AntiYandexVanced
pip install psutil ttkbootstrap
python main.py
```

---

### Kullanım
1. **Yönetici olarak** çalıştırın.
2. „İşlemleri Sonlandır” → „Yandex Ara” → „Yandex'i Sil”.
3. „Arama Ele Geçirmelerini Tara” → „Ele Geçirmeleri Kaldır” (tarayıcıları kapatın).
4. Bir arama motoru seçin → „İlkeyi Uygula”.

---

## 中文

一款 Windows 工具，可彻底移除 Yandex 浏览器，并防止系统默认搜索引擎和默认浏览器被再次劫持。

### 功能
- 结束进程（`browser.exe`、`yandex.exe`）、搜索并删除 Yandex 浏览器、清理注册表
- **扫描搜索劫持** — 检测 Yandex 用来把自己设为默认搜索/浏览器的 11 种途径（安装目录、Uninstall 注册表、UserChoice、StartMenuInternet、`Software\Yandex` 键、通过 `DefaultSearchProvider*` 策略劫持、Chromium `Preferences`、`Web Data` SQLite、Firefox `search.json.mozlz4`、SearchScopes、自启动）
- **移除劫持** — 一键移除所有检测到的劫持途径（带确认）
- **强制默认搜索策略** — 通过 Chromium HKLM 策略和 Firefox `policies.json` 强制使用 10 个搜索引擎之一（Google、Bing、DuckDuckGo、Brave Search、Startpage、Mojeek、Qwant、Ecosia、Yahoo、SearXNG）
- **10 种界面语言** — 自动检测系统语言，无匹配时使用英语

### 安装

**方式 1 — 现成 EXE：** 从 [Releases](https://github.com/retvil/AntiYandexVanced/releases) 页面下载 `AntiYandexVanced.exe` 并以管理员身份运行。

**方式 2 — 从源码运行：**

```bash
git clone https://github.com/retvil/AntiYandexVanced.git
cd AntiYandexVanced
pip install psutil ttkbootstrap
python main.py
```

---

### 使用方法
1. 以**管理员身份**运行。
2. 「结束进程」→「搜索 Yandex」→「删除 Yandex」。
3. 「扫描搜索劫持」→「移除劫持」（请先关闭所有浏览器）。
4. 选择搜索引擎 →「应用策略」。

---

## Contacts / Контакты

- Upstream (original): [TheCawa/AntiYandex](https://github.com/TheCawa/AntiYandex)
- This fork: [retvil/AntiYandexVanced](https://github.com/retvil/AntiYandexVanced)
- Issues and PRs are welcome in this repository.
