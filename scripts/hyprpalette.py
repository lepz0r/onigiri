import json
import subprocess
import argparse

### Parse arguments

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--command-file", type=str, help="External command file")
args = parser.parse_args()

### Get Hyprland's config

get_layout_option = subprocess.run(
    ["hyprctl", "-j", "getoptions", "general:layout"], capture_output=True, text=True
)

get_keybinds = subprocess.run(
    ["hyprctl", "-j", "binds"], capture_output=True, text=True
)


get_workspaces = subprocess.run(
    ["hyprctl", "-j", "workspaces"], capture_output=True, text=True
)

layout_option = json.loads(get_layout_option.stdout)
keybinds = json.loads(get_keybinds.stdout)
workspaces = json.loads(get_workspaces.stdout)
layout = layout_option["str"]

bindds = []

### Functions


def get_bit(binary, bit_index):
    return (binary >> bit_index) & 1


def combiner(current, new, type):
    match type:
        case 0:
            separator = ", "
        case 1:
            separator = "-"
        case _:
            separator = "undefined"
    if len(current) == 0:
        return new
    else:
        return current + separator + new


def replace_key(key):
    match key:
        case "left":
            key = ""
        case "down":
            key = ""
        case "up":
            key = ""
        case "right":
            key = ""
        case "Print":
            key = "Printscreen"

    return key


def generate_keybind(modmask, key):
    keybind = ""
    bit_order = [6, 2, 3, 0, 1, 4, 5, 7]

    for bit_index in bit_order:
        if get_bit(modmask, bit_index) == 1:
            match bit_index:
                case 0:
                    keybind = combiner(keybind, "Shift", 1)
                case 1:
                    keybind = combiner(keybind, "Caps Lock", 1)
                case 2:
                    keybind = combiner(keybind, "Ctrl", 1)
                case 3:
                    keybind = combiner(keybind, "Alt", 1)
                case 4:
                    keybind = combiner(keybind, "Num Lock", 1)
                case 6:
                    keybind = combiner(keybind, "Super", 1)
                case 7:
                    keybind = combiner(keybind, "Scroll Lock", 1)
    return keybind + "-" + replace_key(key).capitalize()


def add_keybind(current_keybind, modmask, key):
    if modmask != 0:
        keybind = generate_keybind(modmask, key)
        output_keybind = combiner(current_keybind, keybind, 0)
    else:
        key = replace_key(key)
        output_keybind = combiner(current_keybind, key, 0)
    return output_keybind


def print_custom_binds(list):
    list_index = 0
    dupes = []
    list = sorted(list, key=lambda x: str(x["priority"]))
    while list_index < len(list):
        if list_index not in dupes:
            current_keybind = list[list_index]
            description = current_keybind["description"]
            dispatcher = current_keybind["dispatcher"]
            arg = current_keybind["arg"]
            keybind = ""
            dupe_finder_list_index = 0

            keybind = add_keybind(
                keybind, current_keybind["modmask"], current_keybind["key"]
            )

            while dupe_finder_list_index < len(list):
                if dupe_finder_list_index != list_index:
                    dupe_finder_current_keybind = list[dupe_finder_list_index]
                    if (
                        description == dupe_finder_current_keybind["description"]
                        and dispatcher == dupe_finder_current_keybind["dispatcher"]
                        and arg == dupe_finder_current_keybind["arg"]
                    ):
                        keybind = add_keybind(
                            keybind,
                            dupe_finder_current_keybind["modmask"],
                            dupe_finder_current_keybind["key"],
                        )
                        dupes.append(dupe_finder_list_index)
                dupe_finder_list_index = dupe_finder_list_index + 1

            print_action(description, keybind, dispatcher + " " + arg, False)
        list_index = list_index + 1


def print_action(description, keybind, command, before_after):
    if len(keybind) > 0:
        keybind = ' <span style="italic" size="smaller">(' + keybind + ")</span>"

    if command.split()[0] == "exec":
        command_output = command.partition(" ")[2]
    else:
        command_output = "hyprctl dispatch " + command

    if before_after:
        bindds_before = []
        bindds_after = []
        for current_keybind in bindds:
            if current_keybind["before"] == command:
                bindds_before.append(current_keybind)

        for current_keybind in bindds:
            if current_keybind["after"] == command:
                bindds_after.append(current_keybind)
        print_custom_binds(bindds_before)
        print(description + keybind + "\0info\x1f" + command_output)
        print_custom_binds(bindds_after)
    else:
        print(description + keybind + "\0info\x1f" + command_output)


### Generate keybind entry

## Define keybind entries
killactive_keybind = ""
cyclenext_keybind = ""
cycleprev_keybind = ""
focusmaster_keybind = ""
mfact_shrink_keybind = ""
mfact_grow_keybind = ""
h_grow_keybind = ""
h_shrink_keybind = ""
v_grow_keybind = ""
v_shrink_keybind = ""
togglefloating_keybind = ""
fullscreen_keybind = ""
maximize_keybind = ""
pin_keybind = ""
swapprev_keybind = ""
swapnext_keybind = ""
swapwithmaster_keybind = ""
movefocus_l_keybind = ""
movefocus_r_keybind = ""
movefocus_u_keybind = ""
movefocus_d_keybind = ""
movewindow_l_keybind = ""
movewindow_r_keybind = ""
movewindow_u_keybind = ""
movewindow_d_keybind = ""
pseudo_keybind = ""
togglesplit_keybind = ""
next_workspace_keybind = ""
prev_workspace_keybind = ""
forcekillactive_keybind = ""
forcerendererreload_keybind = ""

orientationcycle_keybind = ""
addmaster_keybind = ""
removemaster_keybind = ""

mfact_grow_value = "0.025"
mfact_shrink_value = "-0.025"
grow_value = "30"
shrink_value = "-30"
h_grow_value = grow_value
v_grow_value = grow_value
h_shrink_value = shrink_value
v_shrink_value = shrink_value
orientation_rotation = "left top right bottom center"

## Get keybinds

for current_keybind in keybinds:
    if not current_keybind["has_description"]:
        match current_keybind["dispatcher"]:
            case "killactive":
                killactive_keybind = add_keybind(
                    killactive_keybind,
                    current_keybind["modmask"],
                    current_keybind["key"],
                )
            case "layoutmsg":
                match current_keybind["arg"]:
                    case "cyclenext":
                        cyclenext_keybind = add_keybind(
                            cyclenext_keybind,
                            current_keybind["modmask"],
                            current_keybind["key"],
                        )
                    case "cycleprev":
                        cycleprev_keybind = add_keybind(
                            cycleprev_keybind,
                            current_keybind["modmask"],
                            current_keybind["key"],
                        )
                    case "focusmaster":
                        focusmaster_keybind = add_keybind(
                            focusmaster_keybind,
                            current_keybind["modmask"],
                            current_keybind["key"],
                        )
                    case "swapprev":
                        swapprev_keybind = add_keybind(
                            swapprev_keybind,
                            current_keybind["modmask"],
                            current_keybind["key"],
                        )
                    case "swapnext":
                        swapnext_keybind = add_keybind(
                            swapnext_keybind,
                            current_keybind["modmask"],
                            current_keybind["key"],
                        )
                    case "swapwithmaster":
                        swapwithmaster_keybind = add_keybind(
                            swapwithmaster_keybind,
                            current_keybind["modmask"],
                            current_keybind["key"],
                        )
                    case "addmaster":
                        addmaster_keybind = add_keybind(
                            addmaster_keybind,
                            current_keybind["modmask"],
                            current_keybind["key"],
                        )
                    case "removemaster":
                        removemaster_keybind = add_keybind(
                            removemaster_keybind,
                            current_keybind["modmask"],
                            current_keybind["key"],
                        )

                    case _:
                        if "mfact" in current_keybind["arg"]:
                            resize_value = float(current_keybind["arg"].split()[1])
                            if resize_value < 0:
                                mfact_shrink_keybind = add_keybind(
                                    mfact_shrink_keybind,
                                    current_keybind["modmask"],
                                    current_keybind["key"],
                                )
                                mfact_shrink_value = str(resize_value)
                            elif resize_value > 0:
                                mfact_grow_keybind = add_keybind(
                                    mfact_grow_keybind,
                                    current_keybind["modmask"],
                                    current_keybind["key"],
                                )
                                mfact_grow_value = str(resize_value)
                        elif "orientationcycle" in current_keybind["arg"]:
                            orientationcycle_keybind = add_keybind(
                                orientationcycle_keybind,
                                current_keybind["modmask"],
                                current_keybind["key"],
                            )
                            orientation_rotation = (
                                current_keybind["arg"]
                                .split("orientationcycle")[1]
                                .strip()
                            )

            case "resizeactive":
                if "exact" not in current_keybind["arg"]:
                    h_resize_value_current = current_keybind["arg"].split()[0]
                    v_resize_value_current = current_keybind["arg"].split()[1]
                    if "%" in current_keybind:
                        pass
                    else:
                        if v_resize_value_current == "0":
                            if int(h_resize_value_current) > 0:
                                h_grow_keybind = add_keybind(
                                    h_grow_keybind,
                                    current_keybind["modmask"],
                                    current_keybind["key"],
                                )
                                h_grow_value = h_resize_value_current
                            else:
                                h_shrink_keybind = add_keybind(
                                    h_shrink_keybind,
                                    current_keybind["modmask"],
                                    current_keybind["key"],
                                )
                                h_shrink_value = h_resize_value_current
                        elif h_resize_value_current == "0":
                            if h_resize_value_current == "0":
                                if int(v_resize_value_current) > 0:
                                    v_grow_keybind = add_keybind(
                                        v_grow_keybind,
                                        current_keybind["modmask"],
                                        current_keybind["key"],
                                    )
                                    v_grow_value = v_resize_value_current
                                else:
                                    v_shrink_keybind = add_keybind(
                                        v_shrink_keybind,
                                        current_keybind["modmask"],
                                        current_keybind["key"],
                                    )
                                    v_shrink_value = v_resize_value_current
            case "movefocus":
                if current_keybind["arg"] == "l":
                    movefocus_l_keybind = add_keybind(
                        movefocus_l_keybind,
                        current_keybind["modmask"],
                        current_keybind["key"],
                    )
                elif current_keybind["arg"] in ("b", "d"):
                    movefocus_d_keybind = add_keybind(
                        movefocus_d_keybind,
                        current_keybind["modmask"],
                        current_keybind["key"],
                    )
                elif current_keybind["arg"] in ("t", "u"):
                    movefocus_u_keybind = add_keybind(
                        movefocus_u_keybind,
                        current_keybind["modmask"],
                        current_keybind["key"],
                    )
                elif current_keybind["arg"] == "r":
                    movefocus_r_keybind = add_keybind(
                        movefocus_r_keybind,
                        current_keybind["modmask"],
                        current_keybind["key"],
                    )
            case "togglesplit":
                togglesplit_keybind = add_keybind(
                    togglesplit_keybind,
                    current_keybind["modmask"],
                    current_keybind["key"],
                )
            case "movewindow":
                if current_keybind["arg"] == "l":
                    movewindow_l_keybind = add_keybind(
                        movewindow_l_keybind,
                        current_keybind["modmask"],
                        current_keybind["key"],
                    )
                elif current_keybind["arg"] in ("b", "d"):
                    movewindow_d_keybind = add_keybind(
                        movewindow_d_keybind,
                        current_keybind["modmask"],
                        current_keybind["key"],
                    )
                elif current_keybind["arg"] in ("t", "u"):
                    movewindow_u_keybind = add_keybind(
                        movewindow_u_keybind,
                        current_keybind["modmask"],
                        current_keybind["key"],
                    )
                elif current_keybind["arg"] == "r":
                    movewindow_r_keybind = add_keybind(
                        movewindow_r_keybind,
                        current_keybind["modmask"],
                        current_keybind["key"],
                    )

            case "togglefloating":
                togglefloating_keybind = add_keybind(
                    togglefloating_keybind,
                    current_keybind["modmask"],
                    current_keybind["key"],
                )
            case "pseudo":
                pseudo_keybind = add_keybind(
                    pseudo_keybind,
                    current_keybind["modmask"],
                    current_keybind["key"],
                )
            case "fullscreen":
                match current_keybind["arg"]:
                    case "0":
                        fullscreen_keybind = add_keybind(
                            fullscreen_keybind,
                            current_keybind["modmask"],
                            current_keybind["key"],
                        )
                    case "1":
                        maximize_keybind = add_keybind(
                            maximize_keybind,
                            current_keybind["modmask"],
                            current_keybind["key"],
                        )
            case "pin":
                if current_keybind["arg"] == "" or current_keybind["arg"] == "active":
                    pin_keybind = add_keybind(
                        pin_keybind,
                        current_keybind["modmask"],
                        current_keybind["key"],
                    )
            case "workspace":
                match current_keybind["arg"]:
                    case "+1":
                        next_workspace_keybind = add_keybind(
                            next_workspace_keybind,
                            current_keybind["modmask"],
                            current_keybind["key"],
                        )
                    case "-1":
                        prev_workspace_keybind = add_keybind(
                            prev_workspace_keybind,
                            current_keybind["modmask"],
                            current_keybind["key"],
                        )
            case "forcekillactive":
                forcekillactive_keybind = add_keybind(
                    forcekillactive_keybind,
                    current_keybind["modmask"],
                    current_keybind["key"],
                )
            case "forcerendererreload":
                forcerendererreload_keybind = add_keybind(
                    forcerendererreload_keybind,
                    current_keybind["modmask"],
                    current_keybind["key"],
                )
    else:
        description = current_keybind["description"]
        description_part = description.split("␀")
        description = description_part[0]
        description_part_index = 1

        new_keybind = {
            "description": description,
            "modmask": current_keybind["modmask"],
            "key": current_keybind["key"],
            "dispatcher": current_keybind["dispatcher"],
            "arg": current_keybind["arg"],
            "position": "",
            "before": "",
            "after": "",
            "priority": "zzzzz",
        }

        if len(description_part) > 1:
            while description_part_index <= len(description_part) - 2:
                new_keybind[description_part[description_part_index]] = (
                    description_part[description_part_index + 1]
                )
                description_part_index = description_part_index + 1

        bindds.append(new_keybind)


## Workspaces

for current_workspace in workspaces:
    switch_to_keybind = ""
    move_to_silent_keybind = ""
    for current_keybind in keybinds:
        if current_keybind["dispatcher"] == "workspace" and current_keybind[
            "arg"
        ] == str(current_workspace["id"]):
            switch_to_keybind = add_keybind(
                switch_to_keybind,
                current_keybind["modmask"],
                current_keybind["key"],
            )
        if current_keybind["dispatcher"] == "movetoworkspacesilent" and current_keybind[
            "arg"
        ] == str(current_workspace["id"]):
            move_to_silent_keybind = add_keybind(
                move_to_silent_keybind,
                current_keybind["modmask"],
                current_keybind["key"],
            )

    current_workspace["switchtokeybind"] = switch_to_keybind
    current_workspace["movetosilentkeybind"] = move_to_silent_keybind

### Add commands from file
try:
    if args.command_file:
        file = open(args.command_file)
        ext_command = json.loads(file.read())
        for current_command in ext_command:
            keys = ["position", "before", "after", "key"]
            for current_key in keys:
                try:
                    test_key = current_command[current_key]
                except KeyError:
                    current_command[current_key] = ""

            try:
                test_key = current_command["modmask"]
            except KeyError:
                current_command["modmask"] = 0

            try:
                test_key = current_command["priority"]
            except KeyError:
                current_command["priority"] = "zzzzz"

            # current_command["key"] = ""
            bindds.append(current_command)
except FileNotFoundError:
    pass


### Filter

bindds_top = []
for current_keybind in bindds:
    if current_keybind["position"] in ("top", "beginning", "begin", ""):
        if (
            current_keybind["position"] == ""
            and current_keybind["before"] == ""
            and current_keybind["after"] == ""
        ):
            bindds_top.append(current_keybind)
        elif current_keybind["position"] in ("top", "beginning", "begin"):
            bindds_top.append(current_keybind)

bindds_bottom = []
for current_keybind in bindds:
    if current_keybind["position"] in ("bottom", "end", "bot"):
        bindds_bottom.append(current_keybind)


### Print actions

## Print custom keybindings that has description
print_custom_binds(bindds_top)

print_action("Maximize/restore active window", maximize_keybind, "fullscreen 1", True)

print_action(
    "Toggle active window fullscreen", fullscreen_keybind, "fullscreen 0", True
)

print_action("Close active window", killactive_keybind, "killactive", True)

print_action("Move window left", movewindow_l_keybind, "movewindow l", True)
print_action("Move window down", movewindow_d_keybind, "movewindow d", True)
print_action("Move window up", movewindow_u_keybind, "movewindow u", True)
print_action("Move window right", movewindow_r_keybind, "movewindow r", True)

# Workspace related entries goes here

print_action(
    "Switch to previous workspace", prev_workspace_keybind, "workspace -1", True
)

print_action("Switch to next workspace", next_workspace_keybind, "workspace +1", True)


for current_workspace in sorted(workspaces, key=lambda x: x["name"]):
    print_action(
        "Switch to workspace " + current_workspace["name"],
        current_workspace["switchtokeybind"],
        "workspace " + str(current_workspace["id"]),
        True,
    )

for current_workspace in sorted(workspaces, key=lambda x: x["name"]):
    print_action(
        "Move active window to workspace " + current_workspace["name"],
        current_workspace["movetosilentkeybind"],
        "movetoworkspacesilent " + str(current_workspace["id"]),
        True,
    )


if layout == "master":
    print_action("Focus next window", cyclenext_keybind, "layoutmsg cyclenext", True)
    print_action(
        "Focus previous window", cycleprev_keybind, "layoutmsg cycleprev", True
    )
    print_action(
        "Grow master window",
        mfact_grow_keybind,
        "layoutmsg mfact " + mfact_grow_value,
        True,
    )
    print_action(
        "Shrink master window",
        mfact_shrink_keybind,
        "layoutmsg mfact " + mfact_shrink_value,
        True,
    )
    print_action("Focus master", focusmaster_keybind, "layoutmsg focusmaster", True)


print_action("Focus left window", movefocus_l_keybind, "movefocus l", True)
print_action("Focus down window", movefocus_d_keybind, "movefocus d", True)
print_action("Focus up window", movefocus_u_keybind, "movefocus u", True)
print_action("Focus right window", movefocus_r_keybind, "movefocus r", True)

print_action(
    "Toggle focused window floating", togglefloating_keybind, "togglefloating", True
)
if layout == "dwindle":
    print_action("Toggle pseudotiling", pseudo_keybind, "pseudo", True)
    print_action("Toggle split", togglesplit_keybind, "togglesplit", True)

print_action(
    "Grow active window horizontally",
    h_grow_keybind,
    "resizeactive " + h_grow_value + " 0",
    True,
)

print_action(
    "Shrink active window horizontally",
    h_shrink_keybind,
    "resizeactive " + h_shrink_value + " 0",
    True,
)

print_action(
    "Grow active window vertically",
    v_grow_keybind,
    "resizeactive " + "0 " + v_grow_value,
    True,
)

print_action(
    "Shrink active window vertically",
    v_shrink_keybind,
    "resizeactive " + "0 " + v_shrink_value,
    True,
)


print_action("Pin active window", pin_keybind, "pin", True)

if layout == "master":
    print_action(
        "Swap with previous window", swapprev_keybind, "layoutmsg swapprev", True
    )

    print_action("Swap with next window", swapnext_keybind, "layoutmsg swapnext", True)

    print_action(
        "Swap with master", swapwithmaster_keybind, "layoutmsg swapwithmaster", True
    )

    print_action(
        "Cycle orientation (" + orientation_rotation + ")",
        orientationcycle_keybind,
        "layoutmsg orientationcycle " + orientation_rotation,
        True,
    )

    print_action(
        "Add active window to master", addmaster_keybind, "layoutmsg addmaster", True
    )

    print_action(
        "Remove active window from master",
        removemaster_keybind,
        "layoutmsg removemaster",
        True,
    )

print_action("Kill active window", forcekillactive_keybind, "forcekillactive", True)

print_action(
    "Force renderer reload", forcerendererreload_keybind, "forcerendererreload", True
)

print_custom_binds(bindds_bottom)
