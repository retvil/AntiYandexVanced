# Журнал змін

Усі значущі зміни проєкту документуються в цьому файлі.

Формат базується на [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
проєкт дотримується [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> Першоджерело — англійський [CHANGELOG.md](CHANGELOG.md); цей переклад може трохи відставати.

## [2.8.0] - 2026-10-22

### Додано
- **Скан зони IE (zone map)** — знаходить записи zone-map для доменів Яндекса
  (залишки «надійних сайтів»); видалення зносить піддерево домену (спочатку
  експорт)
- **Скан RegisteredApplications** — знаходить записи Яндекса в метаданих
  застосунків за замовчуванням; видалення стирає значення (спочатку експорт)
- **Скан MUICache** — знаходить сліди запуску виконуваних файлів Яндекса;
  видалення стирає значення кешу (спочатку експорт)
- **Сліди інсталяторів у %TEMP%** — scan_traces тепер також репортить
  інсталятори Яндекса, що залишилися у тимчасовій папці користувача
- **Каталоги продуктів per-user** — scan_product_dirs тепер також покриває
  `%LOCALAPPDATA%\Programs\Yandex*` (legacy-встановлення Яндекс Музики /
  Месенджера / Перекладача), папка браузера виключена
- **Kill процесів за шляхом (Vanced)** — браузерний kill тепер також матчить
  процеси, чиї exe лежать під шляхом YandexBrowser (crashpad, updater),
  а не лише вузький список імен browser.exe/yandex.exe
- **Скан hijack стартових URL** — знаходить URL Яндекса в enterprise-політиках
  `RestoreOnStartupURLs` (Edge, Chrome, Chromium, Brave, Vivaldi, Opera,
  Яндекс.Браузер); видалення вичищає значення Яндекса
- **Скан hijack домашньої сторінки Firefox** — знаходить
  `browser.startup.homepage` з посиланням на Яндекс у `prefs.js`
  Firefox/Waterfox; видалення переписує файл (спочатку бекап)

## [2.7.0] - 2026-10-21

### Додано
- **Скан Яндекс.DNS** (Extended) — знаходить мережеві адаптери з DNS-серверами
  Яндекса (77.88.8.x basic/safe/family); видалення повертає адаптеру
  автоматичний DNS; з підтвердженням
- **Скан hijack стартової сторінки** — знаходить legacy-домашню сторінку IE
  (`HKCU\...\Internet Explorer\Main\Start Page`) з посиланням на
  Яндекс/ya.ru; видалення повертає дефолт (обидва видання)

## [2.6.0] - 2026-10-21

### Додано
- **Extended-видання**: скан Store (Appx) застосунків — знаходить Яндекс
  Музику, Алису, Месенджер та інші Store-застосунки Яндекса, видаляє через
  `Remove-AppxPackage`
- **Extended-видання**: скан каталогів небраузерних продуктів під
  `Program Files\Yandex\` (Яндекс.Диск, Punto Switcher, IME, ...) з бекапом
  перед видаленням
- **Extended-видання**: скан локальних даних небраузерних продуктів під
  `%LOCALAPPDATA%\Yandex\` (локальні дані Punto Switcher, апдейтер
  Яндекс.Диска, Beta-збірки) — з підтвердженням, бекап перед видаленням
- **Extended-видання**: «Kill Processes» тепер завершує процеси всіх
  продуктів Яндекса (Яндекс.Диск, Punto Switcher, Store-застосунки),
  а не лише браузера

## [2.5.0] - 2026-10-21

### Додано
- Два видання з однієї кодової бази: **AntiYandexVanced** (видалення
  Яндекс.Браузера + Яндекс.Пошуку) та **AntiYandexExtended** (усі продукти
  Яндекса) — профілі продуктів у `profiles.py` обирають охоплення скану,
  спільний GUI в `app.py`, тонкі точки входу `main.py` / `main_extended.py`
- `build.bat` тепер збирає обидва EXE

## [2.4.0] - 2026-10-21

### Додано
- 16-й–30-й вектори hijack: інтеграція Яндекс.Диска в оболонку (іконки-оверлеї
  + обробники контекстного меню), вимкнений автозапуск (`StartupApproved`),
  `App Paths`, ярлики (Робочий стіл / Меню Пуск / панель завдань),
  каталоги-залишки (ProgramData, Roaming, дані Яндекс.Диска та
  синхронізовані файли), записи `hosts`, правила брандмауера Windows,
  обробники URI-протоколів, розширення браузерів (маніфести Chromium +
  `.xpi` Firefox), куки yandex.ru (Chromium + Firefox), асоціації
  `OpenWithProgids`/`OpenWithList`, сліди Prefetch / CrashDumps / WER,
  винятки Windows Defender, користувацькі розкладки клавіатури (Yandex IME)
- Підтвердження згоди: знахідки, що торкаються користувацьких даних (файли
  Яндекс.Диска, історія Punto Switcher, розширення, куки, винятки Defender),
  потребують явного додаткового підтвердження перед видаленням
- Юніт-тести для байт-детекту `.lnk`, фільтрації рядків hosts, парсингу
  виводу брандмауера та покриття consent-префіксів

## [2.3.0] - 2026-10-20

### Додано
- 13-й–15-й вектори hijack: служби Windows (скан за реєстром, видалення через
  `sc stop` + `sc delete`), Punto Switcher (детект за маркером `punto`),
  файлові асоціації (скан + видалення ProgId у `FileExts\<ext>\UserChoice`)
- Діалог вибору після скану: обрати, які саме знахідки видаляти, замість
  «все або нічого»
- Винятки: зняті галочки можна зберегти до
  `%APPDATA%\AntiYandexVanced\exclusions.json` — майбутні скани автоматично
  їх не обирають, але вони залишаються доступними в діалозі; винятки можна
  скинути з діалогу
- Юніт-тести персистентності винятків і маркера Punto Switcher

## [2.2.0] - 2026-10-20

### Додано
- Бекап перед видаленням: кожен задіяний ключ реєстру / файл профілю
  експортується до `%APPDATA%\AntiYandexVanced\backup\<timestamp>\` перед
  видаленням
- Журнал операцій: `%APPDATA%\AntiYandexVanced\antiyandex.log`
- 12-й вектор hijack: записи Планувальника завдань Windows (завдання апдейтера
  Яндекса)
- Скан/чистка HKCU-політик Chromium (per-user політики, раніше лише HKLM)
- Перевірка прав адміністратора на старті з попередженням у статус-барі
- Пропозиція закрити запущені браузери перед видаленням hijack (запобігає
  «database locked»)
- Пропозиція «відкрити папку звіту», коли частина hijack-знахідок не
  видалилася
- Юніт-тести чистої логіки (пошук двигуна, Firefox policies.json,
  LZ4-декомпресор)

### Виправлено
- Усі оновлення UI з фонових потоків тепер маршаляться до головного потоку
  через `root.after` (tkinter не потокобезпечний)
- Голі `except:` замінені на `except OSError`
- Чистка Web Data тепер видаляє рівно знайдені рядки (за `rowid`), а не за
  підрядком URL — детект і видалення узгоджені
- SQLite-з'єднання закриваються на error-шляхах (`finally`)
- Firefox `policies.json` більше не містить `null` `SuggestURLTemplate`
- Політики Firefox більше не пишуться до неіснуючих папок встановлення
- Захардкоджений український рядок помилки адміна замінений на перекладний
  ключ в усіх 10 мовах UI
- `shutil.rmtree` тепер репортить, які файли заблоковані, замість загальної
  помилки
- Биті LZ4-блоки з невалідними зміщеннями викликають виняток замість
  повернення сміття

## [2.1.2] - 2026-10-20

### Змінено
- Заголовок застосунку скорочено до «Удаление Яндекс» / «Remove Yandex»
  (ru/en/uk)
- Футер притиснуто до правого нижнього кута: автор, версія та клікабельне
  посилання на GitHub
- Посилання репозиторію встановлено на
  `https://github.com/retvil/AntiYandexVanced`

## [2.1.0] - 2026-10-20

### Додано
- Вертикальна компоновка вікна (560×700): центрований стек дій, картки секцій
  на всю ширину
- Світла тема UI на **ttkbootstrap** (тема `flatly`) — заміна CustomTkinter
  на легший ttk-стек
- Футер з автором, версією та клікабельним посиланням на репозиторій GitHub

### Змінено
- Міграція UI-бібліотеки: tkinter → CustomTkinter → ttkbootstrap
- Селектор мови перенесено до правого верхнього кута

## [2.0.0] - 2026-10-20

Форк [TheCawa/AntiYandex](https://github.com/TheCawa/AntiYandex) 1.3.

### Додано
- **Сканер hijack пошуку** — детектить 11 векторів, якими Яндекс
  прописується дефолтним пошуком/браузером:
  - каталоги встановлення на диску
  - записи Uninstall у реєстрі (HKLM, WOW6432Node, HKCU)
  - асоціація браузера за замовчуванням Windows (`UserChoice` ProgId для
    http/https)
  - реєстрації клієнтів браузерів `StartMenuInternet`
  - окремі дерева ключів `Software\Yandex` (HKCU/HKLM/WOW6432Node)
  - hijack через enterprise-політики `DefaultSearchProvider*` (жорсткий
    спосіб закріплення Яндекса)
  - per-profile JSON `Preferences` Chromium (Chrome, Edge, Brave, Vivaldi,
    Яндекс.Браузер)
  - рядки ключових слів пошуковиків у SQLite-базах `Web Data` Chromium
  - Firefox/Waterfox `search.json.mozlz4` (з вбудованим pure-Python
    LZ4-декомпресором блоків)
  - legacy-записи `SearchScopes` IE/Windows
  - записи автозапуску (`Run`/`RunOnce`)
- **Видалення hijack** — видалення всіх знайдених векторів одним кліком,
  у кожного вектора свій remover: рекурсивне видалення ключів реєстру,
  скидання `UserChoice`, чистка `Preferences`, `DELETE FROM keywords` у
  Web Data, скидання `search.json.mozlz4` (Firefox перестворює дефолти),
  видалення значень автозапуску. Заблоковані бази/файли (браузер запущено)
  репортяться, без крашів.
- **Жорстка політика пошуку за замовчуванням** — закріплює один із 10
  пошуковиків (Google, Bing, DuckDuckGo, Brave Search, Startpage, Mojeek,
  Qwant, Ecosia, Yahoo, SearXNG):
  - сімейство Chromium через HKLM `SOFTWARE\Policies\...` значення
    `DefaultSearchProvider*` (Chrome, Edge, Brave, Vivaldi, Opera,
    Яндекс.Браузер)
  - Firefox/Waterfox через `distribution\policies.json` (`SearchEngines` +
    `LockDefaultSearchEngine` + `PreventSearchEngineInstall`)
- Кнопка **«Видалити політики Яндекса»** — вичищає значення політик
  `DefaultSearchProvider*` Яндекса з реєстру
- **10 мов UI** (ru, en, uk, kk, de, fr, es, pl, tr, zh) в окремому модулі
  `translations.py`; мова системи визначається автоматично через Windows UI
  language API (`GetUserDefaultUILanguage`), фолбек на англійську
- Випадний список зміни мови в UI

### Змінено
- Код розбито на модулі: `engines.py`, `yandex_detect.py`, `policies.py`,
  `translations.py`, `main.py`

## [1.3.0] - upstream

База [TheCawa/AntiYandex](https://github.com/TheCawa/AntiYandex):
- Завершення процесів Яндекс.Браузера (`browser.exe`, `yandex.exe`)
- Пошук шляхів встановлення
- Чистка записів Uninstall у реєстрі
- Видалення папки браузера
- Перемикач інтерфейсу RU/EN

[Unreleased]: https://github.com/retvil/AntiYandexVanced/compare/v2.1.2...HEAD
[2.1.2]: https://github.com/retvil/AntiYandexVanced/compare/v2.1.0...v2.1.2
[2.1.0]: https://github.com/retvil/AntiYandexVanced/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/retvil/AntiYandexVanced/compare/v1.3.0...v2.0.0
