import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import os
import shutil
import psutil
import threading
import webbrowser
import winreg

import engines
import policies
import translations
import yandex_detect

APP_VERSION = "2.1.2"
APP_AUTHOR = "Nod33Eset"
GITHUB_URL = "https://github.com/retvil/AntiYandexVanced"

language = translations.detect_system_language()

YANDEX_PATHS = yandex_detect.YANDEX_PATHS

found_path = None

TEXT_MUTED = "#6b7280"
STATUS_COLORS = {
    "ok": "#15803d",
    "warn": "#b45309",
    "info": "#0369a1",
    "bad": "#b91c1c",
}

def t(key):
    return translations.t(language, key)

def update_status(status, color=STATUS_COLORS["info"]):
    status_label.configure(text=status, foreground=color)

def check_registry_for_yandex():
    found_in_reg = False
    try:
        path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as key:
            for i in range(winreg.QueryInfoKey(key)[0]):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, subkey_name) as subkey:
                        name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                        if "Yandex" in name or "Яндекс" in name:
                            found_in_reg = True
                            break
                except: continue
    except: pass

    if found_in_reg:
        update_status(t("reg_found"), STATUS_COLORS["ok"])
        messagebox.showinfo(t("title"), t("reg_found"))
    else:
        update_status(t("reg_not_found"), STATUS_COLORS["bad"])
        messagebox.showwarning(t("title"), t("reg_not_found"))

def kill_yandex_processes():
    killed = False
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() in ["browser.exe", "yandex.exe"]:
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
        update_status(t("status_searching"), STATUS_COLORS["info"])
        hits = [p for p in YANDEX_PATHS if os.path.exists(p)]
        if hits:
            update_status(t("status_found").format(hits[0]), STATUS_COLORS["ok"])
        else:
            update_status(t("status_not_found"), STATUS_COLORS["bad"])
    threading.Thread(target=task, daemon=True).start()

def uninstall_yandex_browser():
    global found_path
    hits = [p for p in YANDEX_PATHS if os.path.exists(p)]
    if not hits:
        messagebox.showwarning(t("title"), t("delete_first"))
        return
    target = hits[0]

    def task():
        global found_path
        try:
            shutil.rmtree(target, ignore_errors=True)
            if not os.path.exists(target):
                yandex_detect.remove_uninstall_entries()
                update_status(t("delete_success"), STATUS_COLORS["ok"])
                messagebox.showinfo(t("title"), t("delete_success"))
                found_path = None
            else:
                raise Exception("Files locked")
        except PermissionError:
            update_status(t("delete_fail"), STATUS_COLORS["bad"])
            messagebox.showerror(t("title"), "Запустите программу от имени администратора для удаления записей реестра")
        except Exception as e:
            update_status(t("delete_fail"), STATUS_COLORS["bad"])
            messagebox.showerror(t("title"), f"{t('delete_fail')}\nError: {e}")

    threading.Thread(target=task, daemon=True).start()

def _render_findings(lines, color):
    findings_box.configure(state=tk.NORMAL)
    findings_box.delete("1.0", tk.END)
    for line in lines:
        findings_box.insert(tk.END, line + "\n")
    findings_box.configure(state=tk.DISABLED)

def scan_hijacks():
    """Scan every known Yandex search-hijack vector and show findings."""
    def task():
        update_status(t("status_searching"), STATUS_COLORS["info"])
        findings = yandex_detect.scan_all()
        if findings:
            _render_findings(
                [t("hijack_found").format(len(findings))] + [f"•  {f}" for f in findings],
                "#1f2937"
            )
            update_status(t("hijack_found").format(len(findings)), STATUS_COLORS["warn"])
        else:
            _render_findings([t("hijack_clean")], STATUS_COLORS["ok"])
            update_status(t("hijack_clean"), STATUS_COLORS["ok"])
    threading.Thread(target=task, daemon=True).start()

def remove_hijacks():
    """Remove all detected hijack vectors after user confirmation."""
    if not messagebox.askyesno(t("title"), t("hijack_remove_confirm")):
        return

    def task():
        removed, failed = yandex_detect.remove_all_hijacks()
        if removed:
            update_status(t("hijack_removed").format(len(removed)), STATUS_COLORS["ok"])
        else:
            update_status(t("hijack_none"), STATUS_COLORS["info"])
        if failed:
            messagebox.showwarning(t("title"), t("hijack_remove_fail").format("\n".join(failed)))
        if removed:
            messagebox.showinfo(t("title"), t("hijack_removed").format("\n".join(removed)))
        elif not failed:
            messagebox.showinfo(t("title"), t("hijack_none"))
        scan_hijacks()
    threading.Thread(target=task, daemon=True).start()

def apply_search_policy():
    """Hard-enforce the selected engine in all Chromium browsers + Firefox."""
    engine = engines.get_engine(engine_menu.get())

    def task():
        applied, failed = policies.apply_chromium(engine, list(policies.CHROMIUM_POLICY_PATHS))
        ff_applied, ff_failed = policies.apply_firefox(engine)
        applied += ff_applied
        failed += ff_failed
        update_status(t("policy_applied").format(", ".join(applied) or "-"), STATUS_COLORS["ok"])
        if failed:
            messagebox.showwarning(t("title"), t("policy_failed").format(", ".join(failed)))
        else:
            messagebox.showinfo(t("title"), t("policy_applied").format(", ".join(applied)))
    threading.Thread(target=task, daemon=True).start()

def remove_yandex_policies():
    """Strip Yandex DefaultSearchProvider policy values from the registry."""
    def task():
        cleaned = policies.remove_yandex_search_policies()
        if cleaned:
            update_status(t("policy_cleaned").format(", ".join(cleaned)), STATUS_COLORS["ok"])
            messagebox.showinfo(t("title"), t("policy_cleaned").format("\n".join(cleaned)))
        else:
            update_status(t("policy_nothing"), STATUS_COLORS["info"])
            messagebox.showinfo(t("title"), t("policy_nothing"))
    threading.Thread(target=task, daemon=True).start()

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
footer.pack(side=BOTTOM, fill=X)

github_link = ttk.Label(
    footer, font=("Segoe UI", 9, "underline"), foreground="#0369a1",
    text="GitHub", cursor="hand2"
)
github_link.pack(side=RIGHT)
github_link.bind("<Button-1>", lambda e: webbrowser.open(GITHUB_URL))

footer_label = ttk.Label(
    footer, font=("Segoe UI", 9), foreground=TEXT_MUTED,
    text=f"AntiYandexVanced {APP_VERSION} by {APP_AUTHOR} |"
)
footer_label.pack(side=RIGHT, padx=(0, 4))

# Status bar: packed second (above footer) so it also survives window resize
status_label = ttk.Label(
    root, font=("Segoe UI", 10), wraplength=400, justify="center",
    anchor="center", padding=(20, 8, 20, 6)
)
status_label.pack(side=BOTTOM, fill=X)

# Policy section card: pinned above the status bar, survives window resize
policy_card = ttk.Labelframe(root, text=t("policy_section"), padding=(16, 8, 16, 12))
policy_card.pack(side=BOTTOM, fill=X, padx=20, pady=(10, 4))

policy_row = ttk.Frame(policy_card)
policy_row.pack(fill=X, pady=(4, 8))

engine_menu = ttk.Combobox(
    policy_row, values=list(engines.ENGINE_NAMES),
    state="readonly", font=("Segoe UI", 11)
)
engine_menu.set(engines.ENGINE_NAMES[0])
engine_menu.pack(fill=X)

btn_policy = ttk.Button(policy_card, bootstyle=SUCCESS, command=apply_search_policy)
btn_policy.pack(fill=X, pady=(0, 6))

btn_unyandex_policy = ttk.Button(policy_card, bootstyle=SECONDARY, command=remove_yandex_policies)
btn_unyandex_policy.pack(fill=X, pady=(0, 2))

def on_language_change(choice):
    global language
    for code, display in translations.LANG_DISPLAY_NAMES.items():
        if display == choice:
            language = code
            break
    update_ui()

# Language selector: top-right corner
lang_bar = ttk.Frame(root, padding=(20, 10, 20, 0))
lang_bar.pack(fill=X)

lang_menu = ttk.Combobox(
    lang_bar, values=list(translations.LANG_DISPLAY_NAMES.values()),
    state="readonly", width=13, font=("Segoe UI", 11)
)
lang_menu.set(translations.LANG_DISPLAY_NAMES[language])
lang_menu.bind("<<ComboboxSelected>>", on_language_change)
lang_menu.pack(side=RIGHT)

lang_label = ttk.Label(lang_bar, font=("Segoe UI", 11), foreground=TEXT_MUTED)
lang_label.pack(side=RIGHT, padx=(0, 8))

# Title centered
main_label = ttk.Label(root, font=("Segoe UI", 18, "bold"), anchor="center")
main_label.pack(fill=X, padx=20, pady=(6, 10))

# Primary actions: full-width stack, same margins as the cards below
actions = ttk.Frame(root)
actions.pack(fill=X, padx=20, pady=(2, 2))

btn_check = ttk.Button(actions, bootstyle=INFO, command=check_yandex_browser)
btn_check.pack(fill=X, pady=2)

btn_registry = ttk.Button(actions, bootstyle=SECONDARY, command=check_registry_for_yandex)
btn_registry.pack(fill=X, pady=2)

btn_kill = ttk.Button(actions, bootstyle=INFO, command=kill_yandex_processes)
btn_kill.pack(fill=X, pady=2)

btn_delete = ttk.Button(actions, bootstyle=DANGER, command=uninstall_yandex_browser)
btn_delete.pack(fill=X, pady=(2, 8))

# Hijack section card: pinned above the policy card, survives window resize
hijack_card = ttk.Labelframe(root, text=t("hijack_section"), padding=(16, 8, 16, 12))
hijack_card.pack(side=BOTTOM, fill=X, padx=20, pady=(6, 4))

btn_hijack = ttk.Button(hijack_card, bootstyle=INFO, command=scan_hijacks)
btn_hijack.pack(fill=X, pady=(2, 8))

findings_box = tk.Text(
    hijack_card, height=4, wrap="word", font=("Consolas", 10),
    relief="flat", background="#f8fafc", foreground="#1f2937",
    borderwidth=0, highlightthickness=1, highlightbackground="#e2e8f0",
    padx=8, pady=6
)
findings_box.pack(fill=X, pady=(0, 8))
findings_box.configure(state=tk.DISABLED)

btn_hijack_remove = ttk.Button(hijack_card, bootstyle=WARNING, command=remove_hijacks)
btn_hijack_remove.pack(fill=X, pady=(0, 2))

def update_ui():
    """Функция обновления всех текстов в интерфейсе"""
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

update_ui()

root.mainloop()

