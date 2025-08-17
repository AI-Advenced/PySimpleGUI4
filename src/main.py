

# all of the tkinter involved imports
import tkinter as tk

# import tkinter.scrolledtext as tkst
import tkinter.font
from tkinter import filedialog
from tkinter import ttk
from tkinter.colorchooser import askcolor

# end of tkinter specific imports
# get the tkinter detailed version
tclversion_detailed = tkinter.Tcl().eval("info patchlevel")
framework_version = tclversion_detailed

import time
import pickle
import calendar
import datetime
import textwrap

import socket
from hashlib import sha256 as hh
import inspect
import traceback
import difflib
import copy
import pprint

try:  # Because Raspberry Pi is still on 3.4....it's not critical if this module isn't imported on the Pi
    from typing import (
        List,
        Any,
        Union,
        Tuple,
        Dict,
        SupportsAbs,
        Optional,
    )  # because this code has to run on 2.7 can't use real type hints.  Must do typing only in comments
except Exception:
    print(
        '*** Skipping import of Typing module. "pip3 install typing" to remove this warning ***'
    )
import random
import warnings
from math import floor
from math import fabs
from functools import wraps

try:  # Because Raspberry Pi is still on 3.4....
    import subprocess
except Exception as e:
    print("** Import error {} **".format(e))

import threading
import itertools
import json
import configparser
import queue

try:
    import webbrowser

    webbrowser_available = True
except Exception:
    webbrowser_available = False

import pydoc
import os
import sys
import ctypes
import platform


import sys
import json
import sys
import time
import datetime
from functools import wraps
from .constants import *




def _main_entry_point():
    # print('Restarting main as a new process...(needed in case you want to GitHub Upgrade)')
    # Relaunch using the same python interpreter that was used to run this function
    interpreter = sys.executable
    if "pythonw" in interpreter:
        interpreter = interpreter.replace("pythonw", "python")
    execute_py_file(__file__, interpreter_command=interpreter)





def _read_mac_global_settings():
    """
    Reads the settings from the PySimpleGUI Global Settings and sets variables that
    are used at runtime to control how certain features behave
    """

    global ENABLE_MAC_MODAL_DISABLE_PATCH
    global ENABLE_MAC_NOTITLEBAR_PATCH
    global ENABLE_MAC_DISABLE_GRAB_ANYWHERE_WITH_TITLEBAR
    global ENABLE_MAC_ALPHA_99_PATCH

    ENABLE_MAC_MODAL_DISABLE_PATCH = pysimplegui_user_settings.get(
        MAC_PATCH_DICT["Disable Modal Windows"][0],
        MAC_PATCH_DICT["Disable Modal Windows"][1],
    )
    ENABLE_MAC_NOTITLEBAR_PATCH = pysimplegui_user_settings.get(
        MAC_PATCH_DICT["Enable No Titlebar Patch"][0],
        MAC_PATCH_DICT["Enable No Titlebar Patch"][1],
    )
    ENABLE_MAC_DISABLE_GRAB_ANYWHERE_WITH_TITLEBAR = pysimplegui_user_settings.get(
        MAC_PATCH_DICT["Disable Grab Anywhere with Titlebar"][0],
        MAC_PATCH_DICT["Disable Grab Anywhere with Titlebar"][1],
    )
    ENABLE_MAC_ALPHA_99_PATCH = pysimplegui_user_settings.get(
        MAC_PATCH_DICT["Set Alpha Channel to 0.99 for MacOS >= 12.3"][0],
        MAC_PATCH_DICT["Set Alpha Channel to 0.99 for MacOS >= 12.3"][1],
    )


def _mac_should_apply_notitlebar_patch():
    """
    Uses a combination of the tkinter version number and the setting from the global settings
    to determine if the notitlebar patch should be applied

    :return:    True if should apply the no titlebar patch on the Mac
    :rtype:     (bool)
    """

    if not running_mac():
        return False

    try:
        tver = [int(n) for n in framework_version.split(".")]
        if (
            tver[0] == 8
            and tver[1] == 6
            and tver[2] < 10
            and ENABLE_MAC_NOTITLEBAR_PATCH
        ):
            return True
    except Exception as e:
        warnings.warn(
            "Exception while trying to parse tkinter version {} Error = {}".format(
                framework_version, e
            ),
            UserWarning,
        )

    return False


def _mac_should_set_alpha_to_99():
    if not running_mac():
        return False

    if not ENABLE_MAC_ALPHA_99_PATCH:
        return False

    # ONLY enable this patch for tkinter version 8.6.12
    if framework_version != "8.6.12":
        return False

    # At this point, we're running a Mac and the alpha patch is enabled
    # Final check is to see if Mac OS version is 12.3 or later
    try:
        platform_mac_ver = platform.mac_ver()[0]
        mac_ver = (
            platform_mac_ver.split(".")
            if "." in platform_mac_ver
            else (platform_mac_ver, 0)
        )
        if (int(mac_ver[0]) >= 12 and int(mac_ver[1]) >= 3) or int(mac_ver[0]) >= 13:
            # print("Mac OS Version is {} and patch enabled so applying the patch".format(platform_mac_ver))
            return True
    except Exception as e:
        warnings.warn(
            "_mac_should_seet_alpha_to_99 Exception while trying check mac_ver. Error = {}".format(
                e
            ),
            UserWarning,
        )
        return False

    return False


def main_mac_feature_control():
    """
    Window to set settings that will be used across all PySimpleGUI programs that choose to use them.
    Use set_options to set the path to the folder for all PySimpleGUI settings.

    :return: True if settings were changed
    :rtype:  (bool)
    """

    current_theme = theme()
    theme("dark red")

    layout = [
        [T("Mac PySimpleGUI Feature Control", font="DEFAIULT 18")],
        [T("Use this window to enable / disable features.")],
        [
            T(
                "Unfortunately, on some releases of tkinter on the Mac, there are problems that"
            )
        ],
        [
            T(
                "create the need to enable and disable sets of features. This window facilitates the control."
            )
        ],
        [T("Feature Control / Settings", font="_ 16 bold")],
        [
            T("You are running tkinter version:", font="_ 12 bold"),
            T(framework_version, font="_ 12 bold"),
        ],
    ]

    for key, value in MAC_PATCH_DICT.items():
        layout += [
            [
                Checkbox(
                    key,
                    k=value[0],
                    default=pysimplegui_user_settings.get(value[0], value[1]),
                )
            ]
        ]
    layout += [
        [
            T(
                "Currently the no titlebar patch "
                + ("WILL" if _mac_should_apply_notitlebar_patch() else "WILL NOT")
                + " be applied"
            )
        ],
        [T("The no titlebar patch will ONLY be applied on tkinter versions < 8.6.10")],
    ]
    layout += [[Button("Ok"), Button("Cancel")]]

    window = Window("Mac Feature Control", layout, keep_on_top=True, finalize=True)
    while True:
        event, values = window.read()
        if event in ("Cancel", WIN_CLOSED):
            break
        if event == "Ok":
            for key, value in values.items():
                print("setting {} to {}".format(key, value))
                pysimplegui_user_settings.set(key, value)
            break
    window.close()
    theme(current_theme)







def _global_settings_get_ttk_scrollbar_info():
    """
    This function reads the ttk scrollbar settings from the global PySimpleGUI settings file.
    Each scrollbar setting is stored with a key that's a TUPLE, not a normal string key.
    The settings are for pieces of the scrollbar and their associated piece of the PySimpleGUI theme.

    The whole ttk scrollbar feature is based on mapping parts of the scrollbar to parts of the PySimpleGUI theme.
    That is what the ttk_part_mapping_dict does, maps between the two lists of items.
    For example, the scrollbar arrow color may map to the theme input text color.

    """
    global ttk_part_mapping_dict, DEFAULT_TTK_THEME
    for ttk_part in TTK_SCROLLBAR_PART_LIST:
        value = pysimplegui_user_settings.get(
            json.dumps(("-ttk scroll-", ttk_part)), ttk_part_mapping_dict[ttk_part]
        )
        ttk_part_mapping_dict[ttk_part] = value

    DEFAULT_TTK_THEME = pysimplegui_user_settings.get("-ttk theme-", DEFAULT_TTK_THEME)


def _global_settings_get_watermark_info():
    if (
        not pysimplegui_user_settings.get("-watermark-", False)
        and not Window._watermark_temp_forced
    ):
        Window._watermark = None
        return
    forced = Window._watermark_temp_forced
    prefix_text = pysimplegui_user_settings.get("-watermark text-", "")

    ver_text = (
        " " + version.split(" ", 1)[0]
        if pysimplegui_user_settings.get(
            "-watermark ver-", False if not forced else True
        )
        or forced
        else ""
    )
    framework_ver_text = (
        " Tk " + framework_version
        if pysimplegui_user_settings.get(
            "-watermark framework ver-", False if not forced else True
        )
        or forced
        else ""
    )
    watermark_font = pysimplegui_user_settings.get("-watermark font-", "_ 9 bold")
    # background_color = pysimplegui_user_settings.get('-watermark bg color-', 'window.BackgroundColor')
    user_text = pysimplegui_user_settings.get("-watermark text-", "")
    python_text = " Py {}.{}.{}".format(
        sys.version_info.major, sys.version_info.minor, sys.version_info.micro
    )
    if user_text:
        text = str(user_text)
    else:
        text = prefix_text + ver_text + python_text + framework_ver_text
    Window._watermark = lambda window: Text(
        text, font=watermark_font, background_color=window.BackgroundColor
    )


def main_global_get_screen_snapshot_symcode():
    pysimplegui_user_settings = UserSettings(
        filename=DEFAULT_USER_SETTINGS_PYSIMPLEGUI_FILENAME,
        path=DEFAULT_USER_SETTINGS_PYSIMPLEGUI_PATH,
    )

    settings = pysimplegui_user_settings.read()

    screenshot_keysym = ""
    for i in range(4):
        keysym = settings.get(json.dumps(("-snapshot keysym-", i)), "")
        if keysym:
            screenshot_keysym += "<{}>".format(keysym)

    screenshot_keysym_manual = settings.get("-snapshot keysym manual-", "")

    # print('BINDING INFO!', screenshot_keysym, screenshot_keysym_manual)
    if screenshot_keysym_manual:
        return screenshot_keysym_manual
    elif screenshot_keysym:
        return screenshot_keysym
    return ""


def main_global_pysimplegui_settings_erase():
    """
    *** WARNING ***
    Deletes the PySimpleGUI settings file without asking for verification


    """
    print(
        "********** WARNING - you are deleting your PySimpleGUI settings file **********"
    )
    print("The file being deleted is:", pysimplegui_user_settings.full_filename)


def main_global_pysimplegui_settings():
    """
    Window to set settings that will be used across all PySimpleGUI programs that choose to use them.
    Use set_options to set the path to the folder for all PySimpleGUI settings.

    :return: True if settings were changed
    :rtype:  (bool)
    """
    global DEFAULT_WINDOW_SNAPSHOT_KEY_CODE, ttk_part_mapping_dict, DEFAULT_TTK_THEME

    key_choices = tuple(sorted(tkinter_keysyms))

    settings = pysimplegui_user_settings.read()

    editor_format_dict = {
        "pycharm": "<editor> --line <line> <file>",
        "notepad++": "<editor> -n<line> <file>",
        "sublime": "<editor> <file>:<line>",
        "vim": "<editor> +<line> <file>",
        "wing": "<editor> <file>:<line>",
        "visual studio": '<editor> <file> /command "edit.goto <line>"',
        "atom": "<editor> <file>:<line>",
        "spyder": "<editor> <file>",
        "thonny": "<editor> <file>",
        "pydev": "<editor> <file>:<line>",
        "idle": "<editor> <file>",
    }

    tooltip = (
        "Format strings for some popular editors/IDEs:\n"
        + "PyCharm - <editor> --line <line> <file>\n"
        + "Notepad++ - <editor> -n<line> <file>\n"
        + "Sublime - <editor> <file>:<line>\n"
        + "vim -  <editor> +<line> <file>\n"
        + "wing - <editor> <file>:<line>\n"
        + 'Visual Studio - <editor> <file> /command "edit.goto <line>"\n'
        + "Atom - <editor> <file>:<line>\n"
        + "Spyder - <editor> <file>\n"
        + "Thonny - <editor> <file>\n"
        + "PyDev - <editor> <file>:<line>\n"
        + "IDLE - <editor> <file>\n"
    )

    tooltip_file_explorer = (
        'This is the program you normally use to "Browse" for files\n'
        + 'For Windows this is normally "explorer". On Linux "nemo" is sometimes used.'
    )

    tooltip_theme = (
        'The normal default theme for PySimpleGUI is "Dark Blue 13\n'
        + 'If you do not call theme("theme name") by your program to change the theme, then the default is used.\n'
        + "This setting allows you to set the theme that PySimpleGUI will use for ALL of your programs that\n"
        + "do not set a theme specifically."
    )

    # ------------------------- TTK Tab -------------------------
    ttk_scrollbar_tab_layout = [
        [
            T("Default TTK Theme", font="_ 16"),
            Combo(
                [],
                DEFAULT_TTK_THEME,
                readonly=True,
                size=(20, 10),
                key="-TTK THEME-",
                font="_ 16",
            ),
        ],
        [HorizontalSeparator()],
        [T("TTK Scrollbar Settings", font="_ 16")],
    ]

    t_len = max([len(l) for l in TTK_SCROLLBAR_PART_LIST])
    ttk_layout = [[]]
    for key, item in ttk_part_mapping_dict.items():
        if key in TTK_SCROLLBAR_PART_THEME_BASED_LIST:
            ttk_layout += [
                [
                    T(key, s=t_len, justification="r"),
                    Combo(
                        PSG_THEME_PART_LIST,
                        default_value=settings.get(("-ttk scroll-", key), item),
                        key=("-TTK SCROLL-", key),
                    ),
                ]
            ]
        elif key in (TTK_SCROLLBAR_PART_ARROW_WIDTH, TTK_SCROLLBAR_PART_SCROLL_WIDTH):
            ttk_layout += [
                [
                    T(key, s=t_len, justification="r"),
                    Combo(
                        list(range(100)),
                        default_value=settings.get(("-ttk scroll-", key), item),
                        key=("-TTK SCROLL-", key),
                    ),
                ]
            ]
        elif key == TTK_SCROLLBAR_PART_RELIEF:
            ttk_layout += [
                [
                    T(key, s=t_len, justification="r"),
                    Combo(
                        RELIEF_LIST,
                        default_value=settings.get(("-ttk scroll-", key), item),
                        readonly=True,
                        key=("-TTK SCROLL-", key),
                    ),
                ]
            ]

    ttk_scrollbar_tab_layout += ttk_layout
    ttk_scrollbar_tab_layout += [
        [Button("Reset Scrollbar Settings"), Button("Test Scrollbar Settings")]
    ]
    ttk_tab = Tab("TTK", ttk_scrollbar_tab_layout)

    layout = [
        [
            T(
                "Global PySimpleGUI Settings",
                text_color=theme_button_color()[0],
                background_color=theme_button_color()[1],
                font="_ 18",
                expand_x=True,
                justification="c",
            )
        ]
    ]

    # ------------------------- Interpreter Tab -------------------------

    interpreter_tab = Tab(
        "Python Interpreter",
        [
            [T("Normally leave this blank")],
            [
                T("Command to run a python program:"),
                In(
                    settings.get("-python command-", ""),
                    k="-PYTHON COMMAND-",
                    enable_events=True,
                ),
                FileBrowse(),
            ],
        ],
        font="_ 16",
        expand_x=True,
    )

    # ------------------------- Editor Tab -------------------------

    editor_tab = Tab(
        "Editor Settings",
        [
            [
                T("Command to invoke your editor:"),
                In(
                    settings.get("-editor program-", ""),
                    k="-EDITOR PROGRAM-",
                    enable_events=True,
                ),
                FileBrowse(),
            ],
            [T("String to launch your editor to edit at a particular line #.")],
            [T("Use tags <editor> <file> <line> to specify the string")],
            [T("that will be executed to edit python files using your editor")],
            [
                T("Edit Format String (hover for tooltip)", tooltip=tooltip),
                In(
                    settings.get("-editor format string-", "<editor> <file>"),
                    k="-EDITOR FORMAT-",
                    tooltip=tooltip,
                ),
            ],
        ],
        font="_ 16",
        expand_x=True,
    )

    # ------------------------- Explorer Tab -------------------------

    explorer_tab = Tab(
        "Explorer Program",
        [
            [
                In(
                    settings.get("-explorer program-", ""),
                    k="-EXPLORER PROGRAM-",
                    tooltip=tooltip_file_explorer,
                )
            ]
        ],
        font="_ 16",
        expand_x=True,
        tooltip=tooltip_file_explorer,
    )

    # ------------------------- Snapshots Tab -------------------------

    snapshots_tab = Tab(
        "Window Snapshots",
        [
            [
                Combo(
                    ("",) + key_choices,
                    default_value=settings.get(
                        json.dumps(("-snapshot keysym-", i)), ""
                    ),
                    readonly=True,
                    k=("-SNAPSHOT KEYSYM-", i),
                    s=(None, 30),
                )
                for i in range(4)
            ],
            [
                T("Manually Entered Bind String:"),
                Input(
                    settings.get("-snapshot keysym manual-", ""),
                    k="-SNAPSHOT KEYSYM MANUAL-",
                ),
            ],
            [
                T("Folder to store screenshots:"),
                Push(),
                In(settings.get("-screenshots folder-", ""), k="-SCREENSHOTS FOLDER-"),
                FolderBrowse(),
            ],
            [
                T("Screenshots Filename or Prefix:"),
                Push(),
                In(
                    settings.get("-screenshots filename-", ""),
                    k="-SCREENSHOTS FILENAME-",
                ),
                FileBrowse(),
            ],
            [Checkbox("Auto-number Images", k="-SCREENSHOTS AUTONUMBER-")],
        ],
        font="_ 16",
        expand_x=True,
    )

    # ------------------------- Theme Tab -------------------------

    theme_tab = Tab(
        "Theme",
        [
            [
                T(
                    'Leave blank for "official" PySimpleGUI default theme: {}'.format(
                        OFFICIAL_PYSIMPLEGUI_THEME
                    )
                )
            ],
            [
                T("Default Theme For All Programs:"),
                Combo(
                    [""] + theme_list(),
                    settings.get("-theme-", None),
                    readonly=True,
                    k="-THEME-",
                    tooltip=tooltip_theme,
                ),
                Checkbox(
                    "Always use custom Titlebar",
                    default=pysimplegui_user_settings.get("-custom titlebar-", False),
                    k="-CUSTOM TITLEBAR-",
                ),
            ],
            [
                Frame(
                    "Window Watermarking",
                    [
                        [
                            Checkbox(
                                "Enable Window Watermarking",
                                pysimplegui_user_settings.get("-watermark-", False),
                                k="-WATERMARK-",
                            )
                        ],
                        [
                            T("Prefix Text String:"),
                            Input(
                                pysimplegui_user_settings.get("-watermark text-", ""),
                                k="-WATERMARK TEXT-",
                            ),
                        ],
                        [
                            Checkbox(
                                "PySimpleGUI Version",
                                pysimplegui_user_settings.get("-watermark ver-", False),
                                k="-WATERMARK VER-",
                            )
                        ],
                        [
                            Checkbox(
                                "Framework Version",
                                pysimplegui_user_settings.get(
                                    "-watermark framework ver-", False
                                ),
                                k="-WATERMARK FRAMEWORK VER-",
                            )
                        ],
                        [
                            T("Font:"),
                            Input(
                                pysimplegui_user_settings.get(
                                    "-watermark font-", "_ 9 bold"
                                ),
                                k="-WATERMARK FONT-",
                            ),
                        ],
                        # [T('Background Color:'), Input(pysimplegui_user_settings.get('-watermark bg color-', 'window.BackgroundColor'), k='-WATERMARK BG COLOR-')],
                    ],
                    font="_ 16",
                    expand_x=True,
                )
            ],
        ],
    )

    settings_tab_group = TabGroup(
        [
            [
                theme_tab,
                ttk_tab,
                interpreter_tab,
                explorer_tab,
                editor_tab,
                snapshots_tab,
            ]
        ]
    )
    layout += [[settings_tab_group]]
    # [T('Buttons (Leave Unchecked To Use Default) NOT YET IMPLEMENTED!',  font='_ 16')],
    #      [Checkbox('Always use TTK buttons'), CBox('Always use TK Buttons')],
    layout += [[B("Ok", bind_return_key=True), B("Cancel"), B("Mac Patch Control")]]

    window = Window("Settings", layout, keep_on_top=True, modal=False, finalize=True)

    # fill in the theme list into the Combo element - must do this AFTER the window is created or a tkinter temp window is auto created by tkinter
    ttk_theme_list = ttk.Style().theme_names()

    window["-TTK THEME-"].update(value=DEFAULT_TTK_THEME, values=ttk_theme_list)

    while True:
        event, values = window.read()
        if event in ("Cancel", WIN_CLOSED):
            break
        if event == "Ok":
            new_theme = (
                OFFICIAL_PYSIMPLEGUI_THEME
                if values["-THEME-"] == ""
                else values["-THEME-"]
            )
            pysimplegui_user_settings.set(
                "-editor program-", values["-EDITOR PROGRAM-"]
            )
            pysimplegui_user_settings.set(
                "-explorer program-", values["-EXPLORER PROGRAM-"]
            )
            pysimplegui_user_settings.set(
                "-editor format string-", values["-EDITOR FORMAT-"]
            )
            pysimplegui_user_settings.set(
                "-python command-", values["-PYTHON COMMAND-"]
            )
            pysimplegui_user_settings.set(
                "-custom titlebar-", values["-CUSTOM TITLEBAR-"]
            )
            pysimplegui_user_settings.set("-theme-", new_theme)
            pysimplegui_user_settings.set("-watermark-", values["-WATERMARK-"])
            pysimplegui_user_settings.set(
                "-watermark text-", values["-WATERMARK TEXT-"]
            )
            pysimplegui_user_settings.set("-watermark ver-", values["-WATERMARK VER-"])
            pysimplegui_user_settings.set(
                "-watermark framework ver-", values["-WATERMARK FRAMEWORK VER-"]
            )
            pysimplegui_user_settings.set(
                "-watermark font-", values["-WATERMARK FONT-"]
            )
            # pysimplegui_user_settings.set('-watermark bg color-', values['-WATERMARK BG COLOR-'])

            # TTK SETTINGS
            pysimplegui_user_settings.set("-ttk theme-", values["-TTK THEME-"])
            DEFAULT_TTK_THEME = values["-TTK THEME-"]

            # Snapshots portion
            screenshot_keysym_manual = values["-SNAPSHOT KEYSYM MANUAL-"]
            pysimplegui_user_settings.set(
                "-snapshot keysym manual-", values["-SNAPSHOT KEYSYM MANUAL-"]
            )
            screenshot_keysym = ""
            for i in range(4):
                pysimplegui_user_settings.set(
                    json.dumps(("-snapshot keysym-", i)),
                    values[("-SNAPSHOT KEYSYM-", i)],
                )
                if values[("-SNAPSHOT KEYSYM-", i)]:
                    screenshot_keysym += "<{}>".format(values[("-SNAPSHOT KEYSYM-", i)])
            if screenshot_keysym_manual:
                DEFAULT_WINDOW_SNAPSHOT_KEY_CODE = screenshot_keysym_manual
            elif screenshot_keysym:
                DEFAULT_WINDOW_SNAPSHOT_KEY_CODE = screenshot_keysym

            pysimplegui_user_settings.set(
                "-screenshots folder-", values["-SCREENSHOTS FOLDER-"]
            )
            pysimplegui_user_settings.set(
                "-screenshots filename-", values["-SCREENSHOTS FILENAME-"]
            )

            # TTK Scrollbar portion
            for key, value in values.items():
                if isinstance(key, tuple):
                    if key[0] == "-TTK SCROLL-":
                        pysimplegui_user_settings.set(
                            json.dumps(("-ttk scroll-", key[1])), value
                        )

            # Upgrade Service Settings
            pysimplegui_user_settings.set(
                "-upgrade show only critical-", values["-UPGRADE SHOW ONLY CRITICAL-"]
            )

            theme(new_theme)

            _global_settings_get_ttk_scrollbar_info()
            _global_settings_get_watermark_info()

            window.close()
            return True
        elif event == "-EDITOR PROGRAM-":
            for key in editor_format_dict.keys():
                if key in values["-EDITOR PROGRAM-"].lower():
                    window["-EDITOR FORMAT-"].update(value=editor_format_dict[key])
        elif event == "Mac Patch Control":
            main_mac_feature_control()
            # re-read the settings in case they changed
            _read_mac_global_settings()
        elif event == "Reset Scrollbar Settings":
            ttk_part_mapping_dict = copy.copy(DEFAULT_TTK_PART_MAPPING_DICT)
            for key, item in ttk_part_mapping_dict.items():
                window[("-TTK SCROLL-", key)].update(item)
        elif event == "Test Scrollbar Settings":
            for ttk_part in TTK_SCROLLBAR_PART_LIST:
                value = values[("-TTK SCROLL-", ttk_part)]
                ttk_part_mapping_dict[ttk_part] = value
            DEFAULT_TTK_THEME = values["-TTK THEME-"]
            for i in range(100):
                Print(i, keep_on_top=True)
            Print("Close this window to continue...", keep_on_top=True)

    window.close()
    # In case some of the settings were modified and tried out, reset the ttk info to be what's in the config file
    style = ttk.Style(Window.hidden_master_root)
    _change_ttk_theme(style, DEFAULT_TTK_THEME)
    _global_settings_get_ttk_scrollbar_info()

    return False




def main_sdk_help():
    """
    Display a window that will display the docstrings for each PySimpleGUI Element and the Window object

    """
    online_help_links = {
        "Button": r"https://PySimpleGUI.org/en/latest/call%20reference/#button-element",
        "ButtonMenu": r"https://PySimpleGUI.org/en/latest/call%20reference/#buttonmenu-element",
        "Canvas": r"https://PySimpleGUI.org/en/latest/call%20reference/#canvas-element",
        "Checkbox": r"https://PySimpleGUI.org/en/latest/call%20reference/#checkbox-element",
        "Column": r"https://PySimpleGUI.org/en/latest/call%20reference/#column-element",
        "Combo": r"https://PySimpleGUI.org/en/latest/call%20reference/#combo-element",
        "Frame": r"https://PySimpleGUI.org/en/latest/call%20reference/#frame-element",
        "Graph": r"https://PySimpleGUI.org/en/latest/call%20reference/#graph-element",
        "HorizontalSeparator": r"https://PySimpleGUI.org/en/latest/call%20reference/#horizontalseparator-element",
        "Image": r"https://PySimpleGUI.org/en/latest/call%20reference/#image-element",
        "Input": r"https://PySimpleGUI.org/en/latest/call%20reference/#input-element",
        "Listbox": r"https://PySimpleGUI.org/en/latest/call%20reference/#listbox-element",
        "Menu": r"https://PySimpleGUI.org/en/latest/call%20reference/#menu-element",
        "MenubarCustom": r"https://PySimpleGUI.org/en/latest/call%20reference/#menubarcustom-element",
        "Multiline": r"https://PySimpleGUI.org/en/latest/call%20reference/#multiline-element",
        "OptionMenu": r"https://PySimpleGUI.org/en/latest/call%20reference/#optionmenu-element",
        "Output": r"https://PySimpleGUI.org/en/latest/call%20reference/#output-element",
        "Pane": r"https://PySimpleGUI.org/en/latest/call%20reference/#pane-element",
        "ProgressBar": r"https://PySimpleGUI.org/en/latest/call%20reference/#progressbar-element",
        "Radio": r"https://PySimpleGUI.org/en/latest/call%20reference/#radio-element",
        "Slider": r"https://PySimpleGUI.org/en/latest/call%20reference/#slider-element",
        "Spin": r"https://PySimpleGUI.org/en/latest/call%20reference/#spin-element",
        "StatusBar": r"https://PySimpleGUI.org/en/latest/call%20reference/#statusbar-element",
        "Tab": r"https://PySimpleGUI.org/en/latest/call%20reference/#tab-element",
        "TabGroup": r"https://PySimpleGUI.org/en/latest/call%20reference/#tabgroup-element",
        "Table": r"https://PySimpleGUI.org/en/latest/call%20reference/#table-element",
        "Text": r"https://PySimpleGUI.org/en/latest/call%20reference/#text-element",
        "Titlebar": r"https://PySimpleGUI.org/en/latest/call%20reference/#titlebar-element",
        "Tree": r"https://PySimpleGUI.org/en/latest/call%20reference/#tree-element",
        "VerticalSeparator": r"https://PySimpleGUI.org/en/latest/call%20reference/#verticalseparator-element",
        "Window": r"https://PySimpleGUI.org/en/latest/call%20reference/#window",
    }

    NOT_AN_ELEMENT = "Not An Element"
    element_classes = Element.__subclasses__()
    element_names = {element.__name__: element for element in element_classes}
    element_names["Window"] = Window
    element_classes.append(Window)
    element_arg_default_dict, element_arg_default_dict_update = {}, {}
    vars3 = [m for m in inspect.getmembers(sys.modules[__name__])]

    functions = [
        m for m in inspect.getmembers(sys.modules[__name__], inspect.isfunction)
    ]
    functions_names_lower = [f for f in functions if f[0][0].islower()]
    functions_names_upper = [f for f in functions if f[0][0].isupper()]
    functions_names = sorted(functions_names_lower) + sorted(functions_names_upper)

    for element in element_classes:
        # Build info about init method
        args = inspect.getfullargspec(element.__init__).args[1:]
        defaults = inspect.getfullargspec(element.__init__).defaults
        # print('------------- {element}----------')
        # print(args)
        # print(defaults)
        if len(args) != len(defaults):
            diff = len(args) - len(defaults)
            defaults = ("NO DEFAULT",) * diff + defaults
        args_defaults = []
        for i, a in enumerate(args):
            args_defaults.append((a, defaults[i]))
        element_arg_default_dict[element.__name__] = args_defaults

        # Build info about update method
        try:
            args = inspect.getfullargspec(element.update).args[1:]
            defaults = inspect.getfullargspec(element.update).defaults
            if args is None or defaults is None:
                element_arg_default_dict_update[element.__name__] = (("", ""),)
                continue
            if len(args) != len(defaults):
                diff = len(args) - len(defaults)
                defaults = ("NO DEFAULT",) * diff + defaults
            args_defaults = []
            for i, a in enumerate(args):
                args_defaults.append((a, defaults[i]))
            element_arg_default_dict_update[element.__name__] = (
                args_defaults if len(args_defaults) else (("", ""),)
            )
        except Exception as e:
            pass

    # Add on the pseudo-elements
    element_names["MenubarCustom"] = MenubarCustom
    element_names["Titlebar"] = Titlebar

    buttons = [
        [B(e, pad=(0, 0), size=(22, 1), font="Courier 10")]
        for e in sorted(element_names.keys())
    ]
    buttons += [[B("Func Search", pad=(0, 0), size=(22, 1), font="Courier 10")]]
    button_col = Col(buttons, vertical_alignment="t")
    mline_col = Column(
        [
            [
                Multiline(
                    size=(100, 46),
                    key="-ML-",
                    write_only=True,
                    reroute_stdout=True,
                    font="Courier 10",
                    expand_x=True,
                    expand_y=True,
                )
            ],
            [
                T(
                    size=(80, 1),
                    font="Courier 10 underline",
                    k="-DOC LINK-",
                    enable_events=True,
                )
            ],
        ],
        pad=(0, 0),
        expand_x=True,
        expand_y=True,
        vertical_alignment="t",
    )
    layout = [[button_col, mline_col]]
    layout += [
        [
            CBox("Summary Only", enable_events=True, k="-SUMMARY-"),
            CBox("Display Only PEP8 Functions", default=True, k="-PEP8-"),
        ]
    ]
    # layout = [[Column(layout, scrollable=True, p=0, expand_x=True, expand_y=True, vertical_alignment='t'), Sizegrip()]]
    layout += [[Button("Exit", size=(15, 1)), Sizegrip()]]

    window = Window(
        "SDK API Call Reference",
        layout,
        resizable=True,
        use_default_focus=False,
        keep_on_top=True,
        icon=EMOJI_BASE64_THINK,
        finalize=True,
        right_click_menu=MENU_RIGHT_CLICK_EDITME_EXIT,
    )
    window["-DOC LINK-"].set_cursor("hand1")
    online_help_link = ""
    ml = window["-ML-"]
    current_element = ""
    try:
        while True:  # Event Loop
            event, values = window.read()
            if event in (WIN_CLOSED, "Exit"):
                break
            if event == "-DOC LINK-":
                if webbrowser_available and online_help_link:
                    webbrowser.open_new_tab(online_help_link)
            if event == "-SUMMARY-":
                event = current_element

            if event in element_names.keys():
                current_element = event
                window["-ML-"].update("")
                online_help_link = online_help_links.get(event, "")
                window["-DOC LINK-"].update(online_help_link)
                if not values["-SUMMARY-"]:
                    elem = element_names[event]
                    ml.print(pydoc.help(elem))
                    # print the aliases for the class
                    ml.print("\n--- Shortcut Aliases for Class ---")
                    for v in vars3:
                        if elem == v[1] and elem.__name__ != v[0]:
                            print(v[0])
                    ml.print("\n--- Init Parms ---")
                else:
                    elem = element_names[event]
                    if inspect.isfunction(elem):
                        ml.print(
                            "Not a class...It is a function",
                            background_color="red",
                            text_color="white",
                        )
                    else:
                        element_methods = [
                            m[0]
                            for m in inspect.getmembers(Element, inspect.isfunction)
                            if not m[0].startswith("_") and not m[0][0].isupper()
                        ]
                        methods = inspect.getmembers(elem, inspect.isfunction)
                        methods = [
                            m[0]
                            for m in methods
                            if not m[0].startswith("_") and not m[0][0].isupper()
                        ]

                        unique_methods = [
                            m
                            for m in methods
                            if m not in element_methods and not m[0][0].isupper()
                        ]

                        properties = inspect.getmembers(
                            elem, lambda o: isinstance(o, property)
                        )
                        properties = [
                            p[0] for p in properties if not p[0].startswith("_")
                        ]
                        ml.print(
                            "--- Methods ---",
                            background_color="red",
                            text_color="white",
                        )
                        ml.print("\n".join(methods))
                        ml.print(
                            "--- Properties ---",
                            background_color="red",
                            text_color="white",
                        )
                        ml.print("\n".join(properties))
                        if elem != NOT_AN_ELEMENT:
                            if issubclass(elem, Element):
                                ml.print(
                                    "Methods Unique to This Element",
                                    background_color="red",
                                    text_color="white",
                                )
                                ml.print("\n".join(unique_methods))
                        ml.print(
                            "========== Init Parms ==========",
                            background_color="#FFFF00",
                            text_color="black",
                        )
                        elem_text_name = event
                        for parm, default in element_arg_default_dict[elem_text_name]:
                            ml.print("{:18}".format(parm), end=" = ")
                            ml.print(default, end=",\n")
                        if elem_text_name in element_arg_default_dict_update:
                            ml.print(
                                "========== Update Parms ==========",
                                background_color="#FFFF00",
                                text_color="black",
                            )
                            for parm, default in element_arg_default_dict_update[
                                elem_text_name
                            ]:
                                ml.print("{:18}".format(parm), end=" = ")
                                ml.print(default, end=",\n")
                ml.set_vscroll_position(0)  # scroll to top of multoline
            elif event == "Func Search":
                search_string = popup_get_text(
                    "Search for this in function list:", keep_on_top=True
                )
                if search_string is not None:
                    online_help_link = ""
                    window["-DOC LINK-"].update("")
                    ml.update("")
                    for f_entry in functions_names:
                        f = f_entry[0]
                        if search_string in f.lower() and not f.startswith("_"):
                            if (values["-PEP8-"] and not f[0].isupper()) or not values[
                                "-PEP8-"
                            ]:
                                if values["-SUMMARY-"]:
                                    ml.print(f)
                                else:
                                    ml.print(
                                        "=========== " + f + "===========",
                                        background_color="#FFFF00",
                                        text_color="black",
                                    )
                                    ml.print(pydoc.help(f_entry[1]))
                ml.set_vscroll_position(0)  # scroll to top of multoline
    except Exception as e:
        _error_popup_with_traceback("Exception in SDK reference", e)
    window.close()



def _main_switch_theme():
    layout = [
        [Text("Click a look and feel color to see demo window")],
        [Listbox(values=theme_list(), size=(20, 20), key="-LIST-")],
        [Button("Choose"), Button("Cancel")],
    ]

    window = Window("Change Themes", layout)

    event, values = window.read(close=True)

    if event == "Choose":
        theme_name = values["-LIST-"][0]
        theme(theme_name)




def _create_main_window():
    """
    Creates the main test harness window.

    :return: The test window
    :rtype:  Window
    """

    # theme('dark blue 3')
    # theme('dark brown 2')
    # theme('dark')
    # theme('dark red')
    # theme('Light Green 6')
    # theme('Dark Grey 8')

    tkversion = tkinter.TkVersion
    tclversion = tkinter.TclVersion
    tclversion_detailed = tkinter.Tcl().eval("info patchlevel")

    print("Starting up PySimpleGUI Diagnostic & Help System")
    print("PySimpleGUI long version = ", version)
    print(
        "PySimpleGUI Version ",
        ver,
        "\ntcl ver = {}".format(tclversion),
        "tkinter version = {}".format(tkversion),
        "\nPython Version {}".format(sys.version),
    )
    print("tcl detailed version = {}".format(tclversion_detailed))
    print("PySimpleGUI.py location", __file__)
    # ------ Menu Definition ------ #
    menu_def = [
        ["&File", ["!&Open", "&Save::savekey", "---", "&Properties", "E&xit"]],
        [
            "&Edit",
            ["&Paste", ["Special", "Normal", "!Disabled"], "Undo"],
        ],
        ["&Debugger", ["Popout", "Launch Debugger"]],
        ["!&Disabled", ["Popout", "Launch Debugger"]],
        ["&Toolbar", ["Command &1", "Command &2", "Command &3", "Command &4"]],
        ["&Help", "&About..."],
    ]

    button_menu_def = [
        "unused",
        ["&Paste", ["Special", "Normal", "!Disabled"], "Undo", "Exit"],
    ]
    treedata = TreeData()

    treedata.Insert(
        "",
        "_A_",
        "Tree Item 1",
        [1, 2, 3],
    )
    treedata.Insert(
        "",
        "_B_",
        "B",
        [4, 5, 6],
    )
    treedata.Insert(
        "_A_",
        "_A1_",
        "Sub Item 1",
        ["can", "be", "anything"],
    )
    treedata.Insert(
        "",
        "_C_",
        "C",
        [],
    )
    treedata.Insert(
        "_C_",
        "_C1_",
        "C1",
        ["or"],
    )
    treedata.Insert("_A_", "_A2_", "Sub Item 2", [None, None])
    treedata.Insert("_A1_", "_A3_", "A30", ["getting deep"])
    treedata.Insert("_C_", "_C2_", "C2", ["nothing", "at", "all"])

    for i in range(100):
        treedata.Insert("_C_", i, i, [])

    frame1 = [
        [
            Input("Input Text", size=(25, 1)),
        ],
        [Multiline(size=(30, 5), default_text="Multiline Input")],
    ]

    frame2 = [
        # [ProgressBar(100, bar_color=('red', 'green'), orientation='h')],
        [
            Listbox(
                ["Listbox 1", "Listbox 2", "Listbox 3"],
                select_mode=SELECT_MODE_EXTENDED,
                size=(20, 5),
                no_scrollbar=True,
            ),
            Spin([1, 2, 3, "a", "b", "c"], initial_value="a", size=(4, 3), wrap=True),
        ],
        [
            Combo(
                ["Combo item %s" % i for i in range(5)],
                size=(20, 3),
                default_value="Combo item 2",
                key="-COMBO1-",
            )
        ],
        [
            Combo(
                ["Combo item %s" % i for i in range(5)],
                size=(20, 3),
                font="Courier 14",
                default_value="Combo item 2",
                key="-COMBO2-",
            )
        ],
        # [Combo(['Combo item 1', 2,3,4], size=(20, 3), readonly=False, text_color='blue', background_color='red', key='-COMBO2-')],
    ]

    frame3 = [
        [Checkbox("Checkbox1", True, k="-CB1-"), Checkbox("Checkbox2", k="-CB2-")],
        [
            Radio("Radio Button1", 1, key="-R1-"),
            Radio("Radio Button2", 1, default=True, key="-R2-", tooltip="Radio 2"),
        ],
        [T("", size=(1, 4))],
    ]

    frame4 = [
        [
            Slider(
                range=(0, 100),
                orientation="v",
                size=(7, 15),
                default_value=40,
                key="-SLIDER1-",
            ),
            Slider(
                range=(0, 100),
                orientation="h",
                size=(11, 15),
                default_value=40,
                key="-SLIDER2-",
            ),
        ],
    ]
    matrix = [[str(x * y) for x in range(1, 5)] for y in range(1, 8)]

    frame5 = [
        vtop(
            [
                Table(
                    values=matrix,
                    headings=matrix[0],
                    auto_size_columns=False,
                    display_row_numbers=True,
                    change_submits=False,
                    justification="right",
                    header_border_width=4,
                    # header_relief=RELIEF_GROOVE,
                    num_rows=10,
                    alternating_row_color="lightblue",
                    key="-TABLE-",
                    col_widths=[5, 5, 5, 5],
                ),
                Tree(
                    data=treedata,
                    headings=["col1", "col2", "col3"],
                    col_widths=[5, 5, 5, 5],
                    change_submits=True,
                    auto_size_columns=False,
                    header_border_width=4,
                    # header_relief=RELIEF_GROOVE,
                    num_rows=8,
                    col0_width=8,
                    key="-TREE-",
                    show_expanded=True,
                ),
            ]
        )
    ]
    frame7 = [
        [
            Image(EMOJI_BASE64_HAPPY_HEARTS, enable_events=True, k="-EMOJI-HEARTS-"),
            T("Do you"),
            Image(HEART_3D_BASE64, subsample=3, enable_events=True, k="-HEART-"),
            T("so far?"),
        ],
        [
            T(
                'Want to be taught PySimpleGUI?\nThen maybe the "Official PySimpleGUI Course" on Udemy is for you.'
            )
        ],
        [
            B(image_data=UDEMY_ICON, enable_events=True, k="-UDEMY-"),
            T("Check docs, announcements, easter eggs on this page for coupons."),
        ],
    ]

    pop_test_tab_layout = [
        [Image(EMOJI_BASE64_HAPPY_IDEA), T("Popup tests? Good idea!")],
        [
            B("Popup", k="P "),
            B("No Titlebar", k="P NoTitle"),
            B("Not Modal", k="P NoModal"),
            B("Non Blocking", k="P NoBlock"),
            B("Auto Close", k="P AutoClose"),
        ],
        [T('"Get" popups too!')],
        [B("Get File"), B("Get Folder"), B("Get Date"), B("Get Text")],
    ]

    GRAPH_SIZE = (500, 200)
    graph_elem = Graph(GRAPH_SIZE, (0, 0), GRAPH_SIZE, key="+GRAPH+")

    frame6 = [[VPush()], [graph_elem]]

    themes_tab_layout = [
        [
            T(
                "You can see a preview of the themes, the color swatches, or switch themes for this window"
            )
        ],
        [
            T(
                "If you want to change the default theme for PySimpleGUI, use the Global Settings"
            )
        ],
        [B("Themes"), B("Theme Swatches"), B("Switch Themes")],
    ]

    upgrade_recommendation_tab_layout = [
        [T("Latest Recommendation and Announcements For You", font="_ 14")],
        [
            T("Severity Level of Update:"),
            T(pysimplegui_user_settings.get("-severity level-", "")),
        ],
        [
            T("Recommended Version To Upgrade To:"),
            T(pysimplegui_user_settings.get("-upgrade recommendation-", "")),
        ],
        [T(pysimplegui_user_settings.get("-upgrade message 1-", ""))],
        [T(pysimplegui_user_settings.get("-upgrade message 2-", ""))],
        [
            Checkbox(
                "Show Only Critical Messages",
                default=pysimplegui_user_settings.get(
                    "-upgrade show only critical-", False
                ),
                key="-UPGRADE SHOW ONLY CRITICAL-",
                enable_events=True,
            )
        ],
        [
            Button("Show Notification Again"),
        ],
    ]
    tab_upgrade = Tab("Upgrade\n", upgrade_recommendation_tab_layout, expand_x=True)

    tab1 = Tab("Graph\n", frame6, tooltip="Graph is in here", title_color="red")
    tab2 = Tab(
        "CB, Radio\nList, Combo",
        [
            [
                Frame(
                    "Multiple Choice Group",
                    frame2,
                    title_color="#FFFFFF",
                    tooltip="Checkboxes, radio buttons, etc",
                    vertical_alignment="t",
                ),
                Frame(
                    "Binary Choice Group",
                    frame3,
                    title_color="#FFFFFF",
                    tooltip="Binary Choice",
                    vertical_alignment="t",
                ),
            ]
        ],
    )
    # tab3 = Tab('Table and Tree', [[Frame('Structured Data Group', frame5, title_color='red', element_justification='l')]], tooltip='tab 3', title_color='red', )
    tab3 = Tab(
        "Table &\nTree",
        [[Column(frame5, element_justification="l", vertical_alignment="t")]],
        tooltip="tab 3",
        title_color="red",
        k="-TAB TABLE-",
    )
    tab4 = Tab(
        "Sliders\n",
        [[Frame("Variable Choice Group", frame4, title_color="blue")]],
        tooltip="tab 4",
        title_color="red",
        k="-TAB VAR-",
    )
    tab5 = Tab(
        "Input\nMultiline",
        [[Frame("TextInput", frame1, title_color="blue")]],
        tooltip="tab 5",
        title_color="red",
        k="-TAB TEXT-",
    )
    tab6 = Tab("Course or\nSponsor", frame7, k="-TAB SPONSOR-")
    tab7 = Tab("Popups\n", pop_test_tab_layout, k="-TAB POPUP-")
    tab8 = Tab("Themes\n", themes_tab_layout, k="-TAB THEMES-")

    def VerLine(version, description, justification="r", size=(40, 1)):
        return [
            T(
                version,
                justification=justification,
                font="Any 12",
                text_color="yellow",
                size=size,
                pad=(0, 0),
            ),
            T(description, font="Any 12", pad=(0, 0)),
        ]

    layout_top = Column(
        [
            [
                Image(
                    EMOJI_BASE64_HAPPY_BIG_SMILE,
                    enable_events=True,
                    key="-LOGO-",
                    tooltip="This is PySimpleGUI logo",
                ),
                Image(
                    data=DEFAULT_BASE64_LOADING_GIF, enable_events=True, key="-IMAGE-"
                ),
                Text(
                    "PySimpleGUI Test Harness",
                    font="ANY 14",
                    tooltip="My tooltip",
                    key="-TEXT1-",
                ),
            ],
            VerLine(ver, "PySimpleGUI Version") + [Image(HEART_3D_BASE64, subsample=4)],
            # VerLine('{}/{}'.format(tkversion, tclversion), 'TK/TCL Versions'),
            VerLine(tclversion_detailed, "detailed tkinter version"),
            VerLine(
                os.path.dirname(os.path.abspath(__file__)),
                "PySimpleGUI Location",
                size=(40, None),
            ),
            VerLine(sys.executable, "Python Executable"),
            VerLine(sys.version, "Python Version", size=(40, 2))
            + [
                Image(
                    PYTHON_COLORED_HEARTS_BASE64,
                    subsample=3,
                    k="-PYTHON HEARTS-",
                    enable_events=True,
                )
            ],
        ],
        pad=0,
    )

    layout_bottom = [
        [
            B(SYMBOL_DOWN, pad=(0, 0), k="-HIDE TABS-"),
            pin(
                Col(
                    [
                        [
                            TabGroup(
                                [
                                    [
                                        tab1,
                                        tab2,
                                        tab3,
                                        tab6,
                                        tab4,
                                        tab5,
                                        tab7,
                                        tab8,
                                        tab_upgrade,
                                    ]
                                ],
                                key="-TAB_GROUP-",
                            )
                        ]
                    ],
                    k="-TAB GROUP COL-",
                )
            ),
        ],
        [
            B("Button", highlight_colors=("yellow", "red"), pad=(1, 0)),
            B(
                "ttk Button",
                use_ttk_buttons=True,
                tooltip="This is a TTK Button",
                pad=(1, 0),
            ),
            B(
                "See-through Mode",
                tooltip="Make the background transparent",
                pad=(1, 0),
            ),
            # B('Upgrade PySimpleGUI from GitHub', button_color='white on red', key='-INSTALL-',pad=(1, 0)),
            B(
                "Global Settings",
                tooltip="Settings across all PySimpleGUI programs",
                pad=(1, 0),
            ),
            B("Exit", tooltip="Exit button", pad=(1, 0)),
        ],
        # [B(image_data=ICON_BUY_ME_A_COFFEE,pad=(1, 0), key='-COFFEE-'),
        [
            B(image_data=UDEMY_ICON, pad=(1, 0), key="-UDEMY-"),
            B("SDK Reference", pad=(1, 0)),
            B("Open GitHub Issue", pad=(1, 0)),
            B("Versions for GitHub", pad=(1, 0)),
            ButtonMenu(
                "ButtonMenu",
                button_menu_def,
                pad=(1, 0),
                key="-BMENU-",
                tearoff=True,
                disabled_text_color="yellow",
            ),
        ],
    ]

    layout = [[]]

    if not theme_use_custom_titlebar():
        layout += [
            [
                Menu(
                    menu_def,
                    key="-MENU-",
                    font="Courier 15",
                    background_color="red",
                    text_color="white",
                    disabled_text_color="yellow",
                    tearoff=True,
                )
            ]
        ]
    else:
        layout += [
            [
                MenubarCustom(
                    menu_def,
                    key="-MENU-",
                    font="Courier 15",
                    bar_background_color=theme_background_color(),
                    bar_text_color=theme_text_color(),
                    background_color="red",
                    text_color="white",
                    disabled_text_color="yellow",
                )
            ]
        ]

    layout += [
        [layout_top]
        + [ProgressBar(max_value=800, size=(20, 25), orientation="v", key="+PROGRESS+")]
    ]
    layout += layout_bottom

    window = Window(
        "PySimpleGUI Main Test Harness",
        layout,
        # font=('Helvetica', 18),
        # background_color='black',
        right_click_menu=[
            "&Right",
            ["Right", "Edit Me", "!&Click", "&Menu", "E&xit", "Properties"],
        ],
        # transparent_color= '#9FB8AD',
        resizable=True,
        keep_on_top=False,
        element_justification="left",  # justify contents to the left
        metadata="My window metadata",
        finalize=True,
        # grab_anywhere=True,
        enable_close_attempted_event=True,
        modal=False,
        # ttk_theme=THEME_CLASSIC,
        # scaling=2,
        # icon=PSG_DEBUGGER_LOGO,
        # icon=PSGDebugLogo,
    )
    # window['-SPONSOR-'].set_cursor(cursor='hand2')
    window._see_through = False
    return window



def main():
    """
    The PySimpleGUI "Test Harness".  This is meant to be a super-quick test of the Elements.
    """
    forced_modal = DEFAULT_MODAL_WINDOWS_FORCED
    # set_options(force_modal_windows=True)
    window = _create_main_window()
    set_options(keep_on_top=True)
    graph_elem = window["+GRAPH+"]
    i = 0
    graph_figures = []
    # Don't use the debug window
    # Print('', location=(0, 0), font='Courier 10', size=(100, 20), grab_anywhere=True)
    # print(window.element_list())
    while True:  # Event Loop
        event, values = window.read(timeout=5)
        if event != TIMEOUT_KEY:
            print(event, values)
            # Print(event, text_color='white', background_color='red', end='')
            # Print(values)
        if (
            event == WIN_CLOSED
            or event == WIN_CLOSE_ATTEMPTED_EVENT
            or event == "Exit"
            or (event == "-BMENU-" and values["-BMENU-"] == "Exit")
        ):
            break
        if i < graph_elem.CanvasSize[0]:
            x = i % graph_elem.CanvasSize[0]
            fig = graph_elem.draw_line(
                (x, 0),
                (x, random.randint(0, graph_elem.CanvasSize[1])),
                width=1,
                color="#{:06x}".format(random.randint(0, 0xFFFFFF)),
            )
            graph_figures.append(fig)
        else:
            x = graph_elem.CanvasSize[0]
            graph_elem.move(-1, 0)
            fig = graph_elem.draw_line(
                (x, 0),
                (x, random.randint(0, graph_elem.CanvasSize[1])),
                width=1,
                color="#{:06x}".format(random.randint(0, 0xFFFFFF)),
            )
            graph_figures.append(fig)
            graph_elem.delete_figure(graph_figures[0])
            del graph_figures[0]
        window["+PROGRESS+"].UpdateBar(i % 800)
        window.Element("-IMAGE-").UpdateAnimation(
            DEFAULT_BASE64_LOADING_GIF, time_between_frames=50
        )
        if event == "Button":
            window.Element("-TEXT1-").SetTooltip("NEW TEXT")
            window.Element("-MENU-").Update(visible=True)
        elif event == "Popout":
            show_debugger_popout_window()
        elif event == "Launch Debugger":
            show_debugger_window()
        elif event == "About...":
            popup(
                "About this program...",
                "You are looking at the test harness for the PySimpleGUI program",
                version,
                keep_on_top=True,
                image=DEFAULT_BASE64_ICON,
            )
        elif event.startswith("See"):
            window._see_through = not window._see_through
            window.set_transparent_color(
                theme_background_color() if window._see_through else ""
            )
        elif event == "Popup":
            popup("This is your basic popup", keep_on_top=True)
        elif event == "Get File":
            popup_scrolled("Returned:", popup_get_file("Get File", keep_on_top=True))
        elif event == "Get Folder":
            popup_scrolled(
                "Returned:", popup_get_folder("Get Folder", keep_on_top=True)
            )
        elif event == "Get Date":
            popup_scrolled("Returned:", popup_get_date(keep_on_top=True))
        elif event == "Get Text":
            popup_scrolled(
                "Returned:", popup_get_text("Enter some text", keep_on_top=True)
            )

        elif event in ("-EMOJI-HEARTS-", "-HEART-", "-PYTHON HEARTS-"):
            popup_scrolled(
                "Oh look!  It's a Udemy discount coupon!",
                "522B20BF5EF123C4AB30",
                "A personal message from Mike -- thank you so very much for supporting PySimpleGUI!",
                title="Udemy Coupon",
                image=EMOJI_BASE64_MIKE,
                keep_on_top=True,
            )
        elif event == "Themes":
            search_string = popup_get_text(
                "Enter a search term or leave blank for all themes",
                "Show Available Themes",
                keep_on_top=True,
            )
            if search_string is not None:
                theme_previewer(search_string=search_string)
        elif event == "Theme Swatches":
            theme_previewer_swatches()
        elif event == "Switch Themes":
            window.close()
            _main_switch_theme()
            window = _create_main_window()
            graph_elem = window["+GRAPH+"]
        elif event == "-HIDE TABS-":
            window["-TAB GROUP COL-"].update(
                visible=window["-TAB GROUP COL-"].metadata == True
            )
            window["-TAB GROUP COL-"].metadata = not window["-TAB GROUP COL-"].metadata
            window["-HIDE TABS-"].update(
                text=SYMBOL_UP if window["-TAB GROUP COL-"].metadata else SYMBOL_DOWN
            )
        elif event == "SDK Reference":
            main_sdk_help()
        elif event == "Global Settings":
            if main_global_pysimplegui_settings():
                theme(
                    pysimplegui_user_settings.get("-theme-", OFFICIAL_PYSIMPLEGUI_THEME)
                )
                window.close()
                window = _create_main_window()
                graph_elem = window["+GRAPH+"]
            else:
                Window("", layout=[[Multiline()]], alpha_channel=0).read(
                    timeout=1, close=True
                )
        elif event.startswith("P "):
            if event == "P ":
                popup("Normal Popup - Modal", keep_on_top=True)
            elif event == "P NoTitle":
                popup_no_titlebar("No titlebar", keep_on_top=True)
            elif event == "P NoModal":
                set_options(force_modal_windows=False)
                popup(
                    "Normal Popup - Not Modal",
                    "You can interact with main window menubar ",
                    "but will have no effect immediately",
                    "button clicks will happen after you close this popup",
                    modal=False,
                    keep_on_top=True,
                )
                set_options(force_modal_windows=forced_modal)
            elif event == "P NoBlock":
                popup_non_blocking(
                    "Non-blocking",
                    "The background window should still be running",
                    keep_on_top=True,
                )
            elif event == "P AutoClose":
                popup_auto_close(
                    "Will autoclose in 3 seconds",
                    auto_close_duration=3,
                    keep_on_top=True,
                )
        elif event == "Versions for GitHub":
            main_get_debug_data()
        elif event == "Edit Me":
            execute_editor(__file__)
        elif event == "Open GitHub Issue":
            window.minimize()
            main_open_github_issue()
            window.normal()

        elif event == "-UPGRADE SHOW ONLY CRITICAL-":
            if not running_trinket():
                pysimplegui_user_settings.set(
                    "-upgrade show only critical-",
                    values["-UPGRADE SHOW ONLY CRITICAL-"],
                )

        i += 1
        # _refresh_debugger()
    print("event = ", event)
    window.close()
    set_options(force_modal_windows=forced_modal)





def show_debugger_window(location=(None, None), *args):
    """
    Shows the large main debugger window
    :param location: Locations (x,y) on the screen to place upper left corner of the window
    :type location:  (int, int)
    :return:         None
    :rtype:          None
    """
    if _Debugger.debugger is None:
        _Debugger.debugger = _Debugger()
    debugger = _Debugger.debugger
    frame = inspect.currentframe()
    prev_frame = inspect.currentframe().f_back
    # frame, *others = inspect.stack()[1]
    try:
        debugger.locals = frame.f_back.f_locals
        debugger.globals = frame.f_back.f_globals
    finally:
        del frame

    if not debugger.watcher_window:
        debugger.watcher_window = debugger._build_main_debugger_window(
            location=location
        )
    return True


def show_debugger_popout_window(location=(None, None), *args):
    """
    Shows the smaller "popout" window.  Default location is the upper right corner of your screen

    :param location: Locations (x,y) on the screen to place upper left corner of the window
    :type location:  (int, int)
    :return:         None
    :rtype:          None
    """
    if _Debugger.debugger is None:
        _Debugger.debugger = _Debugger()
    debugger = _Debugger.debugger
    frame = inspect.currentframe()
    prev_frame = inspect.currentframe().f_back
    # frame = inspect.getframeinfo(prev_frame)
    # frame, *others = inspect.stack()[1]
    try:
        debugger.locals = frame.f_back.f_locals
        debugger.globals = frame.f_back.f_globals
    finally:
        del frame
    if debugger.popout_window:
        debugger.popout_window.Close()
        debugger.popout_window = None
    debugger._build_floating_window(location=location)


def _refresh_debugger():
    """
    Refreshes the debugger windows. USERS should NOT be calling this function. Within PySimpleGUI it is called for the USER every time the Window.Read function is called.

    :return: return code False if user closed the main debugger window.
    :rtype:  (bool)
    """
    if _Debugger.debugger is None:
        _Debugger.debugger = _Debugger()
    debugger = _Debugger.debugger
    Window._read_call_from_debugger = True
    rc = None
    # frame = inspect.currentframe()
    # frame = inspect.currentframe().f_back

    frame, *others = inspect.stack()[1]
    try:
        debugger.locals = frame.f_back.f_locals
        debugger.globals = frame.f_back.f_globals
    finally:
        del frame
    if debugger.popout_window:
        rc = debugger._refresh_floating_window()
    if debugger.watcher_window:
        rc = debugger._refresh_main_debugger_window(debugger.locals, debugger.globals)
    Window._read_call_from_debugger = False
    return rc


def _debugger_window_is_open():
    """
    Determines if one of the debugger window is currently open
    :return: returns True if the popout window or the main debug window is open
    :rtype: (bool)
    """

    if _Debugger.debugger is None:
        return False
    debugger = _Debugger.debugger
    if debugger.popout_window or debugger.watcher_window:
        return True
    return False





def main_get_debug_data(suppress_popup:bool=False):
    """
    Collect up and display the data needed to file GitHub issues.
    This function will place the information on the clipboard.
    You MUST paste the information from the clipboard prior to existing your application (except on Windows).
    :param suppress_popup: If True no popup window will be shown. The string will be only returned, not displayed
    :type suppress_popup:  (bool)
    :returns:              String containing the information to place into the GitHub Issue
    :rtype:                (str)
    """
    message = get_versions()
    clipboard_set(message)

    if not suppress_popup:
        popup_scrolled(
            "*** Version information copied to your clipboard. Paste into your GitHub Issue. ***\n",
            message,
            title="Select and copy this info to your GitHub Issue",
            keep_on_top=True,
            size=(100, 10),
        )

    return message




# -------------------------------- ENTRY POINT IF RUN STANDALONE -------------------------------- #
if __name__ == "__main__":
    # To execute the upgrade from command line, type:
    # python -m PySimpleGUI.PySimpleGUI upgrade
    if len(sys.argv) > 1 and sys.argv[1] == "help":
        main_sdk_help()
        exit(0)
    main()
    exit(0)