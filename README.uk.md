# AntiYandex Vanced

[![Release](https://img.shields.io/github/v/release/retvil/AntiYandexVanced?sort=date)](https://github.com/retvil/AntiYandexVanced/releases) [![Platform Windows](https://img.shields.io/badge/platform-Windows-blue)](https://github.com/retvil/AntiYandexVanced/releases) [![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

**Повне видалення Яндекс.Браузера та жорсткий захист пошуку за замовчуванням від захоплення — 11 векторів детекту, 10 пошуковиків, 10 мов інтерфейсу.**

[🇬🇧 English](README.md) | [🇷🇺 Русский](README.ru.md) | **🇺🇦 Українська** | [🇰🇿 Қазақша](README.kk.md) | [🇩🇪 Deutsch](README.de.md) | [🇫🇷 Français](README.fr.md) | [🇪🇸 Español](README.es.md) | [🇵🇱 Polski](README.pl.md) | [🇹🇷 Türkçe](README.tr.md) | [🇨🇳 中文](README.zh.md)

## Що це?

Яндекс встановлює не просто браузер — він тихо прописується пошуком і браузером за замовчуванням через десяток різних механізмів системи: асоціації в реєстрі, enterprise-політики, налаштування профілів браузерів, навіть бази пошуковиків усередині профілів Chromium. Видалення одного браузера цього не скасовує.

**AntiYandex Vanced** (форк [TheCawa/AntiYandex](https://github.com/TheCawa/AntiYandex)) знаходить **усі 11 векторів захоплення**, прибирає їх однією кнопкою, а потім **жорстко закріплює пошук за замовчуванням** за обраним пошуковиком через enterprise-політики Windows — щоб ніщо не могло тихо повернути все назад.

## Можливості

- **Сканер захоплення** — детект 11 векторів: шляхи встановлення, записи Uninstall у реєстрі, асоціація `UserChoice`, реєстрації `StartMenuInternet`, дерева ключів `Software\Yandex`, hijack через політики `DefaultSearchProvider*`, `Preferences` профілів Chromium, ключові слова в `Web Data` (SQLite), `search.json.mozlz4` Firefox, legacy `SearchScopes`, автозапуск
- **Видалення в один клік** — у кожного вектора свій remover; заблоковані бази чесно репортяться, без крашів
- **Жорстка політика пошуку** — закріплює пошук за одним із 10 пошуковиків (Google, Bing, DuckDuckGo, Brave Search, Startpage, Mojeek, Qwant, Ecosia, Yahoo, SearXNG) через HKLM-політики для Chrome, Edge, Brave, Vivaldi, Opera та Яндекс.Браузера + `policies.json` для Firefox/Waterfox
- **Чистка политик** — вичищає значення `DefaultSearchProvider*` Яндекса з реєстру
- **10 мов інтерфейсу** — ru, en, uk, kk, de, fr, es, pl, tr, zh; мова системи визначається автоматично
- **Легкий інтерфейс** — ttkbootstrap, вертикальна компоновка, зафіксовані статус-бар і футер

## Скріншот

<details>
<summary>Головне вікно</summary>

![Головне вікно AntiYandexVanced](docs/screenshot.png)

</details>

## Готові збірки

Завантажте з [Releases](https://github.com/retvil/AntiYandexVanced/releases):

- **Windows** — `AntiYandexVanced.exe` (портативний, один файл, ~35 МБ)

Запускайте **від імені адміністратора** — HKLM-політики та чистка реєстру потребують підвищених прав.

## Встановлення з джерел

Потрібен Python 3.10+ ([python.org](https://python.org)).

```bash
git clone https://github.com/retvil/AntiYandexVanced.git
cd AntiYandexVanced
pip install psutil ttkbootstrap
python main.py
```

Збірка свого EXE: запустіть `build.bat` (PyInstaller, результат у `dist/`).

## Використання

1. **Завершити процеси** → **Пошук Яндекса** → **Видалити Яндекс** — прибираємо сам браузер.
2. **Сканувати захоплення пошуку** — покаже всі способи, якими Яндекс вріс у систему.
3. **Видалити захоплення** — спершу закрийте всі браузери, потім приберіть усе знайдене.
4. Виберіть пошуковик → **Застосувати політику** — пошук за замовчуванням закріплений на рівні системи.

## FAQ

- **Навіщо адміністратор?** Політики пошуку живуть в HKLM, чистка захоплення торкається системного реєстру — потрібні підвищені права.
- **«Database locked» у результатах?** Під час чистки був запущений Chromium-браузер. Закрийте всі браузери та повторіть видалення.
- **Як зняти політику пошуку?** Кнопка **Зняти політику Яндекса** вичищає значення политик; у Firefox можна також видалити файл `distribution\policies.json`.

## Автор

**Nod33Eset** — форк [TheCawa/AntiYandex](https://github.com/TheCawa/AntiYandex). Issues та PR — вітаються.
