#!/usr/bin/env python3
from pathlib import Path
import configparser
import subprocess
import os

home = str(Path.home())

theme_dirs = [
    "/usr/share/themes/",
    home + "/.themes",
    "/usr/local/share/themes",
    home + "/.local/share/themes",
]
themes = []
theme_entry = ""
env = os.environ.copy()

for theme_dir in theme_dirs:
    try:
        cr_path = Path(theme_dir)
        for cr_theme in cr_path.iterdir():
            if Path(cr_theme / "gtk-3.0").is_dir():
                theme_index = configparser.ConfigParser()
                try:
                    theme_index.read(cr_theme / "index.theme")
                    themes.append(theme_index["X-GNOME-Metatheme"]["Name"])
                except (configparser.MissingSectionHeaderError, KeyError):
                    themes.append(cr_theme.name)
    except FileNotFoundError:
        pass

for theme in themes:
    if theme_entry == "":
        theme_entry = theme
    else:
        theme_entry = theme_entry + "\n" + theme

env["theme_entry"] = theme_entry

rofi = subprocess.run(
    ["sh", "-c", 'echo "$theme_entry" | rofi -dmenu -p "Change GTK 3 theme "'],
    env=env,
    capture_output=True,
    text=True,
)

if rofi.stdout != "":
    subprocess.run(
        [
            "gsettings",
            "set",
            "org.gnome.desktop.interface",
            "gtk-theme",
            rofi.stdout.strip("\n"),
        ]
    )
