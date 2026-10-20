# AntiYandex Vanced

[![Release](https://img.shields.io/github/v/release/retvil/AntiYandexVanced?sort=date)](https://github.com/retvil/AntiYandexVanced/releases) [![Platform Windows](https://img.shields.io/badge/platform-Windows-blue)](https://github.com/retvil/AntiYandexVanced/releases) [![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

**Полное удаление Яндекс.Браузера и жёсткая защита поиска по умолчанию от захвата — 11 векторов детекта, 10 поисковиков, 10 языков интерфейса.**

[🇬🇧 English](README.md) | **🇷🇺 Русский** | [🇺🇦 Українська](README.uk.md) | [🇰🇿 Қазақша](README.kk.md) | [🇩🇪 Deutsch](README.de.md) | [🇫🇷 Français](README.fr.md) | [🇪🇸 Español](README.es.md) | [🇵🇱 Polski](README.pl.md) | [🇹🇷 Türkçe](README.tr.md) | [🇨🇳 中文](README.zh.md)

## Что это?

Яндекс ставит не просто браузер — он тихо прописывается поиском и браузером по умолчанию через десяток разных механизмов системы: ассоциации в реестре, enterprise-политики, настройки профилей браузеров, даже базы поисковиков внутри профилей Chromium. Удаление одного браузера этого не отменяет.

**AntiYandex Vanced** (форк [TheCawa/AntiYandex](https://github.com/TheCawa/AntiYandex)) находит **все 11 векторов захвата**, убирает их одной кнопкой, а затем **жёстко закрепляет поиск по умолчанию** за выбранным вами поисковиком через enterprise-политики Windows — чтобы ничего не могло тихо вернуть всё обратно.

## Возможности

- **Сканер захвата** — детект 11 векторов: пути установки, записи Uninstall в реестре, ассоциация `UserChoice`, регистрации `StartMenuInternet`, деревья ключей `Software\Yandex`, hijack через политики `DefaultSearchProvider*`, `Preferences` профилей Chromium, ключевые слова в `Web Data` (SQLite), `search.json.mozlz4` Firefox, legacy `SearchScopes`, автозапуск
- **Удаление в один клик** — у каждого вектора свой remover; заблокированные базы честно репортятся, без крашей
- **Жёсткая политика поиска** — закрепляет поиск за одним из 10 поисковиков (Google, Bing, DuckDuckGo, Brave Search, Startpage, Mojeek, Qwant, Ecosia, Yahoo, SearXNG) через HKLM-политики для Chrome, Edge, Brave, Vivaldi, Opera и Яндекс.Браузера + `policies.json` для Firefox/Waterfox
- **Чистка политик** — вычищает значения `DefaultSearchProvider*` Яндекса из реестра
- **10 языков интерфейса** — ru, en, uk, kk, de, fr, es, pl, tr, zh; язык системы определяется автоматически
- **Лёгкий интерфейс** — ttkbootstrap, вертикальная компоновка, зафиксированные статус-бар и футер

## Скриншот

<details>
<summary>Главное окно</summary>

![Главное окно AntiYandexVanced](docs/screenshot.png)

</details>

## Готовые сборки

Скачайте из [Releases](https://github.com/retvil/AntiYandexVanced/releases):

- **Windows** — `AntiYandexVanced.exe` (портативный, один файл, ~35 МБ)

Запускайте **от имени администратора** — HKLM-политики и чистка реестра требуют повышенных прав.

## Установка из исходников

Нужен Python 3.10+ ([python.org](https://python.org)).

```bash
git clone https://github.com/retvil/AntiYandexVanced.git
cd AntiYandexVanced
pip install psutil ttkbootstrap
python main.py
```

Сборка своего EXE: запустите `build.bat` (PyInstaller, результат в `dist/`).

## Использование

1. **Завершить процессы** → **Поиск Яндекса** → **Удалить Яндекс** — убираем сам браузер.
2. **Сканировать захват поиска** — покажет все способы, которыми Яндекс врос в систему.
3. **Удалить захват** — сначала закройте все браузеры, затем уберите всё найденное.
4. Выберите поисковик → **Применить политику** — поиск по умолчанию закреплён на уровне системы.

## FAQ

- **Зачем администратор?** Политики поиска живут в HKLM, чистка захвата трогает системный реестр — нужны повышенные права.
- **«Database locked» в результатах?** Во время чистки был запущен Chromium-браузер. Закройте все браузеры и повторите удаление.
- **Как снять политику поиска?** Кнопка **Снять политику Яндекса** вычищает значения политик; в Firefox можно также удалить файл `distribution\policies.json`.

## Автор

**Nod33Eset** — форк [TheCawa/AntiYandex](https://github.com/TheCawa/AntiYandex). Issues и PR — приветствуются.
