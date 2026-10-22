# Registro de cambios

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
y este proyecto se adhiere al [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> La fuente de referencia es el [CHANGELOG.md](CHANGELOG.md) en inglés; esta traducción puede ir ligeramente por detrás.

## [2.8.0] - 2026-10-22

### Añadido
- **Escaneo de zone map de IE** — detecta entradas de zone map para dominios
  de Yandex (residuos de «sitios de confianza»); la eliminación borra el
  subárbol del dominio (exportado primero)
- **Escaneo de RegisteredApplications** — detecta entradas de Yandex en los
  metadatos de aplicaciones predeterminadas; la eliminación borra el valor
  (exportado primero)
- **Escaneo de MUICache** — detecta rastros de ejecución de ejecutables de
  Yandex; la eliminación borra el valor de la caché (exportado primero)
- **Rastros de instaladores en %TEMP%** — scan_traces ahora también informa
  de los instaladores de Yandex dejados en la carpeta temporal del usuario
- **Directorios de productos per-user** — scan_product_dirs ahora también
  cubre `%LOCALAPPDATA%\Programs\Yandex*` (instalaciones legacy de Yandex
  Music / Messenger / Translate), la carpeta del navegador queda excluida
- **Kill de procesos por ruta (Vanced)** — el kill del navegador ahora
  también detecta procesos cuyo ejecutable se encuentra bajo una ruta de
  YandexBrowser (crashpad, updater), no solo la lista estrecha de nombres
  browser.exe/yandex.exe
- **Escaneo de secuestro de URL de inicio** — detecta URL de Yandex en las
  políticas de empresa `RestoreOnStartupURLs` (Edge, Chrome, Chromium,
  Brave, Vivaldi, Opera, Yandex Browser); la eliminación purga los valores
  de Yandex
- **Escaneo de secuestro de la página de inicio de Firefox** — detecta
  `browser.startup.homepage` apuntando a Yandex en el `prefs.js` de
  Firefox/Waterfox; la eliminación reescribe el archivo (copia de seguridad
  primero)

## [2.7.0] - 2026-10-21

### Añadido
- **Escaneo de Yandex.DNS** (Extended) — detecta adaptadores de red
  configurados con servidores DNS de Yandex (77.88.8.x basic/safe/family);
  la eliminación restablece el adaptador a DNS automático; con
  confirmación
- **Escaneo de secuestro de la página de inicio** — detecta la página de
  inicio legacy de IE (`HKCU\...\Internet Explorer\Main\Start Page`)
  apuntando a Yandex/ya.ru; la eliminación restaura el valor
  predeterminado (ambas ediciones)

## [2.6.0] - 2026-10-21

### Añadido
- **Edición Extended**: escaneo de aplicaciones de la Store (Appx) —
  detecta Yandex Music, Alice, Messenger y otras aplicaciones de la Store
  de Yandex, las elimina mediante `Remove-AppxPackage`
- **Edición Extended**: escaneo de directorios de productos no-navegador
  bajo `Program Files\Yandex\` (Yandex Disk, Punto Switcher, IME, ...) con
  copia de seguridad antes de eliminar
- **Edición Extended**: escaneo de datos locales no-navegador bajo
  `%LOCALAPPDATA%\Yandex\` (datos locales de Punto Switcher, updater de
  Yandex Disk, builds Beta) — con confirmación, copia de seguridad antes
  de eliminar
- **Edición Extended**: «Kill Processes» ahora termina los procesos de
  todos los productos de Yandex (Yandex Disk, Punto Switcher, aplicaciones
  de la Store), no solo el navegador

## [2.5.0] - 2026-10-21

### Añadido
- Dos ediciones desde una misma base de código: **AntiYandexVanced**
  (eliminación de Yandex Browser + Búsqueda de Yandex) y
  **AntiYandexExtended** (todos los productos de Yandex) — los perfiles de
  producto en `profiles.py` eligen el alcance del escaneo, GUI compartida
  en `app.py`, puntos de entrada ligeros `main.py` / `main_extended.py`
- `build.bat` ahora compila ambos EXE

## [2.4.0] - 2026-10-21

### Añadido
- Vectores de secuestro 16–30: integración de shell de Yandex Disk
  (overlays de iconos + manejadores de menú contextual), autostart
  deshabilitado (`StartupApproved`), `App Paths`, accesos directos
  (Escritorio / Menú Inicio / barra de tareas), directorios residuales
  (ProgramData, Roaming, datos de Yandex Disk y archivos sincronizados),
  entradas de `hosts`, reglas del firewall de Windows, manejadores de
  protocolos URI, extensiones de navegador (manifiestos Chromium + `.xpi`
  de Firefox), cookies de yandex.ru (Chromium + Firefox), asociaciones
  `OpenWithProgids`/`OpenWithList`, rastros Prefetch / CrashDumps / WER,
  exclusiones de Windows Defender, distribuciones de teclado
  personalizadas (Yandex IME)
- Confirmación de consentimiento: los hallazgos que tocan datos del
  usuario (archivos de Yandex Disk, historial de Punto Switcher,
  extensiones, cookies, exclusiones de Defender) requieren una
  confirmación adicional explícita antes de la eliminación
- Pruebas unitarias para detección de bytes `.lnk`, filtrado de líneas de
  hosts, análisis de la salida del firewall y cobertura de prefijos de
  consentimiento

## [2.3.0] - 2026-10-20

### Añadido
- Vectores de secuestro 13–15: servicios de Windows (escaneo por registro,
  eliminación mediante `sc stop` + `sc delete`), Punto Switcher (detección
  por el marcador `punto`), asociaciones de archivos (escaneo + eliminación
  del ProgId en `FileExts\<ext>\UserChoice`)
- Diálogo de selección tras el escaneo: elegir exactamente qué hallazgos
  eliminar en lugar de «todo o nada»
- Exclusiones: los hallazgos desmarcados se pueden guardar en
  `%APPDATA%\AntiYandexVanced\exclusions.json` — los escaneos futuros los
  deseleccionan automáticamente, pero siguen siendo seleccionables en el
  diálogo; las exclusiones se pueden restablecer desde el diálogo
- Pruebas unitarias para la persistencia de exclusiones y el marcador de
  Punto Switcher

## [2.2.0] - 2026-10-20

### Añadido
- Copia de seguridad antes de eliminar: cada clave de registro / archivo de
  perfil tocado se exporta a
  `%APPDATA%\AntiYandexVanced\backup\<timestamp>\` antes de la eliminación
- Registro de operaciones: `%APPDATA%\AntiYandexVanced\antiyandex.log`
- Vector de secuestro 12: entradas del Programador de tareas de Windows
  (tareas del updater de Yandex)
- Escaneo/limpieza de políticas Chromium en HKCU (políticas por usuario,
  antes solo HKLM)
- Comprobación de derechos de administrador al inicio con aviso en la
  barra de estado
- Aviso de cerrar los navegadores en ejecución antes de eliminar
  secuestros (evita «database locked»)
- Oferta de «abrir la carpeta del informe» cuando algunos elementos de
  secuestro no se pudieron eliminar
- Pruebas unitarias de lógica pura (búsqueda de motor, Firefox
  policies.json, descompresor LZ4)

### Corregido
- Todas las actualizaciones de la UI desde hilos en segundo plano ahora se
  marshalan al hilo principal mediante `root.after` (tkinter no es
  thread-safe)
- Cláusulas `except:` desnudas reemplazadas por `except OSError`
- La limpieza de Web Data ahora elimina exactamente las filas detectadas
  (por `rowid`), no por subcadena de URL — detección y eliminación son
  coherentes
- Las conexiones SQLite se cierran en las rutas de error (`finally`)
- Firefox `policies.json` ya no contiene un `SuggestURLTemplate` `null`
- Las políticas de Firefox ya no se escriben en carpetas de instalación
  inexistentes
- La cadena de error de administrador codificada en ruso reemplazada por
  una clave traducible en los 10 idiomas de la UI
- `shutil.rmtree` ahora informa qué archivos están bloqueados en lugar de
  un error genérico
- Los bloques LZ4 corruptos con offsets de coincidencia inválidos lanzan
  una excepción en lugar de devolver basura

## [2.1.2] - 2026-10-20

### Cambiado
- Título de la aplicación acortado a «Удаление Яндекс» / «Remove Yandex»
  (ru/en/uk)
- Pie de página fijado en la esquina inferior derecha: autor, versión y
  enlace clicable a GitHub
- Enlace del repositorio establecido a
  `https://github.com/retvil/AntiYandexVanced`

## [2.1.0] - 2026-10-20

### Añadido
- Disposición vertical de la ventana (560×700): pila de acciones centrada,
  tarjetas de secciones a todo el ancho
- Tema claro de UI sobre **ttkbootstrap** (tema `flatly`) — CustomTkinter
  reemplazado por una pila ttk más ligera
- Pie de página con autor, versión y enlace clicable al repositorio de
  GitHub

### Cambiado
- Migración de la biblioteca de UI: tkinter → CustomTkinter → ttkbootstrap
- Selector de idioma movido a la esquina superior derecha

## [2.0.0] - 2026-10-20

Fork de [TheCawa/AntiYandex](https://github.com/TheCawa/AntiYandex) 1.3.

### Añadido
- **Escáner de secuestros de búsqueda** — detecta los 11 vectores que
  Yandex usa para instalarse como búsqueda/navegador predeterminado:
  - directorios de instalación en el disco
  - entradas Uninstall del registro (HKLM, WOW6432Node, HKCU)
  - asociación de navegador predeterminado de Windows (ProgId `UserChoice`
    para http/https)
  - registros de clientes de navegador `StartMenuInternet`
  - árboles de claves `Software\Yandex` independientes
    (HKCU/HKLM/WOW6432Node)
  - secuestro mediante políticas de empresa `DefaultSearchProvider*` (la
    forma «dura» en que Yandex se impone)
  - JSON `Preferences` por perfil de Chromium (Chrome, Edge, Brave,
    Vivaldi, Yandex Browser)
  - filas de palabras clave de buscadores en las bases SQLite `Web Data`
    de Chromium
  - Firefox/Waterfox `search.json.mozlz4` (con un descompresor de bloques
    LZ4 pure-Python integrado)
  - entradas legacy `SearchScopes` de IE/Windows
  - entradas de autostart (`Run`/`RunOnce`)
- **Eliminación de secuestros** — eliminación con un clic de cada vector
  detectado, con un remover por vector: eliminación recursiva de claves
  del registro, restablecimiento de `UserChoice`, limpieza de
  `Preferences`, `DELETE FROM keywords` en Web Data, restablecimiento de
  `search.json.mozlz4` (Firefox reconstruye los valores
  predeterminados), eliminación de valores de autostart. Las bases/archivos
  bloqueados (navegador en ejecución) se informan, sin crashes.
- **Política estricta de búsqueda predeterminada** — impone uno de los 10
  buscadores (Google, Bing, DuckDuckGo, Brave Search, Startpage, Mojeek,
  Qwant, Ecosia, Yahoo, SearXNG):
  - familia Chromium mediante valores HKLM `SOFTWARE\Policies\...`
    `DefaultSearchProvider*` (Chrome, Edge, Brave, Vivaldi, Opera,
    Yandex Browser)
  - Firefox/Waterfox mediante `distribution\policies.json` (`SearchEngines`
    + `LockDefaultSearchEngine` + `PreventSearchEngineInstall`)
- Botón **«Eliminar políticas de Yandex»** — purga los valores de política
  `DefaultSearchProvider*` de Yandex del registro
- **10 idiomas de UI** (ru, en, uk, kk, de, fr, es, pl, tr, zh) en un módulo
  dedicado `translations.py`; idioma del sistema detectado automáticamente
  mediante la API de Windows UI language (`GetUserDefaultUILanguage`),
  respaldo en inglés
- Desplegable de cambio de idioma en la UI

### Cambiado
- Código dividido en módulos: `engines.py`, `yandex_detect.py`,
  `policies.py`, `translations.py`, `main.py`

## [1.3.0] - upstream

Base de [TheCawa/AntiYandex](https://github.com/TheCawa/AntiYandex):
- Terminación de los procesos de Yandex Browser (`browser.exe`,
  `yandex.exe`)
- Búsqueda de rutas de instalación
- Limpieza de entradas Uninstall del registro
- Eliminación de la carpeta del navegador
- Conmutador de interfaz RU/EN

[Unreleased]: https://github.com/retvil/AntiYandexVanced/compare/v2.1.2...HEAD
[2.1.2]: https://github.com/retvil/AntiYandexVanced/compare/v2.1.0...v2.1.2
[2.1.0]: https://github.com/retvil/AntiYandexVanced/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/retvil/AntiYandexVanced/compare/v1.3.0...v2.0.0
