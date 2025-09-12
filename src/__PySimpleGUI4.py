#!/usr/bin/python3

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

version = "4.80.2"

_change_log = """
    Changelog since 4.70.1 released to PyPI on 20-Jul-2024

    """

__version__ = version  # For PEP 396 and PEP 345

# The shortened version of version
ver = version

# INFO START
port = "PySimpleGUI"
__license__ = "GPL-3.0 license"
__author__ = "yunluo"
__email__ = "sp91@qq.com"
# INFO END

# 8""""8        8""""8                             8""""8 8   8 8
# 8    8 e    e 8      e  eeeeeee eeeee e     eeee 8    " 8   8 8
# 8eeee8 8    8 8eeeee 8  8  8  8 8   8 8     8    8e     8e  8 8e
# 88     8eeee8     88 8e 8e 8  8 8eee8 8e    8eee 88  ee 88  8 88
# 88       88   e   88 88 88 8  8 88    88    88   88   8 88  8 88
# 88       88   8eee88 88 88 8  8 88    88eee 88ee 88eee8 88ee8 88


"""
    Copyright 2018, 2019, 2020, 2021, 2022, 2023, 2024 PySimpleGUI(tm)
    Copyright 2024 PySimpleSoft, Inc.
    Copyright 2024 MB

    From the inception these have been the project principals upon which it is all built
    1. Fun - it's a serious goal of the project. If we're not having FUN while making stuff, then something's not right
    2. Successful - you need to be successful or it's all for naught
    3. You are the important party - It's your success that determines the success of PySimpleGUI

    If these 3 things are kept at the forefront, then the rest tends to fall into place.

    Please consider sponsoring all open source developers that make software you or your business use. They need your help.
    

    This software is available for your use under a LGPL3+ license

    This notice, these first 150 lines of code shall remain unchanged



    888      .d8888b.  8888888b.  888      .d8888b.          
    888     d88P  Y88b 888   Y88b 888     d88P  Y88b         
    888     888    888 888    888 888          .d88P
    888     888        888   d88P 888         8888"    888   
    888     888  88888 8888888P"  888          "Y8b. 8888888 
    888     888    888 888        888     888    888   888   
    888     Y88b  d88P 888        888     Y88b  d88P         
    88888888 "Y8888P88 888        88888888 "Y8888P"          


    In addition to the normal publishing requirements of LGPL3+, these also apply:

    A final note from mike...
    
        “Don’t aim at success. The more you aim at it and make it a target, the more you are going to miss it. 
        For success, like happiness, cannot be pursued; it must ensue, and it only does so as the unintended side effect of one’s personal dedication to a cause greater.”
            — Viktor Frankl
    
        I first saw this quote in a truncated format:
            "Happiness, cannot be pursued; it must ensue, and it only does so as the unintended side effect of one’s personal dedication to a cause greater."    
    
        Everyone is different, but my experience with the PySimpleGUI project matches this theory.  It's taken a lifetime of trying and "failing" and trying
        to find happiness before I finally figured this truth-for-me out.  If I do a long list of things, and live life in a kind & loving way, then the
        result is happiness.  It's a biproduct, not a directly produced thing.  This should be taught in school.  Or maybe it can't.
        I hope you find happiness, but more importantly, or maybe first, I hope you find that bigger-than-you thing. For me it's always been programming.  It seems to be
        the giving back part, not just the calling, that makes the happiness fusion-reactor operate.

    "Thank you" has fueled this project. I'm incredibly grateful to have users that are in turn grateful. It's a feedback loop of gratitude. What a fantastic thing!
"""

pil_import_attempted = pil_imported = False

warnings.simplefilter("always", UserWarning)

g_time_start = 0
g_time_end = 0
g_time_delta = 0


# These timer routines are to help you quickly time portions of code.  Place the timer_start call at the point
# you want to start timing and the timer_stop at the end point. The delta between the start and stop calls
# is returned from calling timer_stop


def timer_start():
    """
    Time your code easily.... starts the timer.
    Uses the time.time value, a technique known to not be terribly accurage, but tis' gclose enough for our purposes
    """
    global g_time_start

    g_time_start = time.time()


def timer_stop():
    """
    Time your code easily.... stop the timer and print the number of MILLISECONDS since the timer start

    :return: delta in MILLISECONDS from timer_start was called
    :rtype:  int
    """
    global g_time_delta, g_time_end

    g_time_end = time.time()
    g_time_delta = g_time_end - g_time_start
    return int(g_time_delta * 1000)


def timer_stop_usec():
    """
    Time your code easily.... stop the timer and print the number of MICROSECONDS since the timer start

    :return: delta in MICROSECONDS from timer_start was called
    :rtype:  int
    """
    global g_time_delta, g_time_end

    g_time_end = time.time()
    g_time_delta = g_time_end - g_time_start
    return int(g_time_delta * 1000000)


_timeit_counter = 0
MAX_TIMEIT_COUNT = 1000
_timeit_total = 0


# Handy python statements to increment and decrement with wrapping that I don't want to forget
# count = (count + (MAX - 1)) % MAX           # Decrement - roll over to MAX from 0
# count = (count + 1) % MAX                   # Increment to MAX then roll over to 0

"""
    Welcome to the "core" PySimpleGUI code....

    It's a mess.... really... it's a mess internally... it's the external-facing interfaces that
    are not a mess.  The Elements and the methods for them are well-designed.
    PEP8 - this code is far far from PEP8 compliant. 
    It was written PRIOR to learning that PEP8 existed. 

    I'll be honest.... started learning Python in Nov 2017, started writing PySimpleGUI in Feb 2018.
    Released PySimpleGUI in July 2018.  I knew so little about Python that my parameters were all named
    using CamelCase.  DOH!  Someone on Reddit set me straight on that.  So overnight I renamed all of the
    parameters to lower case.  Unfortunately, the internal naming conventions have been set.  Mixing them
    with PEP8 at this moment would be even MORE confusing.

    Code I write now, outside PySimpleGUI, IS PEP8 compliant.  

    The variable and function naming in particular are not compliant.  There is
    liberal use of CamelVariableAndFunctionNames, but for anything externally facing, there are aliases
    available for all functions.  If you've got a serious enough problem with 100% PEP8 compliance
    that you'll pass on this package, then that's your right and I invite you to do so.  However, if
    perhaps you're a practical thinker where it's the results that matter, then you'll have no
    trouble with this code base.  There is consisency however.  

    I truly hope you get a lot of enjoyment out of using PySimpleGUI.  It came from good intentions.
"""






ttk_part_mapping_dict = copy.copy(DEFAULT_TTK_PART_MAPPING_DICT)

# ------------------------------------------------------------------------- #
#                       _TimerPeriodic CLASS                                #
# ------------------------------------------------------------------------- #


class _TimerPeriodic:
    id_counter = 1
    # Dictionary containing the active timers.  Format is {id : _TimerPeriodic object}
    active_timers = {}  # type: dict[int:_TimerPeriodic]

    def __init__(self, window, frequency_ms:int, key=EVENT_TIMER, repeating:bool=True):
        """
        :param window:          The window to send events to
        :type window:           Window
        :param frequency_ms:    How often to send events in milliseconds
        :type frequency_ms:     int
        :param repeating:       If True then the timer will run, repeatedly sending events, until stopped
        :type repeating:        bool
        """
        self.window = window
        self.frequency_ms = frequency_ms
        self.repeating = repeating
        self.key = key
        self.id = _TimerPeriodic.id_counter
        _TimerPeriodic.id_counter += 1
        self.start()

    @classmethod
    def stop_timer_with_id(cls, timer_id):
        """
        Not user callable!
        :return: A simple counter that makes each container element unique
        :rtype:
        """
        timer = cls.active_timers.get(timer_id, None)
        if timer is not None:
            timer.stop()

    @classmethod
    def stop_all_timers_for_window(cls, window):
        """
        Stops all timers for a given window
        :param window:      The window to stop timers for
        :type window:       Window
        """
        for timer in _TimerPeriodic.active_timers.values():
            if timer.window == window:
                timer.running = False

    @classmethod
    def get_all_timers_for_window(cls, window):
        """
        Returns a list of timer IDs for a given window
        :param window:      The window to find timers for
        :type window:       Window
        :return:            List of timer IDs for the window
        :rtype:             List[int]
        """
        timers = []
        for timer in _TimerPeriodic.active_timers.values():
            if timer.window == window:
                timers.append(timer.id)

        return timers

    def timer_thread(self):
        """
        The thread that sends events to the window.  Runs either once or in a loop until timer is stopped
        """

        if not self.running:  # if timer has been cancelled, abort
            del _TimerPeriodic.active_timers[self.id]
            return
        while True:
            time.sleep(self.frequency_ms / 1000)
            if not self.running:  # if timer has been cancelled, abort
                del _TimerPeriodic.active_timers[self.id]
                return
            self.window.write_event_value(self.key, self.id)

            if not self.repeating:  # if timer does not repeat, then exit thread
                del _TimerPeriodic.active_timers[self.id]
                return

    def start(self):
        """
        Starts a timer by starting a timer thread
        Adds timer to the list of active timers
        """
        self.running = True
        self.thread = threading.Thread(target=self.timer_thread, daemon=True)
        self.thread.start()
        _TimerPeriodic.active_timers[self.id] = self

    def stop(self):
        """
        Stops a timer
        """
        self.running = False


def _timeout_alarm_callback_hidden():
    """
    Read Timeout Alarm callback. Will kick a mainloop call out of the tkinter event loop and cause it to return
    """

    del Window._TKAfterID

    # first, get the results table built
    # modify the Results table in the parent FlexForm object
    # print('TIMEOUT CALLBACK')
    Window._root_running_mainloop.quit()  # kick the users out of the mainloop

    # Get window that caused return
    Window._window_that_exited = None

#####################################  -----  RESULTS   ------ ##################################################


# Also, to get to the point in the code where each element's widget is created, look for element + "p lacement" (without the space)


# ==============================  PROGRESS METER ========================================== #

# ========================  EasyPrint           =====#
# ===================================================#
class _DebugWin:
    debug_window = None

    def __init__(
        self,
        size=(None, None),
        location=(None, None),
        relative_location=(None, None),
        font=None,
        no_titlebar=False,
        no_button=False,
        grab_anywhere=False,
        keep_on_top=None,
        do_not_reroute_stdout=True,
        echo_stdout=False,
        resizable=True,
        blocking=False,
    ):
        """

        :param size:                  (w,h) w=characters-wide, h=rows-high
        :type size:                   (int, int)
        :param location:              Location of upper left corner of the window
        :type location:               (int, int)
        :param relative_location:     (x,y) location relative to the default location of the window, in pixels. Normally the window centers.  This location is relative to the location the window would be created. Note they can be negative.
        :type relative_location:      (int, int)
        :param font:                  specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
        :type font:                   (str or (str, int[, str]) or None)
        :param no_titlebar:           If True no titlebar will be shown
        :type no_titlebar:            (bool)
        :param no_button:             show button
        :type no_button:              (bool)
        :param grab_anywhere:         If True: can grab anywhere to move the window (Default = False)
        :type grab_anywhere:          (bool)
        :param location:              Location of upper left corner of the window
        :type location:               (int, int)
        :param do_not_reroute_stdout: bool value
        :type do_not_reroute_stdout:  (bool)
        :param echo_stdout:           If True stdout is sent to both the console and the debug window
        :type echo_stdout:            (bool)
        :param resizable:             if True, makes the window resizble
        :type resizable:              (bool)
        :param blocking:              if True, makes the window block instead of returning immediately
        :type blocking:               (bool)
        """

        # Show a form that's a running counter
        self.size = size
        self.location = location
        self.relative_location = relative_location
        self.font = font
        self.no_titlebar = no_titlebar
        self.no_button = no_button
        self.grab_anywhere = grab_anywhere
        self.keep_on_top = keep_on_top
        self.do_not_reroute_stdout = do_not_reroute_stdout
        self.echo_stdout = echo_stdout
        self.resizable = resizable
        self.blocking = blocking

        win_size = size if size != (None, None) else DEFAULT_DEBUG_WINDOW_SIZE
        self.output_element = Multiline(
            size=win_size,
            autoscroll=True,
            auto_refresh=True,
            reroute_stdout=False if do_not_reroute_stdout else True,
            echo_stdout_stderr=self.echo_stdout,
            reroute_stderr=False if do_not_reroute_stdout else True,
            expand_x=True,
            expand_y=True,
            key="-MULTILINE-",
        )
        if no_button:
            self.layout = [[self.output_element]]
        else:
            if blocking:
                self.quit_button = Button("Quit", key="Quit")
            else:
                self.quit_button = DummyButton("Quit", key="Quit")
            self.layout = [
                [self.output_element],
                [pin(self.quit_button), pin(B("Pause", key="-PAUSE-")), Stretch()],
            ]

        self.layout[-1] += [Sizegrip()]

        self.window = Window(
            "Debug Window",
            self.layout,
            no_titlebar=no_titlebar,
            auto_size_text=True,
            location=location,
            relative_location=relative_location,
            font=font or ("Courier New", 10),
            grab_anywhere=grab_anywhere,
            keep_on_top=keep_on_top,
            finalize=True,
            resizable=resizable,
        )
        return

    def reopen_window(self):
        if self.window is None or (self.window is not None and self.window.is_closed()):
            self.__init__(
                size=self.size,
                location=self.location,
                relative_location=self.relative_location,
                font=self.font,
                no_titlebar=self.no_titlebar,
                no_button=self.no_button,
                grab_anywhere=self.grab_anywhere,
                keep_on_top=self.keep_on_top,
                do_not_reroute_stdout=self.do_not_reroute_stdout,
                resizable=self.resizable,
                echo_stdout=self.echo_stdout,
            )

    def Print(
        self,
        *args,
        end=None,
        sep=None,
        text_color=None,
        background_color=None,
        erase_all=False,
        font=None,
        blocking=None,
    ):
        global SUPPRESS_WIDGET_NOT_FINALIZED_WARNINGS
        suppress = SUPPRESS_WIDGET_NOT_FINALIZED_WARNINGS
        SUPPRESS_WIDGET_NOT_FINALIZED_WARNINGS = True
        sepchar = sep if sep is not None else " "
        endchar = end if end is not None else "\n"
        self.reopen_window()  # if needed, open the window again

        timeout = 0 if not blocking else None
        if erase_all:
            self.output_element.update("")

        if self.do_not_reroute_stdout:
            end_str = str(end) if end is not None else "\n"
            sep_str = str(sep) if sep is not None else " "

            outstring = ""
            num_args = len(args)
            for i, arg in enumerate(args):
                outstring += str(arg)
                if i != num_args - 1:
                    outstring += sep_str
            outstring += end_str
            try:
                self.output_element.update(
                    outstring,
                    append=True,
                    text_color_for_value=text_color,
                    background_color_for_value=background_color,
                    font_for_value=font,
                )
            except Exception:
                self.window = None
                self.reopen_window()
                self.output_element.update(
                    outstring,
                    append=True,
                    text_color_for_value=text_color,
                    background_color_for_value=background_color,
                    font_for_value=font,
                )

        else:
            print(*args, sep=sepchar, end=endchar)
        # This is tricky....changing the button type depending on the blocking parm. If blocking, then the "Quit" button should become a normal button
        if blocking and not self.no_button:
            self.quit_button.BType = BUTTON_TYPE_READ_FORM
            try:  # The window may be closed by user at any time, so have to protect
                self.quit_button.update(text="Click to continue...")
            except Exception:
                self.window = None
        elif not self.no_button:
            self.quit_button.BType = BUTTON_TYPE_CLOSES_WIN_ONLY
            try:  # The window may be closed by user at any time, so have to protect
                self.quit_button.update(text="Quit")
            except Exception:
                self.window = None

        try:  # The window may be closed by user at any time, so have to protect
            if blocking and not self.no_button:
                self.window["-PAUSE-"].update(visible=False)
            elif not self.no_button:
                self.window["-PAUSE-"].update(visible=True)
        except Exception:
            self.window = None

        self.reopen_window()  # if needed, open the window again

        paused = None
        while True:
            event, values = self.window.read(timeout=timeout)

            if event == WIN_CLOSED:
                self.Close()
                break
            elif blocking and event == "Quit":
                break
            elif not paused and event == TIMEOUT_EVENT and not blocking:
                break
            elif event == "-PAUSE-":
                if (
                    blocking or self.no_button
                ):  # if blocking or shouldn't have been a button event, ignore the pause button entirely
                    continue
                if paused:
                    self.window["-PAUSE-"].update(text="Pause")
                    self.quit_button.update(visible=True)
                    break
                paused = True
                self.window["-PAUSE-"].update(text="Resume")
                self.quit_button.update(visible=False)
                timeout = None

        SUPPRESS_WIDGET_NOT_FINALIZED_WARNINGS = suppress

    def Close(self):
        if self.window.XFound:  # increment the number of open windows to get around a bug with debug windows
            Window._IncrementOpenCount()
        self.window.close()
        self.window = None


# ----------------------------------------------------------------- #


#####################################################################
# Animated window while shell command is executed
#####################################################################


def shell_with_animation(
    command,
    args=None,
    image_source=DEFAULT_BASE64_LOADING_GIF,
    message=None,
    background_color=None,
    text_color=None,
    font=None,
    no_titlebar=True,
    grab_anywhere=True,
    keep_on_top=True,
    location=(None, None),
    alpha_channel=None,
    time_between_frames=100,
    transparent_color=None,
):
    """
    Execute a "shell command" (anything capable of being launched using subprocess.run) and
    while the command is running, show an animated popup so that the user knows that a long-running
    command is being executed.  Without this mechanism, the GUI appears locked up.

    :param command:             The command to run
    :type command:              (str)
    :param args:                List of arguments
    :type args:                 List[str]
    :param image_source:        Either a filename or a base64 string.
    :type image_source:         str | bytes
    :param message:             An optional message to be shown with the animation
    :type message:              (str)
    :param background_color:    color of background
    :type background_color:     (str)
    :param text_color:          color of the text
    :type text_color:           (str)
    :param font:                specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:                 str | tuple
    :param no_titlebar:         If True then the titlebar and window frame will not be shown
    :type no_titlebar:          (bool)
    :param grab_anywhere:       If True then you can move the window just clicking anywhere on window, hold and drag
    :type grab_anywhere:        (bool)
    :param keep_on_top:         If True then Window will remain on top of all other windows currently shownn
    :type keep_on_top:          (bool)
    :param location:            (x,y) location on the screen to place the top left corner of your window. Default is to center on screen
    :type location:             (int, int)
    :param alpha_channel:       Window transparency 0 = invisible 1 = completely visible. Values between are see through
    :type alpha_channel:        (float)
    :param time_between_frames: Amount of time in milliseconds between each frame
    :type time_between_frames:  (int)
    :param transparent_color:   This color will be completely see-through in your window. Can even click through
    :type transparent_color:    (str)
    :return:                    The resulting string output from stdout
    :rtype:                     (str)
    """

    global __shell_process__

    real_args = [command]
    if args is not None:
        for arg in args:
            real_args.append(arg)
        # real_args.append(args)
    thread = threading.Thread(target=_process_thread, args=real_args, daemon=True)
    thread.start()

    # Poll to see if the thread is still running.  If so, then continue showing the animation
    while True:
        popup_animated(
            image_source=image_source,
            message=message,
            time_between_frames=time_between_frames,
            transparent_color=transparent_color,
            text_color=text_color,
            background_color=background_color,
            font=font,
            no_titlebar=no_titlebar,
            grab_anywhere=grab_anywhere,
            keep_on_top=keep_on_top,
            location=location,
            alpha_channel=alpha_channel,
        )
        thread.join(timeout=time_between_frames / 1000)
        if not thread.is_alive():
            break
    popup_animated(None)  # stop running the animation

    output = __shell_process__.__str__().replace(
        "\\r\\n", "\n"
    )  # fix up the output string
    output = output[output.index("stdout=b'") + 9 : -2]
    return output

####################################################################################################


pysimplegui_user_settings = UserSettings(
    filename=DEFAULT_USER_SETTINGS_PYSIMPLEGUI_FILENAME,
    path=DEFAULT_USER_SETTINGS_PYSIMPLEGUI_PATH,
)
# ------------------------ Set the "Official PySimpleGUI Theme Colors" ------------------------


theme(theme_global())
# ------------------------ Read the ttk scrollbar info ------------------------
_global_settings_get_ttk_scrollbar_info()

# ------------------------ Read the window watermark info ------------------------
_global_settings_get_watermark_info()

# See if running on Trinket. If Trinket, then use custom titlebars since Trinket doesn't supply any
if running_trinket():
    USE_CUSTOM_TITLEBAR = True

if tclversion_detailed.startswith("8.5"):
    warnings.warn(
        "You are running a VERY old version of tkinter {}. You cannot use PNG formatted images for example.  Please upgrade to 8.6.x".format(
            tclversion_detailed
        ),
        UserWarning,
    )

# Enables the correct application icon to be shown on the Windows taskbar
if running_windows():
    try:
        myappid = "mycompany.myproduct.subproduct.version"  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception as e:
        print("Error using the taskbar icon patch", e)

_read_mac_global_settings()

if _mac_should_set_alpha_to_99():
    # Applyting Mac OS 12.3+ Alpha Channel fix.  Sets the default Alpha Channel to 0.99
    set_options(alpha_channel=0.99)


