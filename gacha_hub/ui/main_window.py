from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QPoint, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon
import os
import sys
import configparser
from gacha_hub.core.launcher import GameLauncher
import shlex
from .game_list_widget import RemovableListWidget
from .icon_utils import get_valid_icon, extract_shortcut_info, extract_url_info
from gacha_hub.ui.persistence import save_games, load_games, get_save_path

if sys.platform.startswith("win"):
    import pythoncom
    import win32com.client

def get_valid_icon(path, default_icon):
    if path and os.path.exists(path):
        ext = os.path.splitext(path)[1].lower()
        if ext in ['.ico', '.exe', '.dll']:
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

class MainWindow(QMainWindow):
    DEFAULT_TRASH_STYLE = (
        "background: #b2bec3; color: #2d3436; border: 2px solid #636e72; border-radius: 8px; font-size: 20px;"
    )
    DELETE_MODE_TRASH_STYLE = (
        "background: #e74c3c; color: white; border: 2px solid #b03a2e; border-radius: 8px; font-size: 20px;"
    )

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gacha Game Hub")
        self.setMinimumSize(900, 600)
        self.games = []  # List of dicts: {name, path, icon, type, launch_target, unique_key, exe, args}
        self.icon_path = os.path.join(os.path.dirname(__file__), "assets", "icons", "game.png")
        self.browser_icon_path = os.path.join(os.path.dirname(__file__), "assets", "icons", "browser.png")
        # Set the window icon to logo.jpg
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "icons", "logo.jpg")
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        self.delete_mode = False
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        sidebar = QVBoxLayout()
        sidebar.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.trash_btn = QPushButton("🗑️")
        self.trash_btn.setFixedSize(40, 40)
        self.trash_btn.setMinimumSize(40, 40)
        self.trash_btn.setStyleSheet(self.DEFAULT_TRASH_STYLE)
        self.trash_btn.clicked.connect(self.toggle_delete_mode)
        sidebar.addWidget(self.trash_btn)
        print("[DEBUG] Trash button added to sidebar")

        self.game_list = RemovableListWidget(self)
        self.game_list.setFixedWidth(220)
        self.game_list.itemClicked.connect(self.launch_selected_game)
        self.game_list.longPressed.connect(self.enable_reorder_mode)
        self.game_list.itemClickedForDelete.connect(self.on_long_press_item)
        self.game_list.model().rowsMoved.connect(self.on_games_reordered)
        sidebar.addWidget(self.game_list)

        self.add_game_btn = QPushButton("+ Add Game")
        self.add_game_btn.setMaximumWidth(220)
        self.add_game_btn.setMinimumWidth(220)
        self.add_game_btn.clicked.connect(self.add_game)
        sidebar.addWidget(self.add_game_btn)

        main_layout.addLayout(sidebar)
        self.main_area = QWidget()
        main_layout.addWidget(self.main_area)

        # Load games from persistence
        self.load_games_from_file()

    def apply_styles(self):
        qss_path = os.path.join(os.path.dirname(__file__), "assets", "styles.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def is_duplicate(self, unique_key):
        for game in self.games:
            if game["unique_key"] == unique_key:
                return True
        return False

    def add_game(self):
        file_dialog = QFileDialog(self, "Select Game Executable, Shortcut, or Internet Shortcut")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Executables (*.exe *.bat *.sh *.app *.lnk *.url);;All Files (*)")
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            ext = os.path.splitext(file_path)[1].lower()
            print(f"[DEBUG] Adding game: {file_path} (ext: {ext})")
            game_name = None
            icon = None
            launch_target = file_path
            game_type = "file"
            unique_key = None
            exe = None
            args = None

            if ext == ".lnk" and sys.platform.startswith("win"):
                try:
                    game_name, exe, args, icon, unique_key = extract_shortcut_info(file_path, self.icon_path)
                    launch_target = (exe, args)
                    game_type = "shortcut"
                    # Try to get the icon path from the shortcut, fallback to default
                    icon_path = None
                    if hasattr(icon, 'name') and icon.name():
                        icon_path = icon.name()
                    elif os.path.exists(file_path):
                        icon_path = file_path
                    else:
                        icon_path = self.icon_path
                    print(f"[DEBUG] Shortcut extracted: exe={exe}, args={args}, icon={icon}, unique_key={unique_key}")
                except Exception as e:
                    print(f"Failed to extract shortcut info: {e}")
                    game_name = os.path.splitext(os.path.basename(file_path))[0]
                    icon = QIcon(self.icon_path)
                    icon_path = self.icon_path
                    unique_key = file_path
                    launch_target = (file_path, "")
                    exe = file_path
                    args = ""
            elif ext == ".exe":
                game_name = os.path.splitext(os.path.basename(file_path))[0]
                icon = get_valid_icon(file_path, self.icon_path)
                icon_path = file_path if not icon.isNull() else self.icon_path
                print(f"[DEBUG] EXE icon: {file_path}, icon.isNull={icon.isNull()}")
                if icon.isNull():
                    print(f"[DEBUG] Icon for {file_path} is null, using default icon: {self.icon_path}")
                launch_target = file_path
                game_type = "exe"
                unique_key = file_path
            elif ext == ".url":
                game_name, url, icon, unique_key = extract_url_info(file_path, self.browser_icon_path, self.icon_path)
                icon_path = self.browser_icon_path if not icon.isNull() else self.icon_path
                print(f"[DEBUG] URL extracted: url={url}, icon={icon}, unique_key={unique_key}")
                launch_target = url
                game_type = "url"
            else:
                game_name = os.path.splitext(os.path.basename(file_path))[0]
                icon = QIcon(self.icon_path)
                icon_path = self.icon_path
                print(f"[DEBUG] Other file: {file_path}, using default icon: {self.icon_path}")
                launch_target = file_path
                game_type = "file"
                unique_key = file_path

            if not launch_target or self.is_duplicate(unique_key):
                print(f"[Duplicate] Attempted unique_key: {unique_key}")
                print(f"[Duplicate] Current unique_keys: {[g['unique_key'] for g in self.games]}")
                QMessageBox.warning(self, "Duplicate Game", f"This game or shortcut is already in your list.")
                return

            self.games.append({
                "name": game_name,
                "path": file_path,
                "icon_path": icon_path,
                "type": game_type,
                "launch_target": launch_target,
                "unique_key": unique_key,
                "exe": exe,
                "args": args
            })
            item = QListWidgetItem(icon, game_name)
            self.game_list.addItem(item)
            print(f"[DEBUG] Game added: {game_name}, icon.isNull={icon.isNull()}, type={game_type}, unique_key={unique_key}")
            self.save_games_to_file()

    def launch_selected_game(self, item):
        idx = self.game_list.row(item)
        game = self.games[idx]
        try:
            if sys.platform.startswith("win"):
                if game["type"] == "shortcut":
                    exe = game.get("exe")
                    args = game.get("args", "")
                    if exe:  # Normal shortcut
                        import subprocess
                        subprocess.Popen([exe] + shlex.split(args))
                    else:  # Protocol shortcut, launch the .lnk file itself
                        os.startfile(game["path"])
                else:
                    os.startfile(game["launch_target"])
            else:
                import subprocess
                if game["type"] == "url":
                    subprocess.Popen(["xdg-open" if sys.platform.startswith("linux") else "open", game["launch_target"]])
                else:
                    subprocess.Popen([game["launch_target"]])
        except Exception as e:
            print(f"[Launch Failed] {game}")
            print(f"[Launch Failed] Exception: {e}")
            QMessageBox.warning(self, "Launch Failed", f"Could not launch {game['name']}.\n{e}")

    def enable_reorder_mode(self, item):
        if not self.delete_mode:
            self.game_list.enable_reorder_mode()

    def toggle_delete_mode(self):
        self.delete_mode = not self.delete_mode
        self.game_list.set_delete_mode(self.delete_mode)
        if self.delete_mode:
            self.trash_btn.setStyleSheet(self.DELETE_MODE_TRASH_STYLE)
        else:
            self.trash_btn.setStyleSheet(self.DEFAULT_TRASH_STYLE)
        if not self.delete_mode:
            self.game_list.setDragDropMode(QListWidget.NoDragDrop)
            self.game_list.setDragEnabled(False)

    def on_long_press_item(self, item):
        if self.delete_mode:
            idx = self.game_list.row(item)
            game = self.games[idx]
            reply = QMessageBox.question(self, "Remove Game", f"Remove '{game['name']}' from your list?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.games.pop(idx)
                self.game_list.takeItem(idx)
                self.save_games_to_file()

    # Remove mouseReleaseEvent override from MainWindow
    # Drag/drop logic should be handled in RemovableListWidget only

    def on_games_reordered(self, *args):
        # Update self.games order to match QListWidget
        new_games = []
        for i in range(self.game_list.count()):
            item = self.game_list.item(i)
            name = item.text()
            # Find the matching game by name and add in new order
            for game in self.games:
                if game["name"] == name:
                    new_games.append(game)
                    break
        self.games = new_games
        self.save_games_to_file()

    def load_games_from_file(self):
        try:
            loaded_games = load_games()
            print(f"[DEBUG] Loaded games from file: {loaded_games}")
            self.games.clear()
            self.game_list.clear()
            for game in loaded_games:
                icon = get_valid_icon(game.get("icon_path", self.icon_path), self.icon_path)
                item = QListWidgetItem(icon, game["name"])
                self.games.append(game)
                self.game_list.addItem(item)
        except Exception as e:
            print(f"[DEBUG] Failed to load games: {e}")

    def save_games_to_file(self):
        try:
            save_games(self.games)
            print(f"[DEBUG] Games saved to file at: {get_save_path()}")
        except Exception as e:
            print(f"[DEBUG] Failed to save games: {e}") 