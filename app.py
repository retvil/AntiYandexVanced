"""Shared GUI for the AntiYandex editions.

Entry points (main.py, main_extended.py) call run() with a product profile
from profiles.py; the profile selects the scan scope and the product name.
"""

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
import ctypes
import os
import shutil
import psutil
import threading
import webbrowser
import winreg

import backup
import engines
import exclusions
import policies
import products_detect
import profiles
import translations
import yandex_detect

APP_VERSION = "2.8.0"
APP_AUTHOR = "Nod33Eset"
GITHUB_URL = "https://github.com/retvil/AntiYandexVanced"

YANDEX_PATHS = yandex_detect.YANDEX_PATHS

TEXT_MUTED = "#6b7280"
STATUS_COLORS = {
    "ok": "#15803d",
    "warn": "#b45309",
    "info": "#0369a1",
    "bad": "#b91c1c",
}

# Browser processes that lock profile databases during hijack removal
BROWSER_PROCESSES = {
    "chrome.exe", "msedge.exe", "brave.exe", "vivaldi.exe", "opera.exe",
    "firefox.exe", "waterfox.exe", "browser.exe",
}

# Set by run(); module-level functions below read these.
PROFILE: str = profiles.EXTENDED
language: str = ""
root: ttk.Window
status_label: ttk.Label
findings_box: tk.Text
engine_menu: ttk.Combobox

last_findings: list[str] = []


def t(key):
    return translations.t(language, key)

def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except OSError:
        return False

def update_status(status, color=STATUS_COLORS["info"]):
    status_label.configure(text=status, foreground=color)

def run_in_ui(fn):
    """Run a UI-touching callable on the main thread (tkinter is not thread-safe)."""
    root.after(0, fn)

def check_registry_for_yandex():
    found = yandex_detect.scan_uninstall_entries()
    if found:
        update_status(t("reg_found"), STATUS_COLORS["ok"])
        messagebox.showinfo(t("title"), t("reg_found"))
    else:
        update_status(t("reg_not_found"), STATUS_COLORS["bad"])
        messagebox.showwarning(t("title"), t("reg_not_found"))

def kill_yandex_processes():
    killed = False
    extended = PROFILE == profiles.EXTENDED
    for proc in psutil.process_iter(['name', 'exe']):
        try:
            name = proc.info['name']
            if extended:
                hit = products_detect.is_product_process(name)
            else:
                hit = bool(name) and name.lower() in ("browser.exe", "yandex.exe")
                if not hit:
                    exe = (proc.info.get('exe') or "").lower()
                    hit = "yandexbrowser" in exe
            if hit:
                proc.kill()
                killed = True
        except (psutil.NoSuchProcess, psutil.AccessDenied): continue

    if killed:
        update_status(t("status_killed"), STATUS_COLORS["ok"])
        messagebox.showinfo(t("title"), t("success_kill"))
    else:
        update_status(t("status_no_proc"), STATUS_COLORS["warn"])
        messagebox.showwarning(t("title"), t("not_found_warning"))

def check_yandex_browser():
    def task():
        run_in_ui(lambda: update_status(t("status_searching"), STATUS_COLORS["info"]))
        hits = [p for p in YANDEX_PATHS if os.path.exists(p)]
        if hits:
            run_in_ui(lambda: update_status(t("status_found").format(hits[0]), STATUS_COLORS["ok"]))
        else:
            run_in_ui(lambda: update_status(t("status_not_found"), STATUS_COLORS["bad"]))
    threading.Thread(target=task, daemon=True).start()

def uninstall_yandex_browser():
    hits = [p for p in YANDEX_PATHS if os.path.exists(p)]
    if not hits:
        messagebox.showwarning(t("title"), t("delete_first"))
        return
    target = hits[0]

    def task():
        try:
            shutil.rmtree(target, ignore_errors=False)
        except shutil.Error as exc:
            locked = "; ".join(str(f) for f in getattr(exc, "args", ())[:3])
            def fail_locked():
                update_status(t("delete_fail"), STATUS_COLORS["bad"])
                messagebox.showerror(t("title"), f"{t('delete_fail')}\n{locked}")
            run_in_ui(fail_locked)
            return
        except PermissionError:
            def fail_admin():
                update_status(t("delete_fail"), STATUS_COLORS["bad"])
                messagebox.showerror(t("title"), t("delete_fail_admin"))
            run_in_ui(fail_admin)
            return
        except OSError as exc:
            def fail_other():
                update_status(t("delete_fail"), STATUS_COLORS["bad"])
                messagebox.showerror(t("title"), f"{t('delete_fail')}\nError: {exc}")
            run_in_ui(fail_other)
            return
        if not os.path.exists(target):
            yandex_detect.remove_uninstall_entries()
            backup.log_action(f"uninstall_yandex_browser: removed {target}")
            def done():
                update_status(t("delete_success"), STATUS_COLORS["ok"])
                messagebox.showinfo(t("title"), t("delete_success"))
            run_in_ui(done)
        else:
            def fail_locked2():
                update_status(t("delete_fail"), STATUS_COLORS["bad"])
                messagebox.showerror(t("title"), f"{t('delete_fail')}\nFiles locked")
            run_in_ui(fail_locked2)

    threading.Thread(target=task, daemon=True).start()

def _render_findings(lines):
    findings_box.configure(state=tk.NORMAL)
    findings_box.delete("1.0", tk.END)
    for line in lines:
        findings_box.insert(tk.END, line + "\n")
    findings_box.configure(state=tk.DISABLED)

def scan_hijacks():
    """Scan the profile's Yandex hijack vectors, show findings, offer selection."""
    def task():
        run_in_ui(lambda: update_status(t("status_searching"), STATUS_COLORS["info"]))
        findings = yandex_detect.scan_all(PROFILE)
        def done():
            global last_findings
            last_findings = findings
            if findings:
                _render_findings(
                    [t("hijack_found").format(len(findings))] + [f"•  {f}" for f in findings]
                )
                update_status(t("hijack_found").format(len(findings)), STATUS_COLORS["warn"])
                _open_selection_dialog(findings)
            else:
                _render_findings([t("hijack_clean")])
                update_status(t("hijack_clean"), STATUS_COLORS["ok"])
        run_in_ui(done)
    threading.Thread(target=task, daemon=True).start()

def _running_browsers() -> list[str]:
    names = set()
    for proc in psutil.process_iter(['name']):
        try:
            name = (proc.info['name'] or "").lower()
            if name in BROWSER_PROCESSES:
                names.add(name)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return sorted(names)

def _kill_browsers() -> None:
    for proc in psutil.process_iter(['name']):
        try:
            if (proc.info['name'] or "").lower() in BROWSER_PROCESSES:
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

def remove_hijacks():
    """Open the selection dialog for the last scan results."""
    if not last_findings:
        scan_hijacks()
        return
    _open_selection_dialog(last_findings)

def _remove_selected_task(selected: list[str]) -> None:
    """Background removal of the user-selected findings + result reporting."""
    removed, failed = yandex_detect.remove_selected(selected)
    def done():
        if removed:
            update_status(t("hijack_removed").format(len(removed)), STATUS_COLORS["ok"])
        else:
            update_status(t("hijack_none"), STATUS_COLORS["info"])
        if failed:
            message = t("hijack_remove_fail").format("\n".join(failed))
            if backup._session_dir is not None and any(backup._session_dir.rglob("*")):
                message += "\n\n" + t("backup_done").format(path=backup.BASE_DIR)
            messagebox.showwarning(t("title"), message)
            if messagebox.askyesno(t("title"), t("open_log_ask")):
                os.startfile(backup.BASE_DIR)
        if removed:
            messagebox.showinfo(t("title"), t("hijack_removed").format("\n".join(removed)))
        elif not failed:
            messagebox.showinfo(t("title"), t("hijack_none"))
    run_in_ui(done)
    run_in_ui(scan_hijacks)

def _open_selection_dialog(findings: list[str]) -> None:
    """Modal dialog: pick findings to remove, manage exclusions."""
    excluded = exclusions.load()
    dialog = ttk.Toplevel(title=t("select_title"), size=(620, 520), minsize=(520, 420))
    dialog.transient(root)
    dialog.grab_set()

    ttk.Label(
        dialog, text=t("select_hint"), wraplength=580, justify="left",
        font=("Segoe UI", 10), foreground=TEXT_MUTED, padding=(12, 10, 12, 6)
    ).pack(fill="x")

    # Scrollable checkbox list
    outer = ttk.Frame(dialog)
    outer.pack(fill="both", expand=True, padx=12, pady=(0, 8))
    canvas = tk.Canvas(outer, highlightthickness=0)
    scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    list_frame = ttk.Frame(canvas, padding=(4, 4, 16, 4))
    list_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=list_frame, anchor="nw", width=560)
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(event):
        canvas.yview_scroll(-1 * (event.delta // 120), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    vars_by_finding: dict[str, tk.BooleanVar] = {}
    for finding in findings:
        var = tk.BooleanVar(value=not exclusions.is_excluded(finding, excluded))
        vars_by_finding[finding] = var
        tk.Checkbutton(
            list_frame, text=finding, variable=var, anchor="w", justify="left",
            wraplength=520, font=("Segoe UI", 9), bg="#ffffff"
        ).pack(fill="x", anchor="w", pady=1)

    buttons = ttk.Frame(dialog, padding=(12, 4, 12, 12))
    buttons.pack(fill="x", side="bottom")

    def close():
        canvas.unbind_all("<MouseWheel>")
        dialog.destroy()

    def on_remove():
        selected = [f for f, var in vars_by_finding.items() if var.get()]
        if not selected:
            messagebox.showinfo(t("select_title"), t("select_none"), parent=dialog)
            return
        if any(f.startswith(yandex_detect.CONSENT_PREFIXES) for f in selected):
            if not messagebox.askyesno(t("title"), t("consent_confirm"), parent=dialog):
                return
        running = _running_browsers()
        if running and not messagebox.askyesno(t("title"), t("close_browsers_confirm")):
            return
        if running:
            _kill_browsers()
        close()
        threading.Thread(target=_remove_selected_task, args=(selected,), daemon=True).start()

    def on_exclude():
        unchecked = [f for f, var in vars_by_finding.items() if not var.get()]
        for finding in unchecked:
            exclusions.add(finding)
        update_status(t("exclusions_saved").format(len(unchecked)), STATUS_COLORS["info"])

    def on_reset():
        exclusions.clear()
        for var in vars_by_finding.values():
            var.set(True)
        update_status(t("exclusions_cleared"), STATUS_COLORS["info"])

    ttk.Button(buttons, bootstyle="danger", text=t("select_remove_btn"), command=on_remove).pack(side="left", fill="x", expand=True, padx=(0, 6))
    ttk.Button(buttons, bootstyle="secondary", text=t("select_exclude_btn"), command=on_exclude).pack(side="left", padx=(0, 6))
    ttk.Button(buttons, bootstyle="secondary", text=t("select_reset_exclusions_btn"), command=on_reset).pack(side="left", padx=(0, 6))
    ttk.Button(buttons, bootstyle="secondary", text=t("select_cancel_btn"), command=close).pack(side="left")

def apply_search_policy():
    """Hard-enforce the selected engine in all Chromium browsers + Firefox."""
    engine_name = engine_menu.get()
    if not engine_name:
        return
    engine = engines.get_engine(engine_name)

    def task():
        applied, failed = policies.apply_chromium(engine, list(policies.CHROMIUM_POLICY_PATHS))
        ff_applied, ff_failed = policies.apply_firefox(engine)
        applied += ff_applied
        failed += ff_failed
        backup.log_action(
            f"apply_search_policy: engine={engine.name} applied={applied} failed={failed}"
        )
        def done():
            update_status(t("policy_applied").format(", ".join(applied) or "-"), STATUS_COLORS["ok"])
            if failed:
                messagebox.showwarning(t("title"), t("policy_failed").format(", ".join(failed)))
            else:
                messagebox.showinfo(t("title"), t("policy_applied").format(", ".join(applied)))
        run_in_ui(done)
    threading.Thread(target=task, daemon=True).start()

def remove_yandex_policies():
    """Strip Yandex DefaultSearchProvider policy values from the registry."""
    def task():
        cleaned = policies.remove_yandex_search_policies()
        backup.log_action(f"remove_yandex_policies: cleaned={cleaned}")
        def done():
            if cleaned:
                update_status(t("policy_cleaned").format(", ".join(cleaned)), STATUS_COLORS["ok"])
                messagebox.showinfo(t("title"), t("policy_cleaned").format("\n".join(cleaned)))
            else:
                update_status(t("policy_nothing"), STATUS_COLORS["info"])
                messagebox.showinfo(t("title"), t("policy_nothing"))
        run_in_ui(done)
    threading.Thread(target=task, daemon=True).start()

def run(profile_name: str) -> None:
    """Build the GUI for one product profile and start the main loop."""
    global PROFILE, language
    global root, status_label, findings_box, engine_menu, main_label
    global btn_check, btn_registry, btn_kill, btn_delete
    global btn_hijack, btn_hijack_remove, policy_card, hijack_card
    global btn_policy, btn_unyandex_policy, lang_label

    PROFILE = profiles.validate(profile_name)
    language = translations.detect_system_language()

    # --- GUI ---
    root = ttk.Window(themename="flatly", size=(400, 700), minsize=(360, 680))
    root.title(t("title"))

    # App icon (logo.ico next to the script)
    _icon = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.ico")
    if os.path.exists(_icon):
        root.iconbitmap(_icon)

    style = ttk.Style()
    style.configure("Card.TFrame", background="#ffffff", relief="flat")
    style.configure("Card.TLabel", background="#ffffff")
    style.configure("CardTitle.TLabel", background="#ffffff", font=("Segoe UI", 11, "bold"))
    style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"), foreground="#334155")

    # Footer: pinned bottom-right, packed FIRST so it keeps its space when the
    # window is resized smaller (pack gives space to earlier widgets first)
    footer = ttk.Frame(root, padding=(16, 4, 16, 10))
    footer.pack(side="bottom", fill="x")

    github_link = ttk.Label(
        footer, font=("Segoe UI", 9, "underline"), foreground="#0369a1",
        text="GitHub", cursor="hand2"
    )
    github_link.pack(side="right")
    github_link.bind("<Button-1>", lambda e: webbrowser.open(GITHUB_URL))

    footer_label = ttk.Label(
        footer, font=("Segoe UI", 9), foreground=TEXT_MUTED,
        text=f"{profiles.PRODUCT_NAMES[PROFILE]} {APP_VERSION} by {APP_AUTHOR} |"
    )
    footer_label.pack(side="right", padx=(0, 4))

    # Status bar: packed second (above footer) so it also survives window resize
    status_label = ttk.Label(
        root, font=("Segoe UI", 10), justify="center",
        anchor="center", padding=(20, 8, 20, 6)
    )
    status_label.pack(side="bottom", fill="x")

    def _retune_wraplength(event=None):
        """Keep the status text wrapping inside the window at any width."""
        width = status_label.winfo_width()
        if width > 1:
            new_wrap = max(120, width - 40)
            # only reconfigure on actual change — otherwise this Configure
            # handler feeds its own event loop and the window never settles
            if status_label.cget("wraplength") != new_wrap:
                status_label.configure(wraplength=new_wrap)

    root.bind("<Configure>", _retune_wraplength)

    # Policy section card: pinned above the status bar, survives window resize
    policy_card = ttk.Labelframe(root, text=t("policy_section"), padding=(16, 8, 16, 12))
    policy_card.pack(side="bottom", fill="x", padx=20, pady=(10, 4))

    policy_row = ttk.Frame(policy_card)
    policy_row.pack(fill="x", pady=(4, 8))

    engine_menu = ttk.Combobox(
        policy_row, values=list(engines.ENGINE_NAMES),
        state="readonly", font=("Segoe UI", 11)
    )
    engine_menu.set(engines.ENGINE_NAMES[0])
    engine_menu.pack(fill="x")

    btn_policy = ttk.Button(policy_card, bootstyle="success", command=apply_search_policy)
    btn_policy.pack(fill="x", pady=(0, 6))

    btn_unyandex_policy = ttk.Button(policy_card, bootstyle="secondary", command=remove_yandex_policies)
    btn_unyandex_policy.pack(fill="x", pady=(0, 2))

    def on_language_change(choice):
        global language
        for code, display in translations.LANG_DISPLAY_NAMES.items():
            if display == choice:
                language = code
                break
        update_ui()

    # Language selector: top-right corner
    lang_bar = ttk.Frame(root, padding=(20, 10, 20, 0))
    lang_bar.pack(fill="x")

    lang_menu = ttk.Combobox(
        lang_bar, values=list(translations.LANG_DISPLAY_NAMES.values()),
        state="readonly", width=13, font=("Segoe UI", 11)
    )
    lang_menu.set(translations.LANG_DISPLAY_NAMES[language])
    lang_menu.bind("<<ComboboxSelected>>", on_language_change)
    lang_menu.pack(side="right")

    lang_label = ttk.Label(lang_bar, font=("Segoe UI", 11), foreground=TEXT_MUTED)
    lang_label.pack(side="right", padx=(0, 8))

    # Title centered
    main_label = ttk.Label(root, font=("Segoe UI", 18, "bold"), anchor="center")
    main_label.pack(fill="x", padx=20, pady=(6, 10))

    # Primary actions: full-width stack, same margins as the cards below
    actions = ttk.Frame(root)
    actions.pack(fill="x", padx=20, pady=(2, 2))

    btn_check = ttk.Button(actions, bootstyle="info", command=check_yandex_browser)
    btn_check.pack(fill="x", pady=2)

    btn_registry = ttk.Button(actions, bootstyle="secondary", command=check_registry_for_yandex)
    btn_registry.pack(fill="x", pady=2)

    btn_kill = ttk.Button(actions, bootstyle="info", command=kill_yandex_processes)
    btn_kill.pack(fill="x", pady=2)

    btn_delete = ttk.Button(actions, bootstyle="danger", command=uninstall_yandex_browser)
    btn_delete.pack(fill="x", pady=(2, 6))

    # Hijack section card: pinned above the policy card, survives window resize
    hijack_card = ttk.Labelframe(root, text=t("hijack_section"), padding=(16, 8, 16, 12))
    hijack_card.pack(side="bottom", fill="x", padx=20, pady=(6, 4))

    btn_hijack = ttk.Button(hijack_card, bootstyle="info", command=scan_hijacks)
    btn_hijack.pack(fill="x", pady=(2, 6))

    findings_box = tk.Text(
        hijack_card, height=3, wrap="word", font=("Consolas", 10),
        relief="flat", background="#f8fafc", foreground="#1f2937",
        borderwidth=0, highlightthickness=1, highlightbackground="#e2e8f0",
        padx=8, pady=6
    )
    findings_box.pack(fill="x", pady=(0, 6))
    findings_box.configure(state=tk.DISABLED)

    btn_hijack_remove = ttk.Button(hijack_card, bootstyle="warning", command=remove_hijacks)
    btn_hijack_remove.pack(fill="x", pady=(0, 2))

    def update_ui():
        """Refresh every translatable text in the interface."""
        root.title(t("title"))
        main_label.configure(text=t("title"))
        btn_check.configure(text=t("search_btn"))
        btn_registry.configure(text=t("registry_check_btn"))
        btn_kill.configure(text=t("kill_btn"))
        btn_delete.configure(text=t("delete_btn"))
        btn_hijack.configure(text=t("hijack_btn"))
        btn_hijack_remove.configure(text=t("hijack_remove_btn"))
        policy_card.configure(text=t("policy_section"))
        hijack_card.configure(text=t("hijack_section"))
        btn_policy.configure(text=t("policy_btn"))
        btn_unyandex_policy.configure(text=t("policy_unyandex_btn"))
        lang_label.configure(text=t("lang_label"))
        update_status(t("status_wait"))
        _render_findings([])  # stale findings are in the previous language

    update_ui()

    if not is_admin():
        update_status(t("warn_no_admin"), STATUS_COLORS["warn"])

    root.mainloop()
