# AntiYandex Vanced

[![Release](https://img.shields.io/github/v/release/retvil/AntiYandexVanced?sort=date)](https://github.com/retvil/AntiYandexVanced/releases) [![Platform Windows](https://img.shields.io/badge/platform-Windows-blue)](https://github.com/retvil/AntiYandexVanced/releases) [![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

**Elimina por completo Yandex Browser y bloquea tu buscador predeterminado contra el secuestro — 11 vectores de detección, 10 buscadores, 10 idiomas de interfaz.**

[🇬🇧 English](README.md) | [🇷🇺 Русский](README.ru.md) | [🇺🇦 Українська](README.uk.md) | [🇰🇿 Қазақша](README.kk.md) | [🇩🇪 Deutsch](README.de.md) | [🇫🇷 Français](README.fr.md) | **🇪🇸 Español** | [🇵🇱 Polski](README.pl.md) | [🇹🇷 Türkçe](README.tr.md) | [🇨🇳 中文](README.zh.md)

## ¿Qué es esto?

Yandex no instala solo un navegador — se registra silenciosamente como buscador y navegador predeterminado a través de una docena de mecanismos del sistema: asociaciones en el registro, políticas de empresa, ajustes de perfiles de navegadores, incluso bases de datos de buscadores dentro de los perfiles Chromium. Eliminar el navegador por sí solo no deshace todo eso.

**AntiYandex Vanced** (un fork de [TheCawa/AntiYandex](https://github.com/TheCawa/AntiYandex)) encuentra **los 11 vectores de secuestro**, los elimina con un clic y luego **bloquea tu buscador predeterminado** al motor que elijas mediante políticas de empresa de Windows — para que nada pueda recuperarlo silenciosamente.

## Características

- **Escáner de secuestros** — detecta 11 vectores: rutas de instalación, entradas Uninstall del registro, asociación `UserChoice`, registros `StartMenuInternet`, árboles de claves `Software\Yandex`, secuestro vía políticas `DefaultSearchProvider*`, `Preferences` de perfiles Chromium, palabras clave en `Web Data` (SQLite), `search.json.mozlz4` de Firefox, `SearchScopes` legacy, entradas de autostart
- **Eliminación con un clic** — cada vector tiene su propio remover; las bases bloqueadas se reportan honestamente, sin crashes
- **Política estricta de búsqueda** — bloquea el buscador predeterminado a uno de 10 motores (Google, Bing, DuckDuckGo, Brave Search, Startpage, Mojeek, Qwant, Ecosia, Yahoo, SearXNG) vía políticas HKLM para Chrome, Edge, Brave, Vivaldi, Opera y Yandex Browser + `policies.json` para Firefox/Waterfox
- **Limpieza de políticas** — purga los valores `DefaultSearchProvider*` de Yandex del registro
- **10 idiomas de interfaz** — ru, en, uk, kk, de, fr, es, pl, tr, zh; idioma del sistema detectado automáticamente
- **Interfaz ligera** — ttkbootstrap, disposición vertical, barra de estado y pie de página fijados

## Captura de pantalla

<details>
<summary>Ventana principal</summary>

![Ventana principal de AntiYandexVanced](docs/screenshot.png)

</details>

## Builds listos

Descarga desde [Releases](https://github.com/retvil/AntiYandexVanced/releases):

- **Windows** — `AntiYandexVanced.exe` (portable, archivo único, ~35 MB)

Ejecútalo **como administrador** — las políticas HKLM y la limpieza del registro requieren permisos elevados.

## Instalación desde el código fuente

Se requiere Python 3.10+ ([python.org](https://python.org)).

```bash
git clone https://github.com/retvil/AntiYandexVanced.git
cd AntiYandexVanced
pip install psutil ttkbootstrap
python main.py
```

Compilar tu propio EXE: ejecuta `build.bat` (PyInstaller, resultado en `dist/`).

## Uso

1. **Terminar procesos** → **Buscar Yandex** → **Eliminar Yandex** — eliminamos el navegador en sí.
2. **Escanear secuestros de búsqueda** — muestra todas las formas en que Yandex se enraizó en el sistema.
3. **Eliminar secuestros** — cierra primero todos los navegadores, luego elimina todo lo encontrado.
4. Elige un motor → **Aplicar política** — el buscador predeterminado queda bloqueado a nivel del sistema.

## FAQ

- **¿Por qué administrador?** Las políticas de búsqueda viven en HKLM, la limpieza toca el registro del sistema — se necesitan permisos elevados.
- **¿«Database locked» en los resultados?** Un navegador Chromium estaba en ejecución durante la limpieza. Cierra todos los navegadores y repite la eliminación.
- **¿Cómo quito la política de búsqueda?** El botón **Quitar políticas de Yandex** purga los valores; en Firefox también puedes eliminar el archivo `distribution\policies.json`.

## Autor y apoyo

**Nod33Eset** — fork de [TheCawa/AntiYandex](https://github.com/TheCawa/AntiYandex). Issues y PR bienvenidos.

Si la herramienta te libró de Yandex, puedes apoyar el desarrollo:

**Cripto:**

- BTC: `bc1qunld3rsp37qf5gg69aune50y0qqkd0eugg7j97`
- TON: `UQDmvr4SKOxSION3Yky6aOgzAnCDXySPuAbG4EKJa5JUT7tC`
- USDT (TRC20): `TBPJSSLu1mUcX54g9UyxUohYGf2fuRvbwd`
- USDT (ERC20): `0x25CAED3776Ef5b18E03392bC5b254Bbd78E8180C`
- USDT (SOL): `3qgN5z291CEcj2FUi2Zza5DioxKgNw72kC7P52pCcTrG`

## Licencia

MIT — ver [LICENSE](LICENSE).
