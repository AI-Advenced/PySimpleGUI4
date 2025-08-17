
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

from ..core import Element
from ..constants import *





class _QuickMeter:
    active_meters = {}
    exit_reasons = {}

    def __init__(
        self,
        title,
        current_value,
        max_value,
        key,
        *args,
        orientation="v",
        bar_color=(None, None),
        button_color=(None, None),
        size=DEFAULT_PROGRESS_BAR_SIZE,
        border_width=None,
        grab_anywhere=False,
        no_titlebar=False,
        keep_on_top=None,
        no_button=False,
    ):
        """

        :param title:         text to display in element
        :type title:          (str)
        :param current_value: current value
        :type current_value:  (int)
        :param max_value:     max value of progress meter
        :type max_value:      (int)
        :param key:           Used with window.find_element and with return values to uniquely identify this element
        :type key:            str | int | tuple | object
        :param *args:         stuff to output
        :type *args:          (Any)
        :param orientation:   'horizontal' or 'vertical' ('h' or 'v' work) (Default value = 'vertical' / 'v')
        :type orientation:    (str)
        :param bar_color:     The 2 colors that make up a progress bar. Either a tuple of 2 strings or a string. Tuple - (bar, background). A string with 1 color changes the background of the bar only. A string with 2 colors separated by "on" like "red on blue" specifies a red bar on a blue background.
        :type bar_color:      (str, str) or str
        :param button_color:  button color (foreground, background)
        :type button_color:   (str, str) | str
        :param size:          (w,h) w=characters-wide, h=rows-high (Default value = DEFAULT_PROGRESS_BAR_SIZE)
        :type size:           (int, int)
        :param border_width:  width of border around element
        :type border_width:   (int)
        :param grab_anywhere: If True: can grab anywhere to move the window (Default = False)
        :type grab_anywhere:  (bool)
        :param no_titlebar:   If True: window will be created without a titlebar
        :type no_titlebar:    (bool)
        :param keep_on_top:   If True the window will remain above all current windows
        :type keep_on_top:    (bool)
        :param no_button:     If True: window will be created without a cancel button
        :type no_button:      (bool)
        """
        self.start_time = datetime.datetime.utcnow()
        self.key = key
        self.orientation = orientation
        self.bar_color = bar_color
        self.size = size
        self.grab_anywhere = grab_anywhere
        self.button_color = button_color
        self.border_width = border_width
        self.no_titlebar = no_titlebar
        self.title = title
        self.current_value = current_value
        self.max_value = max_value
        self.close_reason = None
        self.keep_on_top = keep_on_top
        self.no_button = no_button
        self.window = self.BuildWindow(*args)

    def BuildWindow(self, *args):
        layout = []
        if self.orientation.lower().startswith("h"):
            col = []
            col += [
                [T("".join(map(lambda x: str(x) + "\n", args)), key="-OPTMSG-")]
            ]  ### convert all *args into one string that can be updated
            col += [
                [T("", size=(30, 10), key="-STATS-")],
                [
                    ProgressBar(
                        max_value=self.max_value,
                        orientation="h",
                        key="-PROG-",
                        size=self.size,
                        bar_color=self.bar_color,
                    )
                ],
            ]
            if not self.no_button:
                col += [[Cancel(button_color=self.button_color), Stretch()]]
            layout = [Column(col)]
        else:
            col = [
                [
                    ProgressBar(
                        max_value=self.max_value,
                        orientation="v",
                        key="-PROG-",
                        size=self.size,
                        bar_color=self.bar_color,
                    )
                ]
            ]
            col2 = []
            col2 += [
                [T("".join(map(lambda x: str(x) + "\n", args)), key="-OPTMSG-")]
            ]  ### convert all *args into one string that can be updated
            col2 += [[T("", size=(30, 10), key="-STATS-")]]
            if not self.no_button:
                col2 += [[Cancel(button_color=self.button_color), Stretch()]]

            layout = [Column(col), Column(col2)]
        self.window = Window(
            self.title,
            grab_anywhere=self.grab_anywhere,
            border_depth=self.border_width,
            no_titlebar=self.no_titlebar,
            disable_close=True,
            keep_on_top=self.keep_on_top,
        )
        self.window.Layout([layout]).Finalize()

        return self.window

    def UpdateMeter(
        self, current_value, max_value, *args
    ):  ### support for *args when updating
        self.current_value = current_value
        self.max_value = max_value
        self.window.Element("-PROG-").UpdateBar(self.current_value, self.max_value)
        self.window.Element("-STATS-").Update("\n".join(self.ComputeProgressStats()))
        self.window.Element("-OPTMSG-").Update(
            value="".join(map(lambda x: str(x) + "\n", args))
        )  ###  update the string with the args
        event, values = self.window.read(timeout=0)
        if event in ("Cancel", None) or current_value >= max_value:
            exit_reason = (
                METER_REASON_CANCELLED
                if event in ("Cancel", None)
                else METER_REASON_REACHED_MAX
                if current_value >= max_value
                else METER_STOPPED
            )
            self.window.close()
            del _QuickMeter.active_meters[self.key]
            _QuickMeter.exit_reasons[self.key] = exit_reason
            return _QuickMeter.exit_reasons[self.key]
        return METER_OK

    def ComputeProgressStats(self):
        utc = datetime.datetime.utcnow()
        time_delta = utc - self.start_time
        total_seconds = time_delta.total_seconds()
        if not total_seconds:
            total_seconds = 1
        try:
            time_per_item = total_seconds / self.current_value
        except Exception:
            time_per_item = 1
        seconds_remaining = (self.max_value - self.current_value) * time_per_item
        time_remaining = str(datetime.timedelta(seconds=seconds_remaining))
        time_remaining_short = time_remaining.split(".")[0]
        time_delta_short = str(time_delta).split(".")[0]
        total_time = time_delta + datetime.timedelta(seconds=seconds_remaining)
        total_time_short = str(total_time).split(".")[0]
        self.stat_messages = [
            "{} of {}".format(self.current_value, self.max_value),
            "{} %".format(100 * self.current_value // self.max_value),
            "",
            " {:6.2f} Iterations per Second".format(self.current_value / total_seconds),
            " {:6.2f} Seconds per Iteration".format(
                total_seconds / (self.current_value if self.current_value else 1)
            ),
            "",
            "{} Elapsed Time".format(time_delta_short),
            "{} Time Remaining".format(time_remaining_short),
            "{} Estimated Total Time".format(total_time_short),
        ]
        return self.stat_messages




def one_line_progress_meter(
    title:str,
    current_value:int,
    max_value:int,
    *args,
    key="OK for 1 meter",
    orientation:str="v",
    bar_color=(None, None),
    button_color=None,
    size=DEFAULT_PROGRESS_BAR_SIZE,
    border_width=None,
    grab_anywhere=False,
    no_titlebar=False,
    keep_on_top=None,
    no_button=False,
):
    """
    :param title:         text to display in titlebar of window
    :type title:          (str)
    :param current_value: current value
    :type current_value:  (int)
    :param max_value:     max value of progress meter
    :type max_value:      (int)
    :param key:           Used to differentiate between multiple meters. Used to cancel meter early. Now optional as there is a default value for single meters
    :type key:            str | int | tuple | object
    :param orientation:   'horizontal' or 'vertical' ('h' or 'v' work) (Default value = 'vertical' / 'v')
    :type orientation:    (str)
    :param bar_color:     The 2 colors that make up a progress bar. Either a tuple of 2 strings or a string. Tuple - (bar, background). A string with 1 color changes the background of the bar only. A string with 2 colors separated by "on" like "red on blue" specifies a red bar on a blue background.
    :type bar_color:      (str, str) or str
    :param button_color:  button color (foreground, background)
    :type button_color:   (str, str) | str
    :param size:          (w,h) w=characters-wide, h=rows-high (Default value = DEFAULT_PROGRESS_BAR_SIZE)
    :type size:           (int, int)
    :param border_width:  width of border around element
    :type border_width:   (int)
    :param grab_anywhere: If True: can grab anywhere to move the window (Default = False)
    :type grab_anywhere:  (bool)
    :param no_titlebar:   If True: no titlebar will be shown on the window
    :type no_titlebar:    (bool)
    :param keep_on_top:   If True the window will remain above all current windows
    :type keep_on_top:    (bool)
    :param no_button:     If True: window will be created without a cancel button
    :type no_button:      (bool)
    :return:              True if updated successfully. False if user closed the meter with the X or Cancel button
    :rtype:               (bool)
    """
    if key not in _QuickMeter.active_meters:
        meter = _QuickMeter(
            title,
            current_value,
            max_value,
            key,
            *args,
            orientation=orientation,
            bar_color=bar_color,
            button_color=button_color,
            size=size,
            border_width=border_width,
            grab_anywhere=grab_anywhere,
            no_titlebar=no_titlebar,
            keep_on_top=keep_on_top,
            no_button=no_button,
        )
        _QuickMeter.active_meters[key] = meter
        _QuickMeter.exit_reasons[key] = None

    else:
        meter = _QuickMeter.active_meters[key]

    rc = meter.UpdateMeter(
        current_value, max_value, *args
    )  ### pass the *args to to UpdateMeter function
    OneLineProgressMeter.exit_reasons = getattr(
        OneLineProgressMeter, "exit_reasons", _QuickMeter.exit_reasons
    )
    exit_reason = OneLineProgressMeter.exit_reasons.get(key)
    return (
        METER_OK if exit_reason in (None, METER_REASON_REACHED_MAX) else METER_STOPPED
    )


def one_line_progress_meter_cancel(key="OK for 1 meter"):
    """
    Cancels and closes a previously created One Line Progress Meter window

    :param key: Key used when meter was created
    :type key:  (Any)
    :return:    None
    :rtype:     None
    """
    try:
        meter = _QuickMeter.active_meters[key]
        meter.window.Close()
        del _QuickMeter.active_meters[key]
        _QuickMeter.exit_reasons[key] = METER_REASON_CANCELLED
    except Exception:  # meter is already deleted
        return

