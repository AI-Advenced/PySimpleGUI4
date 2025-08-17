

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

from .constants import *




def list_of_look_and_feel_values():
    """
    Get a list of the valid values to pass into your call to change_look_and_feel

    :return: list of valid string values
    :rtype:  List[str]
    """

    return sorted(list(LOOK_AND_FEEL_TABLE.keys()))


def theme(new_theme=None):
    """
    Sets / Gets the current Theme.  If none is specified then returns the current theme.
    This call replaces the ChangeLookAndFeel / change_look_and_feel call which only sets the theme.

    :param new_theme: the new theme name to use
    :type new_theme:  (str)
    :return:          the currently selected theme
    :rtype:           (str)
    """
    global TRANSPARENT_BUTTON

    if new_theme is not None:
        change_look_and_feel(new_theme)
        TRANSPARENT_BUTTON = (theme_background_color(), theme_background_color())
    return CURRENT_LOOK_AND_FEEL


def theme_background_color(color=None):
    """
    Sets/Returns the background color currently in use
    Used for Windows and containers (Column, Frame, Tab) and tables

    :param color: new background color to use (optional)
    :type color:  (str)
    :return:      color string of the background color currently in use
    :rtype:       (str)
    """
    if color is not None:
        set_options(background_color=color)
    return DEFAULT_BACKGROUND_COLOR


# This "constant" is misleading but rather than remove and break programs, will try this method instead
TRANSPARENT_BUTTON = (
    theme_background_color(),
    theme_background_color(),
)  # replaces an older version that had hardcoded numbers


def theme_element_background_color(color=None):
    """
    Sets/Returns the background color currently in use for all elements except containers

    :return: (str) - color string of the element background color currently in use
    :rtype:  (str)
    """
    if color is not None:
        set_options(element_background_color=color)
    return DEFAULT_ELEMENT_BACKGROUND_COLOR


def theme_text_color(color=None):
    """
    Sets/Returns the text color currently in use

    :return: (str) - color string of the text color currently in use
    :rtype:  (str)
    """
    if color is not None:
        set_options(text_color=color)
    return DEFAULT_TEXT_COLOR


def theme_text_element_background_color(color=None):
    """
    Sets/Returns the background color for text elements

    :return: (str) - color string of the text background color currently in use
    :rtype:  (str)
    """
    if color is not None:
        set_options(text_element_background_color=color)
    return DEFAULT_TEXT_ELEMENT_BACKGROUND_COLOR


def theme_input_background_color(color=None):
    """
    Sets/Returns the input element background color currently in use

    :return: (str) - color string of the input element background color currently in use
    :rtype:  (str)
    """
    if color is not None:
        set_options(input_elements_background_color=color)
    return DEFAULT_INPUT_ELEMENTS_COLOR


def theme_input_text_color(color=None):
    """
    Sets/Returns the input element entry color (not the text but the thing that's displaying the text)

    :return: (str) - color string of the input element color currently in use
    :rtype:  (str)
    """
    if color is not None:
        set_options(input_text_color=color)
    return DEFAULT_INPUT_TEXT_COLOR


def theme_button_color(color=None):
    """
    Sets/Returns the button color currently in use

    :return: (str, str) - TUPLE with color strings of the button color currently in use (button text color, button background color)
    :rtype:  (str, str)
    """
    if color is not None:
        if color == COLOR_SYSTEM_DEFAULT:
            color_tuple = (COLOR_SYSTEM_DEFAULT, COLOR_SYSTEM_DEFAULT)
        else:
            color_tuple = button_color_to_tuple(color, (None, None))
        if color_tuple == (None, None):
            if not SUPPRESS_ERROR_POPUPS:
                popup_error("theme_button_color - bad color string passed in", color)
            else:
                print(
                    "** Badly formatted button color... not a tuple nor string **",
                    color,
                )
            set_options(button_color=color)  # go ahead and try with their string
        else:
            set_options(button_color=color_tuple)
    return DEFAULT_BUTTON_COLOR


def theme_button_color_background():
    """
    Returns the button color background currently in use. Note this function simple calls the theme_button_color
    function and splits apart the tuple

    :return: color string of the button color background currently in use
    :rtype:  (str)
    """
    return theme_button_color()[1]


def theme_button_color_text():
    """
    Returns the button color text currently in use.  Note this function simple calls the theme_button_color
    function and splits apart the tuple

    :return: color string of the button color text currently in use
    :rtype:  (str)
    """
    return theme_button_color()[0]


def theme_progress_bar_color(color=None):
    """
    Sets/Returns the progress bar colors by the current color theme

    :return: (str, str) - TUPLE with color strings of the ProgressBar color currently in use(button text color, button background color)
    :rtype:  (str, str)
    """
    if color is not None:
        set_options(progress_meter_color=color)
    return DEFAULT_PROGRESS_BAR_COLOR


def theme_slider_color(color=None):
    """
    Sets/Returns the slider color (used for sliders)

    :return: color string of the slider color currently in use
    :rtype:  (str)
    """
    if color is not None:
        set_options(scrollbar_color=color)
    return DEFAULT_SCROLLBAR_COLOR


def theme_border_width(border_width=None):
    """
    Sets/Returns the border width currently in use
    Used by non ttk elements at the moment

    :return: border width currently in use
    :rtype:  (int)
    """
    if border_width is not None:
        set_options(border_width=border_width)
    return DEFAULT_BORDER_WIDTH


def theme_slider_border_width(border_width=None):
    """
    Sets/Returns the slider border width currently in use

    :return: border width currently in use for sliders
    :rtype:  (int)
    """
    if border_width is not None:
        set_options(slider_border_width=border_width)
    return DEFAULT_SLIDER_BORDER_WIDTH


def theme_progress_bar_border_width(border_width=None):
    """
    Sets/Returns the progress meter border width currently in use

    :return: border width currently in use for progress meters
    :rtype:  (int)
    """
    if border_width is not None:
        set_options(progress_meter_border_depth=border_width)
    return DEFAULT_PROGRESS_BAR_BORDER_WIDTH


def theme_element_text_color(color=None):
    """
    Sets/Returns the text color used by elements that have text as part of their display (Tables, Trees and Sliders)

    :return: color string currently in use
    :rtype:  (str)
    """
    if color is not None:
        set_options(element_text_color=color)
    return DEFAULT_ELEMENT_TEXT_COLOR


def theme_list():
    """
    Returns a sorted list of the currently available color themes

    :return: A sorted list of the currently available color themes
    :rtype:  List[str]
    """
    return list_of_look_and_feel_values()


def theme_add_new(new_theme_name, new_theme_dict):
    """
    Add a new theme to the dictionary of themes

    :param new_theme_name: text to display in element
    :type new_theme_name:  (str)
    :param new_theme_dict: text to display in element
    :type new_theme_dict:  (dict)
    """
    global LOOK_AND_FEEL_TABLE
    try:
        LOOK_AND_FEEL_TABLE[new_theme_name] = new_theme_dict
    except Exception as e:
        print("Exception during adding new theme {}".format(e))


def theme_use_custom_titlebar():
    """
    Returns True if a custom titlebar will be / should be used.
    The setting is in the Global Settings window and can be overwridden
    using set_options call

    :return:        True if a custom titlebar / custom menubar should be used
    :rtype:         (bool)
    """
    if USE_CUSTOM_TITLEBAR is False:
        return False

    return USE_CUSTOM_TITLEBAR or pysimplegui_user_settings.get(
        "-custom titlebar-", False
    )


def theme_global(new_theme=None):
    """
    Sets / Gets the global PySimpleGUI Theme.  If none is specified then returns the global theme from user settings.
    Note the theme must be a standard, built-in PySimpleGUI theme... not a user-created theme.

    :param new_theme: the new theme name to use
    :type new_theme:  (str)
    :return:          the currently selected theme
    :rtype:           (str)
    """
    if new_theme is not None:
        if new_theme not in theme_list():
            popup_error_with_traceback(
                "Cannot use custom themes with theme_global call",
                "Your request to use theme {} cannot be performed.".format(new_theme),
                "The PySimpleGUI Global User Settings are meant for PySimpleGUI standard items, not user config items",
                "You can use any of the many built-in themes instead or use your own UserSettings file to store your custom theme",
            )
            return pysimplegui_user_settings.get("-theme-", CURRENT_LOOK_AND_FEEL)
        pysimplegui_user_settings.set("-theme-", new_theme)
        theme(new_theme)
        return new_theme
    else:
        return pysimplegui_user_settings.get("-theme-", CURRENT_LOOK_AND_FEEL)


def theme_previewer(
    columns=12,
    scrollable=False,
    scroll_area_size=(None, None),
    search_string=None,
    location=(None, None),
):
    """
    Displays a "Quick Reference Window" showing all of the different Look and Feel settings that are available.
    They are sorted alphabetically.  The legacy color names are mixed in, but otherwise they are sorted into Dark and Light halves

    :param columns:          The number of themes to display per row
    :type columns:           int
    :param scrollable:       If True then scrollbars will be added
    :type scrollable:        bool
    :param scroll_area_size: Size of the scrollable area (The Column Element used to make scrollable)
    :type scroll_area_size:  (int, int)
    :param search_string:    If specified then only themes containing this string will be shown
    :type search_string:     str
    :param location:         Location on the screen to place the window. Defaults to the center like all windows
    :type location:          (int, int)
    """

    current_theme = theme()

    # Show a "splash" type message so the user doesn't give up waiting
    popup_quick_message(
        "Hang on for a moment, this will take a bit to create....",
        keep_on_top=True,
        background_color="red",
        text_color="#FFFFFF",
        auto_close=True,
        non_blocking=True,
    )

    web = False

    win_bg = "black"

    def sample_layout():
        return [
            [Text("Text element"), InputText("Input data here", size=(10, 1))],
            [
                Button("Ok"),
                Button("Disabled", disabled=True),
                Slider((1, 10), orientation="h", size=(5, 15)),
            ],
        ]

    names = list_of_look_and_feel_values()
    names.sort()
    if search_string not in (None, ""):
        names = [
            name
            for name in names
            if search_string.lower().replace(" ", "") in name.lower().replace(" ", "")
        ]

    if search_string not in (None, ""):
        layout = [
            [
                Text(
                    'Themes containing "{}"'.format(search_string),
                    font="Default 18",
                    background_color=win_bg,
                )
            ]
        ]
    else:
        layout = [
            [Text("List of all themes", font="Default 18", background_color=win_bg)]
        ]

    col_layout = []
    row = []
    for count, theme_name in enumerate(names):
        theme(theme_name)
        if not count % columns:
            col_layout += [row]
            row = []
        row += [
            Frame(
                theme_name,
                sample_layout() if not web else [[T(theme_name)]] + sample_layout(),
                pad=(2, 2),
            )
        ]
    if row:
        col_layout += [row]

    layout += [
        [
            Column(
                col_layout,
                scrollable=scrollable,
                size=scroll_area_size,
                pad=(0, 0),
                background_color=win_bg,
                key="-COL-",
            )
        ]
    ]
    window = Window(
        "Preview of Themes",
        layout,
        background_color=win_bg,
        resizable=True,
        location=location,
        keep_on_top=True,
        finalize=True,
        modal=True,
    )
    window["-COL-"].expand(
        True, True, True
    )  # needed so that col will expand with the window
    window.read(close=True)
    theme(current_theme)


preview_all_look_and_feel_themes = theme_previewer


def _theme_preview_window_swatches():
    # Begin the layout with a header
    layout = [
        [
            Text(
                "Themes as color swatches",
                text_color="white",
                background_color="black",
                font="Default 25",
            )
        ],
        [
            Text(
                "Tooltip and right click a color to get the value",
                text_color="white",
                background_color="black",
                font="Default 15",
            )
        ],
        [
            Text(
                "Left click a color to copy to clipboard",
                text_color="white",
                background_color="black",
                font="Default 15",
            )
        ],
    ]
    layout = [[Column(layout, element_justification="c", background_color="black")]]
    # Create the pain part, the rows of Text with color swatches
    for i, theme_name in enumerate(theme_list()):
        theme(theme_name)
        colors = [
            theme_background_color(),
            theme_text_color(),
            theme_input_background_color(),
            theme_input_text_color(),
        ]
        if theme_button_color() != COLOR_SYSTEM_DEFAULT:
            colors.append(theme_button_color()[0])
            colors.append(theme_button_color()[1])
        colors = list(set(colors))  # de-duplicate items
        row = [
            T(
                theme(),
                background_color="black",
                text_color="white",
                size=(20, 1),
                justification="r",
            )
        ]
        for color in colors:
            if color != COLOR_SYSTEM_DEFAULT:
                row.append(
                    T(
                        SYMBOL_SQUARE,
                        text_color=color,
                        background_color="black",
                        pad=(0, 0),
                        font="DEFAUlT 20",
                        right_click_menu=["Nothing", [color]],
                        tooltip=color,
                        enable_events=True,
                        key=(i, color),
                    )
                )
        layout += [row]
    # place layout inside of a Column so that it's scrollable
    layout = [
        [
            Column(
                layout,
                size=(500, 900),
                scrollable=True,
                vertical_scroll_only=True,
                background_color="black",
            )
        ]
    ]
    # finish the layout by adding an exit button
    layout += [[B("Exit")]]

    # create and return Window that uses the layout
    return Window(
        "Theme Color Swatches",
        layout,
        background_color="black",
        finalize=True,
        keep_on_top=True,
    )


def theme_previewer_swatches():
    """
    Display themes in a window as color swatches.
    Click on a color swatch to see the hex value printed on the console.
    If you hover over a color or right click it you'll also see the hext value.
    """
    current_theme = theme()
    popup_quick_message(
        "This is going to take a minute...",
        text_color="white",
        background_color="red",
        font="Default 20",
        keep_on_top=True,
    )
    window = _theme_preview_window_swatches()
    theme(OFFICIAL_PYSIMPLEGUI_THEME)
    # col_height = window.get_screen_size()[1]-200
    # if window.size[1] > 100:
    #     window.size = (window.size[0], col_height)
    # window.move(window.get_screen_size()[0] // 2 - window.size[0] // 2, 0)

    while True:  # Event Loop
        event, values = window.read()
        if event == WIN_CLOSED or event == "Exit":
            break
        if isinstance(event, tuple):  # someone clicked a swatch
            chosen_color = event[1]
        else:
            if event[0] == "#":  # someone right clicked
                chosen_color = event
            else:
                chosen_color = ""
        print("Copied to clipboard color = ", chosen_color)
        clipboard_set(chosen_color)
        # window.TKroot.clipboard_clear()
        # window.TKroot.clipboard_append(chosen_color)
    window.close()
    theme(current_theme)


def change_look_and_feel(index, force=False):
    """
    Change the "color scheme" of all future PySimpleGUI Windows.
    The scheme are string names that specify a group of colors. Background colors, text colors, button colors.
    There are 13 different color settings that are changed at one time using a single call to ChangeLookAndFeel
    The look and feel table itself has these indexes into the dictionary LOOK_AND_FEEL_TABLE.
    The original list was (prior to a major rework and renaming)... these names still work...
    In Nov 2019 a new Theme Formula was devised to make choosing a theme easier:
    The "Formula" is:
    ["Dark" or "Light"] Color Number
    Colors can be Blue Brown Grey Green Purple Red Teal Yellow Black
    The number will vary for each pair. There are more DarkGrey entries than there are LightYellow for example.
    Default = The default settings (only button color is different than system default)
    Default1 = The full system default including the button (everything's gray... how sad... don't be all gray... please....)
    :param index: the name of the index into the Look and Feel table (does not have to be exact, can be "fuzzy")
    :type index:  (str)
    :param force: no longer used
    :type force:  (bool)
    :return:      None
    :rtype:       None
    """
    global CURRENT_LOOK_AND_FEEL

    # if running_mac() and not force:
    #     print('*** Changing look and feel is not supported on Mac platform ***')
    #     return

    requested_theme_name = index
    theme_names_list = list_of_look_and_feel_values()
    # normalize available l&f values by setting all to lower case
    lf_values_lowercase = [item.lower() for item in theme_names_list]
    # option 1
    opt1 = requested_theme_name.replace(" ", "").lower()
    # option 3 is option 1 with gray replaced with grey
    opt3 = opt1.replace("gray", "grey")
    # option 2 (reverse lookup)
    optx = requested_theme_name.lower().split(" ")
    optx.reverse()
    opt2 = "".join(optx)

    # search for valid l&f name
    if requested_theme_name in theme_names_list:
        ix = theme_names_list.index(requested_theme_name)
    elif opt1 in lf_values_lowercase:
        ix = lf_values_lowercase.index(opt1)
    elif opt2 in lf_values_lowercase:
        ix = lf_values_lowercase.index(opt2)
    elif opt3 in lf_values_lowercase:
        ix = lf_values_lowercase.index(opt3)
    else:
        ix = random.randint(0, len(lf_values_lowercase) - 1)
        print(
            "** Warning - {} Theme is not a valid theme. Change your theme call. **".format(
                index
            )
        )
        print("valid values are", list_of_look_and_feel_values())
        print(
            "Instead, please enjoy a random Theme named {}".format(
                list_of_look_and_feel_values()[ix]
            )
        )

    selection = theme_names_list[ix]
    CURRENT_LOOK_AND_FEEL = selection
    try:
        colors = LOOK_AND_FEEL_TABLE[selection]

        # Color the progress bar using button background and input colors...unless they're the same
        if colors["PROGRESS"] != COLOR_SYSTEM_DEFAULT:
            if colors["PROGRESS"] == DEFAULT_PROGRESS_BAR_COMPUTE:
                if (
                    colors["BUTTON"][1] != colors["INPUT"]
                    and colors["BUTTON"][1] != colors["BACKGROUND"]
                ):
                    colors["PROGRESS"] = colors["BUTTON"][1], colors["INPUT"]
                else:  # if the same, then use text input on top of input color
                    colors["PROGRESS"] = (colors["TEXT_INPUT"], colors["INPUT"])
        else:
            colors["PROGRESS"] = DEFAULT_PROGRESS_BAR_COLOR_OFFICIAL
        # call to change all the colors
        SetOptions(
            background_color=colors["BACKGROUND"],
            text_element_background_color=colors["BACKGROUND"],
            element_background_color=colors["BACKGROUND"],
            text_color=colors["TEXT"],
            input_elements_background_color=colors["INPUT"],
            # button_color=colors['BUTTON'] if not running_mac() else None,
            button_color=colors["BUTTON"],
            progress_meter_color=colors["PROGRESS"],
            border_width=colors["BORDER"],
            slider_border_width=colors["SLIDER_DEPTH"],
            progress_meter_border_depth=colors["PROGRESS_DEPTH"],
            scrollbar_color=(colors["SCROLL"]),
            element_text_color=colors["TEXT"],
            input_text_color=colors["TEXT_INPUT"],
        )
    except Exception:  # most likely an index out of range
        print("** Warning - Theme value not valid. Change your theme call. **")
        print("valid values are", list_of_look_and_feel_values())


# ------------------------ Color processing functions ------------------------


def _hex_to_hsl(hex):
    r, g, b = _hex_to_rgb(hex)
    return _rgb_to_hsl(r, g, b)


def _hex_to_rgb(hex):
    hex = hex.lstrip("#")
    hlen = len(hex)
    return tuple(int(hex[i : i + hlen // 3], 16) for i in range(0, hlen, hlen // 3))


def _rgb_to_hsl(r, g, b):
    r = float(r)
    g = float(g)
    b = float(b)
    high = max(r, g, b)
    low = min(r, g, b)
    h, s, v = ((high + low) / 2,) * 3
    if high == low:
        h = s = 0.0
    else:
        d = high - low
        l = (high + low) / 2
        s = d / (2 - high - low) if l > 0.5 else d / (high + low)
        h = {
            r: (g - b) / d + (6 if g < b else 0),
            g: (b - r) / d + 2,
            b: (r - g) / d + 4,
        }[high]
        h /= 6
    return h, s, v


def _hsl_to_rgb(h, s, l):
    def hue_to_rgb(p, q, t):
        t += 1 if t < 0 else 0
        t -= 1 if t > 1 else 0
        if t < 1 / 6:
            return p + (q - p) * 6 * t
        if t < 1 / 2:
            return q
        if t < 2 / 3:
            p + (q - p) * (2 / 3 - t) * 6
        return p

    if s == 0:
        r, g, b = l, l, l
    else:
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1 / 3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1 / 3)

    return r, g, b


def _hsv_to_hsl(h, s, v):
    l = 0.5 * v * (2 - s)
    s = v * s / (1 - fabs(2 * l - 1))
    return h, s, l


def _hsl_to_hsv(h, s, l):
    v = (2 * l + s * (1 - fabs(2 * l - 1))) / 2
    s = 2 * (v - l) / v
    return h, s, v





def _change_ttk_theme(style, theme_name):
    global ttk_theme_in_use
    if theme_name not in style.theme_names():
        _error_popup_with_traceback(
            'You are trying to use TTK theme "{}"'.format(theme_name),
            "This is not legal for your system",
            "The valid themes to choose from are: {}".format(
                ", ".join(style.theme_names())
            ),
        )
        return False

    style.theme_use(theme_name)
    ttk_theme_in_use = theme_name
    return True



def _make_ttk_style_name(base_style, element, primary_style=False):
    Window._counter_for_ttk_widgets += 1
    style_name = (
        str(Window._counter_for_ttk_widgets) + "___" + str(element.Key) + base_style
    )
    if primary_style:
        element.ttk_style_name = style_name
    return style_name


def _make_ttk_scrollbar(element, orientation, window):
    """
    Creates a ttk scrollbar for elements as they are being added to the layout

    :param element:     The element
    :type element:      (Element)
    :param orientation: The orientation vertical ('v') or horizontal ('h')
    :type orientation:  (str)
    :param window:      The window containing the scrollbar
    :type window:       (Window)
    """

    style = ttk.Style()
    _change_ttk_theme(style, window.TtkTheme)
    if orientation[0].lower() == "v":
        orient = "vertical"
        style_name = _make_ttk_style_name(".Vertical.TScrollbar", element)
        # style_name_thumb = _make_ttk_style_name('.Vertical.TScrollbar.thumb', element)
        element.vsb_style = style
        element.vsb = ttk.Scrollbar(
            element.element_frame,
            orient=orient,
            command=element.Widget.yview,
            style=style_name,
        )
        element.vsb_style_name = style_name
    else:
        orient = "horizontal"
        style_name = _make_ttk_style_name(".Horizontal.TScrollbar", element)
        element.hsb_style = style
        element.hsb = ttk.Scrollbar(
            element.element_frame,
            orient=orient,
            command=element.Widget.xview,
            style=style_name,
        )
        element.hsb_style_name = style_name

    # ------------------ Get the colors using heirarchy of element, window, options, settings ------------------
    # Trough Color
    if element.ttk_part_overrides.sbar_trough_color is not None:
        trough_color = element.ttk_part_overrides.sbar_trough_color
    elif window.ttk_part_overrides.sbar_trough_color is not None:
        trough_color = window.ttk_part_overrides.sbar_trough_color
    elif ttk_part_overrides_from_options.sbar_trough_color is not None:
        trough_color = ttk_part_overrides_from_options.sbar_trough_color
    else:
        trough_color = element.scroll_trough_color
    # Relief
    if element.ttk_part_overrides.sbar_relief is not None:
        scroll_relief = element.ttk_part_overrides.sbar_relief
    elif window.ttk_part_overrides.sbar_relief is not None:
        scroll_relief = window.ttk_part_overrides.sbar_relief
    elif ttk_part_overrides_from_options.sbar_relief is not None:
        scroll_relief = ttk_part_overrides_from_options.sbar_relief
    else:
        scroll_relief = element.scroll_relief
    # Frame Color
    if element.ttk_part_overrides.sbar_frame_color is not None:
        frame_color = element.ttk_part_overrides.sbar_frame_color
    elif window.ttk_part_overrides.sbar_frame_color is not None:
        frame_color = window.ttk_part_overrides.sbar_frame_color
    elif ttk_part_overrides_from_options.sbar_frame_color is not None:
        frame_color = ttk_part_overrides_from_options.sbar_frame_color
    else:
        frame_color = element.scroll_frame_color
    # Background Color
    if element.ttk_part_overrides.sbar_background_color is not None:
        background_color = element.ttk_part_overrides.sbar_background_color
    elif window.ttk_part_overrides.sbar_background_color is not None:
        background_color = window.ttk_part_overrides.sbar_background_color
    elif ttk_part_overrides_from_options.sbar_background_color is not None:
        background_color = ttk_part_overrides_from_options.sbar_background_color
    else:
        background_color = element.scroll_background_color
    # Arrow Color
    if element.ttk_part_overrides.sbar_arrow_color is not None:
        arrow_color = element.ttk_part_overrides.sbar_arrow_color
    elif window.ttk_part_overrides.sbar_arrow_color is not None:
        arrow_color = window.ttk_part_overrides.sbar_arrow_color
    elif ttk_part_overrides_from_options.sbar_arrow_color is not None:
        arrow_color = ttk_part_overrides_from_options.sbar_arrow_color
    else:
        arrow_color = element.scroll_arrow_color
    # Arrow Width
    if element.ttk_part_overrides.sbar_arrow_width is not None:
        arrow_width = element.ttk_part_overrides.sbar_arrow_width
    elif window.ttk_part_overrides.sbar_arrow_width is not None:
        arrow_width = window.ttk_part_overrides.sbar_arrow_width
    elif ttk_part_overrides_from_options.sbar_arrow_width is not None:
        arrow_width = ttk_part_overrides_from_options.sbar_arrow_width
    else:
        arrow_width = element.scroll_arrow_width
    # Scroll Width
    if element.ttk_part_overrides.sbar_width is not None:
        scroll_width = element.ttk_part_overrides.sbar_width
    elif window.ttk_part_overrides.sbar_width is not None:
        scroll_width = window.ttk_part_overrides.sbar_width
    elif ttk_part_overrides_from_options.sbar_width is not None:
        scroll_width = ttk_part_overrides_from_options.sbar_width
    else:
        scroll_width = element.scroll_width

    if trough_color not in (None, COLOR_SYSTEM_DEFAULT):
        style.configure(style_name, troughcolor=trough_color)

    if frame_color not in (None, COLOR_SYSTEM_DEFAULT):
        style.configure(style_name, framecolor=frame_color)
    if frame_color not in (None, COLOR_SYSTEM_DEFAULT):
        style.configure(style_name, bordercolor=frame_color)

    if (background_color not in (None, COLOR_SYSTEM_DEFAULT)) and (
        arrow_color not in (None, COLOR_SYSTEM_DEFAULT)
    ):
        style.map(
            style_name,
            background=[
                ("selected", background_color),
                ("active", arrow_color),
                ("background", background_color),
                ("!focus", background_color),
            ],
        )
    if (background_color not in (None, COLOR_SYSTEM_DEFAULT)) and (
        arrow_color not in (None, COLOR_SYSTEM_DEFAULT)
    ):
        style.map(
            style_name,
            arrowcolor=[
                ("selected", arrow_color),
                ("active", background_color),
                ("background", background_color),
                ("!focus", arrow_color),
            ],
        )

    if scroll_width not in (None, COLOR_SYSTEM_DEFAULT):
        style.configure(style_name, width=scroll_width)
    if arrow_width not in (None, COLOR_SYSTEM_DEFAULT):
        style.configure(style_name, arrowsize=arrow_width)

    if scroll_relief not in (None, COLOR_SYSTEM_DEFAULT):
        style.configure(style_name, relief=scroll_relief)

