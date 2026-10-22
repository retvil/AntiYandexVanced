# 更新日志

本项目的所有重要变更均记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)，
并遵循 [Semantic Versioning](https://semver.org/spec/v2.0.0.html)。

> 以英文 [CHANGELOG.md](CHANGELOG.md) 为准；本翻译可能略有滞后。

## [2.8.0] - 2026-10-22

### 新增
- **IE 区域映射扫描（zone map）** — 检测 Yandex 域名的 zone-map 条目
  （“受信任的站点”残留）；删除时清除该域名的子树（先导出）
- **RegisteredApplications 扫描** — 检测默认应用元数据中的 Yandex 条目；
  删除时清除该值（先导出）
- **MUICache 扫描** — 检测 Yandex 可执行文件的运行痕迹；删除时清除缓存
  值（先导出）
- **%TEMP% 安装程序痕迹** — scan_traces 现在也会报告遗留在用户临时目录
  中的 Yandex 安装程序
- **按用户的产品目录** — scan_product_dirs 现在也覆盖
  `%LOCALAPPDATA%\Programs\Yandex*`（Yandex Music / Messenger /
  Translate 的旧版桌面安装），浏览器文件夹除外
- **按路径结束进程（Vanced）** — 浏览器范围的 kill 现在也会匹配可执行
  文件位于 YandexBrowser 路径下的进程（crashpad、updater），而不仅是
  browser.exe/yandex.exe 的狭窄名称列表
- **启动 URL 劫持扫描** — 检测 `RestoreOnStartupURLs` 企业策略中的
  Yandex URL（Edge、Chrome、Chromium、Brave、Vivaldi、Opera、Yandex
  浏览器）；删除时清除 Yandex 的值
- **Firefox 主页劫持扫描** — 检测 Firefox/Waterfox `prefs.js` 中指向
  Yandex 的 `browser.startup.homepage`；删除时重写该文件（先备份）

## [2.7.0] - 2026-10-21

### 新增
- **Yandex.DNS 扫描**（Extended）— 检测配置了 Yandex DNS 服务器
  （77.88.8.x basic/safe/family）的网络适配器；删除时将适配器恢复为
  自动 DNS；需确认
- **起始页劫持扫描** — 检测指向 Yandex/ya.ru 的旧版 IE 主页
  （`HKCU\...\Internet Explorer\Main\Start Page`）；删除时恢复默认值
  （两个版本）

## [2.6.0] - 2026-10-21

### 新增
- **Extended 版本**：Store（Appx）应用扫描 — 检测 Yandex Music、Alice、
  Messenger 及其他 Yandex Store 应用，通过 `Remove-AppxPackage` 移除
- **Extended 版本**：`Program Files\Yandex\` 下的非浏览器产品目录扫描
  （Yandex Disk、Punto Switcher、IME 等），删除前备份
- **Extended 版本**：`%LOCALAPPDATA%\Yandex\` 下的非浏览器本地数据扫描
  （Punto Switcher 本地数据、Yandex Disk 更新器、Beta 构建）— 需确认，
  删除前备份
- **Extended 版本**：「Kill Processes」现在会结束所有 Yandex 产品的进程
  （Yandex Disk、Punto Switcher、Store 应用），而不仅是浏览器

## [2.5.0] - 2026-10-21

### 新增
- 同一代码库的两个版本：**AntiYandexVanced**（移除 Yandex 浏览器 +
  Yandex 搜索）和 **AntiYandexExtended**（所有 Yandex 产品）—
  `profiles.py` 中的产品配置选择扫描范围，共享 GUI 位于 `app.py`，
  轻量入口 `main.py` / `main_extended.py`
- `build.bat` 现在构建两个 EXE

## [2.4.0] - 2026-10-21

### 新增
- 第 16–30 个劫持向量：Yandex Disk 外壳集成（图标覆盖 + 右键菜单
  处理器）、禁用的自启动（`StartupApproved`）、`App Paths`、快捷方式
  （桌面 / 开始菜单 / 任务栏）、残留目录（ProgramData、Roaming、
  Yandex Disk 数据及同步文件）、`hosts` 条目、Windows 防火墙规则、
  URI 协议处理器、浏览器扩展（Chromium manifest + Firefox `.xpi`）、
  yandex.ru cookies（Chromium + Firefox）、`OpenWithProgids`/
  `OpenWithList` 关联、Prefetch / CrashDumps / WER 痕迹、Windows
  Defender 排除项、自定义键盘布局（Yandex IME）
- 同意确认：涉及用户数据的检测结果（Yandex Disk 文件、Punto Switcher
  历史、扩展、cookies、Defender 排除项）在删除前需要明确的额外确认
- 针对 `.lnk` 字节检测、hosts 行过滤、防火墙输出解析和同意前缀覆盖的
  单元测试

## [2.3.0] - 2026-10-20

### 新增
- 第 13–15 个劫持向量：Windows 服务（基于注册表的扫描，通过
  `sc stop` + `sc delete` 移除）、Punto Switcher（通过 `punto` 标记
  检测）、文件关联（`FileExts\<ext>\UserChoice` ProgId 扫描 + 移除）
- 扫描后的选择对话框：精确选择要移除哪些检测结果，而非“全有或全无”
- 排除项：取消勾选的检测结果可保存到
  `%APPDATA%\AntiYandexVanced\exclusions.json` — 之后的扫描会自动取消
  选择它们，但在对话框中仍可手动选择；排除项可从对话框重置
- 排除项持久化和 Punto Switcher 标记的单元测试

## [2.2.0] - 2026-10-20

### 新增
- 删除前备份：每个被触及的注册表键 / 配置文件在删除前导出到
  `%APPDATA%\AntiYandexVanced\backup\<timestamp>\`
- 操作日志：`%APPDATA%\AntiYandexVanced\antiyandex.log`
- 第 12 个劫持向量：Windows 任务计划程序条目（Yandex 更新器任务）
- HKCU Chromium 策略扫描/清理（按用户策略，此前仅 HKLM）
- 启动时检查管理员权限，并在状态栏显示警告
- 移除劫持前提示关闭正在运行的浏览器（防止“database locked”）
- 当部分劫持项未能移除时，提供“打开报告文件夹”选项
- 纯逻辑的单元测试（引擎查找、Firefox policies.json、LZ4 解压器）

### 修复
- 来自后台线程的所有 UI 更新现在通过 `root.after` 编组到主线程
  （tkinter 非线程安全）
- 裸 `except:` 子句替换为 `except OSError`
- Web Data 清理现在精确删除检测到的行（按 `rowid`），而非按 URL 子串 —
  检测与删除保持一致
- SQLite 连接在错误路径上关闭（`finally`）
- Firefox `policies.json` 不再包含 `null` 的 `SuggestURLTemplate`
- Firefox 策略不再写入不存在的安装文件夹
- 硬编码的俄语管理员错误字符串替换为全部 10 种 UI 语言的可翻译键
- `shutil.rmtree` 现在报告哪些文件被锁定，而非笼统错误
- 匹配偏移无效的损坏 LZ4 块抛出异常，而非返回垃圾数据

## [2.1.2] - 2026-10-20

### 变更
- 应用标题缩短为「Удаление Яндекс」/「Remove Yandex」（ru/en/uk）
- 页脚固定在右下角：作者、版本和可点击的 GitHub 链接
- 仓库链接设置为 `https://github.com/retvil/AntiYandexVanced`

## [2.1.0] - 2026-10-20

### 新增
- 垂直窗口布局（560×700）：居中的操作堆栈、全宽的分区卡片
- 基于 **ttkbootstrap** 的浅色主题（`flatly` 主题）— 以更轻量的 ttk
  技术栈替换 CustomTkinter
- 包含作者、版本和可点击 GitHub 仓库链接的页脚

### 变更
- UI 库迁移：tkinter → CustomTkinter → ttkbootstrap
- 语言选择器移至右上角

## [2.0.0] - 2026-10-20

[TheCawa/AntiYandex](https://github.com/TheCawa/AntiYandex) 1.3 的 fork。

### 新增
- **搜索劫持扫描器** — 检测 Yandex 用来安装为默认搜索/浏览器的 11 个
  向量：
  - 磁盘上的安装目录
  - 注册表 Uninstall 条目（HKLM、WOW6432Node、HKCU）
  - Windows 默认浏览器关联（http/https 的 `UserChoice` ProgId）
  - `StartMenuInternet` 浏览器客户端注册
  - 独立的 `Software\Yandex` 键树（HKCU/HKLM/WOW6432Node）
  - 通过 `DefaultSearchProvider*` 企业策略的劫持（Yandex 强行生效的
    “硬”手段）
  - Chromium 配置文件的按配置 `Preferences` JSON（Chrome、Edge、Brave、
    Vivaldi、Yandex 浏览器）
  - Chromium `Web Data` SQLite 数据库中的搜索引擎关键词行
  - Firefox/Waterfox `search.json.mozlz4`（内置纯 Python LZ4 块解压器）
  - 旧版 IE/Windows `SearchScopes` 条目
  - 自启动条目（`Run`/`RunOnce`）
- **劫持移除** — 一键移除每个检测到的向量，每个向量有专属 remover：
  递归删除注册表键、重置 `UserChoice`、清理 `Preferences`、在 Web Data
  中执行 `DELETE FROM keywords`、重置 `search.json.mozlz4`（Firefox 会
  重建默认值）、删除自启动值。被锁定的数据库/文件（浏览器正在运行）
  会被如实报告，不会崩溃。
- **硬性默认搜索策略** — 强制使用 10 个搜索引擎之一（Google、Bing、
  DuckDuckGo、Brave Search、Startpage、Mojeek、Qwant、Ecosia、Yahoo、
  SearXNG）：
  - Chromium 家族通过 HKLM `SOFTWARE\Policies\...` 的
    `DefaultSearchProvider*` 值（Chrome、Edge、Brave、Vivaldi、Opera、
    Yandex 浏览器）
  - Firefox/Waterfox 通过 `distribution\policies.json`（`SearchEngines` +
    `LockDefaultSearchEngine` + `PreventSearchEngineInstall`）
- **「移除 Yandex 策略」按钮** — 从注册表中清除 Yandex 的
  `DefaultSearchProvider*` 策略值
- **10 种 UI 语言**（ru、en、uk、kk、de、fr、es、pl、tr、zh），位于独立
  模块 `translations.py`；通过 Windows UI language API
  （`GetUserDefaultUILanguage`）自动检测系统语言，无匹配时回退到英语
- UI 中的语言切换下拉框

### 变更
- 代码拆分为模块：`engines.py`、`yandex_detect.py`、`policies.py`、
  `translations.py`、`main.py`

## [1.3.0] - upstream

[TheCawa/AntiYandex](https://github.com/TheCawa/AntiYandex) 基线：
- 结束 Yandex 浏览器进程（`browser.exe`、`yandex.exe`）
- 搜索安装路径
- 清理注册表 Uninstall 条目
- 删除浏览器文件夹
- RU/EN 界面切换

[Unreleased]: https://github.com/retvil/AntiYandexVanced/compare/v2.1.2...HEAD
[2.1.2]: https://github.com/retvil/AntiYandexVanced/compare/v2.1.0...v2.1.2
[2.1.0]: https://github.com/retvil/AntiYandexVanced/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/retvil/AntiYandexVanced/compare/v1.3.0...v2.0.0
