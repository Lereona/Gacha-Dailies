import os
import sys
from PySide6.QtGui import QIcon
import configparser

if sys.platform.startswith("win"):
    import pythoncom
    import win32com.client

def get_valid_icon(path, default_icon):
    if path and os.path.exists(path):
        ext = os.path.splitext(path)[1].lower()
        if ext in ['.ico', '.exe', '.dll', '.jpg', '.jpeg', '.png', '.bmp']:
            icon = QIcon(path)
            if not icon.isNull():
                return icon
    return QIcon(default_icon)

def extract_shortcut_info(lnk_path, default_icon):
    pythoncom.CoInitialize()
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(lnk_path)
    target = shortcut.Targetpath
    arguments = shortcut.Arguments
    icon_location = shortcut.IconLocation.split(",")[0] if shortcut.IconLocation else ""
    name = os.path.splitext(os.path.basename(lnk_path))[0]
    icon = None
    if icon_location and os.path.exists(icon_location):
        ext = os.path.splitext(icon_location)[1].lower()
        if ext in ['.ico', '.exe', '.dll']:
            icon = QIcon(icon_location)
    if (not icon or icon.isNull()) and target and os.path.exists(target):
        ext = os.path.splitext(target)[1].lower()
        if ext in ['.ico', '.exe', '.dll']:
            icon = QIcon(target)
    if (not icon or icon.isNull()) and os.path.exists(lnk_path):
        icon = QIcon(lnk_path)
    if not icon or icon.isNull():
        icon = QIcon(default_icon)
    # If both target and arguments are empty, treat as protocol shortcut
    if not target and not arguments:
        unique_key = lnk_path
        return name, "", "", icon, unique_key
    unique_key = f"{target} {arguments}".strip()
    return name, target, arguments, icon, unique_key

def extract_url_info(url_path, browser_icon, default_icon):
    config = configparser.ConfigParser()
    config.read(url_path, encoding="utf-8")
    url = None
    name = os.path.splitext(os.path.basename(url_path))[0]
    icon = None
    icon_file = None
    icon_index = 0
    if "InternetShortcut" in config:
        section = config["InternetShortcut"]
        url = section.get("URL", None)
        icon_file = section.get("IconFile", None)
        icon_index = int(section.get("IconIndex", 0))
    if not url:
        print(f"[DEBUG] Could not find URL in {url_path}. Config sections: {config.sections()}")
        print(f"[DEBUG] Config content: {dict(config.items('InternetShortcut')) if 'InternetShortcut' in config else {}}")
    if icon_file:
        icon_file = os.path.expandvars(icon_file)
    if icon_file and os.path.exists(icon_file):
        ext = os.path.splitext(icon_file)[1].lower()
        if ext in ['.ico', '.exe', '.dll']:
            icon = QIcon(icon_file)
    if not icon or icon.isNull():
        if browser_icon and os.path.exists(browser_icon):
            icon = QIcon(browser_icon)
    if not icon or icon.isNull():
        icon = QIcon(default_icon)
    if url:
        unique_key = f"{url}|{icon_file}" if icon_file else url
    else:
        unique_key = url_path
    return name, url, icon, unique_key 