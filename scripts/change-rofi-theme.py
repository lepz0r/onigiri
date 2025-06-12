#!/usr/bin/env python3
from pathlib import Path
import subprocess
import os

home = str(Path.home())
env = os.environ.copy()

colorschemes = []
colorschemes_entry = ""
colorschemes_dir = Path(home + "/.config/rofi/themes")


for colorscheme in colorschemes_dir.iterdir():
    colorschemes.append(colorscheme.name)

for cr_colorscheme in sorted(colorschemes):
    if cr_colorscheme.endswith(".rasi"):
        cr_colorscheme = cr_colorscheme[:-5]
        if cr_colorscheme != "common.rasi":
            if colorschemes_entry == "":
                colorschemes_entry = cr_colorscheme
            else:
                colorschemes_entry = colorschemes_entry + "\n" + cr_colorscheme


rofi = subprocess.run(
    [
        "sh",
        "-c",
        'echo "'
        + colorschemes_entry
        + '" | rofi -theme $HOME/.config/hypr/conf/rofi-config.rasi -dmenu -p "Change bar color scheme "',
    ],
    env=env,
    capture_output=True,
    text=True,
)

if rofi.stdout != "":
    with open(home + "/.config/hypr/conf/rofi-config.rasi", "w") as rofi_config:
        rofi_config.write(
            '@import "~/.config/rofi/config.rasi"'
            + "\n"
            + '@theme "'
            + rofi.stdout.strip("\n")
            + '"'
            + "\n"
            + '@import "../rofi-userconfig.rasi"'
            + "\n"
        )
