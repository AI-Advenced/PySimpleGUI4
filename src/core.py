

import tkinter as tk
from tkinter import ttk
from typing import Any, Union, Tuple, Optional, Dict, List
import copy
import warnings



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

# 导入本地模块
from .constants import *
from .themes import *


# ------------------------------------------------------------------------- #
#                       ToolTip used by the Elements                        #
# ------------------------------------------------------------------------- #

class ToolTip:
    """
    Create a tooltip for a given widget
    (inspired by https://stackoverflow.com/a/36221216)
    This is an INTERNALLY USED only class.  Users should not refer to this class at all.
    """

    def __init__(self, widget, text, timeout=DEFAULT_TOOLTIP_TIME):
        """
        :param widget:  The tkinter widget
        :type widget:   widget type varies
        :param text:    text for the tooltip. It can inslude \n
        :type text:     (str)
        :param timeout: Time in milliseconds that mouse must remain still before tip is shown
        :type timeout:  (int)
        """
        self.widget = widget
        self.text = text
        self.timeout = timeout
        # self.wraplength = wraplength if wraplength else widget.winfo_screenwidth() // 2
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)

    def enter(self, event=None):
        """
        Called by tkinter when mouse enters a widget
        :param event: from tkinter.  Has x,y coordinates of mouse
        :type event:

        """
        self.x = event.x
        self.y = event.y
        self.schedule()

    def leave(self, event=None):
        """
        Called by tktiner when mouse exits a widget
        :param event: from tkinter.  Event info that's not used by function.
        :type event:

        """
        self.unschedule()
        self.hidetip()

    def schedule(self):
        """
        Schedule a timer to time how long mouse is hovering
        """
        self.unschedule()
        self.id = self.widget.after(self.timeout, self.showtip)

    def unschedule(self):
        """
        Cancel timer used to time mouse hover
        """
        if self.id:
            self.widget.after_cancel(self.id)
        self.id = None

    def showtip(self):
        """
        Creates a topoltip window with the tooltip text inside of it
        """
        if self.tipwindow:
            return
        x = self.widget.winfo_rootx() + self.x + DEFAULT_TOOLTIP_OFFSET[0]
        y = self.widget.winfo_rooty() + self.y + DEFAULT_TOOLTIP_OFFSET[1]
        self.tipwindow = tk.Toplevel(self.widget)
        # if not sys.platform.startswith('darwin'):
        try:
            self.tipwindow.wm_overrideredirect(True)
            # if running_mac() and ENABLE_MAC_NOTITLEBAR_PATCH:
            if _mac_should_apply_notitlebar_patch():
                self.tipwindow.wm_overrideredirect(False)
        except Exception as e:
            print("* Error performing wm_overrideredirect in showtip *", e)
        self.tipwindow.wm_geometry("+%d+%d" % (x, y))
        self.tipwindow.wm_attributes("-topmost", 1)

        label = ttk.Label(
            self.tipwindow,
            text=self.text,
            justify=tk.LEFT,
            background=TOOLTIP_BACKGROUND_COLOR,
            relief=tk.SOLID,
            borderwidth=1,
        )
        if TOOLTIP_FONT is not None:
            label.config(font=TOOLTIP_FONT)
        label.pack()

    def hidetip(self):
        """
        Destroy the tooltip window
        """
        if self.tipwindow:
            self.tipwindow.destroy()
        self.tipwindow = None




class TTKPartOverrides:
    """
    This class contains "overrides" to the defaults for ttk scrollbars that are defined in the global settings file.
    This class is used in every element, in the Window class and there's a global one that is used by set_options.
    """

    def __init__(
        self,
        sbar_trough_color=None,
        sbar_background_color=None,
        sbar_arrow_color=None,
        sbar_width=None,
        sbar_arrow_width=None,
        sbar_frame_color=None,
        sbar_relief=None,
    ):
        self.sbar_trough_color = sbar_trough_color
        self.sbar_background_color = sbar_background_color
        self.sbar_arrow_color = sbar_arrow_color
        self.sbar_width = sbar_width
        self.sbar_arrow_width = sbar_arrow_width
        self.sbar_frame_color = sbar_frame_color
        self.sbar_relief = sbar_relief


ttk_part_overrides_from_options = TTKPartOverrides()




# ---------------------------------------------------------------------- #
# Cascading structure.... Objects get larger                             #
#   Button                                                               #
#       Element                                                          #
#           Row                                                          #
#               Form                                                     #
# ---------------------------------------------------------------------- #
# ------------------------------------------------------------------------- #
#                       Element CLASS                                       #
# ------------------------------------------------------------------------- #
class Element:
    """The base class for all Elements. Holds the basic description of an Element like size and colors"""

    def __init__(
        self,
        type_,
        size=(None, None),
        auto_size_text=None,
        font=None,
        background_color=None,
        text_color=None,
        key=None,
        pad=None,
        tooltip=None,
        visible=True,
        metadata=None,
        sbar_trough_color=None,
        sbar_background_color=None,
        sbar_arrow_color=None,
        sbar_width=None,
        sbar_arrow_width=None,
        sbar_frame_color=None,
        sbar_relief=None,
    ):
        """
        Element base class. Only used internally.  User will not create an Element object by itself

        :param type_:                        The type of element. These constants all start with "ELEM_TYPE_"
        :type type_:                         (int) (could be enum)
        :param size:                        w=characters-wide, h=rows-high. If an int instead of a tuple is supplied, then height is auto-set to 1
        :type size:                         (int, int) | (None, None) | int
        :param auto_size_text:              True if the Widget should be shrunk to exactly fit the number of chars to show
        :type auto_size_text:               bool
        :param font:                        specifies the font family, size. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
        :type font:                         (str or (str, int[, str]) or None)
        :param background_color:            color of background. Can be in #RRGGBB format or a color name "black"
        :type background_color:             (str)
        :param text_color:                  element's text color. Can be in #RRGGBB format or a color name "black"
        :type text_color:                   (str)
        :param key:                         Identifies an Element. Should be UNIQUE to this window.
        :type key:                          str | int | tuple | object
        :param pad:                         Amount of padding to put around element in pixels (left/right, top/bottom). If an int is given, then auto-converted to tuple (int, int)
        :type pad:                          (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
        :param tooltip:                     text, that will appear when mouse hovers over the element
        :type tooltip:                      (str)
        :param visible:                     set visibility state of the element (Default = True)
        :type visible:                      (bool)
        :param metadata:                    User metadata that can be set to ANYTHING
        :type metadata:                     (Any)
        :param sbar_trough_color:           Scrollbar color of the trough
        :type sbar_trough_color:            (str)
        :param sbar_background_color:       Scrollbar color of the background of the arrow buttons at the ends AND the color of the "thumb" (the thing you grab and slide). Switches to arrow color when mouse is over
        :type sbar_background_color:        (str)
        :param sbar_arrow_color:            Scrollbar color of the arrow at the ends of the scrollbar (it looks like a button). Switches to background color when mouse is over
        :type sbar_arrow_color:             (str)
        :param sbar_width:                  Scrollbar width in pixels
        :type sbar_width:                   (int)
        :param sbar_arrow_width:            Scrollbar width of the arrow on the scrollbar. It will potentially impact the overall width of the scrollbar
        :type sbar_arrow_width:             (int)
        :param sbar_frame_color:            Scrollbar Color of frame around scrollbar (available only on some ttk themes)
        :type sbar_frame_color:             (str)
        :param sbar_relief:                 Scrollbar relief that will be used for the "thumb" of the scrollbar (the thing you grab that slides). Should be a constant that is defined at starting with "RELIEF_" - RELIEF_RAISED, RELIEF_SUNKEN, RELIEF_FLAT, RELIEF_RIDGE, RELIEF_GROOVE, RELIEF_SOLID
        :type sbar_relief:                  (str)
        """

        if size is not None and size != (None, None):
            if isinstance(size, int):
                size = (size, 1)
            if isinstance(size, tuple) and len(size) == 1:
                size = (size[0], 1)

        if pad is not None and pad != (None, None):
            if isinstance(pad, int):
                pad = (pad, pad)

        self.Size = size
        self.Type = type_
        self.AutoSizeText = auto_size_text

        self.Pad = pad
        self.Font = font

        self.TKStringVar = None
        self.TKIntVar = None
        self.TKText = None
        self.TKEntry = None
        self.TKImage = None
        self.ttk_style_name = ""  # The ttk style name (if this is a ttk widget)
        self.ttk_style = None  # The ttk Style object (if this is a ttk widget)
        self._metadata = None  # type: Any

        self.ParentForm = None  # type: Window
        self.ParentContainer = None  # will be a Form, Column, or Frame element # UNBIND
        self.TextInputDefault = None
        self.Position = (0, 0)  # Default position Row 0, Col 0
        self.BackgroundColor = (
            background_color
            if background_color is not None
            else DEFAULT_ELEMENT_BACKGROUND_COLOR
        )
        self.TextColor = (
            text_color if text_color is not None else DEFAULT_ELEMENT_TEXT_COLOR
        )
        self.Key = key  # dictionary key for return values
        self.Tooltip = tooltip
        self.TooltipObject = None
        self._visible = visible
        self.TKRightClickMenu = None
        self.Widget = (
            None  # Set when creating window. Has the main tkinter widget for element
        )
        self.Tearoff = False  # needed because of right click menu code
        self.ParentRowFrame = None  # type tk.Frame
        self.metadata = metadata
        self.user_bind_dict = {}  # Used when user defines a tkinter binding using bind method - convert bind string to key modifier
        self.user_bind_event = None  # Used when user defines a tkinter binding using bind method - event data from tkinter
        # self.pad_used = (0, 0)  # the amount of pad used when was inserted into the layout
        self._popup_menu_location = (None, None)
        self.pack_settings = None
        self.vsb_style_name = None  # ttk style name used for the verical scrollbar if one is attached to element
        self.hsb_style_name = None  # ttk style name used for the horizontal scrollbar if one is attached to element
        self.vsb_style = None  # The ttk style used for the vertical scrollbar if one is attached to element
        self.hsb_style = None  # The ttk style used for the horizontal scrollbar if one is attached to element
        self.hsb = None  # The horizontal scrollbar if one is attached to element
        self.vsb = None  # The vertical scrollbar if one is attached to element
        ## TTK Scrollbar Settings
        self.ttk_part_overrides = TTKPartOverrides(
            sbar_trough_color=sbar_trough_color,
            sbar_background_color=sbar_background_color,
            sbar_arrow_color=sbar_arrow_color,
            sbar_width=sbar_width,
            sbar_arrow_width=sbar_arrow_width,
            sbar_frame_color=sbar_frame_color,
            sbar_relief=sbar_relief,
        )

        PSG_THEME_PART_FUNC_MAP = {
            PSG_THEME_PART_BACKGROUND: theme_background_color,
            PSG_THEME_PART_BUTTON_BACKGROUND: theme_button_color_background,
            PSG_THEME_PART_BUTTON_TEXT: theme_button_color_text,
            PSG_THEME_PART_INPUT_BACKGROUND: theme_input_background_color,
            PSG_THEME_PART_INPUT_TEXT: theme_input_text_color,
            PSG_THEME_PART_TEXT: theme_text_color,
            PSG_THEME_PART_SLIDER: theme_slider_color,
        }

        # class Theme_Parts():
        #     PSG_THEME_PART_FUNC_MAP = {PSG_THEME_PART_BACKGROUND: theme_background_color,
        if sbar_trough_color is not None:
            self.scroll_trough_color = sbar_trough_color
        else:
            self.scroll_trough_color = PSG_THEME_PART_FUNC_MAP.get(
                ttk_part_mapping_dict[TTK_SCROLLBAR_PART_TROUGH_COLOR],
                ttk_part_mapping_dict[TTK_SCROLLBAR_PART_TROUGH_COLOR],
            )
            if callable(self.scroll_trough_color):
                self.scroll_trough_color = self.scroll_trough_color()

        if sbar_background_color is not None:
            self.scroll_background_color = sbar_background_color
        else:
            self.scroll_background_color = PSG_THEME_PART_FUNC_MAP.get(
                ttk_part_mapping_dict[TTK_SCROLLBAR_PART_BACKGROUND_COLOR],
                ttk_part_mapping_dict[TTK_SCROLLBAR_PART_BACKGROUND_COLOR],
            )
            if callable(self.scroll_background_color):
                self.scroll_background_color = self.scroll_background_color()

        if sbar_arrow_color is not None:
            self.scroll_arrow_color = sbar_arrow_color
        else:
            self.scroll_arrow_color = PSG_THEME_PART_FUNC_MAP.get(
                ttk_part_mapping_dict[TTK_SCROLLBAR_PART_ARROW_BUTTON_ARROW_COLOR],
                ttk_part_mapping_dict[TTK_SCROLLBAR_PART_ARROW_BUTTON_ARROW_COLOR],
            )
            if callable(self.scroll_arrow_color):
                self.scroll_arrow_color = self.scroll_arrow_color()

        if sbar_frame_color is not None:
            self.scroll_frame_color = sbar_frame_color
        else:
            self.scroll_frame_color = PSG_THEME_PART_FUNC_MAP.get(
                ttk_part_mapping_dict[TTK_SCROLLBAR_PART_FRAME_COLOR],
                ttk_part_mapping_dict[TTK_SCROLLBAR_PART_FRAME_COLOR],
            )
            if callable(self.scroll_frame_color):
                self.scroll_frame_color = self.scroll_frame_color()

        if sbar_relief is not None:
            self.scroll_relief = sbar_relief
        else:
            self.scroll_relief = ttk_part_mapping_dict[TTK_SCROLLBAR_PART_RELIEF]

        if sbar_width is not None:
            self.scroll_width = sbar_width
        else:
            self.scroll_width = ttk_part_mapping_dict[TTK_SCROLLBAR_PART_SCROLL_WIDTH]

        if sbar_arrow_width is not None:
            self.scroll_arrow_width = sbar_arrow_width
        else:
            self.scroll_arrow_width = ttk_part_mapping_dict[
                TTK_SCROLLBAR_PART_ARROW_WIDTH
            ]

        if not hasattr(self, "DisabledTextColor"):
            self.DisabledTextColor = None
        if not hasattr(self, "ItemFont"):
            self.ItemFont = None
        if not hasattr(self, "RightClickMenu"):
            self.RightClickMenu = None
        if not hasattr(self, "Disabled"):
            self.Disabled = None  # in case the element hasn't defined this, add it here

    @property
    def visible(self):
        """
        Returns visibility state for the element.  This is a READONLY property
        :return: Visibility state for element
        :rtype:  (bool)
        """
        return self._visible

    @property
    def metadata(self):
        """
        Metadata is an Element property that you can use at any time to hold any value
        :return: the current metadata value
        :rtype:  (Any)
        """
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        """
         Metadata is an Element property that you can use at any time to hold any value
        :param value: Anything you want it to be
        :type value:  (Any)
        """
        self._metadata = value

    @property
    def key(self):
        """
        Returns key for the element.  This is a READONLY property.
        Keys can be any hashable object (basically anything except a list... tuples are ok, but not lists)
        :return: The window's Key
        :rtype:  (Any)
        """
        return self.Key

    @property
    def widget(self):
        """
        Returns tkinter widget for the element.  This is a READONLY property.
        The implementation is that the Widget member variable is returned. This is a backward compatible addition
        :return:    The element's underlying tkinter widget
        :rtype:     (tkinter.Widget)
        """
        return self.Widget

    def _RightClickMenuCallback(self, event):
        """
        Callback function that's called when a right click happens. Shows right click menu as result

        :param event: information provided by tkinter about the event including x,y location of click
        :type event:

        """
        if self.Type == ELEM_TYPE_TAB_GROUP:
            try:
                index = self.Widget.index("@{},{}".format(event.x, event.y))
                tab = self.Widget.tab(index, "text")
                key = self.find_key_from_tab_name(tab)
                tab_element = self.ParentForm.key_dict[key]
                if (
                    tab_element.RightClickMenu is None
                ):  # if this tab didn't explicitly have a menu, then don't show anything
                    return
                tab_element.TKRightClickMenu.tk_popup(event.x_root, event.y_root, 0)
                self.TKRightClickMenu.grab_release()
            except Exception:
                pass
            return
        self.TKRightClickMenu.tk_popup(event.x_root, event.y_root, 0)
        self.TKRightClickMenu.grab_release()
        if self.Type == ELEM_TYPE_GRAPH:
            self._update_position_for_returned_values(event)

    def _tearoff_menu_callback(self, parent, menu):
        """
        Callback function that's called when a right click menu is torn off.
        The reason for this function is to relocate the torn-off menu. It will default to 0,0 otherwise
        This callback moves the right click menu window to the location of the current window

        :param parent: information provided by tkinter - the parent of the Meny
        :type parent:
        :param menu:   information provided by tkinter - the menu window
        :type menu:

        """
        if self._popup_menu_location == (None, None):
            winx, winy = self.ParentForm.current_location()
        else:
            winx, winy = self._popup_menu_location
        # self.ParentForm.TKroot.update()
        self.ParentForm.TKroot.tk.call(
            "wm", "geometry", menu, "+{}+{}".format(winx, winy)
        )

    def _MenuItemChosenCallback(self, item_chosen):  # TEXT Menu item callback
        """
        Callback function called when user chooses a menu item from menubar, Button Menu or right click menu

        :param item_chosen: String holding the value chosen.
        :type item_chosen:  str

        """
        # print('IN MENU ITEM CALLBACK', item_chosen)
        self.MenuItemChosen = item_chosen
        self.ParentForm.LastButtonClicked = self.MenuItemChosen
        self.ParentForm.FormRemainedOpen = True
        _exit_mainloop(self.ParentForm)
        # Window._window_that_exited = self.ParentForm
        # self.ParentForm.TKroot.quit()  # kick the users out of the mainloop

    def _FindReturnKeyBoundButton(self, form):
        """
        Searches for which Button has the flag Button.BindReturnKey set.  It is called recursively when a
        "Container Element" is encountered. Func has to walk entire window including these "sub-forms"

        :param form: the Window object to search
        :type form:
        :return:     Button Object if a button is found, else None
        :rtype:      Button | None
        """
        for row in form.Rows:
            for element in row:
                if element.Type == ELEM_TYPE_BUTTON:
                    if element.BindReturnKey:
                        return element
                if element.Type == ELEM_TYPE_COLUMN:
                    rc = self._FindReturnKeyBoundButton(element)
                    if rc is not None:
                        return rc
                if element.Type == ELEM_TYPE_FRAME:
                    rc = self._FindReturnKeyBoundButton(element)
                    if rc is not None:
                        return rc
                if element.Type == ELEM_TYPE_TAB_GROUP:
                    rc = self._FindReturnKeyBoundButton(element)
                    if rc is not None:
                        return rc
                if element.Type == ELEM_TYPE_TAB:
                    rc = self._FindReturnKeyBoundButton(element)
                    if rc is not None:
                        return rc
                if element.Type == ELEM_TYPE_PANE:
                    rc = self._FindReturnKeyBoundButton(element)
                    if rc is not None:
                        return rc
        return None

    def _TextClickedHandler(self, event):
        """
        Callback that's called when a text element is clicked on with events enabled on the Text Element.
        Result is that control is returned back to user (quits mainloop).

        :param event:
        :type event:

        """
        # If this is a minimize button for a custom titlebar, then minimize the window
        if self.Key in (
            TITLEBAR_MINIMIZE_KEY,
            TITLEBAR_MAXIMIZE_KEY,
            TITLEBAR_CLOSE_KEY,
        ):
            self.ParentForm._custom_titlebar_callback(self.Key)
        self._generic_callback_handler(self.DisplayText)
        return

    def _ReturnKeyHandler(self, event):
        """
        Internal callback for the ENTER / RETURN key. Results in calling the ButtonCallBack for element that has the return key bound to it, just as if button was clicked.

        :param event:
        :type event:

        """
        # if the element is disabled, ignore the event
        if self.Disabled:
            return

        MyForm = self.ParentForm
        button_element = self._FindReturnKeyBoundButton(MyForm)
        if button_element is not None:
            # if the Button has been disabled, then don't perform the callback
            if button_element.Disabled:
                return
            button_element.ButtonCallBack()

    def _generic_callback_handler(self, alternative_to_key=None, force_key_to_be=None):
        """
        Peforms the actions that were in many of the callback functions previously.  Combined so that it's
        easier to modify and is in 1 place now

        :param alternate_to_key: If key is None, then use this value instead
        :type alternate_to_key:  Any
        """
        if force_key_to_be is not None:
            self.ParentForm.LastButtonClicked = force_key_to_be
        elif self.Key is not None:
            self.ParentForm.LastButtonClicked = self.Key
        else:
            self.ParentForm.LastButtonClicked = alternative_to_key
        self.ParentForm.FormRemainedOpen = True

        _exit_mainloop(self.ParentForm)
        # if self.ParentForm.CurrentlyRunningMainloop:
        #     Window._window_that_exited = self.ParentForm
        #     self.ParentForm.TKroot.quit()  # kick the users out of the mainloop

    def _ListboxSelectHandler(self, event):
        """
        Internal callback function for when a listbox item is selected

        :param event: Information from tkinter about the callback
        :type event:

        """
        self._generic_callback_handler("")

    def _ComboboxSelectHandler(self, event):
        """
        Internal callback function for when an entry is selected in a Combobox.
        :param event: Event data from tkinter (not used)
        :type event:

        """
        self._generic_callback_handler("")

    def _SpinboxSelectHandler(self, event=None):
        """
        Internal callback function for when an entry is selected in a Spinbox.
        Note that the parm is optional because it's not used if arrows are used to change the value
        but if the return key is pressed, it will include the event parm
        :param event: Event data passed in by tkinter (not used)
        :type event:
        """
        self._generic_callback_handler("")

    def _RadioHandler(self):
        """
        Internal callback for when a radio button is selected and enable events was set for radio
        """
        self._generic_callback_handler("")

    def _CheckboxHandler(self):
        """
        Internal callback for when a checkbnox is selected and enable events was set for checkbox
        """
        self._generic_callback_handler("")

    def _TabGroupSelectHandler(self, event):
        """
        Internal callback for when a Tab is selected and enable events was set for TabGroup

        :param event: Event data passed in by tkinter (not used)
        :type event:
        """
        self._generic_callback_handler("")

    def _KeyboardHandler(self, event):
        """
        Internal callback for when a key is pressed andd return keyboard events was set for window

        :param event: Event data passed in by tkinter (not used)
        :type event:
        """

        # if the element is disabled, ignore the event
        if self.Disabled:
            return
        self._generic_callback_handler("")

    def _ClickHandler(self, event):
        """
        Internal callback for when a mouse was clicked... I think.

        :param event: Event data passed in by tkinter (not used)
        :type event:
        """
        self._generic_callback_handler("")

    def _this_elements_window_closed(self, quick_check=True):
        if self.ParentForm is not None:
            return self.ParentForm.is_closed(quick_check=quick_check)

        return True

    def _user_bind_callback(self, bind_string, event, propagate=True):
        """
        Used when user binds a tkinter event directly to an element

        :param bind_string: The event that was bound so can lookup the key modifier
        :type bind_string:  (str)
        :param event:       Event data passed in by tkinter (not used)
        :type event:        (Any)
        :param propagate:   If True then tkinter will be told to propagate the event to the element
        :type propagate:    (bool)
        """
        key_suffix = self.user_bind_dict.get(bind_string, "")
        self.user_bind_event = event
        if self.Type == ELEM_TYPE_GRAPH:
            self._update_position_for_returned_values(event)
        if self.Key is not None:
            if isinstance(self.Key, str):
                key = self.Key + str(key_suffix)
            else:
                key = (
                    self.Key,
                    key_suffix,
                )  # old way (pre 2021) was to make a brand new tuple
                # key = self.Key + (key_suffix,)   # in 2021 tried this. It will break existing applications though - if key is a tuple, add one more item
        else:
            key = bind_string

        self._generic_callback_handler(force_key_to_be=key)

        return "break" if propagate is not True else None

    def bind(self, bind_string, key_modifier, propagate=True):
        """
        Used to add tkinter events to an Element.
        The tkinter specific data is in the Element's member variable user_bind_event
        :param bind_string:  The string tkinter expected in its bind function
        :type bind_string:   (str)
        :param key_modifier: Additional data to be added to the element's key when event is returned
        :type key_modifier:  (str)
        :param propagate:    If True then tkinter will be told to propagate the event to the element
        :type propagate:     (bool)
        """
        if (
            not self._widget_was_created()
        ):  # if widget hasn't been created yet, then don't allow
            return

        try:
            self.Widget.bind(
                bind_string,
                lambda evt: self._user_bind_callback(bind_string, evt, propagate),
            )
        except Exception as e:
            self.Widget.unbind_all(bind_string)
            return

        self.user_bind_dict[bind_string] = key_modifier

    def unbind(self, bind_string):
        """
        Removes a previously bound tkinter event from an Element.
        :param bind_string: The string tkinter expected in its bind function
        :type bind_string:  (str)
        """
        if (
            not self._widget_was_created()
        ):  # if widget hasn't been created yet, then don't allow
            return
        self.Widget.unbind(bind_string)
        self.user_bind_dict.pop(bind_string, None)

    def set_tooltip(self, tooltip_text):
        """
        Called by application to change the tooltip text for an Element.  Normally invoked using the Element Object such as: window.Element('key').SetToolTip('New tip').

        :param tooltip_text: the text to show in tooltip.
        :type tooltip_text:  (str)
        """

        if self.TooltipObject:
            try:
                self.TooltipObject.leave()
            except Exception:
                pass

        self.TooltipObject = ToolTip(
            self.Widget, text=tooltip_text, timeout=DEFAULT_TOOLTIP_TIME
        )

    def set_focus(self, force=False):
        """
        Sets the current focus to be on this element

        :param force: if True will call focus_force otherwise calls focus_set
        :type force:  bool
        """
        if (
            not self._widget_was_created()
        ):  # if widget hasn't been created yet, then don't allow
            return
        try:
            if force:
                self.Widget.focus_force()
            else:
                self.Widget.focus_set()
        except Exception as e:
            _error_popup_with_traceback(
                "Exception blocking focus. Check your element's Widget", e
            )

    def block_focus(self, block=True):
        """
        Enable or disable the element from getting focus by using the keyboard.
        If the block parameter is True, then this element will not be given focus by using
        the keyboard to go from one element to another.
        You CAN click on the element and utilize it.

        :param block: if True the element will not get focus via the keyboard
        :type block:  bool
        """
        if (
            not self._widget_was_created()
        ):  # if widget hasn't been created yet, then don't allow
            return
        try:
            self.ParentForm.TKroot.focus_force()
            if block:
                self.Widget.configure(takefocus=0)
            else:
                self.Widget.configure(takefocus=1)
        except Exception as e:
            _error_popup_with_traceback(
                "Exception blocking focus. Check your element's Widget", e
            )

    def get_next_focus(self):
        """
        Gets the next element that should get focus after this element.

        :return:    Element that will get focus after this one
        :rtype:     (Element)
        """
        if (
            not self._widget_was_created()
        ):  # if widget hasn't been created yet, then don't allow
            return None

        try:
            next_widget_focus = self.widget.tk_focusNext()
            return self.ParentForm.widget_to_element(next_widget_focus)
        except Exception as e:
            _error_popup_with_traceback(
                "Exception getting next focus. Check your element's Widget", e
            )

    def get_previous_focus(self):
        """
        Gets the element that should get focus previous to this element.

        :return:    Element that should get the focus before this one
        :rtype:     (Element)
        """
        if (
            not self._widget_was_created()
        ):  # if widget hasn't been created yet, then don't allow
            return None
        try:
            next_widget_focus = self.widget.tk_focusPrev()  # tkinter.Widget
            return self.ParentForm.widget_to_element(next_widget_focus)
        except Exception as e:
            _error_popup_with_traceback(
                "Exception getting previous focus. Check your element's Widget", e
            )

    def set_size(self, size=(None, None)):
        """
        Changes the size of an element to a specific size.
        It's possible to specify None for one of sizes so that only 1 of the element's dimensions are changed.

        :param size: The size in characters, rows typically. In some cases they are pixels
        :type size:  (int, int)
        """
        try:
            if size[0] is not None:
                self.Widget.config(width=size[0])
        except Exception:
            print("Warning, error setting width on element with key=", self.Key)
        try:
            if size[1] is not None:
                self.Widget.config(height=size[1])
        except Exception:
            try:
                self.Widget.config(length=size[1])
            except Exception:
                print("Warning, error setting height on element with key=", self.Key)

        if self.Type == ELEM_TYPE_GRAPH:
            self.CanvasSize = size

    def get_size(self):
        """
        Return the size of an element in Pixels.  Care must be taken as some elements use characters to specify their size but will return pixels when calling this get_size method.
        :return: width and height of the element
        :rtype:  (int, int)
        """
        try:
            w = self.Widget.winfo_width()
            h = self.Widget.winfo_height()
        except Exception:
            print("Warning, error getting size of element", self.Key)
            w = h = None
        return w, h

    def hide_row(self):
        """
        Hide the entire row an Element is located on.
        Use this if you must have all space removed when you are hiding an element, including the row container
        """
        try:
            self.ParentRowFrame.pack_forget()
        except Exception:
            print("Warning, error hiding element row for key =", self.Key)

    def unhide_row(self):
        """
        Unhides (makes visible again) the row container that the Element is located on.
        Note that it will re-appear at the bottom of the window / container, most likely.
        """
        try:
            self.ParentRowFrame.pack()
        except Exception:
            print("Warning, error hiding element row for key =", self.Key)

    def expand(self, expand_x=False, expand_y=False, expand_row=True):
        """
        Causes the Element to expand to fill available space in the X and Y directions.  Can specify which or both directions

        :param expand_x:   If True Element will expand in the Horizontal directions
        :type expand_x:    (bool)
        :param expand_y:   If True Element will expand in the Vertical directions
        :type expand_y:    (bool)
        :param expand_row: If True the row containing the element will also expand. Without this your element is "trapped" within the row
        :type expand_row:  (bool)
        """
        if expand_x and expand_y:
            fill = tk.BOTH
        elif expand_x:
            fill = tk.X
        elif expand_y:
            fill = tk.Y
        else:
            return

        if not self._widget_was_created():
            return
        self.Widget.pack(expand=True, fill=fill)
        self.ParentRowFrame.pack(expand=expand_row, fill=fill)
        if self.element_frame is not None:
            self.element_frame.pack(expand=True, fill=fill)

    def set_cursor(self, cursor=None, cursor_color=None):
        """
        Sets the cursor for the current Element.
        "Cursor" is used in 2 different ways in this call.
        For the parameter "cursor" it's actually the mouse pointer.
        If you do not want any mouse pointer, then use the string "none"
        For the parameter "cursor_color" it's the color of the beam used when typing into an input element

        :param cursor:       The tkinter cursor name
        :type cursor:        (str)
        :param cursor_color: color to set the "cursor" to
        :type cursor_color:  (str)
        """
        if not self._widget_was_created():
            return
        if cursor is not None:
            try:
                self.Widget.config(cursor=cursor)
            except Exception as e:
                print("Warning bad cursor specified ", cursor)
                print(e)
        if cursor_color is not None:
            try:
                self.Widget.config(insertbackground=cursor_color)
            except Exception as e:
                print("Warning bad cursor color", cursor_color)
                print(e)

    def set_vscroll_position(self, percent_from_top):
        """
        Attempts to set the vertical scroll postition for an element's Widget
        :param percent_from_top: From 0 to 1.0, the percentage from the top to move scrollbar to
        :type percent_from_top:  (float)
        """
        if self.Type == ELEM_TYPE_COLUMN and self.Scrollable:
            widget = self.widget.canvas  # scrollable column is a special case
        else:
            widget = self.widget

        try:
            widget.yview_moveto(percent_from_top)
        except Exception as e:
            print("Warning setting the vertical scroll (yview_moveto failed)")
            print(e)

    def _widget_was_created(self):
        """
        Determines if a Widget was created for this element.

        :return: True if a Widget has been created previously (Widget is not None)
        :rtype:  (bool)
        """
        if self.Widget is not None:
            return True
        else:
            if SUPPRESS_WIDGET_NOT_FINALIZED_WARNINGS:
                return False

            warnings.warn(
                "You cannot Update element with key = {} until the window.read() is called or set finalize=True when creating window".format(
                    self.Key
                ),
                UserWarning,
            )
            if not SUPPRESS_ERROR_POPUPS:
                _error_popup_with_traceback(
                    "Unable to complete operation on element with key {}".format(
                        self.Key
                    ),
                    "You cannot perform operations (such as calling update) on an Element until:",
                    " window.read() is called or finalize=True when Window created.",
                    'Adding a "finalize=True" parameter to your Window creation will likely fix this.',
                    _create_error_message(),
                )
            return False

    def _grab_anywhere_on_using_control_key(self):
        """
        Turns on Grab Anywhere functionality AFTER a window has been created.  Don't try on a window that's not yet
        been Finalized or Read.
        """
        self.Widget.bind("<Control-Button-1>", self.ParentForm._StartMove)
        self.Widget.bind("<Control-ButtonRelease-1>", self.ParentForm._StopMove)
        self.Widget.bind("<Control-B1-Motion>", self.ParentForm._OnMotion)

    def _grab_anywhere_on(self):
        """
        Turns on Grab Anywhere functionality AFTER a window has been created.  Don't try on a window that's not yet
        been Finalized or Read.
        """
        self.Widget.bind("<ButtonPress-1>", self.ParentForm._StartMove)
        self.Widget.bind("<ButtonRelease-1>", self.ParentForm._StopMove)
        self.Widget.bind("<B1-Motion>", self.ParentForm._OnMotion)

    def _grab_anywhere_off(self):
        """
        Turns off Grab Anywhere functionality AFTER a window has been created.  Don't try on a window that's not yet
        been Finalized or Read.
        """
        self.Widget.unbind("<ButtonPress-1>")
        self.Widget.unbind("<ButtonRelease-1>")
        self.Widget.unbind("<B1-Motion>")

    def grab_anywhere_exclude(self):
        """
        Excludes this element from being used by the grab_anywhere feature
        Handy for elements like a Graph element when dragging is enabled. You want the Graph element to get the drag events instead of the window dragging.
        """
        self.ParentForm._grab_anywhere_ignore_these_list.append(self.Widget)

    def grab_anywhere_include(self):
        """
        Includes this element in the grab_anywhere feature
        This will allow you to make a Multline element drag a window for example
        """
        self.ParentForm._grab_anywhere_include_these_list.append(self.Widget)

    def set_right_click_menu(self, menu=None):
        """
        Sets a right click menu for an element.
        If a menu is already set for the element, it will call the tkinter destroy method to remove it
        :param menu:                   A list of lists of Menu items to show when this element is right clicked. See user docs for exact format.
        :type menu:                    List[List[ List[str] | str ]]
        """
        if menu == MENU_RIGHT_CLICK_DISABLED:
            return
        if menu is None:
            menu = self.ParentForm.RightClickMenu
            if menu is None:
                return
        if menu:
            # If previously had a menu destroy it
            if self.TKRightClickMenu:
                try:
                    self.TKRightClickMenu.destroy()
                except Exception:
                    pass
            top_menu = tk.Menu(
                self.ParentForm.TKroot,
                tearoff=self.ParentForm.right_click_menu_tearoff,
                tearoffcommand=self._tearoff_menu_callback,
            )

            if self.ParentForm.right_click_menu_background_color not in (
                COLOR_SYSTEM_DEFAULT,
                None,
            ):
                top_menu.config(bg=self.ParentForm.right_click_menu_background_color)
            if self.ParentForm.right_click_menu_text_color not in (
                COLOR_SYSTEM_DEFAULT,
                None,
            ):
                top_menu.config(fg=self.ParentForm.right_click_menu_text_color)
            if self.ParentForm.right_click_menu_disabled_text_color not in (
                COLOR_SYSTEM_DEFAULT,
                None,
            ):
                top_menu.config(
                    disabledforeground=self.ParentForm.right_click_menu_disabled_text_color
                )
            if self.ParentForm.right_click_menu_font is not None:
                top_menu.config(font=self.ParentForm.right_click_menu_font)

            if self.ParentForm.right_click_menu_selected_colors[0] not in (
                COLOR_SYSTEM_DEFAULT,
                None,
            ):
                top_menu.config(
                    activeforeground=self.ParentForm.right_click_menu_selected_colors[0]
                )
            if self.ParentForm.right_click_menu_selected_colors[1] not in (
                COLOR_SYSTEM_DEFAULT,
                None,
            ):
                top_menu.config(
                    activebackground=self.ParentForm.right_click_menu_selected_colors[1]
                )
            AddMenuItem(top_menu, menu[1], self, right_click_menu=True)
            self.TKRightClickMenu = top_menu
            if self.ParentForm.RightClickMenu:  # if the top level has a right click menu, then setup a callback for the Window itself
                if self.ParentForm.TKRightClickMenu is None:
                    self.ParentForm.TKRightClickMenu = top_menu
                    if running_mac():
                        self.ParentForm.TKroot.bind(
                            "<ButtonRelease-2>", self.ParentForm._RightClickMenuCallback
                        )
                    else:
                        self.ParentForm.TKroot.bind(
                            "<ButtonRelease-3>", self.ParentForm._RightClickMenuCallback
                        )
            if running_mac():
                self.Widget.bind("<ButtonRelease-2>", self._RightClickMenuCallback)
            else:
                self.Widget.bind("<ButtonRelease-3>", self._RightClickMenuCallback)

    def save_element_screenshot_to_disk(self, filename=None):
        """
        Saves an image of the PySimpleGUI window provided into the filename provided

        :param filename:        Optional filename to save screenshot to. If not included, the User Settinds are used to get the filename
        :return:                A PIL ImageGrab object that can be saved or manipulated
        :rtype:                 (PIL.ImageGrab | None)
        """
        global pil_import_attempted, pil_imported, PIL, ImageGrab, Image

        if not pil_import_attempted:
            try:
                import PIL as PIL
                from PIL import ImageGrab
                from PIL import Image

                pil_imported = True
                pil_import_attempted = True
            except Exception:
                pil_imported = False
                pil_import_attempted = True
                print("FAILED TO IMPORT PIL!")
                return None
        try:
            # Add a little to the X direction if window has a titlebar
            rect = (
                self.widget.winfo_rootx(),
                self.widget.winfo_rooty(),
                self.widget.winfo_rootx() + self.widget.winfo_width(),
                self.widget.winfo_rooty() + self.widget.winfo_height(),
            )

            grab = ImageGrab.grab(bbox=rect)
            # Save the grabbed image to disk
        except Exception as e:
            # print(e)
            popup_error_with_traceback(
                "Screen capture failure",
                "Error happened while trying to save screencapture of an element",
                e,
            )
            return None

        # return grab
        if filename is None:
            folder = pysimplegui_user_settings.get("-screenshots folder-", "")
            filename = pysimplegui_user_settings.get("-screenshots filename-", "")
            full_filename = os.path.join(folder, filename)
        else:
            full_filename = filename
        if full_filename:
            try:
                grab.save(full_filename)
            except Exception as e:
                popup_error_with_traceback(
                    "Screen capture failure",
                    "Error happened while trying to save screencapture",
                    e,
                )
        else:
            popup_error_with_traceback(
                "Screen capture failure",
                "You have attempted a screen capture but have not set up a good filename to save to",
            )
        return grab

    def _pack_forget_save_settings(self, alternate_widget=None):
        """
        Performs a pack_forget which will make a widget invisible.
        This method saves the pack settings so that they can be restored if the element is made visible again

        :param alternate_widget:   Widget to use that's different than the one defined in Element.Widget. These are usually Frame widgets
        :type alternate_widget:    (tk.Widget)
        """

        if alternate_widget is not None and self.Widget is None:
            return

        widget = alternate_widget if alternate_widget is not None else self.Widget
        # if the widget is already invisible (i.e. not packed) then will get an error
        try:
            pack_settings = widget.pack_info()
            self.pack_settings = pack_settings
            widget.pack_forget()
        except Exception:
            pass

    def _pack_restore_settings(self, alternate_widget=None):
        """
        Restores a previously packated widget which will make it visible again.
        If no settings were saved, then the widget is assumed to have not been unpacked and will not try to pack it again

        :param alternate_widget:   Widget to use that's different than the one defined in Element.Widget. These are usually Frame widgets
        :type alternate_widget:    (tk.Widget)
        """

        # if there are no saved pack settings, then assume it hasnb't been packaed before. The request will be ignored
        if self.pack_settings is None:
            return

        widget = alternate_widget if alternate_widget is not None else self.Widget
        if widget is not None:
            widget.pack(**self.pack_settings)

    def update(self, *args, **kwargs):
        """
        A dummy update call.  This will only be called if an element hasn't implemented an update method
        It is provided here for docstring purposes.  If you got here by browing code via PyCharm, know
        that this is not the function that will be called.  Your actual element's update method will be called.

        If you call update, you must call window.refresh if you want the change to happen prior to your next
        window.read() call. Normally uou don't do this as the window.read call is likely going to happen next.
        """
        print(
            "* Base Element Class update was called. Your element does not seem to have an update method"
        )

    def __call__(self, *args, **kwargs):
        """
        Makes it possible to "call" an already existing element.  When you do make the "call", it actually calls
        the Update method for the element.
        Example:    If this text element was in yoiur layout:
                    sg.Text('foo', key='T')
                    Then you can call the Update method for that element by writing:
                    window.find_element('T')('new text value')
        """
        return self.update(*args, **kwargs)

    SetTooltip = set_tooltip
    SetFocus = set_focus



# ------------------------------------------------------------------------- #
#                       Window CLASS                                        #
# ------------------------------------------------------------------------- #
class Window:
    """
    Represents a single Window
    """

    NumOpenWindows = 0
    _user_defined_icon = None
    hidden_master_root = None  # type: tk.Tk
    _animated_popup_dict = {}  # type: Dict
    _active_windows = {}  # type: Dict[Window, tk.Tk()]
    _move_all_windows = False  # if one window moved, they will move
    _window_that_exited = None  # type: Window
    _root_running_mainloop = None  # type: tk.Tk()    # (may be the hidden root or a window's root)
    _timeout_key = None
    _TKAfterID = None  # timer that is used to run reads with timeouts
    _window_running_mainloop = None  # The window that is running the mainloop
    _container_element_counter = (
        0  # used to get a number of Container Elements (Frame, Column, Tab)
    )
    _read_call_from_debugger = False
    _timeout_0_counter = 0  # when timeout=0 then go through each window one at a time
    _counter_for_ttk_widgets = 0
    _floating_debug_window_build_needed = False
    _main_debug_window_build_needed = False
    # rereouted stdout info. List of tuples (window, element, previous destination)
    _rerouted_stdout_stack = []  # type: List[Tuple[Window, Element]]
    _rerouted_stderr_stack = []  # type: List[Tuple[Window, Element]]
    _original_stdout = None
    _original_stderr = None
    _watermark = None
    _watermark_temp_forced = False
    _watermark_user_text = ""

    def __init__(
        self,
        title,
        layout=None,
        default_element_size=None,
        default_button_element_size=(None, None),
        auto_size_text=None,
        auto_size_buttons=None,
        location=(None, None),
        relative_location=(None, None),
        size=(None, None),
        element_padding=None,
        margins=(None, None),
        button_color=None,
        font=None,
        progress_bar_color=(None, None),
        background_color=None,
        border_depth=None,
        auto_close=False,
        auto_close_duration=DEFAULT_AUTOCLOSE_TIME,
        icon=None,
        force_toplevel=False,
        alpha_channel=None,
        return_keyboard_events=False,
        use_default_focus=True,
        text_justification=None,
        no_titlebar=False,
        grab_anywhere=False,
        grab_anywhere_using_control=True,
        keep_on_top=None,
        resizable=False,
        disable_close=False,
        disable_minimize=False,
        right_click_menu=None,
        transparent_color=None,
        debugger_enabled=True,
        right_click_menu_background_color=None,
        right_click_menu_text_color=None,
        right_click_menu_disabled_text_color=None,
        right_click_menu_selected_colors=(None, None),
        right_click_menu_font=None,
        right_click_menu_tearoff=False,
        finalize=False,
        element_justification="left",
        ttk_theme=None,
        use_ttk_buttons=None,
        modal=False,
        enable_close_attempted_event=False,
        enable_window_config_events=False,
        titlebar_background_color=None,
        titlebar_text_color=None,
        titlebar_font=None,
        titlebar_icon=None,
        use_custom_titlebar=None,
        scaling=None,
        sbar_trough_color=None,
        sbar_background_color=None,
        sbar_arrow_color=None,
        sbar_width=None,
        sbar_arrow_width=None,
        sbar_frame_color=None,
        sbar_relief=None,
        watermark=None,
        metadata=None,
    ):
        """
        :param title:                                The title that will be displayed in the Titlebar and on the Taskbar
        :type title:                                 (str)
        :param layout:                               The layout for the window. Can also be specified in the Layout method
        :type layout:                                List[List[Element]] | Tuple[Tuple[Element]]
        :param default_element_size:                 size in characters (wide) and rows (high) for all elements in this window
        :type default_element_size:                  (int, int) - (width, height)
        :param default_button_element_size:          (width, height) size in characters (wide) and rows (high) for all Button elements in this window
        :type default_button_element_size:           (int, int)
        :param auto_size_text:                       True if Elements in Window should be sized to exactly fir the length of text
        :type auto_size_text:                        (bool)
        :param auto_size_buttons:                    True if Buttons in this Window should be sized to exactly fit the text on this.
        :type auto_size_buttons:                     (bool)
        :param relative_location:                    (x,y) location relative to the default location of the window, in pixels. Normally the window centers.  This location is relative to the location the window would be created. Note they can be negative.
        :type relative_location:                     (int, int)
        :param location:                             (x,y) location, in pixels, to locate the upper left corner of the window on the screen. Default is to center on screen. None will not set any location meaning the OS will decide
        :type location:                              (int, int) or (None, None) or None
        :param size:                                 (width, height) size in pixels for this window. Normally the window is autosized to fit contents, not set to an absolute size by the user. Try not to set this value. You risk, the contents being cut off, etc. Let the layout determine the window size instead
        :type size:                                  (int, int)
        :param element_padding:                      Default amount of padding to put around elements in window (left/right, top/bottom) or ((left, right), (top, bottom)), or an int. If an int, then it's converted into a tuple (int, int)
        :type element_padding:                       (int, int) or ((int, int),(int,int)) or int
        :param margins:                              (left/right, top/bottom) Amount of pixels to leave inside the window's frame around the edges before your elements are shown.
        :type margins:                               (int, int)
        :param button_color:                         Default button colors for all buttons in the window
        :type button_color:                          (str, str) | str
        :param font:                                 specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
        :type font:                                  (str or (str, int[, str]) or None)
        :param progress_bar_color:                   (bar color, background color) Sets the default colors for all progress bars in the window
        :type progress_bar_color:                    (str, str)
        :param background_color:                     color of background
        :type background_color:                      (str)
        :param border_depth:                         Default border depth (width) for all elements in the window
        :type border_depth:                          (int)
        :param auto_close:                           If True, the window will automatically close itself
        :type auto_close:                            (bool)
        :param auto_close_duration:                  Number of seconds to wait before closing the window
        :type auto_close_duration:                   (int)
        :param icon:                                 Can be either a filename or Base64 value. For Windows if filename, it MUST be ICO format. For Linux, must NOT be ICO. Most portable is to use a Base64 of a PNG file. This works universally across all OS's
        :type icon:                                  (str | bytes)
        :param force_toplevel:                       If True will cause this window to skip the normal use of a hidden master window
        :type force_toplevel:                        (bool)
        :param alpha_channel:                        Sets the opacity of the window. 0 = invisible 1 = completely visible. Values bewteen 0 & 1 will produce semi-transparent windows in SOME environments (The Raspberry Pi always has this value at 1 and cannot change.
        :type alpha_channel:                         (float)
        :param return_keyboard_events:               if True key presses on the keyboard will be returned as Events from Read calls
        :type return_keyboard_events:                (bool)
        :param use_default_focus:                    If True will use the default focus algorithm to set the focus to the "Correct" element
        :type use_default_focus:                     (bool)
        :param text_justification:                   Default text justification for all Text Elements in window
        :type text_justification:                    'left' | 'right' | 'center'
        :param no_titlebar:                          If true, no titlebar nor frame will be shown on window. This means you cannot minimize the window and it will not show up on the taskbar
        :type no_titlebar:                           (bool)
        :param grab_anywhere:                        If True can use mouse to click and drag to move the window. Almost every location of the window will work except input fields on some systems
        :type grab_anywhere:                         (bool)
        :param grab_anywhere_using_control:          If True can use CONTROL key + left mouse mouse to click and drag to move the window. DEFAULT is TRUE. Unlike normal grab anywhere, it works on all elements.
        :type grab_anywhere_using_control:           (bool)
        :param keep_on_top:                          If True, window will be created on top of all other windows on screen. It can be bumped down if another window created with this parm
        :type keep_on_top:                           (bool)
        :param resizable:                            If True, allows the user to resize the window. Note the not all Elements will change size or location when resizing.
        :type resizable:                             (bool)
        :param disable_close:                        If True, the X button in the top right corner of the window will no work.  Use with caution and always give a way out toyour users
        :type disable_close:                         (bool)
        :param disable_minimize:                     if True the user won't be able to minimize window.  Good for taking over entire screen and staying that way.
        :type disable_minimize:                      (bool)
        :param right_click_menu:                     A list of lists of Menu items to show when this element is right clicked. See user docs for exact format.
        :type right_click_menu:                      List[List[ List[str] | str ]]
        :param transparent_color:                    Any portion of the window that has this color will be completely transparent. You can even click through these spots to the window under this window.
        :type transparent_color:                     (str)
        :param debugger_enabled:                     If True then the internal debugger will be enabled
        :type debugger_enabled:                      (bool)
        :param right_click_menu_background_color:    Background color for right click menus
        :type right_click_menu_background_color:     (str)
        :param right_click_menu_text_color:          Text color for right click menus
        :type right_click_menu_text_color:           (str)
        :param right_click_menu_disabled_text_color: Text color for disabled right click menu items
        :type right_click_menu_disabled_text_color:  (str)
        :param right_click_menu_selected_colors:     Text AND background colors for a selected item. Can be a Tuple OR a color string. simplified-button-color-string "foreground on background". Can be a single color if want to set only the background. Normally a tuple, but can be a simplified-dual-color-string "foreground on background". Can be a single color if want to set only the background.
        :type right_click_menu_selected_colors:      (str, str) | str | Tuple
        :param right_click_menu_font:                Font for right click menus
        :type right_click_menu_font:                 (str or (str, int[, str]) or None)
        :param right_click_menu_tearoff:             If True then all right click menus can be torn off
        :type right_click_menu_tearoff:              bool
        :param finalize:                             If True then the Finalize method will be called. Use this rather than chaining .Finalize for cleaner code
        :type finalize:                              (bool)
        :param element_justification:                All elements in the Window itself will have this justification 'left', 'right', 'center' are valid values
        :type element_justification:                 (str)
        :param ttk_theme:                            Set the tkinter ttk "theme" of the window.  Default = DEFAULT_TTK_THEME.  Sets all ttk widgets to this theme as their default
        :type ttk_theme:                             (str)
        :param use_ttk_buttons:                      Affects all buttons in window. True = use ttk buttons. False = do not use ttk buttons.  None = use ttk buttons only if on a Mac
        :type use_ttk_buttons:                       (bool)
        :param modal:                                If True then this window will be the only window a user can interact with until it is closed
        :type modal:                                 (bool)
        :param enable_close_attempted_event:         If True then the window will not close when "X" clicked. Instead an event WINDOW_CLOSE_ATTEMPTED_EVENT if returned from window.read
        :type enable_close_attempted_event:          (bool)
        :param enable_window_config_events:          If True then window configuration events (resizing or moving the window) will return WINDOW_CONFIG_EVENT from window.read. Note you will get several when Window is created.
        :type enable_window_config_events:           (bool)
        :param titlebar_background_color:            If custom titlebar indicated by use_custom_titlebar, then use this as background color
        :type titlebar_background_color:             (str | None)
        :param titlebar_text_color:                  If custom titlebar indicated by use_custom_titlebar, then use this as text color
        :type titlebar_text_color:                   (str | None)
        :param titlebar_font:                        If custom titlebar indicated by use_custom_titlebar, then use this as title font
        :type titlebar_font:                         (str or (str, int[, str]) or None)
        :param titlebar_icon:                        If custom titlebar indicated by use_custom_titlebar, then use this as the icon (file or base64 bytes)
        :type titlebar_icon:                         (bytes | str)
        :param use_custom_titlebar:                  If True, then a custom titlebar will be used instead of the normal titlebar
        :type use_custom_titlebar:                   bool
        :param scaling:                              Apply scaling to the elements in the window. Can be set on a global basis using set_options
        :type scaling:                               float
        :param sbar_trough_color:                    Scrollbar color of the trough
        :type sbar_trough_color:                     (str)
        :param sbar_background_color:                Scrollbar color of the background of the arrow buttons at the ends AND the color of the "thumb" (the thing you grab and slide). Switches to arrow color when mouse is over
        :type sbar_background_color:                 (str)
        :param sbar_arrow_color:                     Scrollbar color of the arrow at the ends of the scrollbar (it looks like a button). Switches to background color when mouse is over
        :type sbar_arrow_color:                      (str)
        :param sbar_width:                           Scrollbar width in pixels
        :type sbar_width:                            (int)
        :param sbar_arrow_width:                     Scrollbar width of the arrow on the scrollbar. It will potentially impact the overall width of the scrollbar
        :type sbar_arrow_width:                      (int)
        :param sbar_frame_color:                     Scrollbar Color of frame around scrollbar (available only on some ttk themes)
        :type sbar_frame_color:                      (str)
        :param sbar_relief:                          Scrollbar relief that will be used for the "thumb" of the scrollbar (the thing you grab that slides). Should be a constant that is defined at starting with "RELIEF_" - RELIEF_RAISED, RELIEF_SUNKEN, RELIEF_FLAT, RELIEF_RIDGE, RELIEF_GROOVE, RELIEF_SOLID
        :type sbar_relief:                           (str)
        :param watermark:                            If True, then turns on watermarking temporarily for ALL windows created from this point forward. See global settings doc for more info
        :type watermark:                             bool
        :param metadata:                             User metadata that can be set to ANYTHING
        :type metadata:                              (Any)
        """

        self._metadata = None  # type: Any
        self.AutoSizeText = (
            auto_size_text if auto_size_text is not None else DEFAULT_AUTOSIZE_TEXT
        )
        self.AutoSizeButtons = (
            auto_size_buttons
            if auto_size_buttons is not None
            else DEFAULT_AUTOSIZE_BUTTONS
        )
        self.Title = str(title)
        self.Rows = []  # a list of ELEMENTS for this row
        self.DefaultElementSize = (
            default_element_size
            if default_element_size is not None
            else DEFAULT_ELEMENT_SIZE
        )
        self.DefaultButtonElementSize = (
            default_button_element_size
            if default_button_element_size != (None, None)
            else DEFAULT_BUTTON_ELEMENT_SIZE
        )
        if DEFAULT_WINDOW_LOCATION != (None, None) and location == (None, None):
            self.Location = DEFAULT_WINDOW_LOCATION
        else:
            self.Location = location
        self.RelativeLoction = relative_location
        self.ButtonColor = button_color_to_tuple(button_color)
        self.BackgroundColor = (
            background_color if background_color else DEFAULT_BACKGROUND_COLOR
        )
        self.ParentWindow = None
        self.Font = font if font else DEFAULT_FONT
        self.RadioDict = {}
        self.BorderDepth = border_depth
        if icon:
            self.WindowIcon = icon
        elif Window._user_defined_icon is not None:
            self.WindowIcon = Window._user_defined_icon
        else:
            self.WindowIcon = DEFAULT_WINDOW_ICON
        self.AutoClose = auto_close
        self.NonBlocking = False
        self.TKroot = None  # type: tk.Tk
        self.TKrootDestroyed = False
        self.CurrentlyRunningMainloop = False
        self.FormRemainedOpen = False
        self.TKAfterID = None
        self.ProgressBarColor = progress_bar_color
        self.AutoCloseDuration = auto_close_duration
        self.RootNeedsDestroying = False
        self.Shown = False
        self.ReturnValues = None
        self.ReturnValuesList = []
        self.ReturnValuesDictionary = {}
        self.DictionaryKeyCounter = 0
        self.LastButtonClicked = None
        self.LastButtonClickedWasRealtime = False
        self.UseDictionary = False
        self.UseDefaultFocus = use_default_focus
        self.ReturnKeyboardEvents = return_keyboard_events
        self.LastKeyboardEvent = None
        self.TextJustification = text_justification
        self.NoTitleBar = no_titlebar
        self.Grab = grab_anywhere
        self.GrabAnywhere = grab_anywhere
        self.GrabAnywhereUsingControlKey = grab_anywhere_using_control
        if keep_on_top is None and DEFAULT_KEEP_ON_TOP is not None:
            keep_on_top = DEFAULT_KEEP_ON_TOP
        elif keep_on_top is None:
            keep_on_top = False
        self.KeepOnTop = keep_on_top
        self.ForceTopLevel = force_toplevel
        self.Resizable = resizable
        self._AlphaChannel = (
            alpha_channel if alpha_channel is not None else DEFAULT_ALPHA_CHANNEL
        )
        self.Timeout = None
        self.TimeoutKey = TIMEOUT_KEY
        self.TimerCancelled = False
        self.DisableClose = disable_close
        self.DisableMinimize = disable_minimize
        self._Hidden = False
        self._Size = size
        self.XFound = False
        if element_padding is not None:
            if isinstance(element_padding, int):
                element_padding = (element_padding, element_padding)

        if element_padding is None:
            self.ElementPadding = DEFAULT_ELEMENT_PADDING
        else:
            self.ElementPadding = element_padding
        self.RightClickMenu = right_click_menu
        self.Margins = margins if margins != (None, None) else DEFAULT_MARGINS
        self.ContainerElemementNumber = Window._GetAContainerNumber()
        # The dictionary containing all elements and keys for the window
        # The keys are the keys for the elements and the values are the elements themselves.
        self.AllKeysDict = {}
        self.TransparentColor = transparent_color
        self.UniqueKeyCounter = 0
        self.DebuggerEnabled = debugger_enabled
        self.WasClosed = False
        self.ElementJustification = element_justification
        self.FocusSet = False
        self.metadata = metadata
        self.TtkTheme = ttk_theme or DEFAULT_TTK_THEME
        self.UseTtkButtons = (
            use_ttk_buttons if use_ttk_buttons is not None else USE_TTK_BUTTONS
        )
        self.user_bind_dict = {}  # Used when user defines a tkinter binding using bind method - convert bind string to key modifier
        self.user_bind_event = None  # Used when user defines a tkinter binding using bind method - event data from tkinter
        self.modal = modal
        self.thread_queue = None  # type: queue.Queue
        self.thread_lock = None  # type: threading.Lock
        self.thread_timer = None  # type: tk.Misc
        self.thread_strvar = None  # type: tk.StringVar
        self.read_closed_window_count = 0
        self.config_last_size = (None, None)
        self.config_last_location = (None, None)
        self.starting_window_position = (None, None)
        self.not_completed_initial_movement = True
        self.config_count = 0
        self.saw_00 = False
        self.maximized = False
        self.right_click_menu_background_color = (
            right_click_menu_background_color
            if right_click_menu_background_color is not None
            else theme_input_background_color()
        )
        self.right_click_menu_text_color = (
            right_click_menu_text_color
            if right_click_menu_text_color is not None
            else theme_input_text_color()
        )
        self.right_click_menu_disabled_text_color = (
            right_click_menu_disabled_text_color
            if right_click_menu_disabled_text_color is not None
            else COLOR_SYSTEM_DEFAULT
        )
        self.right_click_menu_font = (
            right_click_menu_font if right_click_menu_font is not None else self.Font
        )
        self.right_click_menu_tearoff = right_click_menu_tearoff
        self.auto_close_timer_needs_starting = False
        self.finalize_in_progress = False
        self.close_destroys_window = (
            not enable_close_attempted_event
            if enable_close_attempted_event is not None
            else None
        )
        self.enable_window_config_events = enable_window_config_events
        self.override_custom_titlebar = False
        self.use_custom_titlebar = use_custom_titlebar or theme_use_custom_titlebar()
        self.titlebar_background_color = titlebar_background_color
        self.titlebar_text_color = titlebar_text_color
        self.titlebar_font = titlebar_font
        self.titlebar_icon = titlebar_icon
        self.right_click_menu_selected_colors = _simplified_dual_color_to_tuple(
            right_click_menu_selected_colors,
            (self.right_click_menu_background_color, self.right_click_menu_text_color),
        )
        self.TKRightClickMenu = None
        self._grab_anywhere_ignore_these_list = []
        self._grab_anywhere_include_these_list = []
        self._has_custom_titlebar = use_custom_titlebar
        self._mousex = self._mousey = 0
        self._startx = self._starty = 0
        self.scaling = scaling if scaling is not None else DEFAULT_SCALING
        if self.use_custom_titlebar:
            self.Margins = (0, 0)
            self.NoTitleBar = True
        self._mouse_offset_x = self._mouse_offset_y = 0

        if watermark:
            Window._watermark_temp_forced = True
            _global_settings_get_watermark_info()
        elif not watermark:
            Window._watermark = None
            Window._watermark_temp_forced = False

        self.ttk_part_overrides = TTKPartOverrides(
            sbar_trough_color=sbar_trough_color,
            sbar_background_color=sbar_background_color,
            sbar_arrow_color=sbar_arrow_color,
            sbar_width=sbar_width,
            sbar_arrow_width=sbar_arrow_width,
            sbar_frame_color=sbar_frame_color,
            sbar_relief=sbar_relief,
        )

        if no_titlebar:
            self.override_custom_titlebar = True

        if layout is not None and type(layout) not in (list, tuple):
            warnings.warn("Your layout is not a list or tuple... this is not good!")

        if layout is not None:
            self.Layout(layout)
            if finalize:
                self.Finalize()

        if CURRENT_LOOK_AND_FEEL == "Default":
            print(
                "Window will be a boring gray. Try removing the theme call entirely\n",
                "You will get the default theme or the one set in global settings\n"
                "If you seriously want this gray window and no more nagging, add  theme('DefaultNoMoreNagging')  or theme('Gray Gray Gray') for completely gray/System Defaults",
            )

    @classmethod
    def _GetAContainerNumber(cls):
        """
        Not user callable!
        :return: A simple counter that makes each container element unique
        :rtype:
        """
        cls._container_element_counter += 1
        return cls._container_element_counter

    @classmethod
    def _IncrementOpenCount(self):
        """
        Not user callable!  Increments the number of open windows
        Note - there is a bug where this count easily gets out of sync. Issue has been opened already. No ill effects
        """
        self.NumOpenWindows += 1
        # print('+++++ INCREMENTING Num Open Windows = {} ---'.format(Window.NumOpenWindows))

    @classmethod
    def _DecrementOpenCount(self):
        """
        Not user callable!  Decrements the number of open windows
        """
        self.NumOpenWindows -= 1 * (self.NumOpenWindows != 0)  # decrement if not 0
        # print('----- DECREMENTING Num Open Windows = {} ---'.format(Window.NumOpenWindows))

    @classmethod
    def get_screen_size(self):
        """
        This is a "Class Method" meaning you call it by writing: width, height = Window.get_screen_size()
        Returns the size of the "screen" as determined by tkinter.  This can vary depending on your operating system and the number of monitors installed on your system.  For Windows, the primary monitor's size is returns. On some multi-monitored Linux systems, the monitors are combined and the total size is reported as if one screen.

        :return: Size of the screen in pixels as determined by tkinter
        :rtype:  (int, int)
        """
        root = _get_hidden_master_root()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        return screen_width, screen_height

    @property
    def metadata(self):
        """
        Metadata is available for all windows. You can set to any value.
        :return: the current metadata value
        :rtype:  (Any)
        """
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        """
        Metadata is available for all windows. You can set to any value.
        :param value: Anything you want it to be
        :type value:  (Any)
        """
        self._metadata = value

    # ------------------------- Add ONE Row to Form ------------------------- #
    def add_row(self, *args):
        """
        Adds a single row of elements to a window's self.Rows variables.
        Generally speaking this is NOT how users should be building Window layouts.
        Users, create a single layout (a list of lists) and pass as a parameter to Window object, or call Window.Layout(layout)

        """
        NumRows = len(self.Rows)  # number of existing rows is our row number
        CurrentRowNumber = NumRows  # this row's number
        CurrentRow = []  # start with a blank row and build up
        # -------------------------  Add the elements to a row  ------------------------- #
        for i, element in enumerate(
            args
        ):  # Loop through list of elements and add them to the row
            if isinstance(element, tuple) or isinstance(element, list):
                self.add_row(*element)
                continue
                _error_popup_with_traceback(
                    "Error creating Window layout",
                    "Layout has a LIST instead of an ELEMENT",
                    "This sometimes means you have a badly placed ]",
                    "The offensive list is:",
                    element,
                    "This list will be stripped from your layout",
                )
                continue
            elif callable(element) and not isinstance(element, Element):
                _error_popup_with_traceback(
                    "Error creating Window layout",
                    "Layout has a FUNCTION instead of an ELEMENT",
                    "This likely means you are missing () from your layout",
                    "The offensive list is:",
                    element,
                    "This item will be stripped from your layout",
                )
                continue
            if element.ParentContainer is not None:
                warnings.warn(
                    "*** YOU ARE ATTEMPTING TO REUSE AN ELEMENT IN YOUR LAYOUT! Once placed in a layout, an element cannot be used in another layout. ***",
                    UserWarning,
                )
                _error_popup_with_traceback(
                    "Error detected in layout - Contains an element that has already been used.",
                    "You have attempted to reuse an element in your layout.",
                    "The layout specified has an element that's already been used.",
                    'You MUST start with a "clean", unused layout every time you create a window',
                    "The offensive Element = ",
                    element,
                    "and has a key = ",
                    element.Key,
                    "This item will be stripped from your layout",
                    'Hint - try printing your layout and matching the IDs "print(layout)"',
                )
                continue
            element.Position = (CurrentRowNumber, i)
            element.ParentContainer = self
            CurrentRow.append(element)
            # if this element is a titlebar, then automatically set the window margins to (0,0) and turn off normal titlebar
            if element.metadata == TITLEBAR_METADATA_MARKER:
                self.Margins = (0, 0)
                self.NoTitleBar = True
        # -------------------------  Append the row to list of Rows  ------------------------- #
        self.Rows.append(CurrentRow)

    # ------------------------- Add Multiple Rows to Form ------------------------- #
    def add_rows(self, rows):
        """
        Loops through a list of lists of elements and adds each row, list, to the layout.
        This is NOT the best way to go about creating a window.  Sending the entire layout at one time and passing
        it as a parameter to the Window call is better.

        :param rows: A list of a list of elements
        :type rows:  List[List[Elements]]
        """
        for row in rows:
            try:
                iter(row)
            except TypeError:
                _error_popup_with_traceback(
                    "Error Creating Window Layout",
                    "Error creating Window layout",
                    "Your row is not an iterable (e.g. a list)",
                    "Instead of a list, the type found was {}".format(type(row)),
                    "The offensive row = ",
                    row,
                    "This item will be stripped from your layout",
                )
                continue
            self.add_row(*row)
        # if _optional_window_data(self) is not None:
        #     self.add_row(_optional_window_data(self))
        if Window._watermark is not None:
            self.add_row(Window._watermark(self))

    def layout(self, rows):
        """
        Second of two preferred ways of telling a Window what its layout is. The other way is to pass the layout as
        a parameter to Window object.  The parameter method is the currently preferred method. This call to Layout
        has been removed from examples contained in documents and in the Demo Programs. Trying to remove this call
        from history and replace with sending as a parameter to Window.

        :param rows: Your entire layout
        :type rows:  List[List[Elements]]
        :return:     self so that you can chain method calls
        :rtype:      (Window)
        """
        if self.use_custom_titlebar and not self.override_custom_titlebar:
            if self.titlebar_icon is not None:
                icon = self.titlebar_icon
            elif CUSTOM_TITLEBAR_ICON is not None:
                icon = CUSTOM_TITLEBAR_ICON
            elif self.titlebar_icon is not None:
                icon = self.titlebar_icon
            elif self.WindowIcon == DEFAULT_WINDOW_ICON:
                icon = DEFAULT_BASE64_ICON_16_BY_16
            else:
                icon = None

            new_rows = [
                [
                    Titlebar(
                        title=self.Title,
                        icon=icon,
                        text_color=self.titlebar_text_color,
                        background_color=self.titlebar_background_color,
                        font=self.titlebar_font,
                    )
                ]
            ] + rows
        else:
            new_rows = rows
        self.add_rows(new_rows)
        self._BuildKeyDict()

        if self._has_custom_titlebar_element():
            self.Margins = (0, 0)
            self.NoTitleBar = True
            self._has_custom_titlebar = True
        return self

    def extend_layout(self, container, rows):
        """
        Adds new rows to an existing container element inside of this window
        If the container is a scrollable Column, you need to also call the contents_changed() method

        :param container: The container Element the layout will be placed inside of
        :type container:  Frame | Column | Tab
        :param rows:      The layout to be added
        :type rows:       (List[List[Element]])
        :return:          (Window) self so could be chained
        :rtype:           (Window)
        """
        column = Column(rows, pad=(0, 0), background_color=container.BackgroundColor)
        if self == container:
            frame = self.TKroot
        elif isinstance(container.Widget, TkScrollableFrame):
            frame = container.Widget.TKFrame
        else:
            frame = container.Widget
        PackFormIntoFrame(column, frame, self)
        # sg.PackFormIntoFrame(col, window.TKroot, window)
        self.AddRow(column)
        self.AllKeysDict = self._BuildKeyDictForWindow(self, column, self.AllKeysDict)
        return self

    def LayoutAndRead(self, rows, non_blocking=False):
        """
        Deprecated!!  Now your layout your window's rows (layout) and then separately call Read.

        :param rows:         The layout of the window
        :type rows:          List[List[Element]]
        :param non_blocking: if True the Read call will not block
        :type non_blocking:  (bool)
        """
        _error_popup_with_traceback(
            "LayoutAndRead Depricated",
            "Wow!  You have been using PySimpleGUI for a very long time.",
            "The Window.LayoutAndRead call is no longer supported",
        )

        raise DeprecationWarning(
            "LayoutAndRead is no longer supported... change your call window.Layout(layout).Read()\nor window(title, layout).Read()"
        )
        # self.AddRows(rows)
        # self._Show(non_blocking=non_blocking)
        # return self.ReturnValues

    def LayoutAndShow(self, rows):
        """
        Deprecated - do not use any longer.  Layout your window and then call Read.  Or can add a Finalize call before the Read
        """
        raise DeprecationWarning("LayoutAndShow is no longer supported... ")

    def _Show(self, non_blocking=False):
        """
        NOT TO BE CALLED BY USERS.  INTERNAL ONLY!
        It's this method that first shows the window to the user, collects results

        :param non_blocking: if True, this is a non-blocking call
        :type non_blocking:  (bool)
        :return:             Tuple[Any, Dict] The event, values turple that is returned from Read calls
        :rtype:
        """
        self.Shown = True
        # Compute num rows & num cols (it'll come in handy debugging)
        self.NumRows = len(self.Rows)
        self.NumCols = max(len(row) for row in self.Rows)
        self.NonBlocking = non_blocking

        # Search through entire form to see if any elements set the focus
        # if not, then will set the focus to the first input element
        found_focus = False
        for row in self.Rows:
            for element in row:
                try:
                    if element.Focus:
                        found_focus = True
                except Exception:
                    pass
                try:
                    if element.Key is not None:
                        self.UseDictionary = True
                except Exception:
                    pass

        if not found_focus and self.UseDefaultFocus:
            self.UseDefaultFocus = True
        else:
            self.UseDefaultFocus = False
        # -=-=-=-=-=-=-=-=- RUN the GUI -=-=-=-=-=-=-=-=- ##
        StartupTK(self)
        # If a button or keyboard event happened but no results have been built, build the results
        if self.LastKeyboardEvent is not None or self.LastButtonClicked is not None:
            return _BuildResults(self, False, self)
        return self.ReturnValues

    # ------------------------- SetIcon - set the window's fav icon ------------------------- #
    def set_icon(self, icon=None, pngbase64=None):
        """
        Changes the icon that is shown on the title bar and on the task bar.
        NOTE - The file type is IMPORTANT and depends on the OS!
        Can pass in:
        * filename which must be a .ICO icon file for windows, PNG file for Linux
        * bytes object
        * BASE64 encoded file held in a variable

        :param icon:      Filename or bytes object
        :type icon:       (str)
        :param pngbase64: Base64 encoded image
        :type pngbase64:  (bytes)
        """
        if type(icon) is bytes or pngbase64 is not None:
            wicon = tkinter.PhotoImage(data=icon if icon is not None else pngbase64)
            try:
                self.TKroot.tk.call("wm", "iconphoto", self.TKroot._w, wicon)
            except Exception:
                wicon = tkinter.PhotoImage(data=DEFAULT_BASE64_ICON)
                try:
                    self.TKroot.tk.call("wm", "iconphoto", self.TKroot._w, wicon)
                except Exception:
                    pass
            self.WindowIcon = wicon
            return

        wicon = icon
        try:
            self.TKroot.iconbitmap(icon)
        except Exception:
            try:
                wicon = tkinter.PhotoImage(file=icon)
                self.TKroot.tk.call("wm", "iconphoto", self.TKroot._w, wicon)
            except Exception:
                try:
                    wicon = tkinter.PhotoImage(data=DEFAULT_BASE64_ICON)
                    try:
                        self.TKroot.tk.call("wm", "iconphoto", self.TKroot._w, wicon)
                    except Exception:
                        pass
                except Exception:
                    pass
        self.WindowIcon = wicon

    def _GetElementAtLocation(self, location):
        """
        Given a (row, col) location in a layout, return the element located at that position

        :param location: (int, int) Return the element located at (row, col) in layout
        :type location:
        :return:         (Element) The Element located at that position in this window
        :rtype:
        """

        (row_num, col_num) = location
        row = self.Rows[row_num]
        element = row[col_num]
        return element

    def _GetDefaultElementSize(self):
        """
        Returns the default elementSize

        :return: (width, height) of the default element size
        :rtype:  (int, int)
        """

        return self.DefaultElementSize

    def _AutoCloseAlarmCallback(self):
        """
        Function that's called by tkinter when autoclode timer expires.  Closes the window

        """
        try:
            window = self
            if window:
                if window.NonBlocking:
                    self.Close()
                else:
                    window._Close()
                    self.TKroot.quit()
                    self.RootNeedsDestroying = True
        except Exception:
            pass

    def _TimeoutAlarmCallback(self):
        """
        Read Timeout Alarm callback. Will kick a mainloop call out of the tkinter event loop and cause it to return
        """
        # first, get the results table built
        # modify the Results table in the parent FlexForm object
        # print('TIMEOUT CALLBACK')
        if self.TimerCancelled:
            # print('** timer was cancelled **')
            return
        self.LastButtonClicked = self.TimeoutKey
        self.FormRemainedOpen = True
        self.TKroot.quit()  # kick the users out of the mainloop

    def _calendar_chooser_button_clicked(self, elem):
        """

        :param elem:
        :type elem:
        :return:
        :rtype:
        """
        target_element, strvar, should_submit_window = elem._find_target()

        if elem.calendar_default_date_M_D_Y == (None, None, None):
            now = datetime.datetime.now()
            cur_month, cur_day, cur_year = now.month, now.day, now.year
        else:
            cur_month, cur_day, cur_year = elem.calendar_default_date_M_D_Y

        date_chosen = popup_get_date(
            start_mon=cur_month,
            start_day=cur_day,
            start_year=cur_year,
            close_when_chosen=elem.calendar_close_when_chosen,
            no_titlebar=elem.calendar_no_titlebar,
            begin_at_sunday_plus=elem.calendar_begin_at_sunday_plus,
            locale=elem.calendar_locale,
            location=elem.calendar_location,
            month_names=elem.calendar_month_names,
            day_abbreviations=elem.calendar_day_abbreviations,
            title=elem.calendar_title,
        )
        if date_chosen is not None:
            month, day, year = date_chosen
            now = datetime.datetime.now()
            hour, minute, second = now.hour, now.minute, now.second
            try:
                date_string = calendar.datetime.datetime(
                    year, month, day, hour, minute, second
                ).strftime(elem.calendar_format)
            except Exception as e:
                print("Bad format string in calendar chooser button", e)
                date_string = "Bad format string"

            if target_element is not None and target_element != elem:
                target_element.update(date_string)
            elif target_element == elem:
                elem.calendar_selection = date_string

            strvar.set(date_string)
            elem.TKStringVar.set(date_string)
            if should_submit_window:
                self.LastButtonClicked = target_element.Key
                results = _BuildResults(self, False, self)
        else:
            should_submit_window = False
        return should_submit_window

    # @_timeit_summary
    def read(self, timeout=None, timeout_key=TIMEOUT_KEY, close=False):
        """
        THE biggest deal method in the Window class! This is how you get all of your data from your Window.
            Pass in a timeout (in milliseconds) to wait for a maximum of timeout milliseconds. Will return timeout_key
            if no other GUI events happen first.

        :param timeout:     Milliseconds to wait until the Read will return IF no other GUI events happen first
        :type timeout:      (int)
        :param timeout_key: The value that will be returned from the call if the timer expired
        :type timeout_key:  (Any)
        :param close:       if True the window will be closed prior to returning
        :type close:        (bool)
        :return:            (event, values)
        :rtype:             Tuple[(Any), Dict[Any, Any], List[Any], None]
        """

        if Window._floating_debug_window_build_needed:
            Window._floating_debug_window_build_needed = False
            _Debugger.debugger._build_floating_window()

        if Window._main_debug_window_build_needed:
            Window._main_debug_window_build_needed = False
            _Debugger.debugger._build_main_debugger_window()

        # ensure called only 1 time through a single read cycle
        if not Window._read_call_from_debugger:
            _refresh_debugger()

        # if the user has not added timeout and a debug window is open, then set a timeout for them so the debugger continuously refreshes
        if _debugger_window_is_open() and not Window._read_call_from_debugger:
            if timeout is None or timeout > 3000:
                timeout = 200

        while True:
            Window._root_running_mainloop = self.TKroot
            results = self._read(timeout=timeout, timeout_key=timeout_key)
            if results is not None:
                if results[0] == DEFAULT_WINDOW_SNAPSHOT_KEY:
                    self.save_window_screenshot_to_disk()
                    popup_quick_message(
                        "Saved window screenshot to disk",
                        background_color="#1c1e23",
                        text_color="white",
                        keep_on_top=True,
                        font="_ 30",
                    )
                    continue
            # Post processing for Calendar Chooser Button
            try:
                if (
                    results[0] == timeout_key
                ):  # if a timeout, then not a calendar button
                    break
                elem = self.find_element(
                    results[0], silent_on_error=True
                )  # get the element that caused the event
                if elem.Type == ELEM_TYPE_BUTTON:
                    if elem.BType == BUTTON_TYPE_CALENDAR_CHOOSER:
                        if self._calendar_chooser_button_clicked(
                            elem
                        ):  # returns True if should break out
                            # results[0] = self.LastButtonClicked
                            results = self.ReturnValues
                            break
                        else:
                            continue
                break
            except Exception:
                break  # wasn't a calendar button for sure

        if close:
            self.close()

        return results

    # @_timeit
    def _read(self, timeout=None, timeout_key=TIMEOUT_KEY):
        """
        THE biggest deal method in the Window class! This is how you get all of your data from your Window.
            Pass in a timeout (in milliseconds) to wait for a maximum of timeout milliseconds. Will return timeout_key
            if no other GUI events happen first.

        :param timeout:     Milliseconds to wait until the Read will return IF no other GUI events happen first
        :type timeout:      (int)
        :param timeout_key: The value that will be returned from the call if the timer expired
        :type timeout_key:  (Any)
        :return:            (event, values) (event or timeout_key or None, Dictionary of values or List of values from all elements in the Window)
        :rtype:             Tuple[(Any), Dict[Any, Any], List[Any], None]
        """

        # if there are events in the thread event queue, then return those events before doing anything else.
        if self._queued_thread_event_available():
            self.ReturnValues = results = _BuildResults(self, False, self)
            return results

        if self.finalize_in_progress and self.auto_close_timer_needs_starting:
            self._start_autoclose_timer()
            self.auto_close_timer_needs_starting = False

        timeout = int(timeout) if timeout is not None else None
        if timeout == 0:  # timeout of zero runs the old readnonblocking
            event, values = self._ReadNonBlocking()
            if event is None:
                event = timeout_key
            if values is None:
                event = None
            return event, values  # make event None if values was None and return
        # Read with a timeout
        self.Timeout = timeout
        self.TimeoutKey = timeout_key
        self.NonBlocking = False
        if self.TKrootDestroyed:
            self.read_closed_window_count += 1
            if self.read_closed_window_count > 100:
                popup_error_with_traceback(
                    "Trying to read a closed window",
                    "You have tried 100 times to read a closed window.",
                    "You need to add a check for event == WIN_CLOSED",
                )
            return None, None
        if not self.Shown:
            self._Show()
        else:
            # if already have a button waiting, the return previously built results
            if (
                self.LastButtonClicked is not None
                and not self.LastButtonClickedWasRealtime
            ):
                results = _BuildResults(self, False, self)
                self.LastButtonClicked = None
                return results
            InitializeResults(self)

            if self._queued_thread_event_available():
                self.ReturnValues = results = _BuildResults(self, False, self)
                return results

            # if the last button clicked was realtime, emulate a read non-blocking
            # the idea is to quickly return realtime buttons without any blocks until released
            if self.LastButtonClickedWasRealtime:
                # clear the realtime flag if the element is not a button element (for example a graph element that is dragging)
                if self.AllKeysDict.get(self.LastButtonClicked, None):
                    if (
                        self.AllKeysDict.get(self.LastButtonClicked).Type
                        != ELEM_TYPE_BUTTON
                    ):
                        self.LastButtonClickedWasRealtime = False  # stops from generating events until something changes
                else:  # it is possible for the key to not be in the dicitonary because it has a modifier. If so, then clear the realtime button flag
                    self.LastButtonClickedWasRealtime = (
                        False  # stops from generating events until something changes
                    )

                try:
                    rc = self.TKroot.update()
                except Exception:
                    self.TKrootDestroyed = True
                    Window._DecrementOpenCount()
                    # _my_windows.Decrement()
                    # print('ROOT Destroyed')
                results = _BuildResults(self, False, self)
                if results[0] is not None and results[0] != timeout_key:
                    return results
                else:
                    pass

                # else:
                #     print("** REALTIME PROBLEM FOUND **", results)

            if self.RootNeedsDestroying:
                # print('*** DESTROYING really late***')
                try:
                    self.TKroot.destroy()
                except Exception:
                    pass
                # _my_windows.Decrement()
                self.LastButtonClicked = None
                return None, None

            # normal read blocking code....
            if timeout is not None:
                self.TimerCancelled = False
                self.TKAfterID = self.TKroot.after(timeout, self._TimeoutAlarmCallback)
            self.CurrentlyRunningMainloop = True
            # self.TKroot.protocol("WM_DESTROY_WINDOW", self._OnClosingCallback)
            # self.TKroot.protocol("WM_DELETE_WINDOW", self._OnClosingCallback)
            Window._window_running_mainloop = self
            try:
                Window._root_running_mainloop.mainloop()
            except Exception:
                print("**** EXITING ****")
                exit(-1)
            # print('Out main')
            self.CurrentlyRunningMainloop = False
            # if self.LastButtonClicked != TIMEOUT_KEY:
            try:
                self.TKroot.after_cancel(self.TKAfterID)
                del self.TKAfterID
            except Exception:
                pass
                # print('** tkafter cancel failed **')
            self.TimerCancelled = True
            if self.RootNeedsDestroying:
                # print('*** DESTROYING LATE ***')
                try:
                    self.TKroot.destroy()
                except Exception:
                    pass
                Window._DecrementOpenCount()
                # _my_windows.Decrement()
                self.LastButtonClicked = None
                return None, None
            # if form was closed with X
            if (
                self.LastButtonClicked is None
                and self.LastKeyboardEvent is None
                and self.ReturnValues[0] is None
            ):
                Window._DecrementOpenCount()
                # _my_windows.Decrement()
        # Determine return values
        if self.LastKeyboardEvent is not None or self.LastButtonClicked is not None:
            results = _BuildResults(self, False, self)
            if not self.LastButtonClickedWasRealtime:
                self.LastButtonClicked = None
            return results
        else:
            if self._queued_thread_event_available():
                self.ReturnValues = results = _BuildResults(self, False, self)
                return results
            if (
                not self.XFound
                and self.Timeout != 0
                and self.Timeout is not None
                and self.ReturnValues[0] is None
            ):  # Special Qt case because returning for no reason so fake timeout
                self.ReturnValues = (
                    self.TimeoutKey,
                    self.ReturnValues[1],
                )  # fake a timeout
            elif (
                not self.XFound and self.ReturnValues[0] is None
            ):  # Return a timeout event... can happen when autoclose used on another window
                # print("*** Faking timeout ***")
                self.ReturnValues = (
                    self.TimeoutKey,
                    self.ReturnValues[1],
                )  # fake a timeout
            return self.ReturnValues

    def _ReadNonBlocking(self):
        """
        Should be NEVER called directly by the user.  The user can call Window.read(timeout=0) to get same effect

        :return: (event, values). (event or timeout_key or None, Dictionary of values or List of values from all elements in the Window)
        :rtype:  Tuple[(Any), Dict[Any, Any] | List[Any] | None]
        """
        if self.TKrootDestroyed:
            try:
                self.TKroot.quit()
                self.TKroot.destroy()
            except Exception:
                pass
                # print('DESTROY FAILED')
            return None, None
        if not self.Shown:
            self._Show(non_blocking=True)
        try:
            rc = self.TKroot.update()
        except Exception:
            self.TKrootDestroyed = True
            Window._DecrementOpenCount()
            # _my_windows.Decrement()
            # print("read failed")
            # return None, None
        if self.RootNeedsDestroying:
            # print('*** DESTROYING LATE ***', self.ReturnValues)
            self.TKroot.destroy()
            Window._DecrementOpenCount()
            # _my_windows.Decrement()
            self.Values = None
            self.LastButtonClicked = None
            return None, None
        return _BuildResults(self, False, self)

    def _start_autoclose_timer(self):
        duration = (
            DEFAULT_AUTOCLOSE_TIME
            if self.AutoCloseDuration is None
            else self.AutoCloseDuration
        )
        self.TKAfterID = self.TKroot.after(
            int(duration * 1000), self._AutoCloseAlarmCallback
        )

    def finalize(self):
        """
        Use this method to cause your layout to built into a real tkinter window.  In reality this method is like
        Read(timeout=0).  It doesn't block and uses your layout to create tkinter widgets to represent the elements.
        Lots of action!

        :return: Returns 'self' so that method "Chaining" can happen (read up about it as it's very cool!)
        :rtype:  (Window)
        """

        if self.TKrootDestroyed:
            return self
        self.finalize_in_progress = True

        self.Read(timeout=1)

        if self.AutoClose:
            self.auto_close_timer_needs_starting = True
        # add the window to the list of active windows
        Window._active_windows[self] = Window.hidden_master_root
        return self
        # OLD CODE FOLLOWS
        if not self.Shown:
            self._Show(non_blocking=True)
        try:
            rc = self.TKroot.update()
        except Exception:
            self.TKrootDestroyed = True
            Window._DecrementOpenCount()
            print("** Finalize failed **")
            # _my_windows.Decrement()
            # return None, None
        return self

    def refresh(self):
        """
        Refreshes the window by calling tkroot.update().  Can sometimes get away with a refresh instead of a Read.
        Use this call when you want something to appear in your Window immediately (as soon as this function is called).
        If you change an element in a window, your change will not be visible until the next call to Window.read
        or a call to Window.refresh()

        :return: `self` so that method calls can be easily "chained"
        :rtype:  (Window)
        """

        if self.TKrootDestroyed:
            return self
        try:
            rc = self.TKroot.update()
        except Exception:
            pass
        return self

    def fill(self, values_dict):
        """
        Fill in elements that are input fields with data based on a 'values dictionary'

        :param values_dict: pairs
        :type values_dict:  (Dict[Any, Any]) - {Element_key : value}
        :return:            returns self so can be chained with other methods
        :rtype:             (Window)
        """

        FillFormWithValues(self, values_dict)
        return self

    def _find_closest_key(self, search_key):
        if not isinstance(search_key, str):
            search_key = str(search_key)
        matches = difflib.get_close_matches(
            search_key, [str(k) for k in self.AllKeysDict.keys()]
        )
        if not len(matches):
            return None
        for k in self.AllKeysDict.keys():
            if matches[0] == str(k):
                return k
        return matches[0] if len(matches) else None

    def FindElement(self, key, silent_on_error=False):
        """
        ** Warning ** This call will eventually be depricated. **

        It is suggested that you modify your code to use the recommended window[key] lookup or the PEP8 compliant window.find_element(key)

        For now, you'll only see a message printed and the call will continue to funcation as before.

        :param key:             Used with window.find_element and with return values to uniquely identify this element
        :type key:              str | int | tuple | object
        :param silent_on_error: If True do not display popup nor print warning of key errors
        :type silent_on_error:  (bool)
        :return:                Return value can be: the Element that matches the supplied key if found; an Error Element if silent_on_error is False; None if silent_on_error True;
        :rtype:                 Element | Error Element | None
        """

        warnings.warn(
            "Use of FindElement is not recommended.\nEither switch to the recommended window[key] format\nor the PEP8 compliant find_element",
            UserWarning,
        )
        print(
            "** Warning - FindElement should not be used to look up elements. window[key] or window.find_element are recommended. **"
        )

        return self.find_element(key, silent_on_error=silent_on_error)

    def find_element(
        self, key, silent_on_error=False, supress_guessing=None, supress_raise=None
    ):
        """
        Find element object associated with the provided key.
        THIS METHOD IS NO LONGER NEEDED to be called by the user

        You can perform the same operation by writing this statement:
        element = window[key]

        You can drop the entire "find_element" function name and use [ ] instead.

        However, if you wish to perform a lookup without error checking, and don't have error popups turned
        off globally, you'll need to make this call so that you can disable error checks on this call.

        find_element is typically used in combination with a call to element's update method (or any other element method!):
        window[key].update(new_value)

        Versus the "old way"
        window.FindElement(key).Update(new_value)

        This call can be abbreviated to any of these:
        find_element = FindElement == Element == Find
        With find_element being the PEP8 compliant call that should be used.

        Rememeber that this call will return None if no match is found which may cause your code to crash if not
        checked for.

        :param key:              Used with window.find_element and with return values to uniquely identify this element
        :type key:               str | int | tuple | object
        :param silent_on_error:  If True do not display popup nor print warning of key errors
        :type silent_on_error:   (bool)
        :param supress_guessing: Override for the global key guessing setting.
        :type supress_guessing:  (bool | None)
        :param supress_raise:    Override for the global setting that determines if a key error should raise an exception
        :type supress_raise:     (bool | None)
        :return:                 Return value can be: the Element that matches the supplied key if found; an Error Element if silent_on_error is False; None if silent_on_error True
        :rtype:                  Element | ErrorElement | None
        """

        key_error = False
        closest_key = None
        supress_guessing = (
            supress_guessing if supress_guessing is not None else SUPPRESS_KEY_GUESSING
        )
        supress_raise = (
            supress_raise if supress_raise is not None else SUPPRESS_RAISE_KEY_ERRORS
        )
        try:
            element = self.AllKeysDict[key]
        except KeyError:
            key_error = True
            closest_key = self._find_closest_key(key)
            if not silent_on_error:
                print(
                    "** Error looking up your element using the key: ",
                    key,
                    "The closest matching key: ",
                    closest_key,
                )
                _error_popup_with_traceback(
                    "Key Error",
                    "Problem finding your key " + str(key),
                    "Closest match = " + str(closest_key),
                    emoji=EMOJI_BASE64_KEY,
                )
                element = ErrorElement(key=key)
            else:
                element = None
            if not supress_raise:
                raise KeyError(key)

        if key_error:
            if not supress_guessing and closest_key is not None:
                element = self.AllKeysDict[closest_key]

        return element

    Element = find_element  # Shortcut function
    Find = find_element  # Shortcut function, most likely not used by many people.
    Elem = find_element  # NEW for 2019!  More laziness... Another shortcut

    def find_element_with_focus(self):
        """
        Returns the Element that currently has focus as reported by tkinter. If no element is found None is returned!
        :return: An Element if one has been found with focus or None if no element found
        :rtype:  Element | None
        """
        element = _FindElementWithFocusInSubForm(self)
        return element

    def widget_to_element(self, widget):
        """
        Returns the element that matches a supplied tkinter widget.
        If no matching element is found, then None is returned.


        :return:    Element that uses the specified widget
        :rtype:     Element | None
        """
        if self.AllKeysDict is None or len(self.AllKeysDict) == 0:
            return None
        for key, element in self.AllKeysDict.items():
            if element.Widget == widget:
                return element
        return None

    def _BuildKeyDict(self):
        """
        Used internally only! Not user callable
        Builds a dictionary containing all elements with keys for this window.
        """
        dict = {}
        self.AllKeysDict = self._BuildKeyDictForWindow(self, self, dict)

    def _BuildKeyDictForWindow(self, top_window, window, key_dict):
        """
        Loop through all Rows and all Container Elements for this window and create the keys for all of them.
        Note that the calls are recursive as all pathes must be walked

        :param top_window: The highest level of the window
        :type top_window:  (Window)
        :param window:     The "sub-window" (container element) to be searched
        :type window:      Column | Frame | TabGroup | Pane | Tab
        :param key_dict:   The dictionary as it currently stands.... used as part of recursive call
        :type key_dict:
        :return:           (dict) Dictionary filled with all keys in the window
        :rtype:
        """
        for row_num, row in enumerate(window.Rows):
            for col_num, element in enumerate(row):
                if element.Type == ELEM_TYPE_COLUMN:
                    key_dict = self._BuildKeyDictForWindow(
                        top_window, element, key_dict
                    )
                if element.Type == ELEM_TYPE_FRAME:
                    key_dict = self._BuildKeyDictForWindow(
                        top_window, element, key_dict
                    )
                if element.Type == ELEM_TYPE_TAB_GROUP:
                    key_dict = self._BuildKeyDictForWindow(
                        top_window, element, key_dict
                    )
                if element.Type == ELEM_TYPE_PANE:
                    key_dict = self._BuildKeyDictForWindow(
                        top_window, element, key_dict
                    )
                if element.Type == ELEM_TYPE_TAB:
                    key_dict = self._BuildKeyDictForWindow(
                        top_window, element, key_dict
                    )
                if (
                    element.Key is None
                ):  # if no key has been assigned.... create one for input elements
                    if element.Type == ELEM_TYPE_BUTTON:
                        element.Key = element.ButtonText
                    elif element.Type == ELEM_TYPE_TAB:
                        element.Key = element.Title
                    if element.Type in (
                        ELEM_TYPE_MENUBAR,
                        ELEM_TYPE_BUTTONMENU,
                        ELEM_TYPE_INPUT_SLIDER,
                        ELEM_TYPE_GRAPH,
                        ELEM_TYPE_IMAGE,
                        ELEM_TYPE_INPUT_CHECKBOX,
                        ELEM_TYPE_INPUT_LISTBOX,
                        ELEM_TYPE_INPUT_COMBO,
                        ELEM_TYPE_INPUT_MULTILINE,
                        ELEM_TYPE_INPUT_OPTION_MENU,
                        ELEM_TYPE_INPUT_SPIN,
                        ELEM_TYPE_INPUT_RADIO,
                        ELEM_TYPE_INPUT_TEXT,
                        ELEM_TYPE_PROGRESS_BAR,
                        ELEM_TYPE_TABLE,
                        ELEM_TYPE_TREE,
                        ELEM_TYPE_TAB_GROUP,
                        ELEM_TYPE_SEPARATOR,
                    ):
                        element.Key = top_window.DictionaryKeyCounter
                        top_window.DictionaryKeyCounter += 1
                if element.Key is not None:
                    if element.Key in key_dict.keys():
                        if (
                            element.Type == ELEM_TYPE_BUTTON
                            and WARN_DUPLICATE_BUTTON_KEY_ERRORS
                        ):  # for Buttons see if should complain
                            warnings.warn(
                                "*** Duplicate key found in your layout {} ***".format(
                                    element.Key
                                ),
                                UserWarning,
                            )
                            warnings.warn(
                                "*** Replaced new key with {} ***".format(
                                    str(element.Key) + str(self.UniqueKeyCounter)
                                )
                            )
                            if not SUPPRESS_ERROR_POPUPS:
                                _error_popup_with_traceback(
                                    "Duplicate key found in your layout",
                                    "Dupliate key: {}".format(element.Key),
                                    "Is being replaced with: {}".format(
                                        str(element.Key) + str(self.UniqueKeyCounter)
                                    ),
                                    "The line of code above shows you which layout, but does not tell you exactly where the element was defined",
                                    "The element type is {}".format(element.Type),
                                )
                        element.Key = str(element.Key) + str(self.UniqueKeyCounter)
                        self.UniqueKeyCounter += 1
                    key_dict[element.Key] = element
        return key_dict

    def element_list(self):
        """
        Returns a list of all elements in the window

        :return: List of all elements in the window and container elements in the window
        :rtype:  List[Element]
        """
        return self._build_element_list()

    def _build_element_list(self):
        """
        Used internally only! Not user callable
        Builds a dictionary containing all elements with keys for this window.
        """
        elem_list = []
        elem_list = self._build_element_list_for_form(self, self, elem_list)
        return elem_list

    def _build_element_list_for_form(self, top_window, window, elem_list):
        """
        Loop through all Rows and all Container Elements for this window and create a list
        Note that the calls are recursive as all pathes must be walked

        :param top_window: The highest level of the window
        :type top_window:  (Window)
        :param window:     The "sub-window" (container element) to be searched
        :type window:      Column | Frame | TabGroup | Pane | Tab
        :param elem_list:  The element list as it currently stands.... used as part of recursive call
        :type elem_list:   ???
        :return:           List of all elements in this sub-window
        :rtype:            List[Element]
        """
        for row_num, row in enumerate(window.Rows):
            for col_num, element in enumerate(row):
                elem_list.append(element)
                if element.Type in (
                    ELEM_TYPE_COLUMN,
                    ELEM_TYPE_FRAME,
                    ELEM_TYPE_TAB_GROUP,
                    ELEM_TYPE_PANE,
                    ELEM_TYPE_TAB,
                ):
                    elem_list = self._build_element_list_for_form(
                        top_window, element, elem_list
                    )
        return elem_list

    def save_to_disk(self, filename):
        """
        Saves the values contained in each of the input areas of the form. Basically saves what would be returned from a call to Read.  It takes these results and saves them to disk using pickle.
         Note that every element in your layout that is to be saved must have a key assigned to it.

        :param filename: Filename to save the values to in pickled form
        :type filename:  str
        """
        try:
            event, values = _BuildResults(self, False, self)
            remove_these = []
            for key in values:
                if self.Element(key).Type == ELEM_TYPE_BUTTON:
                    remove_these.append(key)
            for key in remove_these:
                del values[key]
            with open(filename, "wb") as sf:
                pickle.dump(values, sf)
        except Exception:
            print("*** Error saving Window contents to disk ***")

    def load_from_disk(self, filename):
        """
        Restore values from a previous call to SaveToDisk which saves the returned values dictionary in Pickle format

        :param filename: Pickle Filename to load
        :type filename:  (str)
        """
        try:
            with open(filename, "rb") as df:
                self.Fill(pickle.load(df))
        except Exception:
            print("*** Error loading form to disk ***")

    def get_screen_dimensions(self):
        """
        Get the screen dimensions.  NOTE - you must have a window already open for this to work (blame tkinter not me)

        :return: Tuple containing width and height of screen in pixels
        :rtype:  Tuple[None, None] | Tuple[width, height]
        """

        if self.TKrootDestroyed or self.TKroot is None:
            return Window.get_screen_size()
        screen_width = (
            self.TKroot.winfo_screenwidth()
        )  # get window info to move to middle of screen
        screen_height = self.TKroot.winfo_screenheight()
        return screen_width, screen_height

    def move(self, x, y):
        """
        Move the upper left corner of this window to the x,y coordinates provided
        :param x: x coordinate in pixels
        :type x:  (int)
        :param y: y coordinate in pixels
        :type y:  (int)
        """
        try:
            self.TKroot.geometry("+%s+%s" % (x, y))
            self.config_last_location = (int(x), (int(y)))

        except Exception:
            pass

    def move_to_center(self):
        """
        Recenter your window after it's been moved or the size changed.

        This is a conveinence method. There are no tkinter calls involved, only pure PySimpleGUI API calls.
        """
        if not self._is_window_created("tried Window.move_to_center"):
            return
        screen_width, screen_height = self.get_screen_dimensions()
        win_width, win_height = self.size
        x, y = (screen_width - win_width) // 2, (screen_height - win_height) // 2
        self.move(x, y)

    def minimize(self):
        """
        Minimize this window to the task bar
        """
        if not self._is_window_created("tried Window.minimize"):
            return
        if self.use_custom_titlebar:
            self._custom_titlebar_minimize()
        else:
            self.TKroot.iconify()
        self.maximized = False

    def maximize(self):
        """
        Maximize the window. This is done differently on a windows system versus a linux or mac one.  For non-Windows
        the root attribute '-fullscreen' is set to True.  For Windows the "root" state is changed to "zoomed"
        The reason for the difference is the title bar is removed in some cases when using fullscreen option
        """

        if not self._is_window_created("tried Window.maximize"):
            return
        if not running_linux():
            self.TKroot.state("zoomed")
        else:
            self.TKroot.attributes("-fullscreen", True)
        # this method removes the titlebar too
        # self.TKroot.attributes('-fullscreen', True)
        self.maximized = True

    def normal(self):
        """
        Restore a window to a non-maximized state.  Does different things depending on platform.  See Maximize for more.
        """
        if not self._is_window_created("tried Window.normal"):
            return
        if self.use_custom_titlebar:
            self._custom_titlebar_restore()
        else:
            if self.TKroot.state() == "iconic":
                self.TKroot.deiconify()
            else:
                if not running_linux():
                    self.TKroot.state("normal")
                else:
                    self.TKroot.attributes("-fullscreen", False)
            self.maximized = False

    def _StartMoveUsingControlKey(self, event):
        """
        Used by "Grab Anywhere" style windows. This function is bound to mouse-down. It marks the beginning of a drag.
        :param event: event information passed in by tkinter. Contains x,y position of mouse
        :type event:  (event)
        """
        self._start_move_save_offset(event)
        return

    def _StartMoveGrabAnywhere(self, event):
        """
        Used by "Grab Anywhere" style windows. This function is bound to mouse-down. It marks the beginning of a drag.
        :param event: event information passed in by tkinter. Contains x,y position of mouse
        :type event:  (event)
        """
        if (
            isinstance(event.widget, GRAB_ANYWHERE_IGNORE_THESE_WIDGETS)
            or event.widget in self._grab_anywhere_ignore_these_list
        ) and event.widget not in self._grab_anywhere_include_these_list:
            # print('Found widget to ignore in grab anywhere...')
            return
        self._start_move_save_offset(event)

    def _StartMove(self, event):
        self._start_move_save_offset(event)
        return

    def _StopMove(self, event):
        """
        Used by "Grab Anywhere" style windows. This function is bound to mouse-up. It marks the ending of a drag.
        Sets the position of the window to this final x,y coordinates
        :param event: event information passed in by tkinter. Contains x,y position of mouse
        :type event:  (event)
        """
        return

    def _start_move_save_offset(self, event):
        self._mousex = event.x + event.widget.winfo_rootx()
        self._mousey = event.y + event.widget.winfo_rooty()
        geometry = self.TKroot.geometry()
        location = geometry[geometry.find("+") + 1 :].split("+")
        self._startx = int(location[0])
        self._starty = int(location[1])
        self._mouse_offset_x = self._mousex - self._startx
        self._mouse_offset_y = self._mousey - self._starty
        # ------ Move All Windows code ------
        if Window._move_all_windows:
            # print('Moving all')
            for win in Window._active_windows:
                if win == self:
                    continue
                geometry = win.TKroot.geometry()
                location = geometry[geometry.find("+") + 1 :].split("+")
                _startx = int(location[0])
                _starty = int(location[1])
                win._mouse_offset_x = event.x_root - _startx
                win._mouse_offset_y = event.y_root - _starty

    def _OnMotionUsingControlKey(self, event):
        self._OnMotion(event)

    def _OnMotionGrabAnywhere(self, event):
        """
        Used by "Grab Anywhere" style windows. This function is bound to mouse motion. It actually moves the window
        :param event: event information passed in by tkinter. Contains x,y position of mouse
        :type event:  (event)
        """
        if (
            isinstance(event.widget, GRAB_ANYWHERE_IGNORE_THESE_WIDGETS)
            or event.widget in self._grab_anywhere_ignore_these_list
        ) and event.widget not in self._grab_anywhere_include_these_list:
            # print('Found widget to ignore in grab anywhere...')
            return

        self._OnMotion(event)

    def _OnMotion(self, event):
        self.TKroot.geometry(
            f"+{event.x_root - self._mouse_offset_x}+{event.y_root - self._mouse_offset_y}"
        )
        # print(f"+{event.x_root}+{event.y_root}")
        # ------ Move All Windows code ------
        try:
            if Window._move_all_windows:
                for win in Window._active_windows:
                    if win == self:
                        continue
                    win.TKroot.geometry(
                        f"+{event.x_root - win._mouse_offset_x}+{event.y_root - win._mouse_offset_y}"
                    )
        except Exception as e:
            print("on motion error", e)

    def _focus_callback(self, event):
        print("Focus event = {} window = {}".format(event, self.Title))

    def _config_callback(self, event):
        """
        Called when a config event happens for the window

        :param event:            From tkinter and is not used
        :type event:             Any
        """
        self.LastButtonClicked = WINDOW_CONFIG_EVENT
        self.FormRemainedOpen = True
        self.user_bind_event = event
        _exit_mainloop(self)

    def _move_callback(self, event):
        """
        Called when a control + arrow key is pressed.
        This is a built-in window positioning key sequence

        :param event:            From tkinter and is not used
        :type event:             Any
        """
        if not self._is_window_created("Tried to move window using arrow keys"):
            return
        x, y = self.current_location()
        if event.keysym == "Up":
            self.move(x, y - 1)
        elif event.keysym == "Down":
            self.move(x, y + 1)
        elif event.keysym == "Left":
            self.move(x - 1, y)
        elif event.keysym == "Right":
            self.move(x + 1, y)

    """
    def _config_callback(self, event):
        new_x = event.x
        new_y = event.y


        if self.not_completed_initial_movement:
            if self.starting_window_position != (new_x, new_y):
                return
            self.not_completed_initial_movement = False
            return

        if not self.saw_00:
            if new_x == 0 and new_y == 0:
                self.saw_00 = True

        # self.config_count += 1
        # if self.config_count < 40:
        #     return

        print('Move LOGIC')

        if self.config_last_size != (event.width, event.height):
            self.config_last_size = (event.width, event.height)

        if self.config_last_location[0] != new_x or self.config_last_location[1] != new_y:
            if self.config_last_location == (None, None):
                self.config_last_location = (new_x, new_y)
                return

        deltax = self.config_last_location[0] - event.x
        deltay = self.config_last_location[1] - event.y
        if deltax == 0 and deltay == 0:
            print('not moving so returning')
            return
        if Window._move_all_windows:
            print('checking all windows')
            for window in Window._active_windows:
                if window == self:
                    continue
                x = window.TKroot.winfo_x() + deltax
                y = window.TKroot.winfo_y() + deltay
                # window.TKroot.geometry("+%s+%s" % (x, y))  # this is what really moves the window
                # window.config_last_location = (x,y)
    """

    def _KeyboardCallback(self, event):
        """
        Window keyboard callback. Called by tkinter.  Will kick user out of the tkinter event loop. Should only be
        called if user has requested window level keyboard events

        :param event: object provided by tkinter that contains the key information
        :type event:  (event)
        """
        self.LastButtonClicked = None
        self.FormRemainedOpen = True
        if event.char != "":
            self.LastKeyboardEvent = event.char
        else:
            self.LastKeyboardEvent = str(event.keysym) + ":" + str(event.keycode)
        # if not self.NonBlocking:
        #     _BuildResults(self, False, self)
        _exit_mainloop(self)

    def _MouseWheelCallback(self, event):
        """
        Called by tkinter when a mouse wheel event has happened. Only called if keyboard events for the window
        have been enabled

        :param event: object sent in by tkinter that has the wheel direction
        :type event:  (event)
        """
        self.LastButtonClicked = None
        self.FormRemainedOpen = True
        self.LastKeyboardEvent = (
            "MouseWheel:Down" if event.delta < 0 or event.num == 5 else "MouseWheel:Up"
        )
        # if not self.NonBlocking:
        #     _BuildResults(self, False, self)
        _exit_mainloop(self)

    def _Close(self, without_event=False):
        """
        The internal close call that does the real work of building. This method basically sets up for closing
        but doesn't destroy the window like the User's version of Close does

        :parm without_event: if True, then do not cause an event to be generated, "silently" close the window
        :type without_event: (bool)
        """

        try:
            self.TKroot.update()
        except Exception:
            pass

        if not self.NonBlocking or not without_event:
            _BuildResults(self, False, self)
        if self.TKrootDestroyed:
            return
        self.TKrootDestroyed = True
        self.RootNeedsDestroying = True
        return

    def close(self):
        """
        Closes window.  Users can safely call even if window has been destroyed.   Should always call when done with
        a window so that resources are properly freed up within your thread.
        """

        try:
            del Window._active_windows[
                self
            ]  # will only be in the list if window was explicitly finalized
        except Exception:
            pass

        try:
            self.TKroot.update()  # On Linux must call update if the user closed with X or else won't actually close the window
        except Exception:
            pass

        self._restore_stdout()
        self._restore_stderr()

        _TimerPeriodic.stop_all_timers_for_window(self)

        if self.TKrootDestroyed:
            return
        try:
            self.TKroot.destroy()
            self.TKroot.update()
            Window._DecrementOpenCount()
        except Exception:
            pass
        # if down to 1 window, try and destroy the hidden window, if there is one
        # if Window.NumOpenWindows == 1:
        #     try:
        #         Window.hidden_master_root.destroy()
        #         Window.NumOpenWindows = 0  # if no hidden window, then this won't execute
        #     except Exception:
        #         pass
        self.TKrootDestroyed = True

        # Free up anything that was held in the layout and the root variables
        self.Rows = None
        self.TKroot = None

    def is_closed(self, quick_check=None):
        """
        Returns True is the window is maybe closed.  Can be difficult to tell sometimes
        NOTE - the call to TKroot.update was taking over 500 ms sometimes so added a flag to bypass the lengthy call.
        :type quick_check:  bool
        :return:            True if the window was closed or destroyed
        :rtype:             (bool)
        """

        if self.TKrootDestroyed or self.TKroot is None:
            return True

        # if performing a quick check only, then skip calling tkinter for performance reasons
        if quick_check:
            return False

        # see if can do an update... if not, then it's been destroyed
        try:
            rc = self.TKroot.update()
        except Exception:
            return True
        return False

    # IT FINALLY WORKED! 29-Oct-2018 was the first time this damned thing got called
    def _OnClosingCallback(self):
        """
        Internally used method ONLY. Not sure callable.  tkinter calls this when the window is closed by clicking X
        """
        # global _my_windows
        # print('Got closing callback', self.DisableClose)
        if self.DisableClose:
            return
        if (
            self.CurrentlyRunningMainloop
        ):  # quit if this is the current mainloop, otherwise don't quit!
            _exit_mainloop(self)
            if self.close_destroys_window:
                self.TKroot.destroy()  # destroy this window
                self.TKrootDestroyed = True
                self.XFound = True
            else:
                self.LastButtonClicked = WINDOW_CLOSE_ATTEMPTED_EVENT
        elif Window._root_running_mainloop == Window.hidden_master_root:
            _exit_mainloop(self)
        else:
            if self.close_destroys_window:
                self.TKroot.destroy()  # destroy this window
                self.XFound = True
            else:
                self.LastButtonClicked = WINDOW_CLOSE_ATTEMPTED_EVENT
        if self.close_destroys_window:
            self.RootNeedsDestroying = True
        self._restore_stdout()
        self._restore_stderr()

    def disable(self):
        """
        Disables window from taking any input from the user
        """
        if not self._is_window_created("tried Window.disable"):
            return
        self.TKroot.attributes("-disabled", 1)
        # self.TKroot.grab_set_global()

    def enable(self):
        """
        Re-enables window to take user input after having it be Disabled previously
        """
        if not self._is_window_created("tried Window.enable"):
            return
        self.TKroot.attributes("-disabled", 0)
        # self.TKroot.grab_release()

    def hide(self):
        """
        Hides the window from the screen and the task bar
        """
        if not self._is_window_created("tried Window.hide"):
            return
        self._Hidden = True
        self.TKroot.withdraw()

    def un_hide(self):
        """
        Used to bring back a window that was previously hidden using the Hide method
        """
        if not self._is_window_created("tried Window.un_hide"):
            return
        if self._Hidden:
            self.TKroot.deiconify()
            self._Hidden = False

    def is_hidden(self):
        """
            Returns True if the window is currently hidden
        :return:    Returns True if the window is currently hidden
        :rtype:     bool
        """
        return self._Hidden

    def disappear(self):
        """
        Causes a window to "disappear" from the screen, but remain on the taskbar. It does this by turning the alpha
        channel to 0.  NOTE that on some platforms alpha is not supported. The window will remain showing on these
        platforms.  The Raspberry Pi for example does not have an alpha setting
        """
        if not self._is_window_created("tried Window.disappear"):
            return
        self.TKroot.attributes("-alpha", 0)

    def reappear(self):
        """
        Causes a window previously made to "Disappear" (using that method). Does this by restoring the alpha channel
        """
        if not self._is_window_created("tried Window.reappear"):
            return
        self.TKroot.attributes("-alpha", 255)

    def set_alpha(self, alpha):
        """
        Sets the Alpha Channel for a window.  Values are between 0 and 1 where 0 is completely transparent

        :param alpha: 0 to 1. 0 is completely transparent.  1 is completely visible and solid (can't see through)
        :type alpha:  (float)
        """
        if not self._is_window_created("tried Window.set_alpha"):
            return
        self._AlphaChannel = alpha
        self.TKroot.attributes("-alpha", alpha)

    @property
    def alpha_channel(self):
        """
        A property that changes the current alpha channel value (internal value)
        :return: the current alpha channel setting according to self, not read directly from tkinter
        :rtype:  (float)
        """
        return self._AlphaChannel

    @alpha_channel.setter
    def alpha_channel(self, alpha):
        """
        The setter method for this "property".
        Planning on depricating so that a Set call is always used by users. This is more in line with the SDK
        :param alpha: 0 to 1. 0 is completely transparent.  1 is completely visible and solid (can't see through)
        :type alpha:  (float)
        """
        if not self._is_window_created("tried Window.alpha_channel"):
            return
        self._AlphaChannel = alpha
        self.TKroot.attributes("-alpha", alpha)

    def bring_to_front(self):
        """
        Brings this window to the top of all other windows (perhaps may not be brought before a window made to "stay
        on top")
        """
        if not self._is_window_created("tried Window.bring_to_front"):
            return
        if running_windows():
            try:
                self.TKroot.wm_attributes("-topmost", 0)
                self.TKroot.wm_attributes("-topmost", 1)
                if not self.KeepOnTop:
                    self.TKroot.wm_attributes("-topmost", 0)
            except Exception as e:
                warnings.warn("Problem in Window.bring_to_front" + str(e), UserWarning)
        else:
            try:
                self.TKroot.lift()
            except Exception:
                pass

    def send_to_back(self):
        """
        Pushes this window to the bottom of the stack of windows. It is the opposite of BringToFront
        """
        if not self._is_window_created("tried Window.send_to_back"):
            return
        try:
            self.TKroot.lower()
        except Exception:
            pass

    def keep_on_top_set(self):
        """
        Sets keep_on_top after a window has been created.  Effect is the same
        as if the window was created with this set.  The Window is also brought
        to the front
        """
        if not self._is_window_created("tried Window.keep_on_top_set"):
            return
        self.KeepOnTop = True
        self.bring_to_front()
        try:
            self.TKroot.wm_attributes("-topmost", 1)
        except Exception as e:
            warnings.warn(
                "Problem in Window.keep_on_top_set trying to set wm_attributes topmost"
                + str(e),
                UserWarning,
            )

    def keep_on_top_clear(self):
        """
        Clears keep_on_top after a window has been created.  Effect is the same
        as if the window was created with this set.
        """
        if not self._is_window_created("tried Window.keep_on_top_clear"):
            return
        self.KeepOnTop = False
        try:
            self.TKroot.wm_attributes("-topmost", 0)
        except Exception as e:
            warnings.warn(
                "Problem in Window.keep_on_top_clear trying to clear wm_attributes topmost"
                + str(e),
                UserWarning,
            )

    def current_location(self, more_accurate=False, without_titlebar=False):
        """
        Get the current location of the window's top left corner.
        Sometimes, depending on the environment, the value returned does not include the titlebar,etc
        A new option, more_accurate, can be used to get the theoretical upper leftmost corner of the window.
        The titlebar and menubar are crated by the OS. It gets really confusing when running in a webpage (repl, trinket)
        Thus, the values can appear top be "off" due to the sometimes unpredictable way the location is calculated.
        If without_titlebar is set then the location of the root x,y is used which should not include the titlebar but
            may be OS dependent.

        :param more_accurate:    If True, will use the window's geometry to get the topmost location with titlebar, menubar taken into account
        :type more_accurate:     (bool)
        :param without_titlebar: If True, return location of top left of main window area without the titlebar (may be OS dependent?)
        :type without_titlebar:  (bool)
        :return:                 The x and y location in tuple form (x,y)
        :rtype:                  Tuple[(int | None), (int | None)]
        """

        if not self._is_window_created("tried Window.current_location"):
            return None, None
        try:
            if without_titlebar:
                x, y = self.TKroot.winfo_rootx(), self.TKroot.winfo_rooty()
            elif more_accurate:
                geometry = self.TKroot.geometry()
                location = geometry[geometry.find("+") + 1 :].split("+")
                x, y = int(location[0]), int(location[1])
            else:
                x, y = int(self.TKroot.winfo_x()), int(self.TKroot.winfo_y())
        except Exception as e:
            warnings.warn(
                "Error in Window.current_location. Trouble getting x,y location\n"
                + str(e),
                UserWarning,
            )
            x, y = (None, None)
        return x, y

    def current_size_accurate(self):
        """
        Get the current location of the window based on tkinter's geometry setting

        :return:              The x and y size in tuple form (x,y)
        :rtype:               Tuple[(int | None), (int | None)]
        """

        if not self._is_window_created("tried Window.current_location"):
            return None, None
        try:
            geometry = self.TKroot.geometry()
            geometry_tuple = geometry.split("+")
            window_size = geometry_tuple[0].split("x")
            x, y = int(window_size[0]), int(window_size[1])
        except Exception as e:
            warnings.warn(
                "Error in Window.current_size_accurate. Trouble getting x,y size\n{} {}".format(
                    geometry, geometry_tuple
                )
                + str(e),
                UserWarning,
            )
            x, y = (None, None)
        return x, y

    @property
    def size(self):
        """
        Return the current size of the window in pixels

        :return: (width, height) of the window
        :rtype:  Tuple[(int), (int)] or Tuple[None, None]
        """
        if not self._is_window_created("Tried to use Window.size property"):
            return None, None
        win_width = self.TKroot.winfo_width()
        win_height = self.TKroot.winfo_height()
        return win_width, win_height

    @size.setter
    def size(self, size):
        """
        Changes the size of the window, if possible

        :param size: (width, height) of the desired window size
        :type size:  (int, int)
        """
        try:
            self.TKroot.geometry("%sx%s" % (size[0], size[1]))
            self.TKroot.update_idletasks()
        except Exception:
            pass

    def set_size(self, size):
        """
        Changes the size of the window, if possible. You can also use the Window.size prooerty
        to set/get the size.

        :param size: (width, height) of the desired window size
        :type size:  (int, int)
        """
        if not self._is_window_created(
            "Tried to change the size of the window prior to creation."
        ):
            return
        try:
            self.TKroot.geometry("%sx%s" % (size[0], size[1]))
            self.TKroot.update_idletasks()
        except Exception:
            pass

    def set_min_size(self, size):
        """
        Changes the minimum size of the window. Note Window must be read or finalized first.

        :param size: (width, height) tuple (int, int) of the desired window size in pixels
        :type size:  (int, int)
        """
        if not self._is_window_created("tried Window.set_min_size"):
            return
        self.TKroot.minsize(size[0], size[1])
        self.TKroot.update_idletasks()

    def set_resizable(self, x_axis_enable, y_axis_enable):
        """
        Changes if a window can be resized in either the X or the Y direction.
        Note Window must be read or finalized first.

        :param x_axis_enable: If True, the window can be changed in the X-axis direction. If False, it cannot
        :type x_axis_enable: (bool)
        :param y_axis_enable: If True, the window can be changed in the Y-axis direction. If False, it cannot
        :type y_axis_enable: (bool)
        """

        if not self._is_window_created("tried Window.set_resixable"):
            return
        try:
            self.TKroot.resizable(x_axis_enable, y_axis_enable)
        except Exception as e:
            _error_popup_with_traceback(
                "Window.set_resizable - tkinter reported error", e
            )

    def visibility_changed(self):
        """
        When making an element in a column or someplace that has a scrollbar, then you'll want to call this function
        prior to the column's contents_changed() method.
        """
        self.refresh()

    def set_transparent_color(self, color):
        """
        Set the color that will be transparent in your window. Areas with this color will be SEE THROUGH.

        :param color: Color string that defines the transparent color
        :type color:  (str)
        """
        if not self._is_window_created("tried Window.set_transparent_color"):
            return
        try:
            self.TKroot.attributes("-transparentcolor", color)
            self.TransparentColor = color
        except Exception:
            print("Transparent color not supported on this platform (windows only)")

    def mouse_location(self):
        """
        Return the (x,y) location of the mouse relative to the entire screen.  It's the same location that
        you would use to create a window, popup, etc.

        :return:    The location of the mouse pointer
        :rtype:     (int, int)
        """
        if not self._is_window_created("tried Window.mouse_location"):
            return 0, 0

        return self.TKroot.winfo_pointerx(), self.TKroot.winfo_pointery()

    def grab_any_where_on(self):
        """
        Turns on Grab Anywhere functionality AFTER a window has been created.  Don't try on a window that's not yet
        been Finalized or Read.
        """
        if not self._is_window_created("tried Window.grab_any_where_on"):
            return
        self.TKroot.bind("<ButtonPress-1>", self._StartMoveGrabAnywhere)
        self.TKroot.bind("<ButtonRelease-1>", self._StopMove)
        self.TKroot.bind("<B1-Motion>", self._OnMotionGrabAnywhere)

    def grab_any_where_off(self):
        """
        Turns off Grab Anywhere functionality AFTER a window has been created.  Don't try on a window that's not yet
        been Finalized or Read.
        """
        if not self._is_window_created("tried Window.grab_any_where_off"):
            return
        self.TKroot.unbind("<ButtonPress-1>")
        self.TKroot.unbind("<ButtonRelease-1>")
        self.TKroot.unbind("<B1-Motion>")

    def _user_bind_callback(self, bind_string, event, propagate=True):
        """
        Used when user binds a tkinter event directly to an element

        :param bind_string: The event that was bound so can lookup the key modifier
        :type bind_string:  (str)
        :param event:       Event data passed in by tkinter (not used)
        :type event:
        :param propagate:   If True then tkinter will be told to propagate the event
        :type propagate:    (bool)
        """
        # print('bind callback', bind_string, event)
        key = self.user_bind_dict.get(bind_string, "")
        self.user_bind_event = event
        if key is not None:
            self.LastButtonClicked = key
        else:
            self.LastButtonClicked = bind_string
        self.FormRemainedOpen = True
        # if self.CurrentlyRunningMainloop:
        #     self.TKroot.quit()
        _exit_mainloop(self)
        return "break" if propagate is not True else None

    def bind(self, bind_string, key, propagate=True):
        """
        Used to add tkinter events to a Window.
        The tkinter specific data is in the Window's member variable user_bind_event
        :param bind_string: The string tkinter expected in its bind function
        :type bind_string:  (str)
        :param key:         The event that will be generated when the tkinter event occurs
        :type key:          str | int | tuple | object
        :param propagate:   If True then tkinter will be told to propagate the event
        :type propagate:    (bool)
        """
        if not self._is_window_created("tried Window.bind"):
            return
        try:
            self.TKroot.bind(
                bind_string,
                lambda evt: self._user_bind_callback(bind_string, evt, propagate),
            )
        except Exception as e:
            self.TKroot.unbind_all(bind_string)
            return
            # _error_popup_with_traceback('Window.bind error', e)
        self.user_bind_dict[bind_string] = key

    def unbind(self, bind_string):
        """
        Used to remove tkinter events to a Window.
        This implementation removes ALL of the binds of the bind_string from the Window.  If there
        are multiple binds for the Window itself, they will all be removed.  This can be extended later if there
        is a need.
        :param bind_string: The string tkinter expected in its bind function
        :type bind_string:  (str)
        """
        if not self._is_window_created("tried Window.unbind"):
            return
        self.TKroot.unbind(bind_string)

    def _callback_main_debugger_window_create_keystroke(self, event):
        """
        Called when user presses the key that creates the main debugger window
        March 2022 - now causes the user reads to return timeout events automatically
        :param event: (event) not used. Passed in event info
        :type event:
        """
        Window._main_debug_window_build_needed = True
        # exit the event loop in a way that resembles a timeout occurring
        self.LastButtonClicked = self.TimeoutKey
        self.FormRemainedOpen = True
        self.TKroot.quit()  # kick the users out of the mainloop

    def _callback_popout_window_create_keystroke(self, event):
        """
        Called when user presses the key that creates the floating debugger window
        March 2022 - now causes the user reads to return timeout events automatically
        :param event: (event) not used. Passed in event info
        :type event:
        """
        Window._floating_debug_window_build_needed = True
        # exit the event loop in a way that resembles a timeout occurring
        self.LastButtonClicked = self.TimeoutKey
        self.FormRemainedOpen = True
        self.TKroot.quit()  # kick the users out of the mainloop

    def enable_debugger(self):
        """
        Enables the internal debugger. By default, the debugger IS enabled
        """
        if not self._is_window_created("tried Window.enable_debugger"):
            return
        self.TKroot.bind(
            "<Cancel>", self._callback_main_debugger_window_create_keystroke
        )
        self.TKroot.bind("<Pause>", self._callback_popout_window_create_keystroke)
        self.DebuggerEnabled = True

    def disable_debugger(self):
        """
        Disable the internal debugger. By default the debugger is ENABLED
        """
        if not self._is_window_created("tried Window.disable_debugger"):
            return
        self.TKroot.unbind("<Cancel>")
        self.TKroot.unbind("<Pause>")
        self.DebuggerEnabled = False

    def set_title(self, title):
        """
        Change the title of the window

        :param title: The string to set the title to
        :type title:  (str)
        """
        if not self._is_window_created("tried Window.set_title"):
            return
        if self._has_custom_titlebar:
            try:  # just in case something goes badly, don't crash
                self.find_element(TITLEBAR_TEXT_KEY).update(title)
            except Exception:
                pass
        # even with custom titlebar, set the main window's title too so it'll match when minimized
        self.TKroot.wm_title(str(title))

    def make_modal(self):
        """
        Makes a window into a "Modal Window"
        This means user will not be able to interact with other windows until this one is closed

        NOTE - Sorry Mac users - you can't have modal windows.... lobby your tkinter Mac devs
        """
        if not self._is_window_created("tried Window.make_modal"):
            return

        if running_mac() and ENABLE_MAC_MODAL_DISABLE_PATCH:
            return

        # if modal windows have been disabled globally
        if not DEFAULT_MODAL_WINDOWS_ENABLED and not DEFAULT_MODAL_WINDOWS_FORCED:
            # if not DEFAULT_MODAL_WINDOWS_ENABLED:
            return

        try:
            self.TKroot.transient()
            self.TKroot.grab_set()
            self.TKroot.focus_force()
        except Exception as e:
            print("Exception trying to make modal", e)

    def force_focus(self):
        """
        Forces this window to take focus
        """
        if not self._is_window_created("tried Window.force_focus"):
            return
        self.TKroot.focus_force()

    def was_closed(self):
        """
        Returns True if the window was closed

        :return: True if the window is closed
        :rtype:  bool
        """
        return self.TKrootDestroyed

    def set_cursor(self, cursor):
        """
        Sets the cursor for the window.
        If you do not want any mouse pointer, then use the string "none"

        :param cursor: The tkinter cursor name
        :type cursor:  (str)
        """

        if not self._is_window_created("tried Window.set_cursor"):
            return
        try:
            self.TKroot.config(cursor=cursor)
        except Exception as e:
            print("Warning bad cursor specified ", cursor)
            print(e)

    def ding(self, display_number=0):
        """
        Make a "bell" sound. A capability provided by tkinter.  Your window needs to be finalized prior to calling.
        Ring a display's bell is the tkinter description of the call.
        :param display_number: Passed to tkinter's bell method as parameter "displayof".
        :type display_number:  int
        """
        if not self._is_window_created("tried Window.ding"):
            return
        try:
            self.TKroot.bell(display_number)
        except Exception as e:
            if not SUPPRESS_ERROR_POPUPS:
                _error_popup_with_traceback(
                    "Window.ding() - tkinter reported error from bell() call", e
                )

    def _window_tkvar_changed_callback(self, *args):
        """
        Internal callback function for when the thread

        :param event: Information from tkinter about the callback
        :type event:

        """
        # print('Thread callback info', threading.current_thread())
        # print(event)
        # trace_details = traceback.format_stack()
        # print(''.join(trace_details))
        # self.thread_lock.acquire()
        # if self.thread_timer:
        # self.TKroot.after_cancel(id=self.thread_timer)
        # self.thread_timer = None
        # self.thread_lock.release()

        if self._queued_thread_event_available():
            self.FormRemainedOpen = True
            _exit_mainloop(self)

    def _create_thread_queue(self):
        """
        Creates the queue used by threads to communicate with this window
        """

        if self.thread_queue is None:
            self.thread_queue = queue.Queue()

        if self.thread_lock is None:
            self.thread_lock = threading.Lock()

        if self.thread_strvar is None:
            self.thread_strvar = tk.StringVar()
            self.thread_strvar.trace("w", self._window_tkvar_changed_callback)

    def write_event_value(self, key, value):
        """
        Adds a key & value tuple to the queue that is used by threads to communicate with the window

        :param key:   The key that will be returned as the event when reading the window
        :type key:    Any
        :param value: The value that will be in the values dictionary
        :type value:  Any
        """

        if self.thread_queue is None:
            print("*** Warning Window.write_event_value - no thread queue found ***")
            return
        # self.thread_lock.acquire()  # first lock the critical section
        self.thread_queue.put(item=(key, value))
        self.TKroot.tk.willdispatch()  # brilliant bit of code provided by Giuliano who I owe a million thank yous!
        self.thread_strvar.set("new item")

        # self.thread_queue.put(item=(key, value))
        # self.thread_strvar.set('new item')
        # March 28 2021 - finally found a solution!  It needs a little more work and a lock
        # if no timer is running, then one should be started
        # if self.thread_timer is None:
        #     print('Starting a timer')
        #     self.thread_timer = self.TKroot.after(1, self._window_tkvar_changed_callback)
        # self.thread_lock.release()

    def _queued_thread_event_read(self):
        if self.thread_queue is None:
            return None

        try:  # see if something has been posted to Queue
            message = self.thread_queue.get_nowait()
        except queue.Empty:  # get_nowait() will get exception when Queue is empty
            return None

        return message

    def _queued_thread_event_available(self):
        if self.thread_queue is None:
            return False
        # self.thread_lock.acquire()
        qsize = self.thread_queue.qsize()
        if qsize == 0:
            self.thread_timer = None
        # self.thread_lock.release()
        return qsize != 0

    def _RightClickMenuCallback(self, event):
        """
        When a right click menu is specified for an entire window, then this callback catches right clicks
        that happen to the window itself, when there are no elements that are in that area.

        The only portion that is not currently covered correctly is the row frame itself.  There will still
        be parts of the window, at the moment, that don't respond to a right click.  It's getting there, bit
        by bit.

        Callback function that's called when a right click happens. Shows right click menu as result.

        :param event: information provided by tkinter about the event including x,y location of click
        :type event:
        """
        # if there are widgets under the mouse, then see if it's the root only.  If not, then let the widget (element) show their menu instead
        x, y = self.TKroot.winfo_pointerxy()
        widget = self.TKroot.winfo_containing(x, y)
        if widget != self.TKroot:
            return
        self.TKRightClickMenu.tk_popup(event.x_root, event.y_root, 0)
        self.TKRightClickMenu.grab_release()

    def save_window_screenshot_to_disk(self, filename=None):
        """
        Saves an image of the PySimpleGUI window provided into the filename provided

        :param filename:        Optional filename to save screenshot to. If not included, the User Settinds are used to get the filename
        :return:                A PIL ImageGrab object that can be saved or manipulated
        :rtype:                 (PIL.ImageGrab | None)
        """
        global pil_import_attempted, pil_imported, PIL, ImageGrab, Image

        if not pil_import_attempted:
            try:
                import PIL as PIL
                from PIL import ImageGrab
                from PIL import Image

                pil_imported = True
                pil_import_attempted = True
            except Exception:
                pil_imported = False
                pil_import_attempted = True
                print("FAILED TO IMPORT PIL!")
                return None
        try:
            # Get location of window to save
            pos = self.current_location()
            # Add a little to the X direction if window has a titlebar
            if not self.NoTitleBar:
                pos = (pos[0] + 7, pos[1])
            # Get size of wiondow
            size = self.current_size_accurate()
            # Get size of the titlebar
            titlebar_height = self.TKroot.winfo_rooty() - self.TKroot.winfo_y()
            # Add titlebar to size of window so that titlebar and window will be saved
            size = (size[0], size[1] + titlebar_height)
            if not self.NoTitleBar:
                size_adjustment = (2, 1)
            else:
                size_adjustment = (0, 0)
            # Make the "Bounding rectangle" used by PLK to do the screen grap "operation
            rect = (
                pos[0],
                pos[1],
                pos[0] + size[0] + size_adjustment[0],
                pos[1] + size[1] + size_adjustment[1],
            )
            # Grab the image
            grab = ImageGrab.grab(bbox=rect)
            # Save the grabbed image to disk
        except Exception as e:
            # print(e)
            popup_error_with_traceback(
                "Screen capture failure",
                "Error happened while trying to save screencapture",
                e,
            )

            return None
        # return grab
        if filename is None:
            folder = pysimplegui_user_settings.get("-screenshots folder-", "")
            filename = pysimplegui_user_settings.get("-screenshots filename-", "")
            full_filename = os.path.join(folder, filename)
        else:
            full_filename = filename
        if full_filename:
            try:
                grab.save(full_filename)
            except Exception as e:
                popup_error_with_traceback(
                    "Screen capture failure",
                    "Error happened while trying to save screencapture",
                    e,
                )
        else:
            popup_error_with_traceback(
                "Screen capture failure",
                "You have attempted a screen capture but have not set up a good filename to save to",
            )
        return grab

    def perform_long_operation(self, func, end_key=None):
        """
        Call your function that will take a long time to execute.  When it's complete, send an event
        specified by the end_key.

        Starts a thread on your behalf.

        This is a way for you to "ease into" threading without learning the details of threading.
        Your function will run, and when it returns 2 things will happen:
        1. The value you provide for end_key will be returned to you when you call window.read()
        2. If your function returns a value, then the value returned will also be included in your windows.read call in the values dictionary

        IMPORTANT - This method uses THREADS... this means you CANNOT make any PySimpleGUI calls from
        the function you provide with the exception of one function, Window.write_event_value.

        :param func:    A lambda or a function name with no parms
        :type func:     Any
        :param end_key: Optional key that will be generated when the function returns
        :type end_key:  (Any | None)
        :return:        The id of the thread
        :rtype:         threading.Thread
        """

        thread = threading.Thread(
            target=_long_func_thread, args=(self, end_key, func), daemon=True
        )
        thread.start()
        return thread

    @property
    def key_dict(self):
        """
        Returns a dictionary with all keys and their corresponding elements
        { key : Element }
        :return: Dictionary of keys and elements
        :rtype:  Dict[Any, Element]
        """
        return self.AllKeysDict

    def key_is_good(self, key):
        """
        Checks to see if this is a good key for this window
        If there's an element with the key provided, then True is returned
        :param key:     The key to check
        :type key:      str | int | tuple | object
        :return:        True if key is an element in this window
        :rtype:         bool
        """
        if key in self.key_dict:
            return True
        return False

    def get_scaling(self):
        """
        Returns the current scaling value set for this window

        :return:    Scaling according to tkinter. Returns DEFAULT_SCALING if error
        :rtype:     float
        """

        if not self._is_window_created("Tried Window.set_scaling"):
            return DEFAULT_SCALING
        try:
            scaling = self.TKroot.tk.call("tk", "scaling")
        except Exception as e:
            if not SUPPRESS_ERROR_POPUPS:
                _error_popup_with_traceback(
                    "Window.get_scaling() - tkinter reported error", e
                )
            scaling = DEFAULT_SCALING

        return scaling

    def _custom_titlebar_restore_callback(self, event):
        self._custom_titlebar_restore()

    def _custom_titlebar_restore(self):
        if running_linux():
            # if self._skip_first_restore_callback:
            #     self._skip_first_restore_callback = False
            #     return
            self.TKroot.unbind("<Button-1>")
            self.TKroot.deiconify()

            # self.ParentForm.TKroot.wm_overrideredirect(True)
            self.TKroot.wm_attributes("-type", "dock")

        else:
            self.TKroot.unbind("<Expose>")
            self.TKroot.wm_overrideredirect(True)
        if self.TKroot.state() == "iconic":
            self.TKroot.deiconify()
        else:
            if not running_linux():
                self.TKroot.state("normal")
            else:
                self.TKroot.attributes("-fullscreen", False)
        self.maximized = False

    def _custom_titlebar_minimize(self):
        if running_linux():
            self.TKroot.wm_attributes("-type", "normal")
            # self.ParentForm.TKroot.state('icon')
            # return
            # self.ParentForm.maximize()
            self.TKroot.wm_overrideredirect(False)
            # self.ParentForm.minimize()
            # self.ParentForm.TKroot.wm_overrideredirect(False)
            self.TKroot.iconify()
            # self._skip_first_restore_callback = True
            self.TKroot.bind("<Button-1>", self._custom_titlebar_restore_callback)
        else:
            self.TKroot.wm_overrideredirect(False)
            self.TKroot.iconify()
            self.TKroot.bind("<Expose>", self._custom_titlebar_restore_callback)

    def _custom_titlebar_callback(self, key):
        """
        One of the Custom Titlbar buttons was clicked
        :param key:
        :return:
        """
        if key == TITLEBAR_MINIMIZE_KEY:
            if not self.DisableMinimize:
                self._custom_titlebar_minimize()
        elif key == TITLEBAR_MAXIMIZE_KEY:
            if self.Resizable:
                if self.maximized:
                    self.normal()
                else:
                    self.maximize()
        elif key == TITLEBAR_CLOSE_KEY:
            if not self.DisableClose:
                self._OnClosingCallback()

    def timer_start(self, frequency_ms, key=EVENT_TIMER, repeating=True):
        """
        Starts a timer that gnerates Timer Events.  The default is to repeat the timer events until timer is stopped.
        You can provide your own key or a default key will be used.  The default key is defined
        with the constants EVENT_TIMER or TIMER_KEY.  They both equal the same value.
        The values dictionary will contain the timer ID that is returned from this function.

        :param frequency_ms:    How often to generate timer events in milliseconds
        :type frequency_ms:     int
        :param key:             Key to be returned as the timer event
        :type key:              str | int | tuple | object
        :param repeating:       If True then repeat timer events until timer is explicitly stopped
        :type repeating:        bool
        :return:                Timer ID for the timer
        :rtype:                 int
        """
        timer = _TimerPeriodic(
            self, frequency_ms=frequency_ms, key=key, repeating=repeating
        )
        return timer.id

    def timer_stop(self, timer_id):
        """
        Stops a timer with a given ID

        :param timer_id:        Timer ID of timer to stop
        :type timer_id:         int
        :return:
        """
        _TimerPeriodic.stop_timer_with_id(timer_id)

    def timer_stop_all(self):
        """
        Stops all timers for THIS window
        """
        _TimerPeriodic.stop_all_timers_for_window(self)

    def timer_get_active_timers(self):
        """
        Returns a list of currently active timers for a window
        :return:    List of timers for the window
        :rtype:     List[int]
        """
        return _TimerPeriodic.get_all_timers_for_window(self)

    @classmethod
    def _restore_stdout(cls):
        for item in cls._rerouted_stdout_stack:
            (window, element) = item  # type: (Window, Element)
            if not window.is_closed():
                sys.stdout = element
                break
        cls._rerouted_stdout_stack = [
            item for item in cls._rerouted_stdout_stack if not item[0].is_closed()
        ]
        if len(cls._rerouted_stdout_stack) == 0 and cls._original_stdout is not None:
            sys.stdout = cls._original_stdout
        # print('Restored stdout... new stack:',  [item[0].Title for item in cls._rerouted_stdout_stack ])

    @classmethod
    def _restore_stderr(cls):
        for item in cls._rerouted_stderr_stack:
            (window, element) = item  # type: (Window, Element)
            if not window.is_closed():
                sys.stderr = element
                break
        cls._rerouted_stderr_stack = [
            item for item in cls._rerouted_stderr_stack if not item[0].is_closed()
        ]
        if len(cls._rerouted_stderr_stack) == 0 and cls._original_stderr is not None:
            sys.stderr = cls._original_stderr
        # print('Restored stderr... new stack:',  [item[0].Title for item in cls._rerouted_stderr_stack ])

    # def __enter__(self):
    #     """
    #     WAS used with context managers which are no longer needed nor advised.  It is here for legacy support and
    #     am afraid of removing right now
    #     :return: (window)
    #      :rtype:
    #     """
    #     return self

    def __getitem__(self, key):
        """
        Returns Element that matches the passed in key.
        This is "called" by writing code as thus:
        window['element key'].update

        :param key: The key to find
        :type key:  str | int | tuple | object
        :return:    The element found
        :rtype:     Element | Input | Combo | OptionMenu | Listbox | Radio | Checkbox | Spin | Multiline | Text | StatusBar | Output | Button | ButtonMenu | ProgressBar | Image | Canvas | Graph | Frame | VerticalSeparator | HorizontalSeparator | Tab | TabGroup | Slider | Column | Pane | Menu | Table | Tree | ErrorElement | None
        """

        return self.find_element(key)

    def __call__(self, *args, **kwargs):
        """
        Call window.read but without having to type it out.
        window() == window.read()
        window(timeout=50) == window.read(timeout=50)

        :return: The famous event, values that read returns.
        :rtype:  Tuple[Any, Dict[Any, Any]]
        """
        return self.read(*args, **kwargs)

    def _is_window_created(self, additional_message=""):
        msg = str(additional_message)
        if self.TKroot is None:
            warnings.warn(
                'You cannot perform operations on a Window until it is read or finalized. Adding a "finalize=True" parameter to your Window creation will fix this. '
                + msg,
                UserWarning,
            )
            if not SUPPRESS_ERROR_POPUPS:
                _error_popup_with_traceback(
                    "You cannot perform operations on a Window until it is read or finalized.",
                    'Adding a "finalize=True" parameter to your Window creation will likely fix this',
                    msg,
                )
            return False
        return True

    def _has_custom_titlebar_element(self):
        for elem in self.AllKeysDict.values():
            if elem.Key in (
                TITLEBAR_MAXIMIZE_KEY,
                TITLEBAR_CLOSE_KEY,
                TITLEBAR_IMAGE_KEY,
            ):
                return True
            if elem.metadata == TITLEBAR_METADATA_MARKER:
                return True
        return False

    AddRow = add_row
    AddRows = add_rows
    AlphaChannel = alpha_channel
    BringToFront = bring_to_front
    Close = close
    CurrentLocation = current_location
    Disable = disable
    DisableDebugger = disable_debugger
    Disappear = disappear
    Enable = enable
    EnableDebugger = enable_debugger
    Fill = fill
    Finalize = finalize
    # FindElement = find_element
    FindElementWithFocus = find_element_with_focus
    GetScreenDimensions = get_screen_dimensions
    GrabAnyWhereOff = grab_any_where_off
    GrabAnyWhereOn = grab_any_where_on
    Hide = hide
    Layout = layout
    LoadFromDisk = load_from_disk
    Maximize = maximize
    Minimize = minimize
    Move = move
    Normal = normal
    Read = read
    Reappear = reappear
    Refresh = refresh
    SaveToDisk = save_to_disk
    SendToBack = send_to_back
    SetAlpha = set_alpha
    SetIcon = set_icon
    SetTransparentColor = set_transparent_color
    Size = size
    UnHide = un_hide
    VisibilityChanged = visibility_changed
    CloseNonBlocking = close
    CloseNonBlockingForm = close
    start_thread = perform_long_operation
    #
    # def __exit__(self, *a):
    #     """
    #     WAS used with context managers which are no longer needed nor advised.  It is here for legacy support and
    #     am afraid of removing right now
    #     :param *a: (?) Not sure what's passed in.
    #      :type *a:
    #     :return:   Always returns False which was needed for context manager to work
    #      :rtype:
    #     """
    #     self.__del__()
    #     return False
    #
    # def __del__(self):
    #     # print('DELETING WINDOW')
    #     for row in self.Rows:
    #         for element in row:
    #             element.__del__()


# -------------------------------- PEP8-ify the Window Class USER Interfaces -------------------------------- #


FlexForm = Window





class UserSettings:
    # A reserved settings object for use by the setting functions. It's a way for users
    # to access the user settings without diarectly using the UserSettings class
    _default_for_function_interface = None  # type: UserSettings

    def __init__(
        self,
        filename=None,
        path=None,
        silent_on_error=False,
        autosave=True,
        use_config_file=None,
        convert_bools_and_none=True,
    ):
        """
        User Settings

        :param filename:               The name of the file to use. Can be a full path and filename or just filename
        :type filename:                (str or None)
        :param path:                   The folder that the settings file will be stored in. Do not include the filename.
        :type path:                    (str or None)
        :param silent_on_error:        If True errors will not be reported
        :type silent_on_error:         (bool)
        :param autosave:               If True the settings file is saved after every update
        :type autosave:                (bool)
        :param use_config_file:        If True then the file format will be a config.ini rather than json
        :type use_config_file:         (bool)
        :param convert_bools_and_none: If True then "True", "False", "None" will be converted to the Python values True, False, None when using INI files. Default is TRUE
        :type convert_bools_and_none:  (bool)
        """

        self.path = path
        self.filename = filename
        self.full_filename = None
        self.dict = {}
        self.default_value = None
        self.silent_on_error = silent_on_error
        self.autosave = autosave
        if (
            filename is not None
            and filename.endswith(".ini")
            and use_config_file is None
        ):
            warnings.warn(
                "[UserSettings] You have specified a filename with .ini extension but did not set use_config_file. Setting use_config_file for you.",
                UserWarning,
            )
            use_config_file = True
        self.use_config_file = use_config_file
        # self.retain_config_comments = retain_config_comments
        self.convert_bools = convert_bools_and_none
        if use_config_file:
            self.config = configparser.ConfigParser()
            self.config.optionxform = str
            # self.config_dict = {}
            self.section_class_dict = {}  # type: dict[_SectionDict]
        if filename is not None or path is not None:
            self.load(filename=filename, path=path)

    ########################################################################################################
    ## FIRST is the _SectionDict helper class
    ## It is typically not directly accessed, although it is possible to call delete_section, get, set
    ########################################################################################################

    class _SectionDict:
        item_count = 0

        def __init__(
            self, section_name, section_dict, config, user_settings_parent
        ):  # (str, Dict, configparser.ConfigParser)
            """
            The Section Dictionary.  It holds the values for a section.

            :param section_name:                Name of the section
            :type section_name:                 str
            :param section_dict:                Dictionary of values for the section
            :type section_dict:                 dict
            :param config:                      The configparser object
            :type config:                       configparser.ConfigParser
            :param user_settings_parent:        The parent UserSettings object that hdas this section
            :type user_settings_parent:         UserSettings
            """
            self.section_name = section_name
            self.section_dict = section_dict  # type: Dict
            self.new_section = False
            self.config = config  # type: configparser.ConfigParser
            self.user_settings_parent = user_settings_parent  # type: UserSettings
            UserSettings._SectionDict.item_count += 1

            if self.user_settings_parent.convert_bools:
                for key, value in self.section_dict.items():
                    if value == "True":
                        value = True
                        self.section_dict[key] = value
                    elif value == "False":
                        value = False
                        self.section_dict[key] = value
                    elif value == "None":
                        value = None
                        self.section_dict[key] = value
            # print(f'++++++ making a new SectionDict with name = {section_name}')

        def __repr__(self):
            """
            Converts the settings dictionary into a string for easy display

            :return: the dictionary as a string
            :rtype:  (str)
            """
            return_string = "{}:\n".format(self.section_name)
            for entry in self.section_dict.keys():
                return_string += "          {} : {}\n".format(
                    entry, self.section_dict[entry]
                )

            return return_string

        def get(self, key, default=None):
            """
            Returns the value of a specified setting.  If the setting is not found in the settings dictionary, then
            the user specified default value will be returned.  It no default is specified and nothing is found, then
            the "default value" is returned.  This default can be specified in this call, or previously defined
            by calling set_default. If nothing specified now or previously, then None is returned as default.

            :param key:     Key used to lookup the setting in the settings dictionary
            :type key:      (Any)
            :param default: Value to use should the key not be found in the dictionary
            :type default:  (Any)
            :return:        Value of specified settings
            :rtype:         (Any)
            """
            value = self.section_dict.get(key, default)
            if self.user_settings_parent.convert_bools:
                if value == "True":
                    value = True
                elif value == "False":
                    value = False
            return value

        def set(self, key, value):
            value = str(value)  # all values must be strings
            if self.new_section:
                self.config.add_section(self.section_name)
                self.new_section = False
            self.config.set(section=self.section_name, option=key, value=value)
            self.section_dict[key] = value
            if self.user_settings_parent.autosave:
                self.user_settings_parent.save()

        def delete_section(self):
            # print(f'** Section Dict deleting section = {self.section_name}')
            self.config.remove_section(section=self.section_name)
            del self.user_settings_parent.section_class_dict[self.section_name]
            if self.user_settings_parent.autosave:
                self.user_settings_parent.save()

        def __getitem__(self, item):
            # print('*** In SectionDict Get ***')
            return self.get(item)

        def __setitem__(self, item, value):
            """
            Enables setting a setting by using [ ] notation like a dictionary.
            Your code will have this kind of design pattern:
            settings = sg.UserSettings()
            settings[item] = value

            :param item:  The key for the setting to change. Needs to be a hashable type. Basically anything but a list
            :type item:   Any
            :param value: The value to set the setting to
            :type value:  Any
            """
            # print(f'*** In SectionDict SET *** item = {item} value = {value}')
            self.set(item, value)
            self.section_dict[item] = value

        def __delitem__(self, item):
            """
            Delete an individual user setting.  This is the same as calling delete_entry.  The syntax
            for deleting the item using this manner is:
                del settings['entry']
            :param item: The key for the setting to delete
            :type item:  Any
            """
            # print(f'** In SectionDict delete! section name = {self.section_name} item = {item} ')
            self.config.remove_option(section=self.section_name, option=item)
            try:
                del self.section_dict[item]
            except Exception as e:
                pass
                # print(e)
            if self.user_settings_parent.autosave:
                self.user_settings_parent.save()

    ########################################################################################################

    def __repr__(self):
        """
        Converts the settings dictionary into a string for easy display

        :return: the dictionary as a string
        :rtype:  (str)
        """
        if not self.use_config_file:
            return pprint.pformat(self.dict)
        else:
            # rvalue = '-------------------- Settings ----------------------\n'
            rvalue = ""
            for name, section in self.section_class_dict.items():
                rvalue += str(section)

            # rvalue += '\n-------------------- Settings End----------------------\n'
            rvalue += "\n"
            return rvalue

    def set_default_value(self, default):
        """
        Set the value that will be returned if a requested setting is not found

        :param default: value to be returned if a setting is not found in the settings dictionary
        :type default:  Any
        """
        self.default_value = default

    def _compute_filename(self, filename=None, path=None):
        """
        Creates the full filename given the path or the filename or both.

        :param filename: The name of the file to use. Can be a full path and filename or just filename
        :type filename:  (str or None)
        :param path:     The folder that the settings file will be stored in. Do not include the filename.
        :type path:      (str or None)
        :return:         Tuple with (full filename, path, filename)
        :rtype:          Tuple[str, str, str]
        """
        if filename is not None:
            dirname_from_filename = os.path.dirname(
                filename
            )  # see if a path was provided as part of filename
            if dirname_from_filename:
                path = dirname_from_filename
                filename = os.path.basename(filename)
        elif self.filename is not None:
            filename = self.filename
        else:
            if not self.use_config_file:
                filename = (
                    os.path.splitext(
                        os.path.basename(sys.modules["__main__"].__file__)
                    )[0]
                    + ".json"
                )
            else:
                filename = (
                    os.path.splitext(
                        os.path.basename(sys.modules["__main__"].__file__)
                    )[0]
                    + ".ini"
                )

        if path is None:
            if self.path is not None:
                # path = self.path
                path = os.path.expanduser(
                    self.path
                )  # expand user provided path in case it has user ~ in it. Don't think it'll hurt
            elif (
                DEFAULT_USER_SETTINGS_PATH is not None
            ):  # if user set the path manually system-wide using set options
                path = os.path.expanduser(DEFAULT_USER_SETTINGS_PATH)
            elif running_trinket():
                path = os.path.expanduser(DEFAULT_USER_SETTINGS_TRINKET_PATH)
            elif running_replit():
                path = os.path.expanduser(DEFAULT_USER_SETTINGS_REPLIT_PATH)
            elif running_windows():
                path = os.path.expanduser(DEFAULT_USER_SETTINGS_WIN_PATH)
            elif running_linux():
                path = os.path.expanduser(DEFAULT_USER_SETTINGS_LINUX_PATH)
            elif running_mac():
                path = os.path.expanduser(DEFAULT_USER_SETTINGS_MAC_PATH)
            else:
                path = "."

        full_filename = os.path.join(path, filename)
        return full_filename, path, filename

    def set_location(self, filename=None, path=None):
        """
        Sets the location of the settings file

        :param filename: The name of the file to use. Can be a full path and filename or just filename
        :type filename:  (str or None)
        :param path:     The folder that the settings file will be stored in. Do not include the filename.
        :type path:      (str or None)
        """
        cfull_filename, cpath, cfilename = self._compute_filename(
            filename=filename, path=path
        )

        self.filename = cfilename
        self.path = cpath
        self.full_filename = cfull_filename

    def get_filename(self, filename=None, path=None):
        """
        Sets the filename and path for your settings file.  Either paramter can be optional.

        If you don't choose a path, one is provided for you that is OS specific
        Windows path default = users/name/AppData/Local/PySimpleGUI/settings.

        If you don't choose a filename, your application's filename + '.json' will be used.

        Normally the filename and path are split in the user_settings calls. However for this call they
        can be combined so that the filename contains both the path and filename.

        :param filename: The name of the file to use. Can be a full path and filename or just filename
        :type filename:  (str or None)
        :param path:     The folder that the settings file will be stored in. Do not include the filename.
        :type path:      (str or None)
        :return:         The full pathname of the settings file that has both the path and filename combined.
        :rtype:          (str)
        """
        if (
            filename is not None
            or path is not None
            or (filename is None and path is None and self.full_filename is None)
        ):
            self.set_location(filename=filename, path=path)
            self.read()
        return self.full_filename

    def save(self, filename=None, path=None):
        """
        Saves the current settings dictionary.  If a filename or path is specified in the call, then it will override any
        previously specitfied filename to create a new settings file.  The settings dictionary is then saved to the newly defined file.

        :param filename: The fFilename to save to. Can specify a path or just the filename. If no filename specified, then the caller's filename will be used.
        :type filename:  (str or None)
        :param path:     The (optional) path to use to save the file.
        :type path:      (str or None)
        :return:         The full path and filename used to save the settings
        :rtype:          (str)
        """
        if filename is not None or path is not None:
            self.set_location(filename=filename, path=path)
        try:
            if not os.path.exists(self.path):
                os.makedirs(self.path)
            with open(self.full_filename, "w") as f:
                if not self.use_config_file:
                    json.dump(self.dict, f)
                else:
                    self.config.write(f)
        except Exception as e:
            if not self.silent_on_error:
                _error_popup_with_traceback(
                    "UserSettings.save error",
                    "*** UserSettings.save()  Error saving settings to file:***\n",
                    self.full_filename,
                    e,
                )

        return self.full_filename

    def load(self, filename=None, path=None):
        """
        Specifies the path and filename to use for the settings and reads the contents of the file.
        The filename can be a full filename including a path, or the path can be specified separately.
        If  no filename is specified, then the caller's filename will be used with the extension ".json"

        :param filename: Filename to load settings from (and save to in the future)
        :type filename:  (str or None)
        :param path:     Path to the file. Defaults to a specific folder depending on the operating system
        :type path:      (str or None)
        :return:         The settings dictionary (i.e. all settings)
        :rtype:          (dict)
        """
        if filename is not None or path is not None or self.full_filename is None:
            self.set_location(filename, path)
        self.read()
        return self.dict

    def delete_file(self, filename=None, path=None, report_error=False):
        """
        Deltes the filename and path for your settings file.  Either paramter can be optional.
        If you don't choose a path, one is provided for you that is OS specific
        Windows path default = users/name/AppData/Local/PySimpleGUI/settings.
        If you don't choose a filename, your application's filename + '.json' will be used
        Also sets your current dictionary to a blank one.

        :param filename:     The name of the file to use. Can be a full path and filename or just filename
        :type filename:      (str or None)
        :param path:         The folder that the settings file will be stored in. Do not include the filename.
        :type path:          (str or None)
        :param report_error: Determines if an error should be shown if a delete error happen (i.e. file isn't present)
        :type report_error:  (bool)
        """

        if (
            filename is not None
            or path is not None
            or (filename is None and path is None)
        ):
            self.set_location(filename=filename, path=path)
        try:
            os.remove(self.full_filename)
        except Exception as e:
            if report_error:
                _error_popup_with_traceback(
                    "UserSettings delete_file warning ***",
                    "Exception trying to perform os.remove",
                    e,
                )
        self.dict = {}

    def write_new_dictionary(self, settings_dict):
        """
        Writes a specified dictionary to the currently defined settings filename.

        :param settings_dict: The dictionary to be written to the currently defined settings file
        :type settings_dict:  (dict)
        """
        if self.full_filename is None:
            self.set_location()
        self.dict = settings_dict
        self.save()

    def read(self):
        """
        Reads settings file and returns the dictionary.
        If you have anything changed in an existing settings dictionary, you will lose your changes.
        :return: settings dictionary
        :rtype:  (dict)
        """
        if self.full_filename is None:
            return {}
        try:
            if os.path.exists(self.full_filename):
                with open(self.full_filename, "r") as f:
                    if not self.use_config_file:  # if using json
                        self.dict = json.load(f)
                    else:  # if using a config file
                        self.config.read_file(f)
                        # Make a dictionary of SectionDict classses. Keys are the config.sections().
                        self.section_class_dict = {}
                        for section in self.config.sections():
                            section_dict = dict(self.config[section])
                            self.section_class_dict[section] = self._SectionDict(
                                section, section_dict, self.config, self
                            )

                        self.dict = self.section_class_dict
                        self.config_sections = self.config.sections()
                        # self.config_dict = {section_name : dict(self.config[section_name]) for section_name in self.config.sections()}
                    # if self.retain_config_comments:
                    #     self.config_file_contents = f.readlines()
        except Exception as e:
            if not self.silent_on_error:
                _error_popup_with_traceback(
                    "User Settings read warning",
                    "Error reading settings from file",
                    self.full_filename,
                    e,
                )
                # print('*** UserSettings.read - Error reading settings from file: ***\n', self.full_filename, e)
                # print(_create_error_message())

        return self.dict

    def exists(self, filename=None, path=None):
        """
        Check if a particular settings file exists.  Returns True if file exists

        :param filename: The name of the file to use. Can be a full path and filename or just filename
        :type filename:  (str or None)
        :param path:     The folder that the settings file will be stored in. Do not include the filename.
        :type path:      (str or None)
        """
        cfull_filename, cpath, cfilename = self._compute_filename(
            filename=filename, path=path
        )
        if os.path.exists(cfull_filename):
            return True
        return False

    def delete_entry(self, key, section=None, silent_on_error=None):
        """
        Deletes an individual entry.  If no filename has been specified up to this point,
        then a default filename will be used.
        After value has been deleted, the settings file is written to disk.

        :param section:
        :param key: Setting to be deleted. Can be any valid dictionary key type (i.e. must be hashable)
        :type key:  (Any)
        :param silent_on_error: Determines if error should be shown. This parameter overrides the silent on error setting for the object.
        :type silent_on_error:  (bool)
        """
        if self.full_filename is None:
            self.set_location()
            self.read()
        if not self.use_config_file:  # Is using JSON file
            if key in self.dict:
                del self.dict[key]
                if self.autosave:
                    self.save()
            else:
                if silent_on_error is False or (
                    silent_on_error is not True and not self.silent_on_error
                ):
                    _error_popup_with_traceback(
                        "User Settings delete_entry Warning - key",
                        key,
                        " not found in settings",
                    )

        else:
            if section is not None:
                section_dict = self.get(section)
                # print(f'** Trying to delete an entry with a config file in use ** id of section_dict = {id(section_dict)}')
                # section_dict = self.section_class_dict[section]
                del self.get(section)[key]
                # del section_dict[key]
                # del section_dict[key]

    def delete_section(self, section):
        """
        Deletes a section with the name provided in the section parameter.  Your INI file will be saved afterwards if auto-save enabled (default is ON)
        :param section:     Name of the section to delete
        :type section:      str
        """
        if not self.use_config_file:
            return

        section_dict = self.section_class_dict.get(section, None)
        section_dict.delete_section()
        del self.section_class_dict[section]
        if self.autosave:
            self.save()

    def set(self, key, value):
        """
        Sets an individual setting to the specified value.  If no filename has been specified up to this point,
        then a default filename will be used.
        After value has been modified, the settings file is written to disk.
        Note that this call is not value for a config file normally. If it is, then the key is assumed to be the
            Section key and the value written will be the default value.
        :param key:      Setting to be saved. Can be any valid dictionary key type
        :type key:       (Any)
        :param value:    Value to save as the setting's value. Can be anything
        :type value:     (Any)
        :return:         value that key was set to
        :rtype:          (Any)
        """

        if self.full_filename is None:
            self.set_location()
        # if not autosaving, then don't read the file or else will lose changes
        if not self.use_config_file:
            if self.autosave or self.dict == {}:
                self.read()
            self.dict[key] = value
        else:
            self.section_class_dict[key].set(value, self.default_value)

        if self.autosave:
            self.save()
        return value

    def get(self, key, default=None):
        """
        Returns the value of a specified setting.  If the setting is not found in the settings dictionary, then
        the user specified default value will be returned.  It no default is specified and nothing is found, then
        the "default value" is returned.  This default can be specified in this call, or previously defined
        by calling set_default. If nothing specified now or previously, then None is returned as default.

        :param key:     Key used to lookup the setting in the settings dictionary
        :type key:      (Any)
        :param default: Value to use should the key not be found in the dictionary
        :type default:  (Any)
        :return:        Value of specified settings
        :rtype:         (Any)
        """
        if self.default_value is not None:
            default = self.default_value

        if self.full_filename is None:
            self.set_location()
            if self.autosave or self.dict == {}:
                self.read()
        if not self.use_config_file:
            value = self.dict.get(key, default)
        else:
            value = self.section_class_dict.get(key, None)
            if key not in list(self.section_class_dict.keys()):
                self.section_class_dict[key] = self._SectionDict(
                    key, {}, self.config, self
                )
                value = self.section_class_dict[key]
                value.new_section = True
        return value

    def get_dict(self):
        """
        Returns the current settings dictionary.  If you've not setup the filename for the
        settings, a default one will be used and then read.

        Note that you can display the dictionary in text format by printing the object itself.

        :return: The current settings dictionary
        :rtype:  Dict
        """
        if self.full_filename is None:
            self.set_location()
            if self.autosave or self.dict == {}:
                self.read()
                self.save()
        return self.dict

    def __setitem__(self, item, value):
        """
        Enables setting a setting by using [ ] notation like a dictionary.
        Your code will have this kind of design pattern:
        settings = sg.UserSettings()
        settings[item] = value

        :param item:  The key for the setting to change. Needs to be a hashable type. Basically anything but a list
        :type item:   Any
        :param value: The value to set the setting to
        :type value:  Any
        """
        return self.set(item, value)

    def __getitem__(self, item):
        """
        Enables accessing a setting using [ ] notation like a dictionary.
        If the entry does not exist, then the default value will be returned.  This default
        value is None unless user sets by calling UserSettings.set_default_value(default_value)

        :param item: The key for the setting to change. Needs to be a hashable type. Basically anything but a list
        :type item:  Any
        :return:     The setting value
        :rtype:      Any
        """
        return self.get(item, self.default_value)

    def __delitem__(self, item):
        """
        Delete an individual user setting.  This is the same as calling delete_entry.  The syntax
        for deleting the item using this manner is:
            del settings['entry']
        :param item: The key for the setting to delete
        :type item:  Any
        """
        if self.use_config_file:
            return self.get(item)
        else:
            self.delete_entry(key=item)


# Create a singleton for the settings information so that the settings functions can be used
if UserSettings._default_for_function_interface is None:
    UserSettings._default_for_function_interface = UserSettings()


class _Debugger:
    debugger = None
    DEBUGGER_MAIN_WINDOW_THEME = "dark grey 13"
    DEBUGGER_POPOUT_THEME = "dark grey 13"
    WIDTH_VARIABLES = 23
    WIDTH_RESULTS = 46

    WIDTH_WATCHER_VARIABLES = 20
    WIDTH_WATCHER_RESULTS = 60

    WIDTH_LOCALS = 80
    NUM_AUTO_WATCH = 9

    MAX_LINES_PER_RESULT_FLOATING = 4
    MAX_LINES_PER_RESULT_MAIN = 3

    DEBUGGER_POPOUT_WINDOW_FONT = "Sans 8"
    DEBUGGER_VARIABLE_DETAILS_FONT = "Courier 10"

    """
        #     #                    ######
        ##   ##   ##   # #    #    #     # ###### #####  #    #  ####   ####  ###### #####
        # # # #  #  #  # ##   #    #     # #      #    # #    # #    # #    # #      #    #
        #  #  # #    # # # #  #    #     # #####  #####  #    # #      #      #####  #    #
        #     # ###### # #  # #    #     # #      #    # #    # #  ### #  ### #      #####
        #     # #    # # #   ##    #     # #      #    # #    # #    # #    # #      #   #
        #     # #    # # #    #    ######  ###### #####   ####   ####   ####  ###### #    #
    """

    def __init__(self):
        self.watcher_window = None  # type: Window
        self.popout_window = None  # type: Window
        self.local_choices = {}
        self.myrc = ""
        self.custom_watch = ""
        self.locals = {}
        self.globals = {}
        self.popout_choices = {}

    # Includes the DUAL PANE (now 2 tabs)!  Don't forget REPL is there too!
    def _build_main_debugger_window(self, location=(None, None)):
        old_theme = theme()
        theme(_Debugger.DEBUGGER_MAIN_WINDOW_THEME)

        def InVar(key1):
            row1 = [
                T("    "),
                I(key=key1, size=(_Debugger.WIDTH_VARIABLES, 1)),
                T("", key=key1 + "CHANGED_", size=(_Debugger.WIDTH_RESULTS, 1)),
                B("Detail", key=key1 + "DETAIL_"),
                B("Obj", key=key1 + "OBJ_"),
            ]
            return row1

        variables_frame = [
            InVar("_VAR0_"),
            InVar("_VAR1_"),
            InVar("_VAR2_"),
        ]

        interactive_frame = [
            [
                T(">>> "),
                In(
                    size=(83, 1),
                    key="-REPL-",
                    tooltip='Type in any "expression" or "statement"\n and it will be disaplayed below.\nPress RETURN KEY instead of "Go"\nbutton for faster use',
                ),
                B("Go", bind_return_key=True, visible=True),
            ],
            [
                Multiline(
                    size=(93, 26), key="-OUTPUT-", autoscroll=True, do_not_clear=True
                )
            ],
        ]

        autowatch_frame = [
            [
                Button("Choose Variables To Auto Watch", key="-LOCALS-"),
                Button("Clear All Auto Watches"),
                Button("Show All Variables", key="-SHOW_ALL-"),
                Button("Locals", key="-ALL_LOCALS-"),
                Button("Globals", key="-GLOBALS-"),
                Button("Popout", key="-POPOUT-"),
            ]
        ]

        var_layout = []
        for i in range(_Debugger.NUM_AUTO_WATCH):
            var_layout.append(
                [
                    T(
                        "",
                        size=(_Debugger.WIDTH_WATCHER_VARIABLES, 1),
                        key="_WATCH%s_" % i,
                    ),
                    T(
                        "",
                        size=(
                            _Debugger.WIDTH_WATCHER_RESULTS,
                            _Debugger.MAX_LINES_PER_RESULT_MAIN,
                        ),
                        key="_WATCH%s_RESULT_" % i,
                    ),
                ]
            )

        col1 = [
            # [Frame('Auto Watches', autowatch_frame+variable_values, title_color='blue')]
            [
                Frame(
                    "Auto Watches",
                    autowatch_frame + var_layout,
                    title_color=theme_button_color()[0],
                )
            ]
        ]

        col2 = [
            [
                Frame(
                    "Variables or Expressions to Watch",
                    variables_frame,
                    title_color=theme_button_color()[0],
                ),
            ],
            [
                Frame(
                    "REPL-Light - Press Enter To Execute Commands",
                    interactive_frame,
                    title_color=theme_button_color()[0],
                ),
            ],
        ]

        # Tab based layout
        layout = [
            [Text("Debugging: " + self._find_users_code())],
            [TabGroup([[Tab("Variables", col1), Tab("REPL & Watches", col2)]])],
        ]

        # ------------------------------- Create main window -------------------------------
        window = Window(
            "PySimpleGUI Debugger",
            layout,
            icon=PSG_DEBUGGER_LOGO,
            margins=(0, 0),
            location=location,
            keep_on_top=True,
            right_click_menu=[
                [""],
                [
                    "Exit",
                ],
            ],
        )

        Window._read_call_from_debugger = True
        window.finalize()
        Window._read_call_from_debugger = False

        window.Element("_VAR1_").SetFocus()
        self.watcher_window = window
        theme(old_theme)
        return window

    """
        #     #                    #######                               #
        ##   ##   ##   # #    #    #       #    # ###### #    # #####    #        ####   ####  #####
        # # # #  #  #  # ##   #    #       #    # #      ##   #   #      #       #    # #    # #    #
        #  #  # #    # # # #  #    #####   #    # #####  # #  #   #      #       #    # #    # #    #
        #     # ###### # #  # #    #       #    # #      #  # #   #      #       #    # #    # #####
        #     # #    # # #   ##    #        #  #  #      #   ##   #      #       #    # #    # #
        #     # #    # # #    #    #######   ##   ###### #    #   #      #######  ####   ####  #
    """

    def _refresh_main_debugger_window(self, mylocals, myglobals):
        if not self.watcher_window:  # if there is no window setup, nothing to do
            return False
        event, values = self.watcher_window.read(timeout=1)
        if event in (None, "Exit", "_EXIT_", "-EXIT-"):  # EXIT BUTTON / X BUTTON
            try:
                self.watcher_window.close()
            except Exception:
                pass
            self.watcher_window = None
            return False
        # ------------------------------- Process events from REPL Tab -------------------------------
        cmd = values["-REPL-"]  # get the REPL entered
        # BUTTON - GO (NOTE - This button is invisible!!)
        if event == "Go":  # GO BUTTON
            self.watcher_window.Element("-REPL-").Update("")
            self.watcher_window.Element("-OUTPUT-").Update(
                ">>> {}\n".format(cmd), append=True, autoscroll=True
            )

            try:
                result = eval("{}".format(cmd), myglobals, mylocals)
            except Exception as e:
                if sys.version_info[0] < 3:
                    result = "Not available in Python 2"
                else:
                    try:
                        result = exec("{}".format(cmd), myglobals, mylocals)
                    except Exception as e:
                        result = "Exception {}\n".format(e)

            self.watcher_window.Element("-OUTPUT-").Update(
                "{}\n".format(result), append=True, autoscroll=True
            )
        # BUTTON - DETAIL
        elif event.endswith("_DETAIL_"):  # DETAIL BUTTON
            var = values["_VAR{}_".format(event[4])]
            try:
                result = str(eval(str(var), myglobals, mylocals))
            except Exception:
                result = ""
            old_theme = theme()
            theme(_Debugger.DEBUGGER_MAIN_WINDOW_THEME)
            popup_scrolled(
                str(values["_VAR{}_".format(event[4])]) + "\n" + result,
                title=var,
                non_blocking=True,
                font=_Debugger.DEBUGGER_VARIABLE_DETAILS_FONT,
            )
            theme(old_theme)
        # BUTTON - OBJ
        elif event.endswith("_OBJ_"):  # OBJECT BUTTON
            var = values["_VAR{}_".format(event[4])]
            try:
                result = ObjToStringSingleObj(mylocals[var])
            except Exception as e:
                try:
                    result = eval("{}".format(var), myglobals, mylocals)
                    result = ObjToStringSingleObj(result)
                except Exception as e:
                    result = "{}\nError showing object {}".format(e, var)
            old_theme = theme()
            theme(_Debugger.DEBUGGER_MAIN_WINDOW_THEME)
            popup_scrolled(
                str(var) + "\n" + str(result),
                title=var,
                non_blocking=True,
                font=_Debugger.DEBUGGER_VARIABLE_DETAILS_FONT,
            )
            theme(old_theme)
        # ------------------------------- Process Watch Tab -------------------------------
        # BUTTON - Choose Locals to see
        elif event == "-LOCALS-":  # Show all locals BUTTON
            self._choose_auto_watches(mylocals)
        # BUTTON - Locals (quick popup)
        elif event == "-ALL_LOCALS-":
            self._display_all_vars("All Locals", mylocals)
        # BUTTON - Globals (quick popup)
        elif event == "-GLOBALS-":
            self._display_all_vars("All Globals", myglobals)
        # BUTTON - clear all
        elif event == "Clear All Auto Watches":
            if (
                    popup_yes_no(
                        "Do you really want to clear all Auto-Watches?", "Really Clear??"
                    )
                    == "Yes"
            ):
                self.local_choices = {}
                self.custom_watch = ""
        # BUTTON - Popout
        elif event == "-POPOUT-":
            if not self.popout_window:
                self._build_floating_window()
        # BUTTON - Show All
        elif event == "-SHOW_ALL-":
            for key in self.locals:
                self.local_choices[key] = not key.startswith("_")

        # -------------------- Process the manual "watch list" ------------------
        for i in range(3):
            key = "_VAR{}_".format(i)
            out_key = "_VAR{}_CHANGED_".format(i)
            self.myrc = ""
            if self.watcher_window.Element(key):
                var = values[key]
                try:
                    result = eval(str(var), myglobals, mylocals)
                except Exception:
                    result = ""
                self.watcher_window.Element(out_key).Update(str(result))
            else:
                self.watcher_window.Element(out_key).Update("")

        # -------------------- Process the automatic "watch list" ------------------
        slot = 0
        for key in self.local_choices:
            if key == "-CUSTOM_WATCH-":
                continue
            if self.local_choices[key]:
                self.watcher_window.Element("_WATCH{}_".format(slot)).Update(key)
                try:
                    self.watcher_window.Element(
                        "_WATCH{}_RESULT_".format(slot), silent_on_error=True
                    ).Update(mylocals[key])
                except Exception:
                    self.watcher_window.Element("_WATCH{}_RESULT_".format(slot)).Update(
                        ""
                    )
                slot += 1

            if (
                    slot + int(not self.custom_watch in (None, ""))
                    >= _Debugger.NUM_AUTO_WATCH
            ):
                break
        # If a custom watch was set, display that value in the window
        if self.custom_watch:
            self.watcher_window.Element("_WATCH{}_".format(slot)).Update(
                self.custom_watch
            )
            try:
                self.myrc = eval(self.custom_watch, myglobals, mylocals)
            except Exception:
                self.myrc = ""
            self.watcher_window.Element("_WATCH{}_RESULT_".format(slot)).Update(
                self.myrc
            )
            slot += 1
        # blank out all of the slots not used (blank)
        for i in range(slot, _Debugger.NUM_AUTO_WATCH):
            self.watcher_window.Element("_WATCH{}_".format(i)).Update("")
            self.watcher_window.Element("_WATCH{}_RESULT_".format(i)).Update("")

        return True  # return indicating the window stayed open

    def _find_users_code(self):
        try:  # lots can go wrong so wrapping the entire thing
            trace_details = traceback.format_stack()
            file_info_pysimplegui, error_message = None, ""
            for line in reversed(trace_details):
                if __file__ not in line:
                    file_info_pysimplegui = line.split(",")[0]
                    error_message = line
                    break
            if file_info_pysimplegui is None:
                return ""
            error_parts = None
            if error_message != "":
                error_parts = error_message.split(", ")
                if len(error_parts) < 4:
                    error_message = (
                            error_parts[0]
                            + "\n"
                            + error_parts[1]
                            + "\n"
                            + "".join(error_parts[2:])
                    )
            if error_parts is None:
                print("*** Error popup attempted but unable to parse error details ***")
                print(trace_details)
                return ""
            filename = error_parts[0][error_parts[0].index("File ") + 5:]
            return filename
        except Exception:
            return

    """
        ######                                 #     #
        #     #  ####  #####  #    # #####     #  #  # # #    # #####   ####  #    #
        #     # #    # #    # #    # #    #    #  #  # # ##   # #    # #    # #    #
        ######  #    # #    # #    # #    #    #  #  # # # #  # #    # #    # #    #
        #       #    # #####  #    # #####     #  #  # # #  # # #    # #    # # ## #
        #       #    # #      #    # #         #  #  # # #   ## #    # #    # ##  ##
        #        ####  #       ####  #          ## ##  # #    # #####   ####  #    #

        ######                                    #                     #     #
        #     # #    # #    # #####   ####       # #   #      #         #     #   ##   #####   ####
        #     # #    # ##  ## #    # #          #   #  #      #         #     #  #  #  #    # #
        #     # #    # # ## # #    #  ####     #     # #      #         #     # #    # #    #  ####
        #     # #    # #    # #####       #    ####### #      #          #   #  ###### #####       #
        #     # #    # #    # #      #    #    #     # #      #           # #   #    # #   #  #    #
        ######   ####  #    # #       ####     #     # ###### ######       #    #    # #    #  ####
    """

    # displays them into a single text box

    def _display_all_vars(self, title, dict):
        num_cols = 3
        output_text = ""
        num_lines = 2
        cur_col = 0
        out_text = title + "\n"
        longest_line = max([len(key) for key in dict])
        line = []
        sorted_dict = {}
        for key in sorted(dict.keys()):
            sorted_dict[key] = dict[key]
        for key in sorted_dict:
            value = dict[key]
            # wrapped_list = textwrap.wrap(str(value), 60)
            # wrapped_text = '\n'.join(wrapped_list)
            wrapped_text = str(value)
            out_text += "{} - {}\n".format(key, wrapped_text)
            # if cur_col + 1 == num_cols:
            #     cur_col = 0
            #     num_lines += len(wrapped_list)
            # else:
            #     cur_col += 1
        old_theme = theme()
        theme(_Debugger.DEBUGGER_MAIN_WINDOW_THEME)
        popup_scrolled(
            out_text,
            title=title,
            non_blocking=True,
            font=_Debugger.DEBUGGER_VARIABLE_DETAILS_FONT,
            keep_on_top=True,
            icon=PSG_DEBUGGER_LOGO,
        )
        theme(old_theme)

    """
        #####                                        #     #
       #     # #    #  ####   ####   ####  ######    #  #  #   ##   #####  ####  #    #
       #       #    # #    # #    # #      #         #  #  #  #  #    #   #    # #    #
       #       ###### #    # #    #  ####  #####     #  #  # #    #   #   #      ######
       #       #    # #    # #    #      # #         #  #  # ######   #   #      #    #
       #     # #    # #    # #    # #    # #         #  #  # #    #   #   #    # #    #
        #####  #    #  ####   ####   ####  ######     ## ##  #    #   #    ####  #    #

        #     #                                                       #     #
        #     #   ##   #####  #   ##   #####  #      ######  ####     #  #  # # #    #
        #     #  #  #  #    # #  #  #  #    # #      #      #         #  #  # # ##   #
        #     # #    # #    # # #    # #####  #      #####   ####     #  #  # # # #  #
         #   #  ###### #####  # ###### #    # #      #           #    #  #  # # #  # #
          # #   #    # #   #  # #    # #    # #      #      #    #    #  #  # # #   ##
           #    #    # #    # # #    # #####  ###### ######  ####      ## ##  # #    #
    """

    def _choose_auto_watches(self, my_locals):
        old_theme = theme()
        theme(_Debugger.DEBUGGER_MAIN_WINDOW_THEME)
        num_cols = 3
        output_text = ""
        num_lines = 2
        cur_col = 0
        layout = [
            [
                Text(
                    'Choose your "Auto Watch" variables',
                    font="ANY 14",
                    text_color="red",
                )
            ]
        ]
        longest_line = max([len(key) for key in my_locals])
        line = []
        sorted_dict = {}
        for key in sorted(my_locals.keys()):
            sorted_dict[key] = my_locals[key]
        for key in sorted_dict:
            line.append(
                CB(
                    key,
                    key=key,
                    size=(longest_line, 1),
                    default=self.local_choices[key]
                    if key in self.local_choices
                    else False,
                )
            )
            if cur_col + 1 == num_cols:
                cur_col = 0
                layout.append(line)
                line = []
            else:
                cur_col += 1
        if cur_col:
            layout.append(line)

        layout += [
            [
                Text("Custom Watch (any expression)"),
                Input(
                    default_text=self.custom_watch, size=(40, 1), key="-CUSTOM_WATCH-"
                ),
            ]
        ]
        layout += [
            [
                Ok(),
                Cancel(),
                Button("Clear All"),
                Button("Select [almost] All", key="-AUTO_SELECT-"),
            ]
        ]

        window = Window(
            "Choose Watches",
            layout,
            icon=PSG_DEBUGGER_LOGO,
            finalize=True,
            keep_on_top=True,
        )

        while True:  # event loop
            event, values = window.read()
            if event in (None, "Cancel", "-EXIT-"):
                break
            elif event == "Ok":
                self.local_choices = values
                self.custom_watch = values["-CUSTOM_WATCH-"]
                break
            elif event == "Clear All":
                popup_quick_message(
                    "Cleared Auto Watches",
                    auto_close=True,
                    auto_close_duration=3,
                    non_blocking=True,
                    text_color="red",
                    font="ANY 18",
                )
                for key in sorted_dict:
                    window.Element(key).Update(False)
                window.Element("-CUSTOM_WATCH-").Update("")
            elif event == "Select All":
                for key in sorted_dict:
                    window.Element(key).Update(False)
            elif event == "-AUTO_SELECT-":
                for key in sorted_dict:
                    window.Element(key).Update(not key.startswith("_"))

        # exited event loop
        window.Close()
        theme(old_theme)

    """
        ######                            #######
        #     # #    # # #      #####     #       #       ####    ##   ##### # #    #  ####
        #     # #    # # #      #    #    #       #      #    #  #  #    #   # ##   # #    #
        ######  #    # # #      #    #    #####   #      #    # #    #   #   # # #  # #
        #     # #    # # #      #    #    #       #      #    # ######   #   # #  # # #  ###
        #     # #    # # #      #    #    #       #      #    # #    #   #   # #   ## #    #
        ######   ####  # ###### #####     #       ######  ####  #    #   #   # #    #  ####

        #     #
        #  #  # # #    # #####   ####  #    #
        #  #  # # ##   # #    # #    # #    #
        #  #  # # # #  # #    # #    # #    #
        #  #  # # #  # # #    # #    # # ## #
        #  #  # # #   ## #    # #    # ##  ##
         ## ##  # #    # #####   ####  #    #
    """

    def _build_floating_window(self, location=(None, None)):
        """

        :param location:
        :type location:

        """
        if self.popout_window:  # if floating window already exists, close it first
            self.popout_window.Close()
        old_theme = theme()
        theme(_Debugger.DEBUGGER_POPOUT_THEME)
        num_cols = 2
        width_var = 15
        width_value = 30
        layout = []
        line = []
        col = 0
        # self.popout_choices = self.local_choices
        self.popout_choices = {}
        if (
                self.popout_choices == {}
        ):  # if nothing chosen, then choose all non-_ variables
            for key in sorted(self.locals.keys()):
                self.popout_choices[key] = not key.startswith("_")

        width_var = max([len(key) for key in self.popout_choices])
        for key in self.popout_choices:
            if self.popout_choices[key] is True:
                value = str(self.locals.get(key))
                h = min(
                    len(value) // width_value + 1,
                    _Debugger.MAX_LINES_PER_RESULT_FLOATING,
                )
                line += [
                    Text(
                        "{}".format(key),
                        size=(width_var, 1),
                        font=_Debugger.DEBUGGER_POPOUT_WINDOW_FONT,
                    ),
                    Text(" = ", font=_Debugger.DEBUGGER_POPOUT_WINDOW_FONT),
                    Text(
                        value,
                        key=key,
                        size=(width_value, h),
                        font=_Debugger.DEBUGGER_POPOUT_WINDOW_FONT,
                    ),
                ]
                if col + 1 < num_cols:
                    line += [VerticalSeparator(), T(" ")]
                col += 1
            if col >= num_cols:
                layout.append(line)
                line = []
                col = 0
        if col != 0:
            layout.append(line)
        layout = [
            [T(SYMBOL_X, enable_events=True, key="-EXIT-", font="_ 7")],
            [Column(layout)],
        ]

        Window._read_call_from_debugger = True
        self.popout_window = Window(
            "Floating",
            layout,
            alpha_channel=0,
            no_titlebar=True,
            grab_anywhere=True,
            element_padding=(0, 0),
            margins=(0, 0),
            keep_on_top=True,
            right_click_menu=["&Right", ["Debugger::RightClick", "Exit::RightClick"]],
            location=location,
            finalize=True,
        )
        Window._read_call_from_debugger = False

        if location == (None, None):
            screen_size = self.popout_window.GetScreenDimensions()
            self.popout_window.Move(screen_size[0] - self.popout_window.Size[0], 0)
        self.popout_window.SetAlpha(1)
        theme(old_theme)
        return True

    """
        ######
        #     # ###### ###### #####  ######  ####  #    #
        #     # #      #      #    # #      #      #    #
        ######  #####  #####  #    # #####   ####  ######
        #   #   #      #      #####  #           # #    #
        #    #  #      #      #   #  #      #    # #    #
        #     # ###### #      #    # ######  ####  #    #

        #######
        #       #       ####    ##   ##### # #    #  ####
        #       #      #    #  #  #    #   # ##   # #    #
        #####   #      #    # #    #   #   # # #  # #
        #       #      #    # ######   #   # #  # # #  ###
        #       #      #    # #    #   #   # #   ## #    #
        #       ######  ####  #    #   #   # #    #  ####

        #     #
        #  #  # # #    # #####   ####  #    #
        #  #  # # ##   # #    # #    # #    #
        #  #  # # # #  # #    # #    # #    #
        #  #  # # #  # # #    # #    # # ## #
        #  #  # # #   ## #    # #    # ##  ##
         ## ##  # #    # #####   ####  #    #
    """

    def _refresh_floating_window(self):
        if not self.popout_window:
            return
        for key in self.popout_choices:
            if self.popout_choices[key] is True and key in self.locals:
                if key is not None and self.popout_window is not None:
                    self.popout_window.Element(key, silent_on_error=True).Update(
                        self.locals.get(key)
                    )
        event, values = self.popout_window.read(timeout=5)
        if event in (None, "_EXIT_", "Exit::RightClick", "-EXIT-"):
            self.popout_window.Close()
            self.popout_window = None
        elif event == "Debugger::RightClick":
            show_debugger_window()





# ============================== set_options ========#
# Sets the icon to be used by default                #
# ===================================================#
def set_options(
    icon=None,
    button_color=None,
    element_size=(None, None),
    button_element_size=(None, None),
    margins=(None, None),
    element_padding=(None, None),
    auto_size_text=None,
    auto_size_buttons=None,
    font=None,
    border_width=None,
    slider_border_width=None,
    slider_relief=None,
    slider_orientation=None,
    autoclose_time=None,
    message_box_line_width=None,
    progress_meter_border_depth=None,
    progress_meter_style=None,
    progress_meter_relief=None,
    progress_meter_color=None,
    progress_meter_size=None,
    text_justification=None,
    background_color=None,
    element_background_color=None,
    text_element_background_color=None,
    input_elements_background_color=None,
    input_text_color=None,
    scrollbar_color=None,
    text_color=None,
    element_text_color=None,
    debug_win_size=(None, None),
    window_location=(None, None),
    error_button_color=(None, None),
    tooltip_time=None,
    tooltip_font=None,
    use_ttk_buttons=None,
    ttk_theme=None,
    suppress_error_popups=None,
    suppress_raise_key_errors=None,
    suppress_key_guessing=None,
    warn_button_key_duplicates=False,
    enable_treeview_869_patch=None,
    enable_mac_notitlebar_patch=None,
    use_custom_titlebar=None,
    titlebar_background_color=None,
    titlebar_text_color=None,
    titlebar_font=None,
    titlebar_icon=None,
    user_settings_path=None,
    pysimplegui_settings_path=None,
    pysimplegui_settings_filename=None,
    keep_on_top=None,
    dpi_awareness=None,
    scaling=None,
    disable_modal_windows=None,
    force_modal_windows=None,
    tooltip_offset=(None, None),
    sbar_trough_color=None,
    sbar_background_color=None,
    sbar_arrow_color=None,
    sbar_width=None,
    sbar_arrow_width=None,
    sbar_frame_color=None,
    sbar_relief=None,
    alpha_channel=None,
    hide_window_when_creating=None,
    use_button_shortcuts=None,
    watermark_text=None,
):
    """
    :param icon:                            Can be either a filename or Base64 value. For Windows if filename, it MUST be ICO format. For Linux, must NOT be ICO. Most portable is to use a Base64 of a PNG file. This works universally across all OS's
    :type icon:                             bytes | str
    :param button_color:                    Color of the button (text, background)
    :type button_color:                     (str, str) | str
    :param element_size:                    element size (width, height) in characters
    :type element_size:                     (int, int)
    :param button_element_size:             Size of button
    :type button_element_size:              (int, int)
    :param margins:                         (left/right, top/bottom) tkinter margins around outsize. Amount of pixels to leave inside the window's frame around the edges before your elements are shown.
    :type margins:                          (int, int)
    :param element_padding:                 Default amount of padding to put around elements in window (left/right, top/bottom) or ((left, right), (top, bottom))
    :type element_padding:                  (int, int) or ((int, int),(int,int))
    :param auto_size_text:                  True if the Widget should be shrunk to exactly fit the number of chars to show
    :type auto_size_text:                   bool
    :param auto_size_buttons:               True if Buttons in this Window should be sized to exactly fit the text on this.
    :type auto_size_buttons:                (bool)
    :param font:                            specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:                             (str or (str, int[, str]) or None)
    :param border_width:                    width of border around element
    :type border_width:                     (int)
    :param slider_border_width:             Width of the border around sliders
    :type slider_border_width:              (int)
    :param slider_relief:                   Type of relief to use for sliders
    :type slider_relief:                    (str)
    :param slider_orientation:              ???
    :type slider_orientation:               ???
    :param autoclose_time:                  ???
    :type autoclose_time:                   ???
    :param message_box_line_width:          ???
    :type message_box_line_width:           ???
    :param progress_meter_border_depth:     ???
    :type progress_meter_border_depth:      ???
    :param progress_meter_style:            You can no longer set a progress bar style. All ttk styles must be the same for the window
    :type progress_meter_style:             ???
    :param progress_meter_relief:
    :type progress_meter_relief:            ???
    :param progress_meter_color:            ???
    :type progress_meter_color:             ???
    :param progress_meter_size:             ???
    :type progress_meter_size:              ???
    :param text_justification:              Default text justification for all Text Elements in window
    :type text_justification:               'left' | 'right' | 'center'
    :param background_color:                color of background
    :type background_color:                 (str)
    :param element_background_color:        element background color
    :type element_background_color:         (str)
    :param text_element_background_color:   text element background color
    :type text_element_background_color:    (str)
    :param input_elements_background_color: Default color to use for the background of input elements
    :type input_elements_background_color:  (str)
    :param input_text_color:                Default color to use for the text for Input elements
    :type input_text_color:                 (str)
    :param scrollbar_color:                 Default color to use for the slider trough
    :type scrollbar_color:                  (str)
    :param text_color:                      color of the text
    :type text_color:                       (str)
    :param element_text_color:              Default color to use for Text elements
    :type element_text_color:               (str)
    :param debug_win_size:                  window size
    :type debug_win_size:                   (int, int)
    :param window_location:                 Default location to place windows. Not setting will center windows on the display
    :type window_location:                  (int, int) | None
    :param error_button_color:              (Default = (None))
    :type error_button_color:               ???
    :param tooltip_time:                    time in milliseconds to wait before showing a tooltip. Default is 400ms
    :type tooltip_time:                     (int)
    :param tooltip_font:                    font to use for all tooltips
    :type tooltip_font:                     str or Tuple[str, int] or Tuple[str, int, str]
    :param use_ttk_buttons:                 if True will cause all buttons to be ttk buttons
    :type use_ttk_buttons:                  (bool)
    :param ttk_theme:                       Theme to use with ttk widgets.  Choices (on Windows) include - 'default', 'winnative', 'clam', 'alt', 'classic', 'vista', 'xpnative'
    :type ttk_theme:                        (str)
    :param suppress_error_popups:           If True then error popups will not be shown if generated internally to PySimpleGUI
    :type suppress_error_popups:            (bool)
    :param suppress_raise_key_errors:       If True then key errors won't be raised (you'll still get popup error)
    :type suppress_raise_key_errors:        (bool)
    :param suppress_key_guessing:           If True then key errors won't try and find closest matches for you
    :type suppress_key_guessing:            (bool)
    :param warn_button_key_duplicates:      If True then duplicate Button Keys generate warnings (not recommended as they're expected)
    :type warn_button_key_duplicates:       (bool)
    :param enable_treeview_869_patch:       If True, then will use the treeview color patch for tk 8.6.9
    :type enable_treeview_869_patch:        (bool)
    :param enable_mac_notitlebar_patch:     If True then Windows with no titlebar use an alternative technique when tkinter version < 8.6.10
    :type enable_mac_notitlebar_patch:      (bool)
    :param use_custom_titlebar:             If True then a custom titlebar is used instead of the normal system titlebar
    :type use_custom_titlebar:              (bool)
    :param titlebar_background_color:       If custom titlebar indicated by use_custom_titlebar, then use this as background color
    :type titlebar_background_color:        str | None
    :param titlebar_text_color:             If custom titlebar indicated by use_custom_titlebar, then use this as text color
    :type titlebar_text_color:              str | None
    :param titlebar_font:                   If custom titlebar indicated by use_custom_titlebar, then use this as title font
    :type titlebar_font:                    (str or (str, int[, str]) or None) | None
    :param titlebar_icon:                   If custom titlebar indicated by use_custom_titlebar, then use this as the icon (file or base64 bytes)
    :type titlebar_icon:                    bytes | str
    :param user_settings_path:              default path for user_settings API calls. Expanded with os.path.expanduser so can contain ~ to represent user
    :type user_settings_path:               (str)
    :param pysimplegui_settings_path:       default path for the global PySimpleGUI user_settings
    :type pysimplegui_settings_path:        (str)
    :param pysimplegui_settings_filename:   default filename for the global PySimpleGUI user_settings
    :type pysimplegui_settings_filename:    (str)
    :param keep_on_top:                     If True then all windows will automatically be set to keep_on_top=True
    :type keep_on_top:                      (bool)
    :param dpi_awareness:                   If True then will turn on DPI awareness (Windows only at the moment)
    :type dpi_awareness:                    (bool)
    :param scaling:                         Sets the default scaling for all windows including popups, etc.
    :type scaling:                          (float)
    :param disable_modal_windows:           If True then all windows, including popups, will not be modal windows (unless they've been set to FORCED using another option)
    :type disable_modal_windows:            (bool)
    :param force_modal_windows:             If True then all windows will be modal (the disable option will be ignored... all windows will be forced to be modal)
    :type force_modal_windows:              (bool)
    :param tooltip_offset:                  Offset to use for tooltips as a tuple. These values will be added to the mouse location when the widget was entered.
    :type tooltip_offset:                   ((None, None) | (int, int))
    :param sbar_trough_color:               Scrollbar color of the trough
    :type sbar_trough_color:                (str)
    :param sbar_background_color:           Scrollbar color of the background of the arrow buttons at the ends AND the color of the "thumb" (the thing you grab and slide). Switches to arrow color when mouse is over
    :type sbar_background_color:            (str)
    :param sbar_arrow_color:                Scrollbar color of the arrow at the ends of the scrollbar (it looks like a button). Switches to background color when mouse is over
    :type sbar_arrow_color:                 (str)
    :param sbar_width:                      Scrollbar width in pixels
    :type sbar_width:                       (int)
    :param sbar_arrow_width:                Scrollbar width of the arrow on the scrollbar. It will potentially impact the overall width of the scrollbar
    :type sbar_arrow_width:                 (int)
    :param sbar_frame_color:                Scrollbar Color of frame around scrollbar (available only on some ttk themes)
    :type sbar_frame_color:                 (str)
    :param sbar_relief:                     Scrollbar relief that will be used for the "thumb" of the scrollbar (the thing you grab that slides). Should be a constant that is defined at starting with "RELIEF_" - RELIEF_RAISED, RELIEF_SUNKEN, RELIEF_FLAT, RELIEF_RIDGE, RELIEF_GROOVE, RELIEF_SOLID
    :type sbar_relief:                      (str)
    :param alpha_channel:                   Default alpha channel to be used on all windows
    :type alpha_channel:                    (float)
    :param hide_window_when_creating:       If True then alpha will be set to 0 while a window is made and moved to location indicated
    :type hide_window_when_creating:        (bool)
    :param use_button_shortcuts:            If True then Shortcut Char will be used with Buttons
    :type use_button_shortcuts:             (bool)
    :param watermark_text:                  Set the text that will be used if a window is watermarked
    :type watermark_text:                   (str)
    :return:                                None
    :rtype:                                 None
    """

    global DEFAULT_ELEMENT_SIZE
    global DEFAULT_BUTTON_ELEMENT_SIZE
    global DEFAULT_MARGINS  # Margins for each LEFT/RIGHT margin is first term
    global DEFAULT_ELEMENT_PADDING  # Padding between elements (row, col) in pixels
    global DEFAULT_AUTOSIZE_TEXT
    global DEFAULT_AUTOSIZE_BUTTONS
    global DEFAULT_FONT
    global DEFAULT_BORDER_WIDTH
    global DEFAULT_AUTOCLOSE_TIME
    global DEFAULT_BUTTON_COLOR
    global MESSAGE_BOX_LINE_WIDTH
    global DEFAULT_PROGRESS_BAR_BORDER_WIDTH
    global DEFAULT_PROGRESS_BAR_STYLE
    global DEFAULT_PROGRESS_BAR_RELIEF
    global DEFAULT_PROGRESS_BAR_COLOR
    global DEFAULT_PROGRESS_BAR_SIZE
    global DEFAULT_TEXT_JUSTIFICATION
    global DEFAULT_DEBUG_WINDOW_SIZE
    global DEFAULT_SLIDER_BORDER_WIDTH
    global DEFAULT_SLIDER_RELIEF
    global DEFAULT_SLIDER_ORIENTATION
    global DEFAULT_BACKGROUND_COLOR
    global DEFAULT_INPUT_ELEMENTS_COLOR
    global DEFAULT_ELEMENT_BACKGROUND_COLOR
    global DEFAULT_TEXT_ELEMENT_BACKGROUND_COLOR
    global DEFAULT_SCROLLBAR_COLOR
    global DEFAULT_TEXT_COLOR
    global DEFAULT_WINDOW_LOCATION
    global DEFAULT_ELEMENT_TEXT_COLOR
    global DEFAULT_INPUT_TEXT_COLOR
    global DEFAULT_TOOLTIP_TIME
    global DEFAULT_ERROR_BUTTON_COLOR
    global DEFAULT_TTK_THEME
    global USE_TTK_BUTTONS
    global TOOLTIP_FONT
    global SUPPRESS_ERROR_POPUPS
    global SUPPRESS_RAISE_KEY_ERRORS
    global SUPPRESS_KEY_GUESSING
    global WARN_DUPLICATE_BUTTON_KEY_ERRORS
    global ENABLE_TREEVIEW_869_PATCH
    global ENABLE_MAC_NOTITLEBAR_PATCH
    global USE_CUSTOM_TITLEBAR
    global CUSTOM_TITLEBAR_BACKGROUND_COLOR
    global CUSTOM_TITLEBAR_TEXT_COLOR
    global CUSTOM_TITLEBAR_ICON
    global CUSTOM_TITLEBAR_FONT
    global DEFAULT_USER_SETTINGS_PATH
    global DEFAULT_USER_SETTINGS_PYSIMPLEGUI_PATH
    global DEFAULT_USER_SETTINGS_PYSIMPLEGUI_FILENAME
    global DEFAULT_KEEP_ON_TOP
    global DEFAULT_SCALING
    global DEFAULT_MODAL_WINDOWS_ENABLED
    global DEFAULT_MODAL_WINDOWS_FORCED
    global DEFAULT_TOOLTIP_OFFSET
    global DEFAULT_ALPHA_CHANNEL
    global _pysimplegui_user_settings
    global ttk_part_overrides_from_options
    global DEFAULT_HIDE_WINDOW_WHEN_CREATING
    global DEFAULT_USE_BUTTON_SHORTCUTS
    # global _my_windows

    if icon:
        Window._user_defined_icon = icon
        # _my_windows._user_defined_icon = icon

    if button_color is not None:
        if button_color == COLOR_SYSTEM_DEFAULT:
            DEFAULT_BUTTON_COLOR = (COLOR_SYSTEM_DEFAULT, COLOR_SYSTEM_DEFAULT)
        else:
            DEFAULT_BUTTON_COLOR = button_color

    if element_size != (None, None):
        DEFAULT_ELEMENT_SIZE = element_size

    if button_element_size != (None, None):
        DEFAULT_BUTTON_ELEMENT_SIZE = button_element_size

    if margins != (None, None):
        DEFAULT_MARGINS = margins

    if element_padding != (None, None):
        DEFAULT_ELEMENT_PADDING = element_padding

    if auto_size_text is not None:
        DEFAULT_AUTOSIZE_TEXT = auto_size_text

    if auto_size_buttons is not None:
        DEFAULT_AUTOSIZE_BUTTONS = auto_size_buttons

    if font is not None:
        DEFAULT_FONT = font

    if border_width is not None:
        DEFAULT_BORDER_WIDTH = border_width

    if autoclose_time is not None:
        DEFAULT_AUTOCLOSE_TIME = autoclose_time

    if message_box_line_width is not None:
        MESSAGE_BOX_LINE_WIDTH = message_box_line_width

    if progress_meter_border_depth is not None:
        DEFAULT_PROGRESS_BAR_BORDER_WIDTH = progress_meter_border_depth

    if progress_meter_style is not None:
        warnings.warn(
            "You can no longer set a progress bar style. All ttk styles must be the same for the window",
            UserWarning,
        )
        # DEFAULT_PROGRESS_BAR_STYLE = progress_meter_style

    if progress_meter_relief is not None:
        DEFAULT_PROGRESS_BAR_RELIEF = progress_meter_relief

    if progress_meter_color is not None:
        DEFAULT_PROGRESS_BAR_COLOR = progress_meter_color

    if progress_meter_size is not None:
        DEFAULT_PROGRESS_BAR_SIZE = progress_meter_size

    if slider_border_width is not None:
        DEFAULT_SLIDER_BORDER_WIDTH = slider_border_width

    if slider_orientation is not None:
        DEFAULT_SLIDER_ORIENTATION = slider_orientation

    if slider_relief is not None:
        DEFAULT_SLIDER_RELIEF = slider_relief

    if text_justification is not None:
        DEFAULT_TEXT_JUSTIFICATION = text_justification

    if background_color is not None:
        DEFAULT_BACKGROUND_COLOR = background_color

    if text_element_background_color is not None:
        DEFAULT_TEXT_ELEMENT_BACKGROUND_COLOR = text_element_background_color

    if input_elements_background_color is not None:
        DEFAULT_INPUT_ELEMENTS_COLOR = input_elements_background_color

    if element_background_color is not None:
        DEFAULT_ELEMENT_BACKGROUND_COLOR = element_background_color

    if window_location != (None, None):
        DEFAULT_WINDOW_LOCATION = window_location

    if debug_win_size != (None, None):
        DEFAULT_DEBUG_WINDOW_SIZE = debug_win_size

    if text_color is not None:
        DEFAULT_TEXT_COLOR = text_color

    if scrollbar_color is not None:
        DEFAULT_SCROLLBAR_COLOR = scrollbar_color

    if element_text_color is not None:
        DEFAULT_ELEMENT_TEXT_COLOR = element_text_color

    if input_text_color is not None:
        DEFAULT_INPUT_TEXT_COLOR = input_text_color

    if tooltip_time is not None:
        DEFAULT_TOOLTIP_TIME = tooltip_time

    if error_button_color != (None, None):
        DEFAULT_ERROR_BUTTON_COLOR = error_button_color

    if ttk_theme is not None:
        DEFAULT_TTK_THEME = ttk_theme

    if use_ttk_buttons is not None:
        USE_TTK_BUTTONS = use_ttk_buttons

    if tooltip_font is not None:
        TOOLTIP_FONT = tooltip_font

    if suppress_error_popups is not None:
        SUPPRESS_ERROR_POPUPS = suppress_error_popups

    if suppress_raise_key_errors is not None:
        SUPPRESS_RAISE_KEY_ERRORS = suppress_raise_key_errors

    if suppress_key_guessing is not None:
        SUPPRESS_KEY_GUESSING = suppress_key_guessing

    if warn_button_key_duplicates is not None:
        WARN_DUPLICATE_BUTTON_KEY_ERRORS = warn_button_key_duplicates

    if enable_treeview_869_patch is not None:
        ENABLE_TREEVIEW_869_PATCH = enable_treeview_869_patch

    if enable_mac_notitlebar_patch is not None:
        ENABLE_MAC_NOTITLEBAR_PATCH = enable_mac_notitlebar_patch

    if use_custom_titlebar is not None:
        USE_CUSTOM_TITLEBAR = use_custom_titlebar

    if titlebar_background_color is not None:
        CUSTOM_TITLEBAR_BACKGROUND_COLOR = titlebar_background_color

    if titlebar_text_color is not None:
        CUSTOM_TITLEBAR_TEXT_COLOR = titlebar_text_color

    if titlebar_font is not None:
        CUSTOM_TITLEBAR_FONT = titlebar_font

    if titlebar_icon is not None:
        CUSTOM_TITLEBAR_ICON = titlebar_icon

    if user_settings_path is not None:
        DEFAULT_USER_SETTINGS_PATH = user_settings_path

    if pysimplegui_settings_path is not None:
        DEFAULT_USER_SETTINGS_PYSIMPLEGUI_PATH = pysimplegui_settings_path

    if pysimplegui_settings_filename is not None:
        DEFAULT_USER_SETTINGS_PYSIMPLEGUI_FILENAME = pysimplegui_settings_filename

    if (
        pysimplegui_settings_filename is not None
        or pysimplegui_settings_filename is not None
    ):
        _pysimplegui_user_settings = UserSettings(
            filename=DEFAULT_USER_SETTINGS_PYSIMPLEGUI_FILENAME,
            path=DEFAULT_USER_SETTINGS_PYSIMPLEGUI_PATH,
        )

    if keep_on_top is not None:
        DEFAULT_KEEP_ON_TOP = keep_on_top

    if dpi_awareness:
        if running_windows():
            if platform.release() == "7":
                ctypes.windll.user32.SetProcessDPIAware()
            elif platform.release() == "8" or platform.release() == "10":
                ctypes.windll.shcore.SetProcessDpiAwareness(1)

    if scaling is not None:
        DEFAULT_SCALING = scaling

    if disable_modal_windows is not None:
        DEFAULT_MODAL_WINDOWS_ENABLED = not disable_modal_windows

    if force_modal_windows is not None:
        DEFAULT_MODAL_WINDOWS_FORCED = force_modal_windows

    if tooltip_offset != (None, None):
        DEFAULT_TOOLTIP_OFFSET = tooltip_offset

    if alpha_channel is not None:
        DEFAULT_ALPHA_CHANNEL = alpha_channel

    # ---------------- ttk scrollbar section ----------------
    if sbar_background_color is not None:
        ttk_part_overrides_from_options.sbar_background_color = sbar_background_color

    if sbar_trough_color is not None:
        ttk_part_overrides_from_options.sbar_trough_color = sbar_trough_color

    if sbar_arrow_color is not None:
        ttk_part_overrides_from_options.sbar_arrow_color = sbar_arrow_color

    if sbar_frame_color is not None:
        ttk_part_overrides_from_options.sbar_frame_color = sbar_frame_color

    if sbar_relief is not None:
        ttk_part_overrides_from_options.sbar_relief = sbar_relief

    if sbar_arrow_width is not None:
        ttk_part_overrides_from_options.sbar_arrow_width = sbar_arrow_width

    if sbar_width is not None:
        ttk_part_overrides_from_options.sbar_width = sbar_width

    if hide_window_when_creating is not None:
        DEFAULT_HIDE_WINDOW_WHEN_CREATING = hide_window_when_creating

    if use_button_shortcuts is not None:
        DEFAULT_USE_BUTTON_SHORTCUTS = use_button_shortcuts

    if watermark_text is not None:
        Window._watermark_user_text = watermark_text

    return True




# ----====----====----====----====----==== STARTUP TK ====----====----====----====----====----#
def StartupTK(window):
    """
    NOT user callable
    Creates the window (for real) lays out all the elements, etc.  It's a HUGE set of things it does.  It's the basic
    "porting layer" that will change depending on the GUI framework PySimpleGUI is running on top of.

    :param window: you window object
    :type window:  (Window)

    """
    window = window  # type: Window
    # global _my_windows
    # ow = _my_windows.NumOpenWindows
    ow = Window.NumOpenWindows
    # print('Starting TK open Windows = {}'.format(ow))
    if ENABLE_TK_WINDOWS:
        root = tk.Tk()
    elif not ow and not window.ForceTopLevel:
        # if first window being created, make a throwaway, hidden master root.  This stops one user
        # window from becoming the child of another user window. All windows are children of this hidden window
        _get_hidden_master_root()
        root = tk.Toplevel(class_=window.Title)
    else:
        root = tk.Toplevel(class_=window.Title)
    if window.DebuggerEnabled:
        root.bind("<Cancel>", window._callback_main_debugger_window_create_keystroke)
        root.bind("<Pause>", window._callback_popout_window_create_keystroke)

    # If location is None, then there's no need to hide the window.  Let it build where it is going to end up being.
    if DEFAULT_HIDE_WINDOW_WHEN_CREATING is True and window.Location is not None:
        try:
            if (
                not running_mac()
                or (running_mac() and not window.NoTitleBar)
                or (
                    running_mac()
                    and window.NoTitleBar
                    and not _mac_should_apply_notitlebar_patch()
                )
            ):
                root.attributes(
                    "-alpha", 0
                )  # hide window while building it. makes for smoother 'paint'
        except Exception as e:
            print(
                "*** Exception setting alpha channel to zero while creating window ***",
                e,
            )

    if (
        window.BackgroundColor is not None
        and window.BackgroundColor != COLOR_SYSTEM_DEFAULT
    ):
        root.configure(background=window.BackgroundColor)
    Window._IncrementOpenCount()

    window.TKroot = root

    window._create_thread_queue()

    # for the Raspberry Pi. Need to set the attributes here, prior to the building of the window
    # so going ahead and doing it for all platforms, in addition to doing it after the window is packed
    # 2023-April - this call seems to be causing problems on MacOS 13.2.1 Ventura.  Input elements become non-responsive
    # if this call is made here and at the end of building the window
    if not running_mac():
        _no_titlebar_setup(window)

    if not window.Resizable:
        root.resizable(False, False)

    if window.DisableMinimize:
        root.attributes("-toolwindow", 1)

    if window.KeepOnTop:
        root.wm_attributes("-topmost", 1)

    if window.TransparentColor is not None:
        window.SetTransparentColor(window.TransparentColor)

    if window.scaling is not None:
        root.tk.call("tk", "scaling", window.scaling)

    # root.protocol("WM_DELETE_WINDOW", MyFlexForm.DestroyedCallback())
    # root.bind('<Destroy>', MyFlexForm.DestroyedCallback())
    _convert_window_to_tk(window)

    # Make moveable window
    if window.GrabAnywhere is not False and not (
        window.NonBlocking and window.GrabAnywhere is not True
    ):
        if not (
            ENABLE_MAC_DISABLE_GRAB_ANYWHERE_WITH_TITLEBAR
            and running_mac()
            and not window.NoTitleBar
        ):
            root.bind("<ButtonPress-1>", window._StartMoveGrabAnywhere)
            root.bind("<ButtonRelease-1>", window._StopMove)
            root.bind("<B1-Motion>", window._OnMotionGrabAnywhere)
    if window.GrabAnywhereUsingControlKey is not False and not (
        window.NonBlocking and window.GrabAnywhereUsingControlKey is not True
    ):
        root.bind("<Control-Button-1>", window._StartMoveUsingControlKey)
        root.bind("<Control-ButtonRelease-1>", window._StopMove)
        root.bind("<Control-B1-Motion>", window._OnMotionUsingControlKey)
        # also enable movement using Control + Arrow key
        root.bind("<Control-Left>", window._move_callback)
        root.bind("<Control-Right>", window._move_callback)
        root.bind("<Control-Up>", window._move_callback)
        root.bind("<Control-Down>", window._move_callback)

    window.set_icon(window.WindowIcon)
    try:
        alpha_channel = 1 if window.AlphaChannel is None else window.AlphaChannel
        root.attributes("-alpha", alpha_channel)  # Make window visible again
    except Exception as e:
        print(
            "**** Error setting Alpha Channel to {} after window was created ****".format(
                alpha_channel
            ),
            e,
        )
        # pass

    if window.ReturnKeyboardEvents and not window.NonBlocking:
        root.bind("<KeyRelease>", window._KeyboardCallback)
        root.bind("<MouseWheel>", window._MouseWheelCallback)
        root.bind("<Button-4>", window._MouseWheelCallback)
        root.bind("<Button-5>", window._MouseWheelCallback)
    elif window.ReturnKeyboardEvents:
        root.bind("<Key>", window._KeyboardCallback)
        root.bind("<MouseWheel>", window._MouseWheelCallback)
        root.bind("<Button-4>", window._MouseWheelCallback)
        root.bind("<Button-5>", window._MouseWheelCallback)

    DEFAULT_WINDOW_SNAPSHOT_KEY_CODE = main_global_get_screen_snapshot_symcode()

    if DEFAULT_WINDOW_SNAPSHOT_KEY_CODE:
        # print('**** BINDING THE SNAPSHOT!', DEFAULT_WINDOW_SNAPSHOT_KEY_CODE, DEFAULT_WINDOW_SNAPSHOT_KEY)
        window.bind(
            DEFAULT_WINDOW_SNAPSHOT_KEY_CODE,
            DEFAULT_WINDOW_SNAPSHOT_KEY,
            propagate=False,
        )
        # window.bind('<Win_L><F12>', DEFAULT_WINDOW_SNAPSHOT_KEY, )

    if window.NoTitleBar:
        window.TKroot.focus_force()

    if window.AutoClose:
        # if the window is being finalized, then don't start the autoclose timer
        if not window.finalize_in_progress:
            window._start_autoclose_timer()
            # duration = DEFAULT_AUTOCLOSE_TIME if window.AutoCloseDuration is None else window.AutoCloseDuration
            # window.TKAfterID = root.after(int(duration * 1000), window._AutoCloseAlarmCallback)

    if window.Timeout is not None:
        window.TKAfterID = root.after(int(window.Timeout), window._TimeoutAlarmCallback)
    if window.NonBlocking:
        window.TKroot.protocol("WM_DESTROY_WINDOW", window._OnClosingCallback)
        window.TKroot.protocol("WM_DELETE_WINDOW", window._OnClosingCallback)

    else:  # it's a blocking form
        # print('..... CALLING MainLoop')
        window.CurrentlyRunningMainloop = True
        window.TKroot.protocol("WM_DESTROY_WINDOW", window._OnClosingCallback)
        window.TKroot.protocol("WM_DELETE_WINDOW", window._OnClosingCallback)

        if window.modal or DEFAULT_MODAL_WINDOWS_FORCED:
            window.make_modal()

        if window.enable_window_config_events:
            window.TKroot.bind("<Configure>", window._config_callback)

        # ----------------------------------- tkinter mainloop call -----------------------------------
        Window._window_running_mainloop = window
        Window._root_running_mainloop = window.TKroot
        window.TKroot.mainloop()
        window.CurrentlyRunningMainloop = False
        window.TimerCancelled = True
        # print('..... BACK from MainLoop')
        if not window.FormRemainedOpen:
            Window._DecrementOpenCount()
            # _my_windows.Decrement()
        if window.RootNeedsDestroying:
            try:
                window.TKroot.destroy()
            except Exception:
                pass
            window.RootNeedsDestroying = False
    return




def read_all_windows(timeout=None, timeout_key=TIMEOUT_KEY):
    """
    Reads all windows that are "active" when the call is made. "Active" means that it's been finalized or read.
    If a window has not been finalized then it will not be considered an "active window"

    If any of the active windows returns a value then the window and its event and values
    are returned.

    If no windows are open, then the value (None, WIN_CLOSED, None) will be returned
        Since WIN_CLOSED is None, it means (None, None, None) is what's returned when no windows remain opened

    :param timeout:     Time in milliseconds to delay before a returning a timeout event
    :type timeout:      (int)
    :param timeout_key: Key to return when a timeout happens. Defaults to the standard TIMEOUT_KEY
    :type timeout_key:  (Any)
    :return:            A tuple with the  (Window, event, values dictionary/list)
    :rtype:             (Window, Any, Dict | List)
    """

    if len(Window._active_windows) == 0:
        return None, WIN_CLOSED, None

    # first see if any queued events are waiting for any of the windows
    for window in Window._active_windows.keys():
        if window._queued_thread_event_available():
            _BuildResults(window, False, window)
            event, values = window.ReturnValues
            return window, event, values

    Window._root_running_mainloop = Window.hidden_master_root
    Window._timeout_key = timeout_key

    if timeout == 0:
        window = list(Window._active_windows.keys())[Window._timeout_0_counter]
        event, values = window._ReadNonBlocking()
        if event is None:
            event = timeout_key
        if values is None:
            event = None
        Window._timeout_0_counter = (Window._timeout_0_counter + 1) % len(
            Window._active_windows
        )
        return window, event, values

    Window._timeout_0_counter = (
        0  # reset value if not reading with timeout 0 so ready next time needed
    )

    # setup timeout timer
    if timeout is not None:
        try:
            Window.hidden_master_root.after_cancel(Window._TKAfterID)
            del Window._TKAfterID
        except Exception:
            pass

        Window._TKAfterID = Window.hidden_master_root.after(
            timeout, _timeout_alarm_callback_hidden
        )

    # ------------ Call Mainloop ------------
    Window._root_running_mainloop.mainloop()

    try:
        Window.hidden_master_root.after_cancel(Window._TKAfterID)
        del Window._TKAfterID
    except Exception:
        pass
        # print('** tkafter cancel failed **')

    # Get window that caused return

    window = Window._window_that_exited

    if window is None:
        return None, timeout_key, None

    if window.XFound:
        event, values = None, None
        window.close()
        try:
            del Window._active_windows[window]
        except Exception:
            pass
            # print('Error deleting window, but OK')
    else:
        _BuildResults(window, False, window)
        event, values = window.ReturnValues

    return window, event, values




# @_timeit
def PackFormIntoFrame(form, containing_frame, toplevel_form):
    """

    :param form:             a window class
    :type form:              (Window)
    :param containing_frame: ???
    :type containing_frame:  ???
    :param toplevel_form:    ???
    :type toplevel_form:     (Window)

    """

    # Old bindings
    def yscroll_old(event):
        try:
            if event.num == 5 or event.delta < 0:
                VarHolder.canvas_holder.yview_scroll(1, "unit")
            elif event.num == 4 or event.delta > 0:
                VarHolder.canvas_holder.yview_scroll(-1, "unit")
        except Exception:
            pass

    def xscroll_old(event):
        try:
            if event.num == 5 or event.delta < 0:
                VarHolder.canvas_holder.xview_scroll(1, "unit")
            elif event.num == 4 or event.delta > 0:
                VarHolder.canvas_holder.xview_scroll(-1, "unit")
        except Exception:
            pass

    # Chr0nic
    def testMouseHook2(em):
        combo = em.TKCombo
        combo.unbind_class("TCombobox", "<MouseWheel>")
        combo.unbind_class("TCombobox", "<ButtonPress-4>")
        combo.unbind_class("TCombobox", "<ButtonPress-5>")
        containing_frame.unbind_all("<4>")
        containing_frame.unbind_all("<5>")
        containing_frame.unbind_all("<MouseWheel>")
        containing_frame.unbind_all("<Shift-MouseWheel>")

    # Chr0nic
    def testMouseUnhook2(em):
        containing_frame.bind_all("<4>", yscroll_old, add="+")
        containing_frame.bind_all("<5>", yscroll_old, add="+")
        containing_frame.bind_all("<MouseWheel>", yscroll_old, add="+")
        containing_frame.bind_all("<Shift-MouseWheel>", xscroll_old, add="+")

    # Chr0nic
    def testMouseHook(em):
        containing_frame.unbind_all("<4>")
        containing_frame.unbind_all("<5>")
        containing_frame.unbind_all("<MouseWheel>")
        containing_frame.unbind_all("<Shift-MouseWheel>")

    # Chr0nic
    def testMouseUnhook(em):
        containing_frame.bind_all("<4>", yscroll_old, add="+")
        containing_frame.bind_all("<5>", yscroll_old, add="+")
        containing_frame.bind_all("<MouseWheel>", yscroll_old, add="+")
        containing_frame.bind_all("<Shift-MouseWheel>", xscroll_old, add="+")

    def _char_width_in_pixels(font):
        return tkinter.font.Font(font=font).measure("A")  # single character width

    def _char_height_in_pixels(font):
        return tkinter.font.Font(font=font).metrics("linespace")

    def _string_width_in_pixels(font, string):
        return tkinter.font.Font(font=font).measure(string)  # single character width

    # def _valid_theme(style, theme_name):
    #     if theme_name in style.theme_names():
    #         return True
    #     _error_popup_with_traceback('Your Window has an invalid ttk theme specified',
    #                                 'The traceback will show you the Window with the problem layout',
    #                                 '** Invalid ttk theme specified {} **'.format(theme_name),
    #                                 '\nValid choices include: {}'.format(style.theme_names()))
    #
    #     # print('** Invalid ttk theme specified {} **'.format(theme_name),
    #     #       '\nValid choices include: {}'.format(style.theme_names()))
    #     return False

    def _add_grab(element):
        try:
            if form.Grab is True or element.Grab is True:
                # if something already about to the button, then don't do the grab stuff
                if "<Button-1>" not in element.Widget.bind():
                    element.Widget.bind(
                        "<ButtonPress-1>", toplevel_form._StartMoveGrabAnywhere
                    )
                    element.Widget.bind("<ButtonRelease-1>", toplevel_form._StopMove)
                    element.Widget.bind(
                        "<B1-Motion>", toplevel_form._OnMotionGrabAnywhere
                    )
                element.ParentRowFrame.bind(
                    "<ButtonPress-1>", toplevel_form._StartMoveGrabAnywhere
                )
                element.ParentRowFrame.bind(
                    "<ButtonRelease-1>", toplevel_form._StopMove
                )
                element.ParentRowFrame.bind(
                    "<B1-Motion>", toplevel_form._OnMotionGrabAnywhere
                )
                if element.Type == ELEM_TYPE_COLUMN:
                    element.TKColFrame.canvas.bind(
                        "<ButtonPress-1>", toplevel_form._StartMoveGrabAnywhere
                    )
                    element.TKColFrame.canvas.bind(
                        "<ButtonRelease-1>", toplevel_form._StopMove
                    )
                    element.TKColFrame.canvas.bind(
                        "<B1-Motion>", toplevel_form._OnMotionGrabAnywhere
                    )
        except Exception as e:
            pass
            # print(e)

    def _add_right_click_menu_and_grab(element):
        if element.RightClickMenu == MENU_RIGHT_CLICK_DISABLED:
            return
        if (
            element.Type == ELEM_TYPE_TAB_GROUP
        ):  # unless everything disabled, then need to always set a right click menu for tabgroups
            if toplevel_form.RightClickMenu == MENU_RIGHT_CLICK_DISABLED:
                return
            menu = _MENU_RIGHT_CLICK_TABGROUP_DEFAULT
        else:
            menu = (
                element.RightClickMenu
                or form.RightClickMenu
                or toplevel_form.RightClickMenu
            )

        if menu:
            top_menu = tk.Menu(
                toplevel_form.TKroot,
                tearoff=toplevel_form.right_click_menu_tearoff,
                tearoffcommand=element._tearoff_menu_callback,
            )

            if toplevel_form.right_click_menu_background_color not in (
                COLOR_SYSTEM_DEFAULT,
                None,
            ):
                top_menu.config(bg=toplevel_form.right_click_menu_background_color)
            if toplevel_form.right_click_menu_text_color not in (
                COLOR_SYSTEM_DEFAULT,
                None,
            ):
                top_menu.config(fg=toplevel_form.right_click_menu_text_color)
            if toplevel_form.right_click_menu_disabled_text_color not in (
                COLOR_SYSTEM_DEFAULT,
                None,
            ):
                top_menu.config(
                    disabledforeground=toplevel_form.right_click_menu_disabled_text_color
                )
            if toplevel_form.right_click_menu_font is not None:
                top_menu.config(font=toplevel_form.right_click_menu_font)

            if toplevel_form.right_click_menu_selected_colors[0] not in (
                COLOR_SYSTEM_DEFAULT,
                None,
            ):
                top_menu.config(
                    activeforeground=toplevel_form.right_click_menu_selected_colors[0]
                )
            if toplevel_form.right_click_menu_selected_colors[1] not in (
                COLOR_SYSTEM_DEFAULT,
                None,
            ):
                top_menu.config(
                    activebackground=toplevel_form.right_click_menu_selected_colors[1]
                )
            AddMenuItem(top_menu, menu[1], element, right_click_menu=True)
            element.TKRightClickMenu = top_menu
            if toplevel_form.RightClickMenu:  # if the top level has a right click menu, then setup a callback for the Window itself
                if toplevel_form.TKRightClickMenu is None:
                    toplevel_form.TKRightClickMenu = top_menu
                    if running_mac():
                        toplevel_form.TKroot.bind(
                            "<ButtonRelease-2>", toplevel_form._RightClickMenuCallback
                        )
                    else:
                        toplevel_form.TKroot.bind(
                            "<ButtonRelease-3>", toplevel_form._RightClickMenuCallback
                        )
            if running_mac():
                element.Widget.bind(
                    "<ButtonRelease-2>", element._RightClickMenuCallback
                )
            else:
                element.Widget.bind(
                    "<ButtonRelease-3>", element._RightClickMenuCallback
                )
                try:
                    if element.Type == ELEM_TYPE_COLUMN:
                        element.TKColFrame.canvas.bind(
                            "<ButtonRelease-3>", element._RightClickMenuCallback
                        )
                except Exception:
                    pass
        _add_grab(element)

    def _add_expansion(element, row_should_expand, row_fill_direction):
        expand = True
        if element.expand_x and element.expand_y:
            fill = tk.BOTH
            row_fill_direction = tk.BOTH
            row_should_expand = True
        elif element.expand_x:
            fill = tk.X
            row_fill_direction = (
                tk.X
                if row_fill_direction == tk.NONE
                else tk.BOTH
                if row_fill_direction == tk.Y
                else tk.X
            )
        elif element.expand_y:
            fill = tk.Y
            row_fill_direction = (
                tk.Y
                if row_fill_direction == tk.NONE
                else tk.BOTH
                if row_fill_direction == tk.X
                else tk.Y
            )
            row_should_expand = True
        else:
            fill = tk.NONE
            expand = False
        return expand, fill, row_should_expand, row_fill_direction

    tclversion_detailed = tkinter.Tcl().eval("info patchlevel")

    # --------------------------------------------------------------------------- #
    # ****************  Use FlexForm to build the tkinter window ********** ----- #
    # Building is done row by row.                                                #
    # WARNING - You can't use print in this function. If the user has rerouted   #
    # stdout then there will be an error saying the window isn't finalized        #
    # --------------------------------------------------------------------------- #
    ######################### LOOP THROUGH ROWS #########################
    # *********** -------  Loop through ROWS  ------- ***********#
    for row_num, flex_row in enumerate(form.Rows):
        ######################### LOOP THROUGH ELEMENTS ON ROW #########################
        # *********** -------  Loop through ELEMENTS  ------- ***********#
        # *********** Make TK Row                             ***********#
        tk_row_frame = tk.Frame(containing_frame)
        row_should_expand = False
        row_fill_direction = tk.NONE

        if form.ElementJustification is not None:
            row_justify = form.ElementJustification
        else:
            row_justify = "l"

        for col_num, element in enumerate(flex_row):
            element.ParentRowFrame = tk_row_frame
            element.element_frame = None  # for elements that have a scrollbar too
            element.ParentForm = toplevel_form  # save the button's parent form object
            if toplevel_form.Font and (
                element.Font == DEFAULT_FONT or element.Font is None
            ):
                font = toplevel_form.Font
            elif element.Font is not None:
                font = element.Font
            else:
                font = DEFAULT_FONT
            # -------  Determine Auto-Size setting on a cascading basis ------- #
            if element.AutoSizeText is not None:  # if element overide
                auto_size_text = element.AutoSizeText
            elif toplevel_form.AutoSizeText is not None:  # if form override
                auto_size_text = toplevel_form.AutoSizeText
            else:
                auto_size_text = DEFAULT_AUTOSIZE_TEXT
            element_type = element.Type
            # Set foreground color
            text_color = element.TextColor
            elementpad = (
                element.Pad if element.Pad is not None else toplevel_form.ElementPadding
            )
            # element.pad_used = elementpad  # store the value used back into the element
            # Determine Element size
            element_size = element.Size
            if element_size == (None, None) and element_type not in (
                ELEM_TYPE_BUTTON,
                ELEM_TYPE_BUTTONMENU,
            ):  # user did not specify a size
                element_size = toplevel_form.DefaultElementSize
            elif element_size == (None, None) and element_type in (
                ELEM_TYPE_BUTTON,
                ELEM_TYPE_BUTTONMENU,
            ):
                element_size = toplevel_form.DefaultButtonElementSize
            else:
                auto_size_text = (
                    False  # if user has specified a size then it shouldn't autosize
                )

            border_depth = (
                toplevel_form.BorderDepth
                if toplevel_form.BorderDepth is not None
                else DEFAULT_BORDER_WIDTH
            )
            try:
                if element.BorderWidth is not None:
                    border_depth = element.BorderWidth
            except Exception:
                pass

            # -------------------------  COLUMN placement element  ------------------------- #
            if element_type == ELEM_TYPE_COLUMN:
                element = element  # type: Column
                # ----------------------- SCROLLABLE Column ----------------------
                if element.Scrollable:
                    element.Widget = element.TKColFrame = TkScrollableFrame(
                        tk_row_frame, element.VerticalScrollOnly, element, toplevel_form
                    )  # do not use yet!  not working
                    PackFormIntoFrame(
                        element, element.TKColFrame.TKFrame, toplevel_form
                    )
                    element.TKColFrame.TKFrame.update()
                    if element.Size == (
                        None,
                        None,
                    ):  # if no size specified, use column width x column height/2
                        element.TKColFrame.canvas.config(
                            width=element.TKColFrame.TKFrame.winfo_reqwidth()
                            // element.size_subsample_width,
                            height=element.TKColFrame.TKFrame.winfo_reqheight()
                            // element.size_subsample_height,
                        )
                    else:
                        element.TKColFrame.canvas.config(
                            width=element.TKColFrame.TKFrame.winfo_reqwidth()
                            // element.size_subsample_width,
                            height=element.TKColFrame.TKFrame.winfo_reqheight()
                            // element.size_subsample_height,
                        )
                        if None not in (element.Size[0], element.Size[1]):
                            element.TKColFrame.canvas.config(
                                width=element.Size[0], height=element.Size[1]
                            )
                        elif element.Size[1] is not None:
                            element.TKColFrame.canvas.config(height=element.Size[1])
                        elif element.Size[0] is not None:
                            element.TKColFrame.canvas.config(width=element.Size[0])
                    if not element.BackgroundColor in (None, COLOR_SYSTEM_DEFAULT):
                        element.TKColFrame.canvas.config(
                            background=element.BackgroundColor
                        )
                        element.TKColFrame.TKFrame.config(
                            background=element.BackgroundColor,
                            borderwidth=0,
                            highlightthickness=0,
                        )
                        element.TKColFrame.config(
                            background=element.BackgroundColor,
                            borderwidth=0,
                            highlightthickness=0,
                        )
                # ----------------------- PLAIN Column ----------------------
                else:
                    if element.Size != (None, None):
                        element.Widget = element.TKColFrame = TkFixedFrame(tk_row_frame)
                        PackFormIntoFrame(
                            element, element.TKColFrame.TKFrame, toplevel_form
                        )
                        element.TKColFrame.TKFrame.update()
                        if None not in (element.Size[0], element.Size[1]):
                            element.TKColFrame.canvas.config(
                                width=element.Size[0], height=element.Size[1]
                            )
                        elif element.Size[1] is not None:
                            element.TKColFrame.canvas.config(height=element.Size[1])
                        elif element.Size[0] is not None:
                            element.TKColFrame.canvas.config(width=element.Size[0])
                        if not element.BackgroundColor in (None, COLOR_SYSTEM_DEFAULT):
                            element.TKColFrame.canvas.config(
                                background=element.BackgroundColor
                            )
                            element.TKColFrame.TKFrame.config(
                                background=element.BackgroundColor,
                                borderwidth=0,
                                highlightthickness=0,
                            )
                    else:
                        element.Widget = element.TKColFrame = tk.Frame(tk_row_frame)
                        PackFormIntoFrame(element, element.TKColFrame, toplevel_form)
                        if element.BackgroundColor not in (None, COLOR_SYSTEM_DEFAULT):
                            element.TKColFrame.config(
                                background=element.BackgroundColor,
                                borderwidth=0,
                                highlightthickness=0,
                            )

                if element.Justification is None:
                    pass
                elif element.Justification.lower().startswith("l"):
                    row_justify = "l"
                elif element.Justification.lower().startswith("c"):
                    row_justify = "c"
                elif element.Justification.lower().startswith("r"):
                    row_justify = "r"

                # anchor=tk.NW
                # side = tk.LEFT
                # row_justify = element.Justification

                # element.Widget = element.TKColFrame

                expand = True
                if element.expand_x and element.expand_y:
                    fill = tk.BOTH
                    row_fill_direction = tk.BOTH
                    row_should_expand = True
                elif element.expand_x:
                    fill = tk.X
                    row_fill_direction = tk.X
                elif element.expand_y:
                    fill = tk.Y
                    row_fill_direction = tk.Y
                    row_should_expand = True
                else:
                    fill = tk.NONE
                    expand = False

                if element.VerticalAlignment is not None:
                    anchor = tk.CENTER  # Default to center if a bad choice is made

                    if element.VerticalAlignment.lower().startswith("t"):
                        anchor = tk.N
                    if element.VerticalAlignment.lower().startswith("c"):
                        anchor = tk.CENTER
                    if element.VerticalAlignment.lower().startswith("b"):
                        anchor = tk.S
                    element.TKColFrame.pack(
                        side=tk.LEFT,
                        anchor=anchor,
                        padx=elementpad[0],
                        pady=elementpad[1],
                        expand=expand,
                        fill=fill,
                    )
                else:
                    element.TKColFrame.pack(
                        side=tk.LEFT,
                        padx=elementpad[0],
                        pady=elementpad[1],
                        expand=expand,
                        fill=fill,
                    )

                # element.TKColFrame.pack(side=side, padx=elementpad[0], pady=elementpad[1], expand=True, fill='both')
                if not element.visible:
                    element._pack_forget_save_settings()
                    # element.TKColFrame.pack_forget()

                _add_right_click_menu_and_grab(element)
                # if element.Grab:
                #     element._grab_anywhere_on()
                # row_should_expand = True
            # -------------------------  Pane placement element  ------------------------- #
            if element_type == ELEM_TYPE_PANE:
                bd = (
                    element.BorderDepth
                    if element.BorderDepth is not None
                    else border_depth
                )
                element.PanedWindow = element.Widget = tk.PanedWindow(
                    tk_row_frame,
                    orient=tk.VERTICAL
                    if element.Orientation.startswith("v")
                    else tk.HORIZONTAL,
                    borderwidth=bd,
                    bd=bd,
                )
                if element.Relief is not None:
                    element.PanedWindow.configure(relief=element.Relief)
                element.PanedWindow.configure(handlesize=element.HandleSize)
                if element.ShowHandle:
                    element.PanedWindow.config(showhandle=True)
                if element.Size != (None, None):
                    element.PanedWindow.config(
                        width=element.Size[0], height=element.Size[1]
                    )
                if (
                    element.BackgroundColor is not None
                    and element.BackgroundColor != COLOR_SYSTEM_DEFAULT
                ):
                    element.PanedWindow.configure(background=element.BackgroundColor)
                for pane in element.PaneList:
                    pane.Widget = pane.TKColFrame = tk.Frame(element.PanedWindow)
                    pane.ParentPanedWindow = element.PanedWindow
                    PackFormIntoFrame(pane, pane.TKColFrame, toplevel_form)
                    if pane.visible:
                        element.PanedWindow.add(pane.TKColFrame)
                    if (
                        pane.BackgroundColor != COLOR_SYSTEM_DEFAULT
                        and pane.BackgroundColor is not None
                    ):
                        pane.TKColFrame.configure(
                            background=pane.BackgroundColor,
                            highlightbackground=pane.BackgroundColor,
                            highlightcolor=pane.BackgroundColor,
                        )
                expand, fill, row_should_expand, row_fill_direction = _add_expansion(
                    element, row_should_expand, row_fill_direction
                )
                element.PanedWindow.pack(
                    side=tk.LEFT,
                    padx=elementpad[0],
                    pady=elementpad[1],
                    expand=expand,
                    fill=fill,
                )
                # element.PanedWindow.pack(side=tk.LEFT, padx=elementpad[0], pady=elementpad[1], expand=True, fill='both')
                if not element.visible:
                    element._pack_forget_save_settings()
                    # element.PanedWindow.pack_forget()
            # -------------------------  TEXT placement element  ------------------------- #
            elif element_type == ELEM_TYPE_TEXT:
                # auto_size_text = element.AutoSizeText
                element = element  # type: Text
                display_text = element.DisplayText  # text to display
                if not auto_size_text:
                    width, height = element_size
                else:
                    width, height = None, None
                    # lines = display_text.split('\n')
                    # max_line_len = max([len(l) for l in lines])
                    # num_lines = len(lines)
                    # if max_line_len > element_size[0]:  # if text exceeds element size, the will have to wrap
                    #     width = element_size[0]
                    # else:
                    #     width = max_line_len
                    # height = num_lines
                # ---===--- LABEL widget create and place --- #
                element = element  # type: Text
                bd = (
                    element.BorderWidth
                    if element.BorderWidth is not None
                    else border_depth
                )
                stringvar = tk.StringVar()
                element.TKStringVar = stringvar
                stringvar.set(str(display_text))
                if auto_size_text:
                    width = 0
                if element.Justification is not None:
                    justification = element.Justification
                elif toplevel_form.TextJustification is not None:
                    justification = toplevel_form.TextJustification
                else:
                    justification = DEFAULT_TEXT_JUSTIFICATION
                justify = (
                    tk.LEFT
                    if justification.startswith("l")
                    else tk.CENTER
                    if justification.startswith("c")
                    else tk.RIGHT
                )
                anchor = (
                    tk.NW
                    if justification.startswith("l")
                    else tk.N
                    if justification.startswith("c")
                    else tk.NE
                )
                tktext_label = element.Widget = tk.Label(
                    tk_row_frame,
                    textvariable=stringvar,
                    width=width,
                    height=height,
                    justify=justify,
                    bd=bd,
                    font=font,
                )
                # Set wrap-length for text (in PIXELS) == PAIN IN THE ASS
                wraplen = tktext_label.winfo_reqwidth()  # width of widget in Pixels
                if auto_size_text or (
                    not auto_size_text and height == 1
                ):  # if just 1 line high, ensure no wrap happens
                    wraplen = 0
                tktext_label.configure(
                    anchor=anchor, wraplen=wraplen
                )  # set wrap to width of widget
                if element.Relief is not None:
                    tktext_label.configure(relief=element.Relief)
                if (
                    element.BackgroundColor is not None
                    and element.BackgroundColor != COLOR_SYSTEM_DEFAULT
                ):
                    tktext_label.configure(background=element.BackgroundColor)
                if (
                    element.TextColor != COLOR_SYSTEM_DEFAULT
                    and element.TextColor is not None
                ):
                    tktext_label.configure(fg=element.TextColor)
                expand, fill, row_should_expand, row_fill_direction = _add_expansion(
                    element, row_should_expand, row_fill_direction
                )
                tktext_label.pack(
                    side=tk.LEFT,
                    padx=elementpad[0],
                    pady=elementpad[1],
                    expand=expand,
                    fill=fill,
                )
                if not element.visible:
                    element._pack_forget_save_settings()
                    # tktext_label.pack_forget()
                element.TKText = tktext_label
                if element.ClickSubmits:
                    tktext_label.bind("<Button-1>", element._TextClickedHandler)
                if element.Tooltip is not None:
                    element.TooltipObject = ToolTip(
                        element.TKText,
                        text=element.Tooltip,
                        timeout=DEFAULT_TOOLTIP_TIME,
                    )
                _add_right_click_menu_and_grab(element)
                if element.Grab:
                    element._grab_anywhere_on()
            # -------------------------  BUTTON placement element non-ttk version  ------------------------- #
            elif (
                element_type == ELEM_TYPE_BUTTON and element.UseTtkButtons is False
            ) or (
                element_type == ELEM_TYPE_BUTTON
                and element.UseTtkButtons is not True
                and toplevel_form.UseTtkButtons is not True
            ):
                element = element  # type: Button
                element.UseTtkButtons = False  # indicate that ttk button was not used
                stringvar = tk.StringVar()
                element.TKStringVar = stringvar
                element.Location = (row_num, col_num)
                btext = element.ButtonText
                btype = element.BType
                if element.AutoSizeButton is not None:
                    auto_size = element.AutoSizeButton
                else:
                    auto_size = toplevel_form.AutoSizeButtons
                if auto_size is False or element.Size[0] is not None:
                    width, height = element_size
                else:
                    width = 0
                    height = toplevel_form.DefaultButtonElementSize[1]
                if (
                    element.ButtonColor != (None, None)
                    and element.ButtonColor != DEFAULT_BUTTON_COLOR
                ):
                    bc = element.ButtonColor
                elif (
                    toplevel_form.ButtonColor != (None, None)
                    and toplevel_form.ButtonColor != DEFAULT_BUTTON_COLOR
                ):
                    bc = toplevel_form.ButtonColor
                else:
                    bc = DEFAULT_BUTTON_COLOR

                bd = element.BorderWidth
                pos = -1
                if DEFAULT_USE_BUTTON_SHORTCUTS:
                    pos = btext.find(MENU_SHORTCUT_CHARACTER)
                    if pos != -1:
                        if (
                            pos < len(MENU_SHORTCUT_CHARACTER)
                            or btext[pos - len(MENU_SHORTCUT_CHARACTER)] != "\\"
                        ):
                            btext = (
                                btext[:pos]
                                + btext[pos + len(MENU_SHORTCUT_CHARACTER) :]
                            )
                        else:
                            btext = btext.replace(
                                "\\" + MENU_SHORTCUT_CHARACTER, MENU_SHORTCUT_CHARACTER
                            )
                            pos = -1
                tkbutton = element.Widget = tk.Button(
                    tk_row_frame,
                    text=btext,
                    width=width,
                    height=height,
                    justify=tk.CENTER,
                    bd=bd,
                    font=font,
                )
                if pos != -1:
                    tkbutton.config(underline=pos)
                try:
                    if btype != BUTTON_TYPE_REALTIME:
                        tkbutton.config(command=element.ButtonCallBack)

                    else:
                        tkbutton.bind(
                            "<ButtonRelease-1>", element.ButtonReleaseCallBack
                        )
                        tkbutton.bind("<ButtonPress-1>", element.ButtonPressCallBack)
                    if bc != (None, None) and COLOR_SYSTEM_DEFAULT not in bc:
                        tkbutton.config(foreground=bc[0], background=bc[1])
                    else:
                        if bc[0] != COLOR_SYSTEM_DEFAULT:
                            tkbutton.config(foreground=bc[0])
                        if bc[1] != COLOR_SYSTEM_DEFAULT:
                            tkbutton.config(background=bc[1])
                except Exception as e:
                    _error_popup_with_traceback(
                        "Button has a problem....",
                        "The traceback information will not show the line in your layout with the problem, but it does tell you which window.",
                        "Error {}".format(e),
                        # 'Button Text: {}'.format(btext),
                        # 'Button key: {}'.format(element.Key),
                        # 'Color string: {}'.format(bc),
                        "Parent Window's Title: {}".format(toplevel_form.Title),
                    )

                if bd == 0 and not running_mac():
                    tkbutton.config(relief=tk.FLAT)

                element.TKButton = (
                    tkbutton  # not used yet but save the TK button in case
                )
                if elementpad[0] == 0 or elementpad[1] == 0:
                    tkbutton.config(highlightthickness=0)

                ## -------------- TK Button With Image -------------- ##
                if element.ImageFilename:  # if button has an image on it
                    tkbutton.config(highlightthickness=0)
                    try:
                        photo = tk.PhotoImage(file=element.ImageFilename)
                        if element.ImageSubsample:
                            photo = photo.subsample(element.ImageSubsample)
                        if element.zoom:
                            photo = photo.zoom(element.zoom)
                        if element.ImageSize != (None, None):
                            width, height = element.ImageSize
                        else:
                            width, height = photo.width(), photo.height()
                    except Exception as e:
                        _error_popup_with_traceback(
                            "Button Element error {}".format(e),
                            "Image filename: {}".format(element.ImageFilename),
                            "NOTE - file format must be PNG or GIF!",
                            "Button element key: {}".format(element.Key),
                            "Parent Window's Title: {}".format(toplevel_form.Title),
                        )
                    tkbutton.config(
                        image=photo, compound=tk.CENTER, width=width, height=height
                    )
                    tkbutton.image = photo
                if element.ImageData:  # if button has an image on it
                    tkbutton.config(highlightthickness=0)
                    try:
                        photo = tk.PhotoImage(data=element.ImageData)
                        if element.ImageSubsample:
                            photo = photo.subsample(element.ImageSubsample)
                        if element.zoom:
                            photo = photo.zoom(element.zoom)
                        if element.ImageSize != (None, None):
                            width, height = element.ImageSize
                        else:
                            width, height = photo.width(), photo.height()
                        tkbutton.config(
                            image=photo, compound=tk.CENTER, width=width, height=height
                        )
                        tkbutton.image = photo
                    except Exception as e:
                        _error_popup_with_traceback(
                            "Button Element error {}".format(e),
                            "Problem using BASE64 Image data Image Susample",
                            "Buton element key: {}".format(element.Key),
                            "Parent Window's Title: {}".format(toplevel_form.Title),
                        )

                if width != 0:
                    wraplen = width * _char_width_in_pixels(font)
                    tkbutton.configure(
                        wraplength=wraplen
                    )  # set wrap to width of widget
                expand, fill, row_should_expand, row_fill_direction = _add_expansion(
                    element, row_should_expand, row_fill_direction
                )

                tkbutton.pack(
                    side=tk.LEFT,
                    padx=elementpad[0],
                    pady=elementpad[1],
                    expand=expand,
                    fill=fill,
                )
                if not element.visible:
                    element._pack_forget_save_settings()
                    # tkbutton.pack_forget()
                if element.BindReturnKey:
                    element.TKButton.bind("<Return>", element._ReturnKeyHandler)
                if element.Focus is True or (
                    toplevel_form.UseDefaultFocus and not toplevel_form.FocusSet
                ):
                    toplevel_form.FocusSet = True
                    element.TKButton.bind("<Return>", element._ReturnKeyHandler)
                    element.TKButton.focus_set()
                    toplevel_form.TKroot.focus_force()
                if element.Disabled is True:
                    element.TKButton["state"] = "disabled"
                if element.DisabledButtonColor != (
                    None,
                    None,
                ) and element.DisabledButtonColor != (
                    COLOR_SYSTEM_DEFAULT,
                    COLOR_SYSTEM_DEFAULT,
                ):
                    if element.DisabledButtonColor[0] not in (
                        None,
                        COLOR_SYSTEM_DEFAULT,
                    ):
                        element.TKButton["disabledforeground"] = (
                            element.DisabledButtonColor[0]
                        )
                if element.MouseOverColors[1] not in (COLOR_SYSTEM_DEFAULT, None):
                    tkbutton.config(activebackground=element.MouseOverColors[1])
                if element.MouseOverColors[0] not in (COLOR_SYSTEM_DEFAULT, None):
                    tkbutton.config(activeforeground=element.MouseOverColors[0])

                if element.Tooltip is not None:
                    element.TooltipObject = ToolTip(
                        element.TKButton,
                        text=element.Tooltip,
                        timeout=DEFAULT_TOOLTIP_TIME,
                    )
                try:
                    if element.HighlightColors[1] != COLOR_SYSTEM_DEFAULT:
                        tkbutton.config(highlightbackground=element.HighlightColors[1])
                    if element.HighlightColors[0] != COLOR_SYSTEM_DEFAULT:
                        tkbutton.config(highlightcolor=element.HighlightColors[0])
                except Exception as e:
                    _error_popup_with_traceback(
                        "Button Element error {}".format(e),
                        "Button element key: {}".format(element.Key),
                        "Button text: {}".format(btext),
                        "Has a bad highlight color {}".format(element.HighlightColors),
                        "Parent Window's Title: {}".format(toplevel_form.Title),
                    )
                    # print('Button with text: ', btext, 'has a bad highlight color', element.HighlightColors)
                _add_right_click_menu_and_grab(element)

            # -------------------------  BUTTON placement element ttk version ------------------------- #
            elif element_type == ELEM_TYPE_BUTTON:
                element = element  # type: Button
                element.UseTtkButtons = True  # indicate that ttk button was used
                stringvar = tk.StringVar()
                element.TKStringVar = stringvar
                element.Location = (row_num, col_num)
                btext = element.ButtonText
                pos = -1
                if DEFAULT_USE_BUTTON_SHORTCUTS:
                    pos = btext.find(MENU_SHORTCUT_CHARACTER)
                    if pos != -1:
                        if (
                            pos < len(MENU_SHORTCUT_CHARACTER)
                            or btext[pos - len(MENU_SHORTCUT_CHARACTER)] != "\\"
                        ):
                            btext = (
                                btext[:pos]
                                + btext[pos + len(MENU_SHORTCUT_CHARACTER) :]
                            )
                        else:
                            btext = btext.replace(
                                "\\" + MENU_SHORTCUT_CHARACTER, MENU_SHORTCUT_CHARACTER
                            )
                            pos = -1
                btype = element.BType
                if element.AutoSizeButton is not None:
                    auto_size = element.AutoSizeButton
                else:
                    auto_size = toplevel_form.AutoSizeButtons
                if auto_size is False or element.Size[0] is not None:
                    width, height = element_size
                else:
                    width = 0
                    height = toplevel_form.DefaultButtonElementSize[1]
                if (
                    element.ButtonColor != (None, None)
                    and element.ButtonColor != COLOR_SYSTEM_DEFAULT
                ):
                    bc = element.ButtonColor
                elif (
                    toplevel_form.ButtonColor != (None, None)
                    and toplevel_form.ButtonColor != COLOR_SYSTEM_DEFAULT
                ):
                    bc = toplevel_form.ButtonColor
                else:
                    bc = DEFAULT_BUTTON_COLOR
                bd = element.BorderWidth
                tkbutton = element.Widget = ttk.Button(
                    tk_row_frame, text=btext, width=width
                )
                if pos != -1:
                    tkbutton.config(underline=pos)
                if btype != BUTTON_TYPE_REALTIME:
                    tkbutton.config(command=element.ButtonCallBack)
                else:
                    tkbutton.bind("<ButtonRelease-1>", element.ButtonReleaseCallBack)
                    tkbutton.bind("<ButtonPress-1>", element.ButtonPressCallBack)
                style_name = _make_ttk_style_name(
                    ".TButton", element, primary_style=True
                )
                button_style = ttk.Style()
                element.ttk_style = button_style
                _change_ttk_theme(button_style, toplevel_form.TtkTheme)
                button_style.configure(style_name, font=font)

                if bc != (None, None) and COLOR_SYSTEM_DEFAULT not in bc:
                    button_style.configure(
                        style_name, foreground=bc[0], background=bc[1]
                    )
                elif bc[0] != COLOR_SYSTEM_DEFAULT:
                    button_style.configure(style_name, foreground=bc[0])
                elif bc[1] != COLOR_SYSTEM_DEFAULT:
                    button_style.configure(style_name, background=bc[1])

                if bd == 0 and not running_mac():
                    button_style.configure(style_name, relief=tk.FLAT)
                    button_style.configure(style_name, borderwidth=0)
                else:
                    button_style.configure(style_name, borderwidth=bd)
                button_style.configure(style_name, justify=tk.CENTER)

                if element.MouseOverColors[1] not in (COLOR_SYSTEM_DEFAULT, None):
                    button_style.map(
                        style_name, background=[("active", element.MouseOverColors[1])]
                    )
                if element.MouseOverColors[0] not in (COLOR_SYSTEM_DEFAULT, None):
                    button_style.map(
                        style_name, foreground=[("active", element.MouseOverColors[0])]
                    )

                if element.DisabledButtonColor[0] not in (COLOR_SYSTEM_DEFAULT, None):
                    button_style.map(
                        style_name,
                        foreground=[("disabled", element.DisabledButtonColor[0])],
                    )
                if element.DisabledButtonColor[1] not in (COLOR_SYSTEM_DEFAULT, None):
                    button_style.map(
                        style_name,
                        background=[("disabled", element.DisabledButtonColor[1])],
                    )

                if height > 1:
                    button_style.configure(
                        style_name, padding=height * _char_height_in_pixels(font)
                    )  # should this be height instead?
                if width != 0:
                    wraplen = width * _char_width_in_pixels(
                        font
                    )  # width of widget in Pixels
                    button_style.configure(
                        style_name, wraplength=wraplen
                    )  # set wrap to width of widget

                ## -------------- TTK Button With Image -------------- ##
                if element.ImageFilename:  # if button has an image on it
                    button_style.configure(style_name, borderwidth=0)
                    # tkbutton.configure(highlightthickness=0)
                    photo = tk.PhotoImage(file=element.ImageFilename)
                    if element.ImageSubsample:
                        photo = photo.subsample(element.ImageSubsample)
                    if element.zoom:
                        photo = photo.zoom(element.zoom)
                    if element.ImageSize != (None, None):
                        width, height = element.ImageSize
                    else:
                        width, height = photo.width(), photo.height()
                    button_style.configure(
                        style_name,
                        image=photo,
                        compound=tk.CENTER,
                        width=width,
                        height=height,
                    )
                    tkbutton.image = photo
                if element.ImageData:  # if button has an image on it
                    # tkbutton.configure(highlightthickness=0)
                    button_style.configure(style_name, borderwidth=0)

                    photo = tk.PhotoImage(data=element.ImageData)
                    if element.ImageSubsample:
                        photo = photo.subsample(element.ImageSubsample)
                    if element.zoom:
                        photo = photo.zoom(element.zoom)
                    if element.ImageSize != (None, None):
                        width, height = element.ImageSize
                    else:
                        width, height = photo.width(), photo.height()
                    button_style.configure(
                        style_name,
                        image=photo,
                        compound=tk.CENTER,
                        width=width,
                        height=height,
                    )
                    # tkbutton.configure(image=photo, compound=tk.CENTER, width=width, height=height)
                    tkbutton.image = photo

                element.TKButton = (
                    tkbutton  # not used yet but save the TK button in case
                )
                expand, fill, row_should_expand, row_fill_direction = _add_expansion(
                    element, row_should_expand, row_fill_direction
                )
                tkbutton.pack(
                    side=tk.LEFT,
                    padx=elementpad[0],
                    pady=elementpad[1],
                    expand=expand,
                    fill=fill,
                )
                if not element.visible:
                    element._pack_forget_save_settings()
                    # tkbutton.pack_forget()
                if element.BindReturnKey:
                    element.TKButton.bind("<Return>", element._ReturnKeyHandler)
                if element.Focus is True or (
                    toplevel_form.UseDefaultFocus and not toplevel_form.FocusSet
                ):
                    toplevel_form.FocusSet = True
                    element.TKButton.bind("<Return>", element._ReturnKeyHandler)
                    element.TKButton.focus_set()
                    toplevel_form.TKroot.focus_force()
                if element.Disabled is True:
                    element.TKButton["state"] = "disabled"

                tkbutton.configure(
                    style=style_name
                )  # IMPORTANT!  Apply the style to the button!
                _add_right_click_menu_and_grab(element)

                if element.Tooltip is not None:
                    element.TooltipObject = ToolTip(
                        element.TKButton,
                        text=element.Tooltip,
                        timeout=DEFAULT_TOOLTIP_TIME,
                    )
            # -------------------------  BUTTONMENU placement element  ------------------------- #
            elif element_type == ELEM_TYPE_BUTTONMENU:
                element = element  # type: ButtonMenu
                element.Location = (row_num, col_num)
                btext = element.ButtonText
                if element.AutoSizeButton is not None:
                    auto_size = element.AutoSizeButton
                else:
                    auto_size = toplevel_form.AutoSizeButtons
                if auto_size is False or element.Size[0] is not None:
                    width, height = element_size
                else:
                    width = 0
                    height = toplevel_form.DefaultButtonElementSize[1]
                if (
                    element.ButtonColor != (None, None)
                    and element.ButtonColor != DEFAULT_BUTTON_COLOR
                ):
                    bc = element.ButtonColor
                elif (
                    toplevel_form.ButtonColor != (None, None)
                    and toplevel_form.ButtonColor != DEFAULT_BUTTON_COLOR
                ):
                    bc = toplevel_form.ButtonColor
                else:
                    bc = DEFAULT_BUTTON_COLOR
                bd = element.BorderWidth
                if element.ItemFont is None:
                    element.ItemFont = font
                tkbutton = element.Widget = tk.Menubutton(
                    tk_row_frame,
                    text=btext,
                    width=width,
                    height=height,
                    justify=tk.LEFT,
                    bd=bd,
                    font=font,
                )
                element.TKButtonMenu = tkbutton
                if (
                    bc != (None, None)
                    and bc != COLOR_SYSTEM_DEFAULT
                    and bc[1] != COLOR_SYSTEM_DEFAULT
                ):
                    tkbutton.config(foreground=bc[0], background=bc[1])
                    tkbutton.config(activebackground=bc[0])
                    tkbutton.config(activeforeground=bc[1])
                elif bc[0] != COLOR_SYSTEM_DEFAULT:
                    tkbutton.config(foreground=bc[0])
                    tkbutton.config(activebackground=bc[0])
                if bd == 0 and not running_mac():
                    tkbutton.config(relief=RELIEF_FLAT)
                elif bd != 0:
                    tkbutton.config(relief=RELIEF_RAISED)

                element.TKButton = (
                    tkbutton  # not used yet but save the TK button in case
                )
                wraplen = tkbutton.winfo_reqwidth()  # width of widget in Pixels
                if element.ImageFilename:  # if button has an image on it
                    photo = tk.PhotoImage(file=element.ImageFilename)
                    if element.ImageSubsample:
                        photo = photo.subsample(element.ImageSubsample)
                    if element.zoom:
                        photo = photo.zoom(element.zoom)
                    if element.ImageSize != (None, None):
                        width, height = element.ImageSize
                    else:
                        width, height = photo.width(), photo.height()
                    tkbutton.config(
                        image=photo, compound=tk.CENTER, width=width, height=height
                    )
                    tkbutton.image = photo
                if element.ImageData:  # if button has an image on it
                    photo = tk.PhotoImage(data=element.ImageData)
                    if element.ImageSubsample:
                        photo = photo.subsample(element.ImageSubsample)
                    if element.zoom:
                        photo = photo.zoom(element.zoom)
                    if element.ImageSize != (None, None):
                        width, height = element.ImageSize
                    else:
                        width, height = photo.width(), photo.height()
                    tkbutton.config(
                        image=photo, compound=tk.CENTER, width=width, height=height
                    )
                    tkbutton.image = photo
                if width != 0:
                    tkbutton.configure(
                        wraplength=wraplen + 10
                    )  # set wrap to width of widget
                expand, fill, row_should_expand, row_fill_direction = _add_expansion(
                    element, row_should_expand, row_fill_direction
                )
                tkbutton.pack(
                    side=tk.LEFT,
                    padx=elementpad[0],
                    pady=elementpad[1],
                    expand=expand,
                    fill=fill,
                )

                menu_def = element.MenuDefinition

                element.TKMenu = top_menu = tk.Menu(
                    tkbutton,
                    tearoff=element.Tearoff,
                    font=element.ItemFont,
                    tearoffcommand=element._tearoff_menu_callback,
                )

                if element.BackgroundColor not in (COLOR_SYSTEM_DEFAULT, None):
                    top_menu.config(bg=element.BackgroundColor)
                    top_menu.config(activeforeground=element.BackgroundColor)
                if element.TextColor not in (COLOR_SYSTEM_DEFAULT, None):
                    top_menu.config(fg=element.TextColor)
                    top_menu.config(activebackground=element.TextColor)
                if element.DisabledTextColor not in (COLOR_SYSTEM_DEFAULT, None):
                    top_menu.config(disabledforeground=element.DisabledTextColor)
                if element.ItemFont is not None:
                    top_menu.config(font=element.ItemFont)

                AddMenuItem(top_menu, menu_def[1], element)
                if elementpad[0] == 0 or elementpad[1] == 0:
                    tkbutton.config(highlightthickness=0)
                tkbutton.configure(menu=top_menu)
                element.TKMenu = top_menu
                if not element.visible:
                    element._pack_forget_save_settings()
                    # tkbutton.pack_forget()
                if element.Disabled:
                    element.TKButton["state"] = "disabled"
                if element.Tooltip is not None:
                    element.TooltipObject = ToolTip(
                        element.TKButton,
                        text=element.Tooltip,
                        timeout=DEFAULT_TOOLTIP_TIME,
                    )

            # -------------------------  INPUT placement element  ------------------------- #
            elif element_type == ELEM_TYPE_INPUT_TEXT:
                element = element  # type: InputText
                default_text = element.DefaultText
                element.TKStringVar = tk.StringVar()
                element.TKStringVar.set(default_text)
                show = element.PasswordCharacter if element.PasswordCharacter else ""
                bd = border_depth
                if element.Justification is not None:
                    justification = element.Justification
                else:
                    justification = DEFAULT_TEXT_JUSTIFICATION
                justify = (
                    tk.LEFT
                    if justification.startswith("l")
                    else tk.CENTER
                    if justification.startswith("c")
                    else tk.RIGHT
                )
                # anchor = tk.NW if justification == 'left' else tk.N if justification == 'center' else tk.NE
                element.TKEntry = element.Widget = tk.Entry(
                    tk_row_frame,
                    width=element_size[0],
                    textvariable=element.TKStringVar,
                    bd=bd,
                    font=font,
                    show=show,
                    justify=justify,
                )
                if element.ChangeSubmits:
                    element.TKEntry.bind("<Key>", element._KeyboardHandler)
                element.TKEntry.bind("<Return>", element._ReturnKeyHandler)

                if element.BackgroundColor not in (None, COLOR_SYSTEM_DEFAULT):
                    element.TKEntry.configure(
                        background=element.BackgroundColor,
                        selectforeground=element.BackgroundColor,
                    )

                if text_color not in (None, COLOR_SYSTEM_DEFAULT):
                    element.TKEntry.configure(
                        fg=text_color, selectbackground=text_color
                    )
                    element.TKEntry.config(insertbackground=text_color)
                if element.selected_background_color not in (
                    None,
                    COLOR_SYSTEM_DEFAULT,
                ):
                    element.TKEntry.configure(
                        selectbackground=element.selected_background_color
                    )
                if element.selected_text_color not in (None, COLOR_SYSTEM_DEFAULT):
                    element.TKEntry.configure(
                        selectforeground=element.selected_text_color
                    )
                if element.disabled_readonly_background_color not in (
                    None,
                    COLOR_SYSTEM_DEFAULT,
                ):
                    element.TKEntry.config(
                        readonlybackground=element.disabled_readonly_background_color
                    )
                if (
                    element.disabled_readonly_text_color
                    not in (None, COLOR_SYSTEM_DEFAULT)
                    and element.Disabled
                ):
                    element.TKEntry.config(fg=element.disabled_readonly_text_color)

                element.Widget.config(highlightthickness=0)
                # element.pack_keywords = {'side':tk.LEFT, 'padx':elementpad[0], 'pady':elementpad[1], 'expand':False, 'fill':tk.NONE }
                # element.TKEntry.pack(**element.pack_keywords)
                expand, fill, row_should_expand, row_fill_direction = _add_expansion(
                    element, row_should_expand, row_fill_direction
                )
                element.TKEntry.pack(
                    side=tk.LEFT,
                    padx=elementpad[0],
                    pady=elementpad[1],
                    expand=expand,
                    fill=fill,
                )
                if not element.visible:
                    element._pack_forget_save_settings()
                    # element.TKEntry.pack_forget()
                if element.Focus is True or (
                    toplevel_form.UseDefaultFocus and not toplevel_form.FocusSet
                ):
                    toplevel_form.FocusSet = True
                    element.TKEntry.focus_set()
                if element.Disabled:
                    element.TKEntry["state"] = (
                        "readonly" if element.UseReadonlyForDisable else "disabled"
                    )
                if element.ReadOnly:
                    element.TKEntry["state"] = "readonly"

                if element.Tooltip is not None:
                    element.TooltipObject = ToolTip(
                        element.TKEntry,
                        text=element.Tooltip,
                        timeout=DEFAULT_TOOLTIP_TIME,
                    )
                _add_right_click_menu_and_grab(element)

                # row_should_expand = True

            # -------------------------  COMBO placement element  ------------------------- #
            elif element_type == ELEM_TYPE_INPUT_COMBO:
                element = element  # type: Combo
                max_line_len = (
                    max([len(str(l)) for l in element.Values])
                    if len(element.Values)
                    else 0
                )
                if not auto_size_text:
                    width = element_size[0]
                else:
                    width = max_line_len + 1
                element.TKStringVar = tk.StringVar()
                style_name = _make_ttk_style_name(
                    ".TCombobox", element, primary_style=True
                )
                combostyle = ttk.Style()
                element.ttk_style = combostyle
                _change_ttk_theme(combostyle, toplevel_form.TtkTheme)

                # Creates a unique name for each field element(Sure there is a better way to do this)
                # unique_field = _make_ttk_style_name('.TCombobox.field', element)

                # Set individual widget options
                try:
                    if element.TextColor not in (None, COLOR_SYSTEM_DEFAULT):
                        combostyle.configure(style_name, foreground=element.TextColor)
                        combostyle.configure(
                            style_name, selectbackground=element.TextColor
                        )
                        combostyle.configure(style_name, insertcolor=element.TextColor)
                        combostyle.map(
                            style_name,
                            fieldforeground=[("readonly", element.TextColor)],
                        )
                    if element.BackgroundColor not in (None, COLOR_SYSTEM_DEFAULT):
                        combostyle.configure(
                            style_name, selectforeground=element.BackgroundColor
                        )
                        combostyle.map(
                            style_name,
                            fieldbackground=[("readonly", element.BackgroundColor)],
                        )
                        combostyle.configure(
                            style_name, fieldbackground=element.BackgroundColor
                        )

                    if element.button_arrow_color not in (None, COLOR_SYSTEM_DEFAULT):
                        combostyle.configure(
                            style_name, arrowcolor=element.button_arrow_color
                        )
                    if element.button_background_color not in (
                        None,
                        COLOR_SYSTEM_DEFAULT,
                    ):
                        combostyle.configure(
                            style_name, background=element.button_background_color
                        )
                    if element.Readonly:
                        if element.TextColor not in (None, COLOR_SYSTEM_DEFAULT):
                            combostyle.configure(
                                style_name, selectforeground=element.TextColor
                            )
                        if element.BackgroundColor not in (None, COLOR_SYSTEM_DEFAULT):
                            combostyle.configure(
                                style_name, selectbackground=element.BackgroundColor
                            )

                except Exception as e:
                    _error_popup_with_traceback(
                        "Combo Element error {}".format(e),
                        "Combo element key: {}".format(element.Key),
                        "One of your colors is bad. Check the text, background, button background and button arrow colors",
                        "Parent Window's Title: {}".format(toplevel_form.Title),
                    )

                # Strange code that is needed to set the font for the drop-down list
                element._dropdown_newfont = tkinter.font.Font(font=font)
                tk_row_frame.option_add(
                    "*TCombobox*Listbox*Font", element._dropdown_newfont
                )

                element.TKCombo = element.Widget = ttk.Combobox(
                    tk_row_frame,
                    width=width,
                    textvariable=element.TKStringVar,
                    font=font,
                    style=style_name,
                )

                # make tcl call to deal with colors for the drop-down formatting
                try:
                    if element.BackgroundColor not in (
                        None,
                        COLOR_SYSTEM_DEFAULT,
                    ) and element.TextColor not in (None, COLOR_SYSTEM_DEFAULT):
                        element.Widget.tk.eval(
                            "[ttk::combobox::PopdownWindow {}].f.l configure -foreground {} -background {} -selectforeground {} -selectbackground {}".format(
                                element.Widget,
                                element.TextColor,
                                element.BackgroundColor,
                                element.BackgroundColor,
                                element.TextColor,
                            )
                        )
                except Exception as e:
                    pass  # going to let this one slide

                # Chr0nic
                element.TKCombo.bind(
                    "<Enter>", lambda event, em=element: testMouseHook2(em)
                )
                element.TKCombo.bind(
                    "<Leave>", lambda event, em=element: testMouseUnhook2(em)
                )

                if toplevel_form.UseDefaultFocus and not toplevel_form.FocusSet:
                    toplevel_form.FocusSet = True
                    element.TKCombo.focus_set()

                if element.Size[1] != 1 and element.Size[1] is not None:
                    element.TKCombo.configure(height=element.Size[1])
                element.TKCombo["values"] = element.Values
                expand, fill, row_should_expand, row_fill_direction = _add_expansion(
                    element, row_should_expand, row_fill_direction
                )
                element.TKCombo.pack(
                    side=tk.LEFT,
                    padx=elementpad[0],
                    pady=elementpad[1],
                    expand=expand,
                    fill=fill,
                )
                if not element.visible:
                    element._pack_forget_save_settings()
                    # element.TKCombo.pack_forget()
                if element.DefaultValue is not None:
                    element.TKCombo.set(element.DefaultValue)
                    # for i, v in enumerate(element.Values):
                    #     if v == element.DefaultValue:
                    #         element.TKCombo.current(i)
                    #         break
                # elif element.Values:
                #     element.TKCombo.current(0)
                if element.ChangeSubmits:
                    element.TKCombo.bind(
                        "<<ComboboxSelected>>", element._ComboboxSelectHandler
                    )
                if element.BindReturnKey:
                    element.TKCombo.bind("<Return>", element._ComboboxSelectHandler)
                if element.enable_per_char_events:
                    element.TKCombo.bind("<Key>", element._KeyboardHandler)
                if element.Readonly:
                    element.TKCombo["state"] = "readonly"
                if element.Disabled:  # note overrides readonly if disabled
                    element.TKCombo["state"] = "disabled"
                if element.Tooltip is not None:
                    element.TooltipObject = ToolTip(
                        element.TKCombo,
                        text=element.Tooltip,
                        timeout=DEFAULT_TOOLTIP_TIME,
                    )
                _add_right_click_menu_and_grab(element)

            # -------------------------  OPTIONMENU placement Element (Like ComboBox but different) element  ------------------------- #
            elif element_type == ELEM_TYPE_INPUT_OPTION_MENU:
                max_line_len = max([len(str(l)) for l in element.Values])
                if not auto_size_text:
                    width = element_size[0]
                else:
                    width = max_line_len
                element.TKStringVar = tk.StringVar()
                if element.DefaultValue:
                    element.TKStringVar.set(element.DefaultValue)
                element.TKOptionMenu = element.Widget = tk.OptionMenu(
                    tk_row_frame, element.TKStringVar, *element.Values
                )
                element.TKOptionMenu.config(
                    highlightthickness=0, font=font, width=width
                )
                element.TKOptionMenu["menu"].config(font=font)
                element.TKOptionMenu.config(borderwidth=border_depth)
                if (
                    element.BackgroundColor is not None
                    and element.BackgroundColor != COLOR_SYSTEM_DEFAULT
                ):
                    element.TKOptionMenu.configure(background=element.BackgroundColor)
                    element.TKOptionMenu["menu"].config(
                        background=element.BackgroundColor
                    )
                if (
                    element.TextColor != COLOR_SYSTEM_DEFAULT
                    and element.TextColor is not None
                ):
                    element.TKOptionMenu.configure(fg=element.TextColor)
                    element.TKOptionMenu["menu"].config(fg=element.TextColor)
                expand, fill, row_should_expand, row_fill_direction = _add_expansion(
                    element, row_should_expand, row_fill_direction
                )
                element.TKOptionMenu.pack(
                    side=tk.LEFT,
                    padx=elementpad[0],
                    pady=elementpad[1],
                    expand=expand,
                    fill=fill,
                )
                if not element.visible:
                    element._pack_forget_save_settings()
                    # element.TKOptionMenu.pack_forget()
                if element.Disabled:
                    element.TKOptionMenu["state"] = "disabled"
                if element.Tooltip is not None:
                    element.TooltipObject = ToolTip(
                        element.TKOptionMenu,
                        text=element.Tooltip,
                        timeout=DEFAULT_TOOLTIP_TIME,
                    )
            # -------------------------  LISTBOX placement element  ------------------------- #
            elif element_type == ELEM_TYPE_INPUT_LISTBOX:
                element = element  # type: Listbox
                max_line_len = (
                    max([len(str(l)) for l in element.Values])
                    if len(element.Values)
                    else 0
                )
                if not auto_size_text:
                    width = element_size[0]
                else:
                    width = max_line_len
                element_frame = tk.Frame(tk_row_frame)
                element.element_frame = element_frame

                justification = tk.LEFT
                if element.justification is not None:
                    if element.justification.startswith("l"):
                        justification = tk.LEFT
                    elif element.justification.startswith("r"):
                        justification = tk.RIGHT
                    elif element.justification.startswith("c"):
                        justification = tk.CENTER

                element.TKStringVar = tk.StringVar()
                element.TKListbox = element.Widget = tk.Listbox(
                    element_frame,
                    height=element_size[1],
                    width=width,
                    selectmode=element.SelectMode,
                    font=font,
                    exportselection=False,
                )
                # On OLD versions of tkinter the justify option isn't available
                try:
                    element.Widget.config(justify=justification)
                except Exception:
                    pass

                element.Widget.config(highlightthickness=0)
                for index, item in enumerate(element.Values):
                    element.TKListbox.insert(tk.END, item)
                    if (
                        element.DefaultValues is not None
                        and item in element.DefaultValues
                    ):
                        element.TKListbox.selection_set(index)
                if (
                    element.BackgroundColor is not None
                    and element.BackgroundColor != COLOR_SYSTEM_DEFAULT
                ):
                    element.TKListbox.configure(background=element.BackgroundColor)
                if (
                    element.HighlightBackgroundColor is not None
                    and element.HighlightBackgroundColor != COLOR_SYSTEM_DEFAULT
                ):
                    element.TKListbox.config(
                        selectbackground=element.HighlightBackgroundColor
                    )
                if text_color is not None and text_color != COLOR_SYSTEM_DEFAULT:
                    element.TKListbox.configure(fg=text_color)
                if (
                    element.HighlightTextColor is not None
                    and element.HighlightTextColor != COLOR_SYSTEM_DEFAULT
                ):
                    element.TKListbox.config(
                        selectforeground=element.HighlightTextColor
                    )
                if element.ChangeSubmits:
                    element.TKListbox.bind(
                        "<<ListboxSelect>>", element._ListboxSelectHandler
                    )

                if not element.NoScrollbar:
                    _make_ttk_scrollbar(element, "v", toplevel_form)
                    element.Widget.configure(yscrollcommand=element.vsb.set)
                    element.vsb.pack(side=tk.RIGHT, fill="y")

                # Horizontal scrollbar
                if element.HorizontalScroll:
                    _make_ttk_scrollbar(element, "h", toplevel_form)
                    element.hsb.pack(side=tk.BOTTOM, fill="x")
                    element.Widget.configure(xscrollcommand=element.hsb.set)

                if not element.NoScrollbar or element.HorizontalScroll:
                    # Chr0nic
                    element.Widget.bind(
                        "<Enter>", lambda event, em=element: testMouseHook(em)
                    )
                    element.Widget.bind(
                        "<Leave>", lambda event, em=element: testMouseUnhook(em)
                    )

                # else:
                #     element.TKText.config(wrap='word')

                # if not element.NoScrollbar:
                #     # Vertical scrollbar
                #     element.vsb = tk.Scrollbar(element_frame, orient="vertical", command=element.TKListbox.yview)
                #     element.TKListbox.configure(yscrollcommand=element.vsb.set)
                #     element.vsb.pack(side=tk.RIGHT, fill='y')

                # Horizontal scrollbar
                # if element.HorizontalScroll:
                #     hscrollbar = tk.Scrollbar(element_frame, orient=tk.HORIZONTAL)
                #     hscrollbar.pack(side=tk.BOTTOM, fill='x')
                #     hscrollbar.config(command=element.Widget.xview)
                #     element.Widget.configure(xscrollcommand=hscrollbar.set)
                #     element.hsb = hscrollbar
                #
                #     # Chr0nic
                #     element.TKListbox.bind("<Enter>", lambda event, em=element: testMouseHook(em))
                #     element.TKListbox.bind("<Leave>", lambda event, em=element: testMouseUnhook(em))
                #
                #

                expand, fill, row_should_expand, row_fill_direction = _add_expansion(
                    element, row_should_expand, row_fill_direction
                )
                element_frame.pack(
                    side=tk.LEFT,
                    padx=elementpad[0],
                    pady=elementpad[1],
                    fill=fill,
                    expand=expand,
                )
                element.TKListbox.pack(side=tk.LEFT, fill=fill, expand=expand)
                if not element.visible:
                    element._pack_forget_save_settings(alternate_widget=element_frame)
                    # element_frame.pack_forget()
                if element.BindReturnKey:
                    element.TKListbox.bind("<Return>", element._ListboxSelectHandler)
                    element.TKListbox.bind(
                        "<Double-Button-1>", element._ListboxSelectHandler
                    )
                if element.Disabled:
                    element.TKListbox["state"] = "disabled"
                if element.Tooltip is not None:
                    element.TooltipObject = ToolTip(
                        element.TKListbox,
                        text=element.Tooltip,
                        timeout=DEFAULT_TOOLTIP_TIME,
                    )
                _add_right_click_menu_and_grab(element)
            # -------------------------  MULTILINE placement element  ------------------------- #
            elif element_type == ELEM_TYPE_INPUT_MULTILINE:
                element = element  # type: Multiline
                width, height = element_size
                bd = element.BorderWidth
                element.element_frame = element_frame = tk.Frame(tk_row_frame)

                # if element.no_scrollbar:
                element.TKText = element.Widget = tk.Text(
                    element_frame,
                    width=width,
                    height=height,
                    bd=bd,
                    font=font,
                    relief=RELIEF_SUNKEN,
                )
                # else:
                #     element.TKText = element.Widget = tk.scrolledtext.ScrolledText(element_frame, width=width, height=height, bd=bd, font=font, relief=RELIEF_SUNKEN)

                if not element.no_scrollbar:
                    _make_ttk_scrollbar(element, "v", toplevel_form)

                    element.Widget.configure(yscrollcommand=element.vsb.set)
                    element.vsb.pack(side=tk.RIGHT, fill="y")

                # Horizontal scrollbar
                if element.HorizontalScroll:
                    element.TKText.config(wrap="none")
                    _make_ttk_scrollbar(element, "h", toplevel_form)
                    element.hsb.pack(side=tk.BOTTOM, fill="x")
                    element.Widget.configure(xscrollcommand=element.hsb.set)
                else:
                    element.TKText.config(wrap="word")

                if element.wrap_lines:
                    element.TKText.config(wrap="word")
                elif not element.wrap_lines:
                    element.TKText.config(wrap="none")

                if not element.no_scrollbar or element.HorizontalScroll:
                    # Chr0nic
                    element.TKText.bind(
                        "<Enter>", lambda event, em=element: testMouseHook(em)
                    )
                    element.TKText.bind(
                        "<Leave>", lambda event, em=element: testMouseUnhook(em)
                    )

                if element.DefaultText:
                    element.TKText.insert(
                        1.0, element.DefaultText
                    )  # set the default text
                element.TKText.config(highlightthickness=0)
                if text_color is not None and text_color != COLOR_SYSTEM_DEFAULT:
                    element.TKText.configure(fg=text_color, selectbackground=text_color)
                    element.TKText.config(insertbackground=text_color)
                if (
                    element.BackgroundColor is not None
                    and element.BackgroundColor != COLOR_SYSTEM_DEFAULT
                ):
                    element.TKText.configure(
                        background=element.BackgroundColor,
                        selectforeground=element.BackgroundColor,
                    )
                if element.selected_background_color not in (
                    None,
                    COLOR_SYSTEM_DEFAULT,
                ):
                    element.TKText.configure(
                        selectbackground=element.selected_background_color
                    )
                if element.selected_text_color not in (None, COLOR_SYSTEM_DEFAULT):
                    element.TKText.configure(
                        selectforeground=element.selected_text_color
                    )
                element.TKText.tag_configure("center", justify="center")
                element.TKText.tag_configure("left", justify="left")
                element.TKText.tag_configure("right", justify="right")

                if element.Justification.startswith("l"):
                    element.TKText.tag_add("left", 1.0, "end")
                    element.justification_tag = "left"
                elif element.Justification.startswith("r"):
                    element.TKText.tag_add("right", 1.0, "end")
                    element.justification_tag = "right"
                elif element.Justification.startswith("c"):
                    element.TKText.tag_add("center", 1.0, "end")
                    element.justification_tag = "center"
                # if DEFAULT_SCROLLBAR_COLOR not in (None, COLOR_SYSTEM_DEFAULT):               # only works on Linux so not including it
                #     element.TKText.vbar.config(troughcolor=DEFAULT_SCROLLBAR_COLOR)
                expand, fill, row_should_expand, row_fill_direction = _add_expansion(
                    element, row_should_expand, row_fill_direction
                )

                element.element_frame.pack(
                    side=tk.LEFT,
                    padx=elementpad[0],
                    pady=elementpad[1],
                    fill=fill,
                    expand=expand,
                )
                element.Widget.pack(side=tk.LEFT, fill=fill, expand=expand)

                if not element.visible:
                    element._pack_forget_save_settings(alternate_widget=element_frame)
                    # element.element_frame.pack_forget()
                else:
                    # Chr0nic
                    element.TKText.bind(
                        "<Enter>", lambda event, em=element: testMouseHook(em)
                    )
                    element.TKText.bind(
                        "<Leave>", lambda event, em=element: testMouseUnhook(em)
                    )
                if element.ChangeSubmits:
                    element.TKText.bind("<Key>", element._KeyboardHandler)
                if element.EnterSubmits:
                    element.TKText.bind("<Return>", element._ReturnKeyHandler)
                if element.Focus is True or (
                    toplevel_form.UseDefaultFocus and not toplevel_form.FocusSet
                ):
                    toplevel_form.FocusSet = True
                    element.TKText.focus_set()

                if element.Disabled:
                    element.TKText["state"] = "disabled"
                if element.Tooltip is not None:
                    element.TooltipObject = ToolTip(
                        element.TKText,
                        text=element.Tooltip,
                        timeout=DEFAULT_TOOLTIP_TIME,
                    )

                if element.reroute_cprint:
                    cprint_set_output_destination(toplevel_form, element.Key)

                _add_right_click_menu_and_grab(element)

                if element.reroute_stdout:
                    element.reroute_stdout_to_here()
                if element.reroute_stderr:
                    element.reroute_stderr_to_here()

                # row_should_expand = True
            # -------------------------  CHECKBOX pleacement element  ------------------------- #
            elif element_type == ELEM_TYPE_INPUT_CHECKBOX:
                element = element  # type: Checkbox
                width = 0 if auto_size_text else element_size[0]
                default_value = element.InitialState
                element.TKIntVar = tk.IntVar()
                element.TKIntVar.set(default_value if default_value is not None else 0)

                element.TKCheckbutton = element.Widget = tk.Checkbutton(
                    tk_row_frame,
                    anchor=tk.NW,
                    text=element.Text,
                    width=width,
                    variable=element.TKIntVar,
                    bd=border_depth,
                    font=font,
                )
                if element.ChangeSubmits:
                    element.TKCheckbutton.configure(command=element._CheckboxHandler)
                if element.Disabled:
                    element.TKCheckbutton.configure(state="disable")
                if (
                    element.BackgroundColor is not None
                    and element.BackgroundColor != COLOR_SYSTEM_DEFAULT
                ):
                    element.TKCheckbutton.configure(background=element.BackgroundColor)
                    element.TKCheckbutton.configure(
                        selectcolor=element.CheckboxBackgroundColor
                    )  # The background of the checkbox
                    element.TKCheckbutton.configure(
                        activebackground=element.BackgroundColor
                    )
                if text_color is not None and text_color != COLOR_SYSTEM_DEFAULT:
                    element.TKCheckbutton.configure(fg=text_color)
                    element.TKCheckbutton.configure(activeforeground=element.TextColor)

                element.Widget.configure(highlightthickness=element.highlight_thickness)
                if element.BackgroundColor != COLOR_SYSTEM_DEFAULT:
                    element.TKCheckbutton.config(
                        highlightbackground=element.BackgroundColor
                    )
                if element.TextColor != COLOR_SYSTEM_DEFAULT:
                    element.TKCheckbutton.config(highlightcolor=element.TextColor)
                expand, fill, row_should_expand, row_fill_direction = _add_expansion(
                    element, row_should_expand, row_fill_direction
                )
                element.TKCheckbutton.pack(
                    side=tk.LEFT,
                    padx=elementpad[0],
                    pady=elementpad[1],
                    expand=expand,
                    fill=fill,
                )
                if not element.visible:
                    element._pack_forget_save_settings()
                    # element.TKCheckbutton.pack_forget()
                if element.Tooltip is not None:
                    element.TooltipObject = ToolTip(
                        element.TKCheckbutton,
                        text=element.Tooltip,
                        timeout=DEFAULT_TOOLTIP_TIME,
                    )
                _add_right_click_menu_and_grab(element)

            # -------------------------  PROGRESS placement element  ------------------------- #
            elif element_type == ELEM_TYPE_PROGRESS_BAR:
                element = element  # type: ProgressBar
                if element.size_px != (None, None):
                    progress_length, progress_width = element.size_px
                else:
                    width = element_size[0]
                    fnt = tkinter.font.Font()
                    char_width = fnt.measure("A")  # single character width
                    progress_length = width * char_width
                    progress_width = element_size[1]
                direction = element.Orientation
                if element.BarColor != (
                    None,
                    None,
                ):  # if element has a bar color, use it
                    bar_color = element.BarColor
                else:
                    bar_color = DEFAULT_PROGRESS_BAR_COLOR
                if element.Orientation.lower().startswith("h"):
                    base_style_name = ".Horizontal.TProgressbar"
                else:
                    base_style_name = ".Vertical.TProgressbar"
                style_name = _make_ttk_style_name(
                    base_style_name, element, primary_style=True
                )
                element.TKProgressBar = TKProgressBar(
                    tk_row_frame,
                    element.MaxValue,
                    progress_length,
                    progress_width,
                    orientation=direction,
                    BarColor=bar_color,
                    border_width=element.BorderWidth,
                    relief=element.Relief,
                    ttk_theme=toplevel_form.TtkTheme,
                    key=element.Key,
                    style_name=style_name,
                )
                element.Widget = element.TKProgressBar.TKProgressBarForReal
                expand, fill, row_should_expand, row_fill_direction = _add_expansion(
                    element, row_should_expand, row_fill_direction
                )
                element.TKProgressBar.TKProgressBarForReal.pack(
                    side=tk.LEFT,
                    padx=elementpad[0],
                    pady=elementpad[1],
                    expand=expand,
                    fill=fill,
                )
                if not element.visible:
                    element._pack_forget_save_settings(
                        alternate_widget=element.TKProgressBar.TKProgressBarForReal
                    )
                    # element.TKProgressBar.TKProgressBarForReal.pack_forget()
                _add_right_click_menu_and_grab(element)

                # -------------------------  RADIO placement element  ------------------------- #
            elif element_type == ELEM_TYPE_INPUT_RADIO:
                element = element  # type: Radio
                width = 0 if auto_size_text else element_size[0]
                default_value = element.InitialState
                ID = element.GroupID
                # see if ID has already been placed
                value = EncodeRadioRowCol(
                    form.ContainerElemementNumber, row_num, col_num
                )  # value to set intvar to if this radio is selected
                element.EncodedRadioValue = value
                if ID in toplevel_form.RadioDict:
                    RadVar = toplevel_form.RadioDict[ID]
                else:
                    RadVar = tk.IntVar()
                    toplevel_form.RadioDict[ID] = RadVar
                element.TKIntVar = RadVar  # store the RadVar in Radio object
                if (
                    default_value
                ):  # if this radio is the one selected, set RadVar to match
                    element.TKIntVar.set(value)
                element.TKRadio = element.Widget = tk.Radiobutton(
                    tk_row_frame,
                    anchor=tk.NW,
                    text=element.Text,
                    width=width,
                    variable=element.TKIntVar,
                    value=value,
                    bd=border_depth,
                    font=font,
                )
                if element.ChangeSubmits:
                    element.TKRadio.configure(command=element._RadioHandler)
                if not element.BackgroundColor in (None, COLOR_SYSTEM_DEFAULT):
                    element.TKRadio.configure(background=element.BackgroundColor)
                    element.TKRadio.configure(selectcolor=element.CircleBackgroundColor)
                    element.TKRadio.configure(activebackground=element.BackgroundColor)
                if text_color is not None and text_color != COLOR_SYSTEM_DEFAULT:
                    element.TKRadio.configure(fg=text_color)
                    element.TKRadio.configure(activeforeground=text_color)

                element.Widget.configure(highlightthickness=1)
                if element.BackgroundColor != COLOR_SYSTEM_DEFAULT:
                    element.TKRadio.config(highlightbackground=element.BackgroundColor)
                if element.TextColor != COLOR_SYSTEM_DEFAULT:
                    element.TKRadio.config(highlightcolor=element.TextColor)

                if element.Disabled:
                    element.TKRadio["state"] = "disabled"
                expand, fill, row_should_expand, row_fill_direction = _add_expansion(
                    element, row_should_expand, row_fill_direction
                )
                element.TKRadio.pack(
                    side=tk.LEFT,
                    padx=elementpad[0],
                    pady=elementpad[1],
                    expand=expand,
                    fill=fill,
                )
                if not element.visible:
                    element._pack_forget_save_settings()
                    # element.TKRadio.pack_forget()
                if element.Tooltip is not None:
                    element.TooltipObject = ToolTip(
                        element.TKRadio,
                        text=element.Tooltip,
                        timeout=DEFAULT_TOOLTIP_TIME,
                    )
                _add_right_click_menu_and_grab(element)

                # -------------------------  SPIN placement element  ------------------------- #
            elif element_type == ELEM_TYPE_INPUT_SPIN:
                element = element  # type: Spin
                width, height = element_size
                width = 0 if auto_size_text else element_size[0]
                element.TKStringVar = tk.StringVar()
                element.TKSpinBox = element.Widget = tk.Spinbox(
                    tk_row_frame,
                    values=element.Values,
                    textvariable=element.TKStringVar,
                    width=width,
                    bd=border_depth,
                )
                if element.DefaultValue is not None:
                    element.TKStringVar.set(element.DefaultValue)
                element.TKSpinBox.configure(font=font)  # set wrap to width of widget
                if (
                    element.BackgroundColor is not None
                    and element.BackgroundColor != COLOR_SYSTEM_DEFAULT
                ):
                    element.TKSpinBox.configure(background=element.BackgroundColor)
                    element.TKSpinBox.configure(
                        buttonbackground=element.BackgroundColor
                    )
                if text_color not in (None, COLOR_SYSTEM_DEFAULT):
                    element.TKSpinBox.configure(fg=text_color)
                    element.TKSpinBox.config(insertbackground=text_color)
                element.Widget.config(highlightthickness=0)
                if element.wrap:
                    element.Widget.configure(wrap=True)
                expand, fill, row_should_expand, row_fill_direction = _add_expansion(
                    element, row_should_expand, row_fill_direction
                )
                element.TKSpinBox.pack(
                    side=tk.LEFT,
                    padx=elementpad[0],
                    pady=elementpad[1],
                    expand=expand,
                    fill=fill,
                )
                if not element.visible:
                    element._pack_forget_save_settings()
                    # element.TKSpinBox.pack_forget()
                if element.ChangeSubmits:
                    element.TKSpinBox.configure(command=element._SpinboxSelectHandler)
                    # element.TKSpinBox.bind('<ButtonRelease-1>', element._SpinChangedHandler)
                    # element.TKSpinBox.bind('<Up>', element._SpinChangedHandler)
                    # element.TKSpinBox.bind('<Down>', element._SpinChangedHandler)
                if element.Readonly:
                    element.TKSpinBox["state"] = "readonly"
                if element.Disabled:  # note overrides readonly if disabled
                    element.TKSpinBox["state"] = "disabled"
                if element.Tooltip is not None:
                    element.TooltipObject = ToolTip(
                        element.TKSpinBox,
                        text=element.Tooltip,
                        timeout=DEFAULT_TOOLTIP_TIME,
                    )
                if element.BindReturnKey:
                    element.TKSpinBox.bind("<Return>", element._SpinboxSelectHandler)
                _add_right_click_menu_and_grab(element)
                # -------------------------  IMAGE placement element  ------------------------- #
            elif element_type == ELEM_TYPE_IMAGE:
                element = element  # type: Image
                try:
                    if element.Filename is not None:
                        photo = tk.PhotoImage(file=element.Filename)
                    elif element.Data is not None:
                        photo = tk.PhotoImage(data=element.Data)
                    else:
                        photo = None

                    if photo is not None:
                        if element.ImageSubsample:
                            photo = photo.subsample(element.ImageSubsample)
                        if element.zoom:
                            photo = photo.zoom(element.zoom)
                        # print('*ERROR laying out form.... Image Element has no image specified*')
                except Exception as e:
                    photo = None
                    _error_popup_with_traceback(
                        "Your Window has an Image Element with a problem",
                        "The traceback will show you the Window with the problem layout",
                        "Look in this Window's layout for an Image element that has a key of {}".format(
                            element.Key
                        ),
                        "The error occuring is:",
                        e,
                    )

                element.tktext_label = element.Widget = tk.Label(tk_row_frame, bd=0)

                if photo is not None:
                    if (
                        element_size == (None, None)
                        or element_size is None
                        or element_size == toplevel_form.DefaultElementSize
                    ):
                        width, height = photo.width(), photo.height()
                    else:
                        width, height = element_size
                    element.tktext_label.config(image=photo, width=width, height=height)

                if not element.BackgroundColor in (None, COLOR_SYSTEM_DEFAULT):
                    element.tktext_label.config(background=element.BackgroundColor)

                element.tktext_label.image = photo
                # tktext_label.configure(anchor=tk.NW, image=photo)
                expand, fill, row_should_expand, row_fill_direction = _add_expansion(
                    element, row_should_expand, row_fill_direction
                )
                element.tktext_label.pack(
                    side=tk.LEFT,
                    padx=elementpad[0],
                    pady=elementpad[1],
                    expand=expand,
                    fill=fill,
                )

                if not element.visible:
                    element._pack_forget_save_settings()
                    # element.tktext_label.pack_forget()
                if element.Tooltip is not None:
                    element.TooltipObject = ToolTip(
                        element.tktext_label,
                        text=element.Tooltip,
                        timeout=DEFAULT_TOOLTIP_TIME,
                    )
                if element.EnableEvents and element.tktext_label is not None:
                    element.tktext_label.bind("<ButtonPress-1>", element._ClickHandler)

                _add_right_click_menu_and_grab(element)

                # -------------------------  Canvas placement element  ------------------------- #
            elif element_type == ELEM_TYPE_CANVAS:
                element = element  # type: Canvas
                width, height = element_size
                if element._TKCanvas is None:
                    element._TKCanvas = tk.Canvas(
                        tk_row_frame, width=width, height=height, bd=border_depth
                    )
                else:
                    element._TKCanvas.master = tk_row_frame
                element.Widget = element._TKCanvas

                if (
                    element.BackgroundColor is not None
                    and element.BackgroundColor != COLOR_SYSTEM_DEFAULT
                ):
                    element._TKCanvas.configure(
                        background=element.BackgroundColor, highlightthickness=0
                    )
                expand, fill, row_should_expand, row_fill_direction = _add_expansion(
                    element, row_should_expand, row_fill_direction
                )
                element._TKCanvas.pack(
                    side=tk.LEFT,
                    padx=elementpad[0],
                    pady=elementpad[1],
                    expand=expand,
                    fill=fill,
                )
                if not element.visible:
                    element._pack_forget_save_settings()
                    # element._TKCanvas.pack_forget()
                if element.Tooltip is not None:
                    element.TooltipObject = ToolTip(
                        element._TKCanvas,
                        text=element.Tooltip,
                        timeout=DEFAULT_TOOLTIP_TIME,
                    )
                _add_right_click_menu_and_grab(element)

                # -------------------------  Graph placement element  ------------------------- #
            elif element_type == ELEM_TYPE_GRAPH:
                element = element  # type: Graph
                width, height = element_size
                # I don't know why TWO canvases were being defined, on inside the other.  Was it so entire canvas can move?
                # if element._TKCanvas is None:
                #     element._TKCanvas = tk.Canvas(tk_row_frame, width=width, height=height, bd=border_depth)
                # else:
                #     element._TKCanvas.master = tk_row_frame
                element._TKCanvas2 = element.Widget = tk.Canvas(
                    tk_row_frame, width=width, height=height, bd=border_depth
                )
                expand, fill, row_should_expand, row_fill_direction = _add_expansion(
                    element, row_should_expand, row_fill_direction
                )
                element._TKCanvas2.pack(side=tk.LEFT, expand=expand, fill=fill)
                element._TKCanvas2.addtag_all("mytag")
                if (
                    element.BackgroundColor is not None
                    and element.BackgroundColor != COLOR_SYSTEM_DEFAULT
                ):
                    element._TKCanvas2.configure(
                        background=element.BackgroundColor, highlightthickness=0
                    )
                    # element._TKCanvas.configure(background=element.BackgroundColor, highlightthickness=0)
                element._TKCanvas2.pack(
                    side=tk.LEFT,
                    padx=elementpad[0],
                    pady=elementpad[1],
                    expand=expand,
                    fill=fill,
                )
                if not element.visible:
                    element._pack_forget_save_settings()
                    # element._TKCanvas2.pack_forget()
                if element.Tooltip is not None:
                    element.TooltipObject = ToolTip(
                        element._TKCanvas2,
                        text=element.Tooltip,
                        timeout=DEFAULT_TOOLTIP_TIME,
                    )
                if element.ChangeSubmits:
                    element._TKCanvas2.bind(
                        "<ButtonRelease-1>", element.ButtonReleaseCallBack
                    )
                    element._TKCanvas2.bind(
                        "<ButtonPress-1>", element.ButtonPressCallBack
                    )
                if element.DragSubmits:
                    element._TKCanvas2.bind("<Motion>", element.MotionCallBack)
                _add_right_click_menu_and_grab(element)
            # -------------------------  MENU placement element  ------------------------- #
            elif element_type == ELEM_TYPE_MENUBAR:
                element = element  # type: MenuBar
                menu_def = element.MenuDefinition
                element.TKMenu = element.Widget = tk.Menu(
                    toplevel_form.TKroot,
                    tearoff=element.Tearoff,
                    tearoffcommand=element._tearoff_menu_callback,
                )  # create the menubar
                menubar = element.TKMenu
                if (
                    font is not None
                ):  # if a font is used, make sure it's saved in the element
                    element.Font = font
                for menu_entry in menu_def:
                    baritem = tk.Menu(
                        menubar,
                        tearoff=element.Tearoff,
                        tearoffcommand=element._tearoff_menu_callback,
                    )
                    if element.BackgroundColor not in (COLOR_SYSTEM_DEFAULT, None):
                        baritem.config(bg=element.BackgroundColor)
                        baritem.config(activeforeground=element.BackgroundColor)
                    if element.TextColor not in (COLOR_SYSTEM_DEFAULT, None):
                        baritem.config(fg=element.TextColor)
                        baritem.config(activebackground=element.TextColor)
                    if element.DisabledTextColor not in (COLOR_SYSTEM_DEFAULT, None):
                        baritem.config(disabledforeground=element.DisabledTextColor)
                    if font is not None:
                        baritem.config(font=font)
                    pos = menu_entry[0].find(MENU_SHORTCUT_CHARACTER)
                    # print(pos)
                    if pos != -1:
                        if (
                            pos == 0
                            or menu_entry[0][pos - len(MENU_SHORTCUT_CHARACTER)] != "\\"
                        ):
                            menu_entry[0] = (
                                menu_entry[0][:pos] + menu_entry[0][pos + 1 :]
                            )
                    if menu_entry[0][0] == MENU_DISABLED_CHARACTER:
                        menubar.add_cascade(
                            label=menu_entry[0][len(MENU_DISABLED_CHARACTER) :],
                            menu=baritem,
                            underline=pos - 1,
                        )
                        menubar.entryconfig(
                            menu_entry[0][len(MENU_DISABLED_CHARACTER) :],
                            state="disabled",
                        )
                    else:
                        menubar.add_cascade(
                            label=menu_entry[0], menu=baritem, underline=pos
                        )

                    if len(menu_entry) > 1:
                        AddMenuItem(baritem, menu_entry[1], element)
                toplevel_form.TKroot.configure(menu=element.TKMenu)
            # -------------------------  Frame placement element  ------------------------- #
            elif element_type == ELEM_TYPE_FRAME:
                element = element  # type: Frame
                labeled_frame = element.Widget = tk.LabelFrame(
                    tk_row_frame, text=element.Title, relief=element.Relief
                )
                element.TKFrame = labeled_frame
                PackFormIntoFrame(element, labeled_frame, toplevel_form)
                expand, fill, row_should_expand, row_fill_direction = _add_expansion(
                    element, row_should_expand, row_fill_direction
                )
                if element.VerticalAlignment is not None:
                    anchor = tk.CENTER  # Default to center if a bad choice is made
                    if element.VerticalAlignment.lower().startswith("t"):
                        anchor = tk.N
                    if element.VerticalAlignment.lower().startswith("c"):
                        anchor = tk.CENTER
                    if element.VerticalAlignment.lower().startswith("b"):
                        anchor = tk.S
                    labeled_frame.pack(
                        side=tk.LEFT,
                        anchor=anchor,
                        padx=elementpad[0],
                        pady=elementpad[1],
                        expand=expand,
                        fill=fill,
                    )
                else:
                    labeled_frame.pack(
                        side=tk.LEFT,
                        padx=elementpad[0],
                        pady=elementpad[1],
                        expand=expand,
                        fill=fill,
                    )

                if element.Size != (None, None):
                    labeled_frame.config(width=element.Size[0], height=element.Size[1])
                    labeled_frame.pack_propagate(0)
                if not element.visible:
                    element._pack_forget_save_settings()
                    # labeled_frame.pack_forget()
                if (
                    element.BackgroundColor != COLOR_SYSTEM_DEFAULT
                    and element.BackgroundColor is not None
                ):
                    labeled_frame.configure(
                        background=element.BackgroundColor,
                        highlightbackground=element.BackgroundColor,
                        highlightcolor=element.BackgroundColor,
                    )
                if (
                    element.TextColor != COLOR_SYSTEM_DEFAULT
                    and element.TextColor is not None
                ):
                    labeled_frame.configure(foreground=element.TextColor)
                if font is not None:
                    labeled_frame.configure(font=font)
                if element.TitleLocation is not None:
                    labeled_frame.configure(labelanchor=element.TitleLocation)
                if element.BorderWidth is not None:
                    labeled_frame.configure(borderwidth=element.BorderWidth)
                if element.Tooltip is not None:
                    element.TooltipObject = ToolTip(
                        labeled_frame,
                        text=element.Tooltip,
                        timeout=DEFAULT_TOOLTIP_TIME,
                    )
                _add_right_click_menu_and_grab(element)
                # row_should_expand=True
            # -------------------------  Tab placement element  ------------------------- #
            elif element_type == ELEM_TYPE_TAB:
                element = element  # type: Tab
                form = form  # type: TabGroup
                element.TKFrame = element.Widget = tk.Frame(form.TKNotebook)
                PackFormIntoFrame(element, element.TKFrame, toplevel_form)
                state = "normal"
                if element.Disabled:
                    state = "disabled"
                if not element.visible:
                    state = "hidden"
                # this code will add an image to the tab. Use it when adding the image on a tab enhancement
                try:
                    if element.Filename is not None:
                        photo = tk.PhotoImage(file=element.Filename)
                    elif element.Data is not None:
                        photo = tk.PhotoImage(data=element.Data)
                    else:
                        photo = None

                    if element.ImageSubsample and photo is not None:
                        photo = photo.subsample(element.ImageSubsample)
                    if element.zoom and photo is not None:
                        photo = photo.zoom(element.zoom)
                        # print('*ERROR laying out form.... Image Element has no image specified*')
                except Exception as e:
                    photo = None
                    _error_popup_with_traceback(
                        "Your Window has an Tab Element with an IMAGE problem",
                        "The traceback will show you the Window with the problem layout",
                        "Look in this Window's layout for an Image element that has a key of {}".format(
                            element.Key
                        ),
                        "The error occuring is:",
                        e,
                    )

                element.photo = photo
                if photo is not None:
                    if (
                        element_size == (None, None)
                        or element_size is None
                        or element_size == toplevel_form.DefaultElementSize
                    ):
                        width, height = photo.width(), photo.height()
                    else:
                        width, height = element_size
                    element.tktext_label = tk.Label(
                        tk_row_frame, image=photo, width=width, height=height, bd=0
                    )
                else:
                    element.tktext_label = tk.Label(tk_row_frame, bd=0)
                if photo is not None:
                    form.TKNotebook.add(
                        element.TKFrame,
                        text=element.Title,
                        compound=tk.LEFT,
                        state=state,
                        image=photo,
                    )

                # element.photo_image = tk.PhotoImage(data=DEFAULT_BASE64_ICON)
                # form.TKNotebook.add(element.TKFrame, text=element.Title, compound=tk.LEFT, state=state,image = element.photo_image)

                form.TKNotebook.add(element.TKFrame, text=element.Title, state=state)
                # July 28 2022 removing the expansion and pack as a test
                # expand, fill, row_should_expand, row_fill_direction = _add_expansion(element, row_should_expand, row_fill_direction)
                # form.TKNotebook.pack(side=tk.LEFT, padx=elementpad[0], pady=elementpad[1], fill=fill, expand=expand)

                element.ParentNotebook = form.TKNotebook
                element.TabID = form.TabCount
                form.tab_index_to_key[element.TabID] = (
                    element.key
                )  # has a list of the tabs in the notebook and their associated key
                form.TabCount += 1
                if element.BackgroundColor not in (COLOR_SYSTEM_DEFAULT, None):
                    element.TKFrame.configure(
                        background=element.BackgroundColor,
                        highlightbackground=element.BackgroundColor,
                        highlightcolor=element.BackgroundColor,
                    )

                # if element.BorderWidth is not None:
                #     element.TKFrame.configure(borderwidth=element.BorderWidth)
                if element.Tooltip is not None:
                    element.TooltipObject = ToolTip(
                        element.TKFrame,
                        text=element.Tooltip,
                        timeout=DEFAULT_TOOLTIP_TIME,
                    )
                _add_right_click_menu_and_grab(element)
                # row_should_expand = True
            # -------------------------  TabGroup placement element  ------------------------- #
            elif element_type == ELEM_TYPE_TAB_GROUP:
                element = element  # type: TabGroup
                # custom_style = str(element.Key) + 'customtab.TNotebook'
                custom_style = _make_ttk_style_name(
                    ".TNotebook", element, primary_style=True
                )
                style = ttk.Style()
                _change_ttk_theme(style, toplevel_form.TtkTheme)

                if element.TabLocation is not None:
                    position_dict = {
                        "left": "w",
                        "right": "e",
                        "top": "n",
                        "bottom": "s",
                        "lefttop": "wn",
                        "leftbottom": "ws",
                        "righttop": "en",
                        "rightbottom": "es",
                        "bottomleft": "sw",
                        "bottomright": "se",
                        "topleft": "nw",
                        "topright": "ne",
                    }
                    try:
                        tab_position = position_dict[element.TabLocation]
                    except Exception:
                        tab_position = position_dict["top"]
                    style.configure(custom_style, tabposition=tab_position)

                if (
                    element.BackgroundColor is not None
                    and element.BackgroundColor != COLOR_SYSTEM_DEFAULT
                ):
                    style.configure(custom_style, background=element.BackgroundColor)

                # FINALLY the proper styling to get tab colors!
                if (
                    element.SelectedTitleColor is not None
                    and element.SelectedTitleColor != COLOR_SYSTEM_DEFAULT
                ):
                    style.map(
                        custom_style + ".Tab",
                        foreground=[("selected", element.SelectedTitleColor)],
                    )
                if (
                    element.SelectedBackgroundColor is not None
                    and element.SelectedBackgroundColor != COLOR_SYSTEM_DEFAULT
                ):
                    style.map(
                        custom_style + ".Tab",
                        background=[("selected", element.SelectedBackgroundColor)],
                    )
                if (
                    element.TabBackgroundColor is not None
                    and element.TabBackgroundColor != COLOR_SYSTEM_DEFAULT
                ):
                    style.configure(
                        custom_style + ".Tab", background=element.TabBackgroundColor
                    )
                if (
                    element.TextColor is not None
                    and element.TextColor != COLOR_SYSTEM_DEFAULT
                ):
                    style.configure(custom_style + ".Tab", foreground=element.TextColor)
                if element.BorderWidth is not None:
                    style.configure(custom_style, borderwidth=element.BorderWidth)
                if element.TabBorderWidth is not None:
                    style.configure(
                        custom_style + ".Tab", borderwidth=element.TabBorderWidth
                    )  # if ever want to get rid of border around the TABS themselves
                if element.FocusColor not in (None, COLOR_SYSTEM_DEFAULT):
                    style.configure(
                        custom_style + ".Tab", focuscolor=element.FocusColor
                    )

                style.configure(custom_style + ".Tab", font=font)
                element.Style = style
                element.StyleName = custom_style
                element.TKNotebook = element.Widget = ttk.Notebook(
                    tk_row_frame, style=custom_style
                )

                PackFormIntoFrame(element, toplevel_form.TKroot, toplevel_form)

                expand, fill, row_should_expand, row_fill_direction = _add_expansion(
                    element, row_should_expand, row_fill_direction
                )
                element.TKNotebook.pack(
                    anchor=tk.SW,
                    side=tk.LEFT,
                    padx=elementpad[0],
                    pady=elementpad[1],
                    fill=fill,
                    expand=expand,
                )

                if element.ChangeSubmits:
                    element.TKNotebook.bind(
                        "<<NotebookTabChanged>>", element._TabGroupSelectHandler
                    )
                if element.Tooltip is not None:
                    element.TooltipObject = ToolTip(
                        element.TKNotebook,
                        text=element.Tooltip,
                        timeout=DEFAULT_TOOLTIP_TIME,
                    )
                if element.Size != (None, None):
                    element.TKNotebook.configure(
                        width=element.Size[0], height=element.Size[1]
                    )
                _add_right_click_menu_and_grab(element)
                if not element.visible:
                    element._pack_forget_save_settings()
                # row_should_expand = True
                # -------------------  SLIDER placement element  ------------------------- #
            elif element_type == ELEM_TYPE_INPUT_SLIDER:
                element = element  # type: Slider
                slider_length = element_size[0] * _char_width_in_pixels(font)
                slider_width = element_size[1]
                element.TKIntVar = tk.IntVar()
                element.TKIntVar.set(element.DefaultValue)
                if element.Orientation.startswith("v"):
                    range_from = element.Range[1]
                    range_to = element.Range[0]
                    slider_length += DEFAULT_MARGINS[1] * (
                        element_size[0] * 2
                    )  # add in the padding
                else:
                    range_from = element.Range[0]
                    range_to = element.Range[1]
                tkscale = element.Widget = tk.Scale(
                    tk_row_frame,
                    orient=element.Orientation,
                    variable=element.TKIntVar,
                    from_=range_from,
                    to_=range_to,
                    resolution=element.Resolution,
                    length=slider_length,
                    width=slider_width,
                    bd=element.BorderWidth,
                    relief=element.Relief,
                    font=font,
                    tickinterval=element.TickInterval,
                )
                tkscale.config(highlightthickness=0)
                if element.ChangeSubmits:
                    tkscale.config(command=element._SliderChangedHandler)
                if element.BackgroundColor not in (None, COLOR_SYSTEM_DEFAULT):
                    tkscale.configure(background=element.BackgroundColor)
                if element.TroughColor != COLOR_SYSTEM_DEFAULT:
                    tkscale.config(troughcolor=element.TroughColor)
                if element.DisableNumericDisplay:
                    tkscale.config(showvalue=0)
                if text_color not in (None, COLOR_SYSTEM_DEFAULT):
                    tkscale.configure(fg=text_color)
                expand, fill, row_should_expand, row_fill_direction = _add_expansion(
                    element, row_should_expand, row_fill_direction
                )
                tkscale.pack(
                    side=tk.LEFT,
                    padx=elementpad[0],
                    pady=elementpad[1],
                    expand=expand,
                    fill=fill,
                )
                if not element.visible:
                    element._pack_forget_save_settings()
                    # tkscale.pack_forget()
                element.TKScale = tkscale
                if element.Disabled:
                    element.TKScale["state"] = "disabled"
                if element.Tooltip is not None:
                    element.TooltipObject = ToolTip(
                        element.TKScale,
                        text=element.Tooltip,
                        timeout=DEFAULT_TOOLTIP_TIME,
                    )
                _add_right_click_menu_and_grab(element)

            # -------------------------  TABLE placement element  ------------------------- #
            elif element_type == ELEM_TYPE_TABLE:
                element = element  # type: Table
                element.element_frame = frame = tk.Frame(tk_row_frame)
                element.table_frame = frame
                height = element.NumRows
                if element.Justification.startswith("l"):
                    anchor = tk.W
                elif element.Justification.startswith("r"):
                    anchor = tk.E
                else:
                    anchor = tk.CENTER
                column_widths = {}
                # create column width list
                for row in element.Values:
                    for i, col in enumerate(row):
                        col_width = min(len(str(col)), element.MaxColumnWidth)
                        try:
                            if col_width > column_widths[i]:
                                column_widths[i] = col_width
                        except Exception:
                            column_widths[i] = col_width

                if element.ColumnsToDisplay is None:
                    displaycolumns = (
                        element.ColumnHeadings
                        if element.ColumnHeadings is not None
                        else element.Values[0]
                    )
                else:
                    displaycolumns = []
                    for i, should_display in enumerate(element.ColumnsToDisplay):
                        if should_display:
                            if element.ColumnHeadings is not None:
                                displaycolumns.append(element.ColumnHeadings[i])
                            else:
                                displaycolumns.append(str(i))

                column_headings = (
                    element.ColumnHeadings
                    if element.ColumnHeadings is not None
                    else displaycolumns
                )
                if (
                    element.DisplayRowNumbers
                ):  # if display row number, tack on the numbers to front of columns
                    displaycolumns = [
                        element.RowHeaderText,
                    ] + displaycolumns
                    if column_headings is not None:
                        column_headings = [
                            element.RowHeaderText,
                        ] + element.ColumnHeadings
                    else:
                        column_headings = [
                            element.RowHeaderText,
                        ] + displaycolumns
                element.TKTreeview = element.Widget = ttk.Treeview(
                    frame,
                    columns=column_headings,
                    displaycolumns=displaycolumns,
                    show="headings",
                    height=height,
                    selectmode=element.SelectMode,
                )
                treeview = element.TKTreeview
                if element.DisplayRowNumbers:
                    treeview.heading(
                        element.RowHeaderText, text=element.RowHeaderText
                    )  # make a dummy heading
                    row_number_header_width = (
                        _string_width_in_pixels(
                            element.HeaderFont, element.RowHeaderText
                        )
                        + 10
                    )
                    row_number_width = (
                        _string_width_in_pixels(font, str(len(element.Values))) + 10
                    )
                    row_number_width = max(row_number_header_width, row_number_width)
                    treeview.column(
                        element.RowHeaderText,
                        width=row_number_width,
                        minwidth=10,
                        anchor=anchor,
                        stretch=0,
                    )

                headings = (
                    element.ColumnHeadings
                    if element.ColumnHeadings is not None
                    else element.Values[0]
                )
                for i, heading in enumerate(headings):
                    # heading = str(heading)
                    treeview.heading(heading, text=heading)
                    if element.AutoSizeColumns:
                        col_width = column_widths.get(
                            i, len(heading)
                        )  # in case more headings than there are columns of data
                        width = max(
                            col_width * _char_width_in_pixels(font),
                            len(heading) * _char_width_in_pixels(element.HeaderFont),
                        )
                    else:
                        try:
                            width = element.ColumnWidths[i] * _char_width_in_pixels(
                                font
                            )
                        except Exception:
                            width = element.DefaultColumnWidth * _char_width_in_pixels(
                                font
                            )
                    if element.cols_justification is not None:
                        try:
                            if element.cols_justification[i].startswith("l"):
                                col_anchor = tk.W
                            elif element.cols_justification[i].startswith("r"):
                                col_anchor = tk.E
                            elif element.cols_justification[i].startswith("c"):
                                col_anchor = tk.CENTER
                            else:
                                col_anchor = anchor

                        except (
                            Exception
                        ):  # likely didn't specify enough entries (must be one per col)
                            col_anchor = anchor
                    else:
                        col_anchor = anchor
                    treeview.column(
                        heading,
                        width=width,
                        minwidth=10,
                        anchor=col_anchor,
                        stretch=element.expand_x,
                    )
                # Insert values into the tree
                for i, value in enumerate(element.Values):
                    if element.DisplayRowNumbers:
                        value = [i + element.StartingRowNumber] + value
                    id = treeview.insert(
                        "", "end", text=value, iid=i + 1, values=value, tag=i
                    )
                    element.tree_ids.append(id)
                if element.AlternatingRowColor not in (
                    None,
                    COLOR_SYSTEM_DEFAULT,
                ):  # alternating colors
                    for row in range(0, len(element.Values), 2):
                        treeview.tag_configure(
                            row, background=element.AlternatingRowColor
                        )
                if element.RowColors is not None:  # individual row colors
                    for row_def in element.RowColors:
                        if len(row_def) == 2:  # only background is specified
                            treeview.tag_configure(row_def[0], background=row_def[1])
                        else:
                            treeview.tag_configure(
                                row_def[0], background=row_def[2], foreground=row_def[1]
                            )
                # ------ Do Styling of Colors -----
                # style_name = str(element.Key) + 'customtable.Treeview'
                style_name = _make_ttk_style_name(
                    ".Treeview", element, primary_style=True
                )
                element.table_ttk_style_name = style_name
                table_style = ttk.Style()
                element.ttk_style = table_style

                _change_ttk_theme(table_style, toplevel_form.TtkTheme)

                if (
                    element.BackgroundColor is not None
                    and element.BackgroundColor != COLOR_SYSTEM_DEFAULT
                ):
                    table_style.configure(
                        style_name,
                        background=element.BackgroundColor,
                        fieldbackground=element.BackgroundColor,
                    )
                    if element.SelectedRowColors[1] is not None:
                        table_style.map(
                            style_name,
                            background=_fixed_map(
                                table_style,
                                style_name,
                                "background",
                                element.SelectedRowColors,
                            ),
                        )
                if (
                    element.TextColor is not None
                    and element.TextColor != COLOR_SYSTEM_DEFAULT
                ):
                    table_style.configure(style_name, foreground=element.TextColor)
                    if element.SelectedRowColors[0] is not None:
                        table_style.map(
                            style_name,
                            foreground=_fixed_map(
                                table_style,
                                style_name,
                                "foreground",
                                element.SelectedRowColors,
                            ),
                        )
                if element.RowHeight is not None:
                    table_style.configure(style_name, rowheight=element.RowHeight)
                else:
                    table_style.configure(
                        style_name, rowheight=_char_height_in_pixels(font)
                    )
                if (
                    element.HeaderTextColor is not None
                    and element.HeaderTextColor != COLOR_SYSTEM_DEFAULT
                ):
                    table_style.configure(
                        style_name + ".Heading", foreground=element.HeaderTextColor
                    )
                if (
                    element.HeaderBackgroundColor is not None
                    and element.HeaderBackgroundColor != COLOR_SYSTEM_DEFAULT
                ):
                    table_style.configure(
                        style_name + ".Heading",
                        background=element.HeaderBackgroundColor,
                    )
                if element.HeaderFont is not None:
                    table_style.configure(
                        style_name + ".Heading", font=element.HeaderFont
                    )
                else:
                    table_style.configure(style_name + ".Heading", font=font)
                if element.HeaderBorderWidth is not None:
                    table_style.configure(
                        style_name + ".Heading", borderwidth=element.HeaderBorderWidth
                    )
                if element.HeaderRelief is not None:
                    table_style.configure(
                        style_name + ".Heading", relief=element.HeaderRelief
                    )
                table_style.configure(style_name, font=font)
                if element.BorderWidth is not None:
                    table_style.configure(style_name, borderwidth=element.BorderWidth)

                if element.HeaderBackgroundColor not in (
                    None,
                    COLOR_SYSTEM_DEFAULT,
                ) and element.HeaderTextColor not in (None, COLOR_SYSTEM_DEFAULT):
                    table_style.map(
                        style_name + ".Heading",
                        background=[
                            ("pressed", "!focus", element.HeaderBackgroundColor),
                            ("active", element.HeaderTextColor),
                        ],
                    )
                    table_style.map(
                        style_name + ".Heading",
                        foreground=[
                            ("pressed", "!focus", element.HeaderTextColor),
                            ("active", element.HeaderBackgroundColor),
                        ],
                    )

                treeview.configure(style=style_name)
                # scrollable_frame.pack(side=tk.LEFT,  padx=elementpad[0], pady=elementpad[1], expand=True, fill='both')
                if element.enable_click_events:
                    treeview.bind("<ButtonRelease-1>", element._table_clicked)
                if element.right_click_selects:
                    if running_mac():
                        treeview.bind("<Button-2>", element._table_clicked)
                    else:
                        treeview.bind("<Button-3>", element._table_clicked)
                treeview.bind("<<TreeviewSelect>>", element._treeview_selected)
                if element.BindReturnKey:
                    treeview.bind("<Return>", element._treeview_double_click)
                    treeview.bind("<Double-Button-1>", element._treeview_double_click)

                if not element.HideVerticalScroll:
                    _make_ttk_scrollbar(element, "v", toplevel_form)

                    element.Widget.configure(yscrollcommand=element.vsb.set)
                    element.vsb.pack(side=tk.RIGHT, fill="y")

                # Horizontal scrollbar
                if not element.VerticalScrollOnly:
                    # element.Widget.config(wrap='none')
                    _make_ttk_scrollbar(element, "h", toplevel_form)
                    element.hsb.pack(side=tk.BOTTOM, fill="x")
                    element.Widget.configure(xscrollcommand=element.hsb.set)

                if not element.HideVerticalScroll or not element.VerticalScrollOnly:
                    # Chr0nic
                    element.Widget.bind(
                        "<Enter>", lambda event, em=element: testMouseHook(em)
                    )
                    element.Widget.bind(
                        "<Leave>", lambda event, em=element: testMouseUnhook(em)
                    )

                # if not element.HideVerticalScroll:
                #     scrollbar = tk.Scrollbar(frame)
                #     scrollbar.pack(side=tk.RIGHT, fill='y')
                #     scrollbar.config(command=treeview.yview)
                #     treeview.configure(yscrollcommand=scrollbar.set)

                # if not element.VerticalScrollOnly:
                #     hscrollbar = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
                #     hscrollbar.pack(side=tk.BOTTOM, fill='x')
                #     hscrollbar.config(command=treeview.xview)
                #     treeview.configure(xscrollcommand=hscrollbar.set)

                expand, fill, row_should_expand, row_fill_direction = _add_expansion(
                    element, row_should_expand, row_fill_direction
                )
                element.TKTreeview.pack(
                    side=tk.LEFT, padx=0, pady=0, expand=expand, fill=fill
                )
                frame.pack(
                    side=tk.LEFT,
                    padx=elementpad[0],
                    pady=elementpad[1],
                    expand=expand,
                    fill=fill,
                )
                if not element.visible:
                    element._pack_forget_save_settings(
                        alternate_widget=element.element_frame
                    )  # seems like it should be the frame if following other elements conventions
                    # element.TKTreeview.pack_forget()
                if element.Tooltip is not None:
                    element.TooltipObject = ToolTip(
                        element.TKTreeview,
                        text=element.Tooltip,
                        timeout=DEFAULT_TOOLTIP_TIME,
                    )
                _add_right_click_menu_and_grab(element)

                if tclversion_detailed == "8.6.9" and ENABLE_TREEVIEW_869_PATCH:
                    # print('*** tk version 8.6.9 detected.... patching ttk treeview code ***')
                    table_style.map(
                        style_name,
                        foreground=_fixed_map(
                            table_style,
                            style_name,
                            "foreground",
                            element.SelectedRowColors,
                        ),
                        background=_fixed_map(
                            table_style,
                            style_name,
                            "background",
                            element.SelectedRowColors,
                        ),
                    )
            # -------------------------  Tree placement element  ------------------------- #
            elif element_type == ELEM_TYPE_TREE:
                element = element  # type: Tree
                element.element_frame = element_frame = tk.Frame(tk_row_frame)

                height = element.NumRows
                if element.Justification.startswith("l"):  # justification
                    anchor = tk.W
                elif element.Justification.startswith("r"):
                    anchor = tk.E
                else:
                    anchor = tk.CENTER

                if element.ColumnsToDisplay is None:  # Which cols to display
                    displaycolumns = element.ColumnHeadings
                else:
                    displaycolumns = []
                    for i, should_display in enumerate(element.ColumnsToDisplay):
                        if should_display:
                            displaycolumns.append(element.ColumnHeadings[i])
                column_headings = element.ColumnHeadings
                # ------------- GET THE TREEVIEW WIDGET -------------
                element.TKTreeview = element.Widget = ttk.Treeview(
                    element_frame,
                    columns=column_headings,
                    displaycolumns=displaycolumns,
                    show="tree headings" if column_headings is not None else "tree",
                    height=height,
                    selectmode=element.SelectMode,
                )
                treeview = element.TKTreeview
                max_widths = {}
                for key, node in element.TreeData.tree_dict.items():
                    for i, value in enumerate(node.values):
                        max_width = max_widths.get(i, 0)
                        if len(str(value)) > max_width:
                            max_widths[i] = len(str(value))

                if element.ColumnHeadings is not None:
                    for i, heading in enumerate(
                        element.ColumnHeadings
                    ):  # Configure cols + headings
                        treeview.heading(heading, text=heading)
                        if element.AutoSizeColumns:
                            max_width = max_widths.get(i, 0)
                            max_width = max(max_width, len(heading))
                            width = min(element.MaxColumnWidth, max_width + 1)
                        else:
                            try:
                                width = element.ColumnWidths[i]
                            except Exception:
                                width = element.DefaultColumnWidth
                        treeview.column(
                            heading,
                            width=width * _char_width_in_pixels(font) + 10,
                            anchor=anchor,
                        )

                def add_treeview_data(node):
                    """

                    :param node:
                    :type node:

                    """
                    if node.key != "":
                        if node.icon:
                            if node.icon not in element.image_dict:
                                if type(node.icon) is bytes:
                                    photo = tk.PhotoImage(data=node.icon)
                                else:
                                    photo = tk.PhotoImage(file=node.icon)
                                element.image_dict[node.icon] = photo
                            else:
                                photo = element.image_dict.get(node.icon)

                            node.photo = photo
                            try:
                                id = treeview.insert(
                                    element.KeyToID[node.parent],
                                    "end",
                                    iid=None,
                                    text=node.text,
                                    values=node.values,
                                    open=element.ShowExpanded,
                                    image=node.photo,
                                )
                                element.IdToKey[id] = node.key
                                element.KeyToID[node.key] = id
                            except Exception as e:
                                print("Error inserting image into tree", e)
                        else:
                            id = treeview.insert(
                                element.KeyToID[node.parent],
                                "end",
                                iid=None,
                                text=node.text,
                                values=node.values,
                                open=element.ShowExpanded,
                            )
                            element.IdToKey[id] = node.key
                            element.KeyToID[node.key] = id

                    for node in node.children:
                        add_treeview_data(node)

                add_treeview_data(element.TreeData.root_node)
                treeview.column(
                    "#0",
                    width=element.Col0Width * _char_width_in_pixels(font),
                    anchor=tk.W,
                )
                treeview.heading("#0", text=element.col0_heading)

                # ----- configure colors -----
                # style_name = str(element.Key) + '.Treeview'
                style_name = _make_ttk_style_name(
                    ".Treeview", element, primary_style=True
                )
                tree_style = ttk.Style()
                _change_ttk_theme(tree_style, toplevel_form.TtkTheme)

                if (
                    element.BackgroundColor is not None
                    and element.BackgroundColor != COLOR_SYSTEM_DEFAULT
                ):
                    tree_style.configure(
                        style_name,
                        background=element.BackgroundColor,
                        fieldbackground=element.BackgroundColor,
                    )
                    if element.SelectedRowColors[1] is not None:
                        tree_style.map(
                            style_name,
                            background=_fixed_map(
                                tree_style,
                                style_name,
                                "background",
                                element.SelectedRowColors,
                            ),
                        )
                if (
                    element.TextColor is not None
                    and element.TextColor != COLOR_SYSTEM_DEFAULT
                ):
                    tree_style.configure(style_name, foreground=element.TextColor)
                    if element.SelectedRowColors[0] is not None:
                        tree_style.map(
                            style_name,
                            foreground=_fixed_map(
                                tree_style,
                                style_name,
                                "foreground",
                                element.SelectedRowColors,
                            ),
                        )
                if (
                    element.HeaderTextColor is not None
                    and element.HeaderTextColor != COLOR_SYSTEM_DEFAULT
                ):
                    tree_style.configure(
                        style_name + ".Heading", foreground=element.HeaderTextColor
                    )
                if (
                    element.HeaderBackgroundColor is not None
                    and element.HeaderBackgroundColor != COLOR_SYSTEM_DEFAULT
                ):
                    tree_style.configure(
                        style_name + ".Heading",
                        background=element.HeaderBackgroundColor,
                    )
                if element.HeaderFont is not None:
                    tree_style.configure(
                        style_name + ".Heading", font=element.HeaderFont
                    )
                else:
                    tree_style.configure(style_name + ".Heading", font=font)
                if element.HeaderBorderWidth is not None:
                    tree_style.configure(
                        style_name + ".Heading", borderwidth=element.HeaderBorderWidth
                    )
                if element.HeaderRelief is not None:
                    tree_style.configure(
                        style_name + ".Heading", relief=element.HeaderRelief
                    )
                tree_style.configure(style_name, font=font)
                if element.RowHeight:
                    tree_style.configure(style_name, rowheight=element.RowHeight)
                else:
                    tree_style.configure(
                        style_name, rowheight=_char_height_in_pixels(font)
                    )
                if element.BorderWidth is not None:
                    tree_style.configure(style_name, borderwidth=element.BorderWidth)

                treeview.configure(
                    style=style_name
                )  # IMPORTANT! Be sure and set the style name for this widget

                if not element.HideVerticalScroll:
                    _make_ttk_scrollbar(element, "v", toplevel_form)

                    element.Widget.configure(yscrollcommand=element.vsb.set)
                    element.vsb.pack(side=tk.RIGHT, fill="y")

                # Horizontal scrollbar
                if not element.VerticalScrollOnly:
                    # element.Widget.config(wrap='none')
                    _make_ttk_scrollbar(element, "h", toplevel_form)
                    element.hsb.pack(side=tk.BOTTOM, fill="x")
                    element.Widget.configure(xscrollcommand=element.hsb.set)

                if not element.HideVerticalScroll or not element.VerticalScrollOnly:
                    # Chr0nic
                    element.Widget.bind(
                        "<Enter>", lambda event, em=element: testMouseHook(em)
                    )
                    element.Widget.bind(
                        "<Leave>", lambda event, em=element: testMouseUnhook(em)
                    )

                # Horizontal scrollbar
                # if not element.VerticalScrollOnly:
                #     element.TKText.config(wrap='none')
                #     _make_ttk_scrollbar(element, 'h')
                #     element.hsb.pack(side=tk.BOTTOM, fill='x')
                #     element.Widget.configure(xscrollcommand=element.hsb.set)

                # if not element.HideVerticalScroll or not element.VerticalScrollOnly:
                # Chr0nic
                # element.Widget.bind("<Enter>", lambda event, em=element: testMouseHook(em))
                # element.Widget.bind("<Leave>", lambda event, em=element: testMouseUnhook(em))

                # element.scrollbar = scrollbar = tk.Scrollbar(element_frame)
                # scrollbar.pack(side=tk.RIGHT, fill='y')
                # scrollbar.config(command=treeview.yview)
                # treeview.configure(yscrollcommand=scrollbar.set)

                expand, fill, row_should_expand, row_fill_direction = _add_expansion(
                    element, row_should_expand, row_fill_direction
                )
                element.TKTreeview.pack(
                    side=tk.LEFT, padx=0, pady=0, expand=expand, fill=fill
                )
                element_frame.pack(
                    side=tk.LEFT,
                    padx=elementpad[0],
                    pady=elementpad[1],
                    expand=expand,
                    fill=fill,
                )
                if not element.visible:
                    element._pack_forget_save_settings(
                        alternate_widget=element.element_frame
                    )  # seems like it should be the frame if following other elements conventions
                    # element.TKTreeview.pack_forget()
                treeview.bind("<<TreeviewSelect>>", element._treeview_selected)
                if element.Tooltip is not None:  # tooltip
                    element.TooltipObject = ToolTip(
                        element.TKTreeview,
                        text=element.Tooltip,
                        timeout=DEFAULT_TOOLTIP_TIME,
                    )
                _add_right_click_menu_and_grab(element)

                if tclversion_detailed == "8.6.9" and ENABLE_TREEVIEW_869_PATCH:
                    # print('*** tk version 8.6.9 detected.... patching ttk treeview code ***')
                    tree_style.map(
                        style_name,
                        foreground=_fixed_map(
                            tree_style,
                            style_name,
                            "foreground",
                            element.SelectedRowColors,
                        ),
                        background=_fixed_map(
                            tree_style,
                            style_name,
                            "background",
                            element.SelectedRowColors,
                        ),
                    )

            # -------------------------  Separator placement element  ------------------------- #
            elif element_type == ELEM_TYPE_SEPARATOR:
                element = element  # type: VerticalSeparator
                # style_name = str(element.Key) + "Line.TSeparator"
                style_name = _make_ttk_style_name(
                    ".Line.TSeparator", element, primary_style=True
                )
                style = ttk.Style()

                _change_ttk_theme(style, toplevel_form.TtkTheme)

                if element.color not in (None, COLOR_SYSTEM_DEFAULT):
                    style.configure(style_name, background=element.color)
                separator = element.Widget = ttk.Separator(
                    tk_row_frame,
                    orient=element.Orientation,
                )

                expand, fill, row_should_expand, row_fill_direction = _add_expansion(
                    element, row_should_expand, row_fill_direction
                )

                if element.Orientation.startswith("h"):
                    separator.pack(
                        side=tk.LEFT,
                        padx=elementpad[0],
                        pady=elementpad[1],
                        fill=tk.X,
                        expand=True,
                    )
                else:
                    separator.pack(
                        side=tk.LEFT,
                        padx=elementpad[0],
                        pady=elementpad[1],
                        fill=tk.Y,
                        expand=False,
                    )
                element.Widget.configure(
                    style=style_name
                )  # IMPORTANT!  Apply the style
            # -------------------------  SizeGrip placement element  ------------------------- #
            elif element_type == ELEM_TYPE_SIZEGRIP:
                element = element  # type: Sizegrip
                style_name = "Sizegrip.TSizegrip"
                style = ttk.Style()

                _change_ttk_theme(style, toplevel_form.TtkTheme)

                size_grip = element.Widget = ttk.Sizegrip(tk_row_frame)
                toplevel_form.sizegrip_widget = size_grip
                # if no size is specified, then use the background color for the window
                if element.BackgroundColor != COLOR_SYSTEM_DEFAULT:
                    style.configure(style_name, background=element.BackgroundColor)
                else:
                    style.configure(style_name, background=toplevel_form.TKroot["bg"])
                size_grip.configure(style=style_name)

                size_grip.pack(
                    side=tk.BOTTOM,
                    anchor="se",
                    padx=elementpad[0],
                    pady=elementpad[1],
                    fill=tk.X,
                    expand=True,
                )
                # tricky part of sizegrip... it shouldn't cause the row to expand, but should expand and should add X axis if
                # not already filling in that direction.  Otherwise, leaves things alone!
                # row_should_expand = True
                row_fill_direction = (
                    tk.BOTH if row_fill_direction in (tk.Y, tk.BOTH) else tk.X
                )
            # -------------------------  StatusBar placement element  ------------------------- #
            elif element_type == ELEM_TYPE_STATUSBAR:
                # auto_size_text = element.AutoSizeText
                display_text = element.DisplayText  # text to display
                if not auto_size_text:
                    width, height = element_size
                else:
                    lines = display_text.split("\n")
                    max_line_len = max([len(l) for l in lines])
                    num_lines = len(lines)
                    if (
                        max_line_len > element_size[0]
                    ):  # if text exceeds element size, the will have to wrap
                        width = element_size[0]
                    else:
                        width = max_line_len
                    height = num_lines
                # ---===--- LABEL widget create and place --- #
                stringvar = tk.StringVar()
                element.TKStringVar = stringvar
                stringvar.set(display_text)
                if auto_size_text:
                    width = 0
                if element.Justification is not None:
                    justification = element.Justification
                elif toplevel_form.TextJustification is not None:
                    justification = toplevel_form.TextJustification
                else:
                    justification = DEFAULT_TEXT_JUSTIFICATION
                justify = (
                    tk.LEFT
                    if justification.startswith("l")
                    else tk.CENTER
                    if justification.startswith("c")
                    else tk.RIGHT
                )
                anchor = (
                    tk.NW
                    if justification.startswith("l")
                    else tk.N
                    if justification.startswith("c")
                    else tk.NE
                )
                # tktext_label = tk.Label(tk_row_frame, textvariable=stringvar, width=width, height=height,
                #                         justify=justify, bd=border_depth, font=font)
                tktext_label = element.Widget = tk.Label(
                    tk_row_frame,
                    textvariable=stringvar,
                    width=width,
                    height=height,
                    justify=justify,
                    bd=border_depth,
                    font=font,
                )
                # Set wrap-length for text (in PIXELS) == PAIN IN THE ASS
                wraplen = (
                    tktext_label.winfo_reqwidth() + 40
                )  # width of widget in Pixels
                if not auto_size_text and height == 1:
                    wraplen = 0
                # print("wraplen, width, height", wraplen, width, height)
                tktext_label.configure(
                    anchor=anchor, wraplen=wraplen
                )  # set wrap to width of widget
                if element.Relief is not None:
                    tktext_label.configure(relief=element.Relief)
                if (
                    element.BackgroundColor is not None
                    and element.BackgroundColor != COLOR_SYSTEM_DEFAULT
                ):
                    tktext_label.configure(background=element.BackgroundColor)
                if (
                    element.TextColor != COLOR_SYSTEM_DEFAULT
                    and element.TextColor is not None
                ):
                    tktext_label.configure(fg=element.TextColor)
                tktext_label.pack(
                    side=tk.LEFT,
                    padx=elementpad[0],
                    pady=elementpad[1],
                    fill=tk.X,
                    expand=True,
                )
                row_fill_direction = tk.X
                if not element.visible:
                    element._pack_forget_save_settings()
                    # tktext_label.pack_forget()
                element.TKText = tktext_label
                if element.ClickSubmits:
                    tktext_label.bind("<Button-1>", element._TextClickedHandler)
                if element.Tooltip is not None:
                    element.TooltipObject = ToolTip(
                        element.TKText,
                        text=element.Tooltip,
                        timeout=DEFAULT_TOOLTIP_TIME,
                    )
                _add_right_click_menu_and_grab(element)

        # ............................DONE WITH ROW pack the row of widgets ..........................#
        # done with row, pack the row of widgets
        # tk_row_frame.grid(row=row_num+2, sticky=tk.NW, padx=DEFAULT_MARGINS[0])

        anchor = "nw"

        if row_justify.lower().startswith("c"):
            anchor = "n"
            side = tk.LEFT
        elif row_justify.lower().startswith("r"):
            anchor = "ne"
            side = tk.RIGHT
        elif row_justify.lower().startswith("l"):
            anchor = "nw"
            side = tk.LEFT


        tk_row_frame.pack(
            side=tk.TOP,
            anchor=anchor,
            padx=0,
            pady=0,
            expand=row_should_expand,
            fill=row_fill_direction,
        )
        if (
            form.BackgroundColor is not None
            and form.BackgroundColor != COLOR_SYSTEM_DEFAULT
        ):
            tk_row_frame.configure(background=form.BackgroundColor)

    return






def _get_hidden_master_root():
    """
    Creates the hidden master root window.  This window is never visible and represents the overall "application"
    """

    # if one is already made, then skip making another
    if Window.hidden_master_root is None:
        Window._IncrementOpenCount()
        Window.hidden_master_root = tk.Tk()
        Window.hidden_master_root.attributes(
            "-alpha", 0
        )  # HIDE this window really really really
        # if not running_mac():
        try:
            Window.hidden_master_root.wm_overrideredirect(True)
        except Exception as e:
            if not running_mac():
                print(
                    "* Error performing wm_overrideredirect while hiding the hidden master root*",
                    e,
                )
        Window.hidden_master_root.withdraw()
    return Window.hidden_master_root


def _no_titlebar_setup(window):
    """
    Does the operations required to turn off the titlebar for the window.
    The Raspberry Pi required the settings to be make after the window's creation.
    Calling twice seems to have had better overall results so that's what's currently done.
    The MAC has been the problem with this feature.  It's been a chronic problem on the Mac.
    :param window:          window to turn off the titlebar if indicated in the settings
    :type window:           Window
    """
    try:
        if window.NoTitleBar:
            if running_linux():
                # window.TKroot.wm_attributes("-type", 'splash')
                window.TKroot.wm_attributes("-type", "dock")
            else:
                window.TKroot.wm_overrideredirect(True)
                # Special case for Mac. Need to clear flag again if not tkinter version 8.6.10+
                # Previously restricted patch to only certain tkinter versions. Now use the patch setting exclusively regardless of tk ver
                # if running_mac() and ENABLE_MAC_NOTITLEBAR_PATCH and (sum([int(i) for i in tclversion_detailed.split('.')]) < 24):
                # if running_mac() and ENABLE_MAC_NOTITLEBAR_PATCH:
                if _mac_should_apply_notitlebar_patch():
                    print("* Applying Mac no_titlebar patch *")
                    window.TKroot.wm_overrideredirect(False)
    except Exception as e:
        warnings.warn("** Problem setting no titlebar {} **".format(e), UserWarning)


def _convert_window_to_tk(window):
    """

    :type window: (Window)

    """
    master = window.TKroot
    master.title(window.Title)
    InitializeResults(window)

    PackFormIntoFrame(window, master, window)

    window.TKroot.configure(padx=window.Margins[0], pady=window.Margins[1])

    # ....................................... DONE creating and laying out window ..........................#
    if window._Size != (None, None):
        master.geometry("%sx%s" % (window._Size[0], window._Size[1]))
    screen_width = (
        master.winfo_screenwidth()
    )  # get window info to move to middle of screen
    screen_height = master.winfo_screenheight()
    if window.Location is not None:
        if window.Location != (None, None):
            x, y = window.Location
        elif DEFAULT_WINDOW_LOCATION != (None, None):
            x, y = DEFAULT_WINDOW_LOCATION
        else:
            master.update_idletasks()  # don't forget to do updates or values are bad
            win_width = master.winfo_width()
            win_height = master.winfo_height()
            x = screen_width / 2 - win_width / 2
            y = screen_height / 2 - win_height / 2
            if y + win_height > screen_height:
                y = screen_height - win_height
            if x + win_width > screen_width:
                x = screen_width - win_width

        if window.RelativeLoction != (None, None):
            x += window.RelativeLoction[0]
            y += window.RelativeLoction[1]

        move_string = "+%i+%i" % (int(x), int(y))
        master.geometry(move_string)
        window.config_last_location = (int(x), (int(y)))
        window.TKroot.x = int(x)
        window.TKroot.y = int(y)
        window.starting_window_position = (int(x), (int(y)))
        master.update_idletasks()  # don't forget
        master.geometry(move_string)
        master.update_idletasks()  # don't forget
    else:
        master.update_idletasks()
        x, y = int(master.winfo_x()), int(master.winfo_y())
        window.config_last_location = x, y
        window.TKroot.x = x
        window.TKroot.y = y
        window.starting_window_position = x, y
    _no_titlebar_setup(window)

    return

def _set_icon_for_tkinter_window(root, icon=None, pngbase64=None):
    """
    At the moment, this function is only used by the get_filename or folder with the no_window option set.
    Changes the icon that is shown on the title bar and on the task bar.
    NOTE - The file type is IMPORTANT and depends on the OS!
    Can pass in:
    * filename which must be a .ICO icon file for windows, PNG file for Linux
    * bytes object
    * BASE64 encoded file held in a variable

    :param root:      The window being modified
    :type root:       (tk.Tk or tk.TopLevel)
    :param icon:      Filename or bytes object
    :type icon:       (str | bytes)
    :param pngbase64: Base64 encoded image
    :type pngbase64:  (bytes)
    """

    if type(icon) is bytes or pngbase64 is not None:
        wicon = tkinter.PhotoImage(data=icon if icon is not None else pngbase64)
        try:
            root.tk.call("wm", "iconphoto", root._w, wicon)
        except Exception:
            wicon = tkinter.PhotoImage(data=DEFAULT_BASE64_ICON)
            try:
                root.tk.call("wm", "iconphoto", root._w, wicon)
            except Exception as e:
                print("Set icon exception", e)
                pass
        return

    wicon = icon
    try:
        root.iconbitmap(icon)
    except Exception as e:
        try:
            wicon = tkinter.PhotoImage(file=icon)
            root.tk.call("wm", "iconphoto", root._w, wicon)
        except Exception as e:
            try:
                wicon = tkinter.PhotoImage(data=DEFAULT_BASE64_ICON)
                try:
                    root.tk.call("wm", "iconphoto", root._w, wicon)
                except Exception as e:
                    print("Set icon exception", e)
                    pass
            except Exception:
                print("Set icon exception", e)
                pass





def easy_print(
    *args,
    size=(None, None),
    end=None,
    sep=None,
    location=(None, None),
    relative_location=(None, None),
    font=None,
    no_titlebar=False,
    no_button=False,
    grab_anywhere=False,
    keep_on_top=None,
    do_not_reroute_stdout=True,
    echo_stdout=False,
    text_color=None,
    background_color=None,
    colors=None,
    c=None,
    erase_all=False,
    resizable=True,
    blocking=None,
    wait=None,
):
    """
    Works like a "print" statement but with windowing options.  Routes output to the "Debug Window"

    In addition to the normal text and background colors, you can use a "colors" tuple/string
    The "colors" or "c" parameter defines both the text and background in a single parm.
    It can be a tuple or a single single. Both text and background colors need to be specified
    colors -(str, str) or str.  A combined text/background color definition in a single parameter
    c - (str, str) - Colors tuple has format (foreground, backgrouned)
    c - str - can also be a string of the format "foreground on background"  ("white on red")

    :param size:                  (w,h) w=characters-wide, h=rows-high
    :type size:                   (int, int)
    :param end:                   end character
    :type end:                    (str)
    :param sep:                   separator character
    :type sep:                    (str)
    :param location:              Location of upper left corner of the window
    :type location:               (int, int)
    :param relative_location:     (x,y) location relative to the default location of the window, in pixels. Normally the window centers.  This location is relative to the location the window would be created. Note they can be negative.
    :type relative_location:      (int, int)
    :param font:                  specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:                   (str or (str, int[, str]) or None)
    :param no_titlebar:           If True no titlebar will be shown
    :type no_titlebar:            (bool)
    :param no_button:             don't show button
    :type no_button:              (bool)
    :param grab_anywhere:         If True: can grab anywhere to move the window (Default = False)
    :type grab_anywhere:          (bool)
    :param background_color:      color of background
    :type background_color:       (str)
    :param text_color:            color of the text
    :type text_color:             (str)
    :param keep_on_top:           If True the window will remain above all current windows
    :type keep_on_top:            (bool)
    :param location:              Location of upper left corner of the window
    :type location:               (int, int)
    :param do_not_reroute_stdout: do not reroute stdout and stderr. If False, both stdout and stderr will reroute to here
    :type do_not_reroute_stdout:  (bool)
    :param echo_stdout:           If True stdout is sent to both the console and the debug window
    :type echo_stdout:            (bool)
    :param colors:                Either a tuple or a string that has both the text and background colors
    :type colors:                 (str) or (str, str)
    :param c:                     Either a tuple or a string that has both the text and background colors
    :type c:                      (str) or (str, str)
    :param resizable:             if True, the user can resize the debug window. Default is True
    :type resizable:              (bool)
    :param erase_all:             If True when erase the output before printing
    :type erase_all:              (bool)
    :param blocking:              if True, makes the window block instead of returning immediately. The "Quit" button changers to "More"
    :type blocking:               (bool | None)
    :param wait:                  Same as the "blocking" parm. It's an alias.  if True, makes the window block instead of returning immediately. The "Quit" button changes to "Click to Continue..."
    :type wait:                   (bool | None)
    :return:
    :rtype:
    """

    blocking = blocking or wait
    if _DebugWin.debug_window is None:
        _DebugWin.debug_window = _DebugWin(
            size=size,
            location=location,
            relative_location=relative_location,
            font=font,
            no_titlebar=no_titlebar,
            no_button=no_button,
            grab_anywhere=grab_anywhere,
            keep_on_top=keep_on_top,
            do_not_reroute_stdout=do_not_reroute_stdout,
            echo_stdout=echo_stdout,
            resizable=resizable,
            blocking=blocking,
        )
    txt_color, bg_color = _parse_colors_parm(c or colors)
    _DebugWin.debug_window.Print(
        *args,
        end=end,
        sep=sep,
        text_color=text_color or txt_color,
        background_color=background_color or bg_color,
        erase_all=erase_all,
        font=font,
        blocking=blocking,
    )


def easy_print_close():
    """
    Close a previously opened EasyPrint window

    :return:
    :rtype:
    """
    if _DebugWin.debug_window is not None:
        _DebugWin.debug_window.Close()
        _DebugWin.debug_window = None


#                            d8b          888
#                            Y8P          888
#                                         888
#   .d8888b 88888b.  888d888 888 88888b.  888888
#  d88P"    888 "88b 888P"   888 888 "88b 888
#  888      888  888 888     888 888  888 888
#  Y88b.    888 d88P 888     888 888  888 Y88b.
#   "Y8888P 88888P"  888     888 888  888  "Y888
#           888
#           888
#           888




def cprint_set_output_destination(window, multiline_key:str):
    """
    Sets up the color print (cprint) output destination
    :param window:        The window that the cprint call will route the output to
    :type window:         (Window)
    :param multiline_key: Key for the Multiline Element where output will be sent
    :type multiline_key:  (Any)
    :return:              None
    :rtype:               None
    """

    global CPRINT_DESTINATION_WINDOW, CPRINT_DESTINATION_MULTILINE_ELMENT_KEY

    CPRINT_DESTINATION_WINDOW = window
    CPRINT_DESTINATION_MULTILINE_ELMENT_KEY = multiline_key


def cprint(
    *args,
    end=None,
    sep=" ",
    text_color=None,
    font=None,
    t=None,
    background_color=None,
    b=None,
    colors=None,
    c=None,
    window=None,
    key=None,
    justification=None,
    autoscroll=True,
    erase_all=False,
):
    """
    Color print to a multiline element in a window of your choice.
    Must have EITHER called cprint_set_output_destination prior to making this call so that the
    window and element key can be saved and used here to route the output, OR used the window
    and key parameters to the cprint function to specicy these items.

    args is a variable number of things you want to print.

    end - The end char to use just like print uses
    sep - The separation character like print uses
    text_color - The color of the text
            key - overrides the previously defined Multiline key
    window - overrides the previously defined window to output to
    background_color - The color of the background
    colors -(str, str) or str.  A combined text/background color definition in a single parameter

    There are also "aliases" for text_color, background_color and colors (t, b, c)
     t - An alias for color of the text (makes for shorter calls)
    b - An alias for the background_color parameter
    c - (str, str) - "shorthand" way of specifying color. (foreground, backgrouned)
    c - str - can also be a string of the format "foreground on background"  ("white on red")

    With the aliases it's possible to write the same print but in more compact ways:
    cprint('This will print white text on red background', c=('white', 'red'))
    cprint('This will print white text on red background', c='white on red')
    cprint('This will print white text on red background', text_color='white', background_color='red')
    cprint('This will print white text on red background', t='white', b='red')

    :param text_color:       Color of the text
    :type text_color:        (str)
    :param font:             specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike for the value being updated
    :type font:              (str or (str, int[, str]) or None)
    :param background_color: The background color of the line
    :type background_color:  (str)
    :param colors:           Either a tuple or a string that has both the text and background colors "text on background" or just the text color
    :type colors:            (str) or (str, str)
    :param t:                Color of the text
    :type t:                 (str)
    :param b:                The background color of the line
    :type b:                 (str)
    :param c:                Either a tuple or a string.  Same as the color parm
    :type c:                 (str) or (str, str)
    :param end:              end character
    :type end:               (str)
    :param sep:              separator character
    :type sep:               (str)
    :param key:              key of multiline to output to (if you want to override the one previously set)
    :type key:               (Any)
    :param window:           Window containing the multiline to output to (if you want to override the one previously set)
    :type window:            (Window)
    :param justification:    text justification. left, right, center. Can use single characters l, r, c. Sets only for this value, not entire element
    :type justification:     (str)
    :param autoscroll:       If True the contents of the element will automatically scroll as more data added to the end
    :type autoscroll:        (bool)
    :param erase_all         If True the contents of the element will be cleared before printing happens
    :type erase_all          (bool)
    """

    destination_key = CPRINT_DESTINATION_MULTILINE_ELMENT_KEY if key is None else key
    destination_window = window or CPRINT_DESTINATION_WINDOW

    if (destination_window is None and window is None) or (
        destination_key is None and key is None
    ):
        print(
            "** Warning ** Attempting to perform a cprint without a valid window & key",
            "Will instead print on Console",
            "You can specify window and key in this cprint call, or set ahead of time using cprint_set_output_destination",
        )
        print(*args)
        return

    kw_text_color = text_color or t
    kw_background_color = background_color or b
    dual_color = colors or c
    try:
        if isinstance(dual_color, tuple):
            kw_text_color = dual_color[0]
            kw_background_color = dual_color[1]
        elif isinstance(dual_color, str):
            if (
                " on " in dual_color
            ):  # if has "on" in the string, then have both text and background
                kw_text_color = dual_color.split(" on ")[0]
                kw_background_color = dual_color.split(" on ")[1]
            else:  # if no "on" then assume the color string is just the text color
                kw_text_color = dual_color
    except Exception as e:
        print("* cprint warning * you messed up with color formatting", e)

    mline = destination_window.find_element(destination_key, silent_on_error=True)  # type: Multiline
    try:
        # mline = destination_window[destination_key]     # type: Multiline
        if erase_all:
            mline.update("")
        if end is None:
            mline.print(
                *args,
                text_color=kw_text_color,
                background_color=kw_background_color,
                end="",
                sep=sep,
                justification=justification,
                font=font,
                autoscroll=autoscroll,
            )
            mline.print("", justification=justification, autoscroll=autoscroll)
        else:
            mline.print(
                *args,
                text_color=kw_text_color,
                background_color=kw_background_color,
                end=end,
                sep=sep,
                justification=justification,
                font=font,
                autoscroll=autoscroll,
            )
    except Exception as e:
        print(
            "** cprint error trying to print to the multiline. Printing to console instead **",
            e,
        )
        print(*args, end=end, sep=sep)


# ------------------------------------------------------------------------------------------------ #
# A print-like call that can be used to output to a multiline element as if it's an Output element #
# ------------------------------------------------------------------------------------------------ #


def _print_to_element(
    multiline_element,
    *args,
    end=None,
    sep=None,
    text_color=None,
    background_color=None,
    autoscroll=None,
    justification=None,
    font=None,
):
    """
    Print like Python normally prints except route the output to a multiline element and also add colors if desired

    :param multiline_element: The multiline element to be output to
    :type multiline_element:  (Multiline)
    :param args:              The arguments to print
    :type args:               List[Any]
    :param end:               The end char to use just like print uses
    :type end:                (str)
    :param sep:               The separation character like print uses
    :type sep:                (str)
    :param text_color:        color of the text
    :type text_color:         (str)
    :param background_color:  The background color of the line
    :type background_color:   (str)
    :param autoscroll:        If True (the default), the element will scroll to bottom after updating
    :type autoscroll:         (bool)
    :param font:              specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike for the value being updated
    :type font:               str | (str, int)
    """
    end_str = str(end) if end is not None else "\n"
    sep_str = str(sep) if sep is not None else " "

    outstring = ""
    num_args = len(args)
    for i, arg in enumerate(args):
        outstring += str(arg)
        if i != num_args - 1:
            outstring += sep_str
    outstring += end_str

    multiline_element.update(
        outstring,
        append=True,
        text_color_for_value=text_color,
        background_color_for_value=background_color,
        autoscroll=autoscroll,
        justification=justification,
        font_for_value=font,
    )

    try:  # if the element is set to autorefresh, then refresh the parent window
        if multiline_element.AutoRefresh:
            multiline_element.ParentForm.refresh()
    except Exception:
        pass





# ============================== set_global_icon ====#
# Sets the icon to be used by default                #
# ===================================================#
def set_global_icon(icon):
    """
    Sets the icon which will be used any time a window is created if an icon is not provided when the
    window is created.

    :param icon: Either a Base64 byte string or a filename
    :type icon:  bytes | str
    """

    Window._user_defined_icon = icon




def clipboard_set(new_value:str):
    """
    Sets the clipboard to a specific value.
    IMPORTANT NOTE - Your PySimpleGUI application needs to remain running until you've pasted
    your clipboard. This is a tkinter limitation.  A workaround was found for Windows, but you still
    need to stay running for Linux systems.

    :param new_value: value to set the clipboard to. Will be converted to a string
    :type new_value:  (str | bytes)
    """
    root = _get_hidden_master_root()
    root.clipboard_clear()
    root.clipboard_append(str(new_value))
    root.update()


def clipboard_get():
    """
    Gets the clipboard current value.

    :return: The current value of the clipboard
    :rtype:  (str)
    """
    root = _get_hidden_master_root()

    try:
        value = root.clipboard_get()
    except Exception:
        value = ""
    root.update()
    return value






def _long_func_thread(window, end_key:str, original_func):
    """
    Used to run long operations on the user's behalf. Called by the window object

    :param window:        The window that will get the event
    :type window:         (Window)
    :param end_key:       The event that will be sent when function returns. If None then no event will be sent when exiting thread
    :type end_key:        (Any|None)
    :param original_func: The user's function that is called. Can be a function with no arguments or a lambda experession
    :type original_func:  (Any)
    """

    return_value = original_func()
    if end_key is not None:
        window.write_event_value(end_key, return_value)


def _exit_mainloop(exiting_window):
    if (
        exiting_window == Window._window_running_mainloop
        or Window._root_running_mainloop == Window.hidden_master_root
    ):
        Window._window_that_exited = exiting_window
        if Window._root_running_mainloop is not None:
            Window._root_running_mainloop.quit()
        # print('** Exited window mainloop **')



def _process_thread(*args):
    global __shell_process__

    # start running the command with arugments
    try:
        __shell_process__ = subprocess.run(args, shell=True, stdout=subprocess.PIPE)
    except Exception:
        print("Exception running process args = {}".format(args))
        __shell_process__ = None





def fill_form_with_values(window, values_dict:dict):
    """
    Fills a window with values provided in a values dictionary { element_key : new_value }

    :param window:      The window object to fill
    :type window:       (Window)
    :param values_dict: A dictionary with element keys as key and value is values parm for Update call
    :type values_dict:  (Dict[Any, Any])
    :return:            None
    :rtype:             None
    """

    for element_key in values_dict:
        try:
            window.AllKeysDict[element_key].Update(values_dict[element_key])
        except Exception:
            print(
                "Problem filling form. Perhaps bad key?  This is a suspected bad key: {}".format(
                    element_key
                )
            )





def AddToReturnDictionary(form, element, value):
    form.ReturnValuesDictionary[element.Key] = value



def AddToReturnList(form, value):
    form.ReturnValuesList.append(value)


# ----------------------------------------------------------------------------#
# -------  FUNCTION InitializeResults.  Sets up form results matrix  --------#
def InitializeResults(form):
    _BuildResults(form, True, form)


# =====  Radio Button RadVar encoding and decoding =====#
# =====  The value is simply the row * 1000 + col  =====#
def DecodeRadioRowCol(RadValue):
    container = RadValue // 100000
    row = RadValue // 1000
    col = RadValue % 1000
    return container, row, col


def EncodeRadioRowCol(container, row, col):
    RadValue = container * 100000 + row * 1000 + col
    return RadValue


# -------  FUNCTION BuildResults.  Form exiting so build the results to pass back  ------- #
# format of return values is
# (Button Pressed, input_values)
def _BuildResults(form, initialize_only, top_level_form):
    # Results for elements are:
    #   TEXT - Nothing
    #   INPUT - Read value from TK
    #   Button - Button Text and position as a Tuple

    # Get the initialized results so we don't have to rebuild
    # form.DictionaryKeyCounter = 0
    form.ReturnValuesDictionary = {}
    form.ReturnValuesList = []
    _BuildResultsForSubform(form, initialize_only, top_level_form)
    if not top_level_form.LastButtonClickedWasRealtime:
        top_level_form.LastButtonClicked = None
    return form.ReturnValues


def _BuildResultsForSubform(form, initialize_only, top_level_form):
    event = top_level_form.LastButtonClicked
    for row_num, row in enumerate(form.Rows):
        for col_num, element in enumerate(row):
            if element.Key is not None and WRITE_ONLY_KEY in str(element.Key):
                continue
            value = None
            if element.Type == ELEM_TYPE_COLUMN:
                element.DictionaryKeyCounter = top_level_form.DictionaryKeyCounter
                element.ReturnValuesList = []
                element.ReturnValuesDictionary = {}
                _BuildResultsForSubform(element, initialize_only, top_level_form)
                for item in element.ReturnValuesList:
                    AddToReturnList(top_level_form, item)
                if element.UseDictionary:
                    top_level_form.UseDictionary = True
                if element.ReturnValues[0] is not None:  # if a button was clicked
                    event = element.ReturnValues[0]

            if element.Type == ELEM_TYPE_FRAME:
                element.DictionaryKeyCounter = top_level_form.DictionaryKeyCounter
                element.ReturnValuesList = []
                element.ReturnValuesDictionary = {}
                _BuildResultsForSubform(element, initialize_only, top_level_form)
                for item in element.ReturnValuesList:
                    AddToReturnList(top_level_form, item)
                if element.UseDictionary:
                    top_level_form.UseDictionary = True
                if element.ReturnValues[0] is not None:  # if a button was clicked
                    event = element.ReturnValues[0]

            if element.Type == ELEM_TYPE_PANE:
                element.DictionaryKeyCounter = top_level_form.DictionaryKeyCounter
                element.ReturnValuesList = []
                element.ReturnValuesDictionary = {}
                _BuildResultsForSubform(element, initialize_only, top_level_form)
                for item in element.ReturnValuesList:
                    AddToReturnList(top_level_form, item)
                if element.UseDictionary:
                    top_level_form.UseDictionary = True
                if element.ReturnValues[0] is not None:  # if a button was clicked
                    event = element.ReturnValues[0]

            if element.Type == ELEM_TYPE_TAB_GROUP:
                element.DictionaryKeyCounter = top_level_form.DictionaryKeyCounter
                element.ReturnValuesList = []
                element.ReturnValuesDictionary = {}
                _BuildResultsForSubform(element, initialize_only, top_level_form)
                for item in element.ReturnValuesList:
                    AddToReturnList(top_level_form, item)
                if element.UseDictionary:
                    top_level_form.UseDictionary = True
                if element.ReturnValues[0] is not None:  # if a button was clicked
                    event = element.ReturnValues[0]

            if element.Type == ELEM_TYPE_TAB:
                element.DictionaryKeyCounter = top_level_form.DictionaryKeyCounter
                element.ReturnValuesList = []
                element.ReturnValuesDictionary = {}
                _BuildResultsForSubform(element, initialize_only, top_level_form)
                for item in element.ReturnValuesList:
                    AddToReturnList(top_level_form, item)
                if element.UseDictionary:
                    top_level_form.UseDictionary = True
                if element.ReturnValues[0] is not None:  # if a button was clicked
                    event = element.ReturnValues[0]

            if not initialize_only:
                if element.Type == ELEM_TYPE_INPUT_TEXT:
                    try:
                        value = element.TKStringVar.get()
                    except Exception:
                        value = ""
                    if (
                        not top_level_form.NonBlocking
                        and not element.do_not_clear
                        and not top_level_form.ReturnKeyboardEvents
                    ):
                        element.TKStringVar.set("")
                elif element.Type == ELEM_TYPE_INPUT_CHECKBOX:
                    value = element.TKIntVar.get()
                    value = value != 0
                elif element.Type == ELEM_TYPE_INPUT_RADIO:
                    RadVar = element.TKIntVar.get()
                    this_rowcol = EncodeRadioRowCol(
                        form.ContainerElemementNumber, row_num, col_num
                    )
                    # this_rowcol = element.EncodedRadioValue       # could use the saved one
                    value = RadVar == this_rowcol
                elif element.Type == ELEM_TYPE_BUTTON:
                    if top_level_form.LastButtonClicked == element.Key:
                        event = top_level_form.LastButtonClicked
                        if (
                            element.BType != BUTTON_TYPE_REALTIME
                        ):  # Do not clear realtime buttons
                            top_level_form.LastButtonClicked = None
                    if element.BType == BUTTON_TYPE_CALENDAR_CHOOSER:
                        # value = None
                        value = element.calendar_selection
                    else:
                        try:
                            value = element.TKStringVar.get()
                        except Exception:
                            value = None
                elif element.Type == ELEM_TYPE_INPUT_COMBO:
                    element = element  # type: Combo
                    # value = element.TKStringVar.get()
                    try:
                        if (
                            element.TKCombo.current() == -1
                        ):  # if the current value was not in the original list
                            value = element.TKCombo.get()
                        else:
                            value = element.Values[
                                element.TKCombo.current()
                            ]  # get value from original list given index
                    except Exception:
                        value = "*Exception occurred*"
                elif element.Type == ELEM_TYPE_INPUT_OPTION_MENU:
                    value = element.TKStringVar.get()
                elif element.Type == ELEM_TYPE_INPUT_LISTBOX:
                    try:
                        items = element.TKListbox.curselection()
                        value = [element.Values[int(item)] for item in items]
                    except Exception as e:
                        value = ""
                elif element.Type == ELEM_TYPE_INPUT_SPIN:
                    try:
                        value = element.TKStringVar.get()
                        for v in element.Values:
                            if str(v) == value:
                                value = v
                                break
                    except Exception:
                        value = 0
                elif element.Type == ELEM_TYPE_INPUT_SLIDER:
                    try:
                        value = float(element.TKScale.get())
                    except Exception:
                        value = 0
                elif element.Type == ELEM_TYPE_INPUT_MULTILINE:
                    if element.WriteOnly:  # if marked as "write only" when created, then don't include with the values being returned
                        continue
                    try:
                        value = element.TKText.get(1.0, tk.END)
                        if element.rstrip:
                            value = value.rstrip()
                        if (
                            not top_level_form.NonBlocking
                            and not element.do_not_clear
                            and not top_level_form.ReturnKeyboardEvents
                        ):
                            element.TKText.delete("1.0", tk.END)
                    except Exception:
                        value = None
                elif element.Type == ELEM_TYPE_TAB_GROUP:
                    try:
                        value = element.TKNotebook.tab(
                            element.TKNotebook.index("current")
                        )["text"]
                        tab_key = element.find_currently_active_tab_key()
                        # tab_key = element.FindKeyFromTabName(value)
                        if tab_key is not None:
                            value = tab_key
                    except Exception:
                        value = None
                elif element.Type == ELEM_TYPE_TABLE:
                    value = element.SelectedRows
                elif element.Type == ELEM_TYPE_TREE:
                    value = element.SelectedRows
                elif element.Type == ELEM_TYPE_GRAPH:
                    value = element.ClickPosition
                elif element.Type == ELEM_TYPE_MENUBAR:
                    if element.MenuItemChosen is not None:
                        event = top_level_form.LastButtonClicked = (
                            element.MenuItemChosen
                        )
                    value = element.MenuItemChosen
                    element.MenuItemChosen = None
                elif element.Type == ELEM_TYPE_BUTTONMENU:
                    element = element  # type: ButtonMenu
                    value = element.MenuItemChosen
                    if element.part_of_custom_menubar:
                        if element.MenuItemChosen is not None:
                            value = event = element.MenuItemChosen
                            top_level_form.LastButtonClicked = element.MenuItemChosen
                            if element.custom_menubar_key is not None:
                                top_level_form.ReturnValuesDictionary[
                                    element.custom_menubar_key
                                ] = value
                            element.MenuItemChosen = None
                        else:
                            if (
                                element.custom_menubar_key
                                not in top_level_form.ReturnValuesDictionary
                            ):
                                top_level_form.ReturnValuesDictionary[
                                    element.custom_menubar_key
                                ] = None
                            value = None

                    # if element.MenuItemChosen is not None:
                    #     button_pressed_text = top_level_form.LastButtonClicked = element.MenuItemChosen
                    # value = element.MenuItemChosen
                    # element.MenuItemChosen = None
            else:
                value = None

            # if an input type element, update the results
            if element.Type not in (
                ELEM_TYPE_BUTTON,
                ELEM_TYPE_TEXT,
                ELEM_TYPE_IMAGE,
                ELEM_TYPE_OUTPUT,
                ELEM_TYPE_PROGRESS_BAR,
                ELEM_TYPE_COLUMN,
                ELEM_TYPE_FRAME,
                ELEM_TYPE_SEPARATOR,
                ELEM_TYPE_TAB,
            ):
                if not (
                    element.Type == ELEM_TYPE_BUTTONMENU
                    and element.part_of_custom_menubar
                ):
                    AddToReturnList(form, value)
                    AddToReturnDictionary(top_level_form, element, value)
            elif (
                element.Type == ELEM_TYPE_BUTTON
                and element.BType == BUTTON_TYPE_COLOR_CHOOSER
                and element.Target == (None, None)
            ) or (
                element.Type == ELEM_TYPE_BUTTON
                and element.Key is not None
                and (
                    element.BType
                    in (
                        BUTTON_TYPE_SAVEAS_FILE,
                        BUTTON_TYPE_BROWSE_FILE,
                        BUTTON_TYPE_BROWSE_FILES,
                        BUTTON_TYPE_BROWSE_FOLDER,
                        BUTTON_TYPE_CALENDAR_CHOOSER,
                    )
                )
            ):
                AddToReturnList(form, value)
                AddToReturnDictionary(top_level_form, element, value)

    # if this is a column, then will fail so need to wrap with try
    try:
        if form.ReturnKeyboardEvents and form.LastKeyboardEvent is not None:
            event = form.LastKeyboardEvent
            form.LastKeyboardEvent = None
    except Exception:
        pass

    try:
        form.ReturnValuesDictionary.pop(
            None, None
        )  # clean up dictionary include None was included
    except Exception:
        pass

    # if no event was found
    if not initialize_only and event is None and form == top_level_form:
        queued_event_value = form._queued_thread_event_read()
        if queued_event_value is not None:
            event, value = queued_event_value
            AddToReturnList(form, value)
            form.ReturnValuesDictionary[event] = value

    if not form.UseDictionary:
        form.ReturnValues = event, form.ReturnValuesList
    else:
        form.ReturnValues = event, form.ReturnValuesDictionary

    return form.ReturnValues

def _FindElementWithFocusInSubForm(form):
    """
    Searches through a "sub-form" (can be a window or container) for the current element with focus

    :param form: a Window, Column, Frame, or TabGroup (container elements)
    :type form:  container elements
    :return:     Element
    :rtype:      Element | None
    """
    for row_num, row in enumerate(form.Rows):
        for col_num, element in enumerate(row):
            if element.Type == ELEM_TYPE_COLUMN:
                matching_elem = _FindElementWithFocusInSubForm(element)
                if matching_elem is not None:
                    return matching_elem
            elif element.Type == ELEM_TYPE_FRAME:
                matching_elem = _FindElementWithFocusInSubForm(element)
                if matching_elem is not None:
                    return matching_elem
            elif element.Type == ELEM_TYPE_TAB_GROUP:
                matching_elem = _FindElementWithFocusInSubForm(element)
                if matching_elem is not None:
                    return matching_elem
            elif element.Type == ELEM_TYPE_TAB:
                matching_elem = _FindElementWithFocusInSubForm(element)
                if matching_elem is not None:
                    return matching_elem
            elif element.Type == ELEM_TYPE_PANE:
                matching_elem = _FindElementWithFocusInSubForm(element)
                if matching_elem is not None:
                    return matching_elem
            elif element.Type == ELEM_TYPE_INPUT_TEXT:
                if element.TKEntry is not None:
                    if element.TKEntry is element.TKEntry.focus_get():
                        return element
            elif element.Type == ELEM_TYPE_INPUT_MULTILINE:
                if element.TKText is not None:
                    if element.TKText is element.TKText.focus_get():
                        return element
            elif element.Type == ELEM_TYPE_BUTTON:
                if element.TKButton is not None:
                    if element.TKButton is element.TKButton.focus_get():
                        return element
            else:  # The "Catch All" - if type isn't one of the above, try generic element.Widget
                try:
                    if element.Widget is not None:
                        if element.Widget is element.Widget.focus_get():
                            return element
                except Exception:
                    return None

    return None


def AddMenuItem(
    top_menu,
    sub_menu_info,
    element,
    is_sub_menu=False,
    skip=False,
    right_click_menu=False,
):
    """
    Only to be used internally. Not user callable
    :param right_click_menu:
    :param top_menu:      ???
    :type top_menu:       ???
    :param sub_menu_info: ???
    :type sub_menu_info:
    :param element:       ???
    :type element:        idk_yetReally
    :param is_sub_menu:   (Default = False)
    :type is_sub_menu:    (bool)
    :param skip:          (Default = False)
    :type skip:           (bool)

    """
    return_val = None
    if type(sub_menu_info) is str:
        if not is_sub_menu and not skip:
            pos = sub_menu_info.find(MENU_SHORTCUT_CHARACTER)
            if pos != -1:
                if (
                    pos < len(MENU_SHORTCUT_CHARACTER)
                    or sub_menu_info[pos - len(MENU_SHORTCUT_CHARACTER)] != "\\"
                ):
                    sub_menu_info = (
                        sub_menu_info[:pos]
                        + sub_menu_info[pos + len(MENU_SHORTCUT_CHARACTER) :]
                    )
            if sub_menu_info == "---":
                top_menu.add("separator")
            else:
                try:
                    item_without_key = sub_menu_info[
                        : sub_menu_info.index(MENU_KEY_SEPARATOR)
                    ]
                except Exception:
                    item_without_key = sub_menu_info

                if item_without_key[0] == MENU_DISABLED_CHARACTER:
                    top_menu.add_command(
                        label=item_without_key[len(MENU_DISABLED_CHARACTER) :],
                        underline=pos - 1,
                        command=lambda: element._MenuItemChosenCallback(sub_menu_info),
                    )
                    top_menu.entryconfig(
                        item_without_key[len(MENU_DISABLED_CHARACTER) :],
                        state="disabled",
                    )
                else:
                    top_menu.add_command(
                        label=item_without_key,
                        underline=pos,
                        command=lambda: element._MenuItemChosenCallback(sub_menu_info),
                    )
    else:
        i = 0
        while i < (len(sub_menu_info)):
            item = sub_menu_info[i]
            if i != len(sub_menu_info) - 1:
                if type(sub_menu_info[i + 1]) == list:
                    new_menu = tk.Menu(top_menu, tearoff=element.Tearoff)
                    # if a right click menu, then get styling from the top-level window
                    if right_click_menu:
                        window = element.ParentForm
                        if window.right_click_menu_background_color not in (
                            COLOR_SYSTEM_DEFAULT,
                            None,
                        ):
                            new_menu.config(bg=window.right_click_menu_background_color)
                            new_menu.config(
                                activeforeground=window.right_click_menu_background_color
                            )
                        if window.right_click_menu_text_color not in (
                            COLOR_SYSTEM_DEFAULT,
                            None,
                        ):
                            new_menu.config(fg=window.right_click_menu_text_color)
                            new_menu.config(
                                activebackground=window.right_click_menu_text_color
                            )
                        if window.right_click_menu_disabled_text_color not in (
                            COLOR_SYSTEM_DEFAULT,
                            None,
                        ):
                            new_menu.config(
                                disabledforeground=window.right_click_menu_disabled_text_color
                            )
                        if window.right_click_menu_font is not None:
                            new_menu.config(font=window.right_click_menu_font)
                    else:
                        if element.Font is not None:
                            new_menu.config(font=element.Font)
                        if element.BackgroundColor not in (COLOR_SYSTEM_DEFAULT, None):
                            new_menu.config(bg=element.BackgroundColor)
                            new_menu.config(activeforeground=element.BackgroundColor)
                        if element.TextColor not in (COLOR_SYSTEM_DEFAULT, None):
                            new_menu.config(fg=element.TextColor)
                            new_menu.config(activebackground=element.TextColor)
                        if element.DisabledTextColor not in (
                            COLOR_SYSTEM_DEFAULT,
                            None,
                        ):
                            new_menu.config(
                                disabledforeground=element.DisabledTextColor
                            )
                        if element.ItemFont is not None:
                            new_menu.config(font=element.ItemFont)
                    return_val = new_menu
                    pos = sub_menu_info[i].find(MENU_SHORTCUT_CHARACTER)
                    if pos != -1:
                        if (
                            pos < len(MENU_SHORTCUT_CHARACTER)
                            or sub_menu_info[i][pos - len(MENU_SHORTCUT_CHARACTER)]
                            != "\\"
                        ):
                            sub_menu_info[i] = (
                                sub_menu_info[i][:pos]
                                + sub_menu_info[i][pos + len(MENU_SHORTCUT_CHARACTER) :]
                            )
                    if sub_menu_info[i][0] == MENU_DISABLED_CHARACTER:
                        top_menu.add_cascade(
                            label=sub_menu_info[i][len(MENU_DISABLED_CHARACTER) :],
                            menu=new_menu,
                            underline=pos,
                            state="disabled",
                        )
                    else:
                        top_menu.add_cascade(
                            label=sub_menu_info[i], menu=new_menu, underline=pos
                        )
                    AddMenuItem(
                        new_menu,
                        sub_menu_info[i + 1],
                        element,
                        is_sub_menu=True,
                        right_click_menu=right_click_menu,
                    )
                    i += 1  # skip the next one
                else:
                    AddMenuItem(
                        top_menu, item, element, right_click_menu=right_click_menu
                    )
            else:
                AddMenuItem(top_menu, item, element, right_click_menu=right_click_menu)
            i += 1
    return return_val





# Chr0nic || This is probably *very* bad practice. But it works. Simple, but it works...
class VarHolder:
    canvas_holder = None

    def __init__(self):
        self.canvas_holder = None



# ========================   TK CODE STARTS HERE ========================================= #
def _fixed_map(style, style_name, option, highlight_colors=(None, None)):
    # Fix for setting text colour for Tkinter 8.6.9
    # From: https://core.tcl.tk/tk/info/509cafafae

    # default_map = [elm for elm in style.map("Treeview", query_opt=option) if '!' not in elm[0]]
    # custom_map = [elm for elm in style.map(style_name, query_opt=option) if '!' not in elm[0]]
    default_map = [
        elm
        for elm in style.map("Treeview", query_opt=option)
        if "!" not in elm[0] and "selected" not in elm[0]
    ]
    custom_map = [
        elm
        for elm in style.map(style_name, query_opt=option)
        if "!" not in elm[0] and "selected" not in elm[0]
    ]
    if option == "background":
        custom_map.append(
            (
                "selected",
                highlight_colors[1]
                if highlight_colors[1] is not None
                else ALTERNATE_TABLE_AND_TREE_SELECTED_ROW_COLORS[1],
            )
        )
    elif option == "foreground":
        custom_map.append(
            (
                "selected",
                highlight_colors[0]
                if highlight_colors[0] is not None
                else ALTERNATE_TABLE_AND_TREE_SELECTED_ROW_COLORS[0],
            )
        )

    new_map = custom_map + default_map
    return new_map
    #
    # new_map = [elm for elm in style.map(style_name, query_opt=option) if elm[:2] != ('!disabled', '!selected')]
    #
    # if option == 'background':
    #     new_map.append(('selected', highlight_colors[1] if highlight_colors[1] is not None else ALTERNATE_TABLE_AND_TREE_SELECTED_ROW_COLORS[1]))
    # elif option == 'foreground':
    #     new_map.append(('selected', highlight_colors[0] if highlight_colors[0] is not None else ALTERNATE_TABLE_AND_TREE_SELECTED_ROW_COLORS[0]))
    # return new_map
    #


def _add_right_click_menu(element, toplevel_form):
    if element.RightClickMenu == MENU_RIGHT_CLICK_DISABLED:
        return
    if element.RightClickMenu or toplevel_form.RightClickMenu:
        menu = element.RightClickMenu or toplevel_form.RightClickMenu
        top_menu = tk.Menu(
            toplevel_form.TKroot,
            tearoff=toplevel_form.right_click_menu_tearoff,
            tearoffcommand=element._tearoff_menu_callback,
        )

        if toplevel_form.right_click_menu_background_color not in (
            COLOR_SYSTEM_DEFAULT,
            None,
        ):
            top_menu.config(bg=toplevel_form.right_click_menu_background_color)
        if toplevel_form.right_click_menu_text_color not in (
            COLOR_SYSTEM_DEFAULT,
            None,
        ):
            top_menu.config(fg=toplevel_form.right_click_menu_text_color)
        if toplevel_form.right_click_menu_disabled_text_color not in (
            COLOR_SYSTEM_DEFAULT,
            None,
        ):
            top_menu.config(
                disabledforeground=toplevel_form.right_click_menu_disabled_text_color
            )
        if toplevel_form.right_click_menu_font is not None:
            top_menu.config(font=toplevel_form.right_click_menu_font)

        if toplevel_form.right_click_menu_selected_colors[0] not in (
            COLOR_SYSTEM_DEFAULT,
            None,
        ):
            top_menu.config(
                activeforeground=toplevel_form.right_click_menu_selected_colors[0]
            )
        if toplevel_form.right_click_menu_selected_colors[1] not in (
            COLOR_SYSTEM_DEFAULT,
            None,
        ):
            top_menu.config(
                activebackground=toplevel_form.right_click_menu_selected_colors[1]
            )
        AddMenuItem(top_menu, menu[1], element, right_click_menu=True)
        element.TKRightClickMenu = top_menu
        if running_mac():
            element.Widget.bind("<ButtonRelease-2>", element._RightClickMenuCallback)
        else:
            element.Widget.bind("<ButtonRelease-3>", element._RightClickMenuCallback)
