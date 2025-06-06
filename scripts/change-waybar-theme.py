#!/usr/bin/env python3
from pathlib import Path
import subprocess
import os
import psutil
import signal

home = str(Path.home())
env = os.environ.copy()

colorschemes = []
colorschemes_entry = ""
colorschemes_dir = Path(home + "/.config/waybar/colorschemes")


def killall(process_name, sig):
    found = False
    for proc in psutil.process_iter(["pid", "name"]):
        if process_name.lower() in proc.info["name"].lower():
            try:
                proc.send_signal(sig)
                found = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    if not found:
        print(f"No running processes matched '{process_name}'")


for colorscheme in colorschemes_dir.iterdir():
    colorschemes.append(colorscheme.name)

for cr_colorscheme in sorted(colorschemes):
    if not cr_colorscheme.endswith("-common") and cr_colorscheme != "shared":
        if colorschemes_entry == "":
            colorschemes_entry = cr_colorscheme
        else:
            colorschemes_entry = colorschemes_entry + "\n" + cr_colorscheme


rofi = subprocess.run(
    [
        "sh",
        "-c",
        'echo "' + colorschemes_entry + '" | rofi -dmenu -p "Change bar color scheme "',
    ],
    env=env,
    capture_output=True,
    text=True,
)

if rofi.stdout != "":
    with open(home + "/.config/hypr/conf/waybar-style.css", "w") as waybar_css:
        waybar_css.write(
            '@import url("../../waybar/style.css");'
            + "\n"
            + '@import url("../../waybar/colorschemes/'
            + rofi.stdout.strip("\n")
            + '/style.css");'
            + "\n"
            + '@import url("../waybar-userstyle.css");'
            + "\n"
        )
    killall("waybar", signal.SIGUSR2)
