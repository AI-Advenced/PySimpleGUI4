from .core import Window
from .elements import Text, Button, Input
from .constants import *




# MM"""""""`YM
# MM  mmmmm  M
# M'        .M .d8888b. 88d888b. dP    dP 88d888b. .d8888b.
# MM  MMMMMMMM 88'  `88 88'  `88 88    88 88'  `88 Y8ooooo.
# MM  MMMMMMMM 88.  .88 88.  .88 88.  .88 88.  .88       88
# MM  MMMMMMMM `88888P' 88Y888P' `88888P' 88Y888P' `88888P'
# MMMMMMMMMMMM          88                88
#                       dP                dP
# ------------------------------------------------------------------------------------------------------------------ #
# =====================================   Upper PySimpleGUI ======================================================== #
# ------------------------------------------------------------------------------------------------------------------ #
# ----------------------------------- The mighty Popup! ------------------------------------------------------------ #


def popup(
    *args,
    title: str = None,
    button_color=None,
    background_color=None,
    text_color=None,
    button_type=POPUP_BUTTONS_OK,
    auto_close=False,
    auto_close_duration=None,
    custom_text=(None, None),
    non_blocking=False,
    icon=None,
    line_width=None,
    font=None,
    no_titlebar=False,
    grab_anywhere=False,
    keep_on_top=True,
    location=(None, None),
    relative_location=(None, None),
    any_key_closes=False,
    image=None,
    modal=True,
    button_justification=None,
    drop_whitespace=True,
):
    """
    Popup - Display a popup Window with as many parms as you wish to include.  This is the GUI equivalent of the
    "print" statement.  It's also great for "pausing" your program's flow until the user can read some error messages.

    If this popup doesn't have the features you want, then you can easily make your own. Popups can be accomplished in 1 line of code:
    choice, _ = sg.Window('Continue?', [[sg.T('Do you want to continue?')], [sg.Yes(s=10), sg.No(s=10)]], disable_close=True).read(close=True)


    :param title:                 Optional title for the window. If none provided, the first arg will be used instead.
    :type title:                  (str)
    :param button_color:          Color of the buttons shown (text color, button color)
    :type button_color:           (str, str) | str
    :param background_color:      Window's background color
    :type background_color:       (str)
    :param text_color:            text color
    :type text_color:             (str)
    :param button_type:           NOT USER SET!  Determines which pre-defined buttons will be shown (Default value = POPUP_BUTTONS_OK). There are many Popup functions and they call Popup, changing this parameter to get the desired effect.
    :type button_type:            (int)
    :param auto_close:            If True the window will automatically close
    :type auto_close:             (bool)
    :param auto_close_duration:   time in seconds to keep window open before closing it automatically
    :type auto_close_duration:    (int)
    :param custom_text:           A string or pair of strings that contain the text to display on the buttons
    :type custom_text:            (str, str) | str
    :param non_blocking:          If True then will immediately return from the function without waiting for the user's input.
    :type non_blocking:           (bool)
    :param icon:                  icon to display on the window. Same format as a Window call
    :type icon:                   str | bytes
    :param line_width:            Width of lines in characters.  Defaults to MESSAGE_BOX_LINE_WIDTH
    :type line_width:             (int)
    :param font:                  specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:                   str | Tuple[font_name, size, modifiers]
    :param no_titlebar:           If True will not show the frame around the window and the titlebar across the top
    :type no_titlebar:            (bool)
    :param grab_anywhere:         If True can grab anywhere to move the window. If no_titlebar is True, grab_anywhere should likely be enabled too
    :type grab_anywhere:          (bool)
    :param location:              Location on screen to display the top left corner of window. Defaults to window centered on screen
    :type location:               (int, int)
    :param relative_location:     (x,y) location relative to the default location of the window, in pixels. Normally the window centers.  This location is relative to the location the window would be created. Note they can be negative.
    :type relative_location:      (int, int)
    :param keep_on_top:           If True the window will remain above all current windows
    :type keep_on_top:            (bool)
    :param any_key_closes:        If True then will turn on return_keyboard_events for the window which will cause window to close as soon as any key is pressed.  Normally the return key only will close the window.  Default is false.
    :type any_key_closes:         (bool)
    :param image:                 Image to include at the top of the popup window
    :type image:                  (str) or (bytes)
    :param modal:                 If True then makes the popup will behave like a Modal window... all other windows are non-operational until this one is closed. Default = True
    :type modal:                  bool
    :param button_justification:  Speficies if buttons should be left, right or centered. Default is left justified
    :type button_justification:   str
    :param drop_whitespace:       Controls is whitespace should be removed when wrapping text.  Parameter is passed to textwrap.fill. Default is to drop whitespace (so popup remains backward compatible)
    :type drop_whitespace:        bool
    :return:                      Returns text of the button that was pressed.  None will be returned if user closed window with X
    :rtype:                       str | None
    """

    if not args:
        args_to_print = [""]
    else:
        args_to_print = args
    if line_width is not None:
        local_line_width = line_width
    else:
        local_line_width = MESSAGE_BOX_LINE_WIDTH
    _title = title if title is not None else args_to_print[0]

    layout = [[]]
    max_line_total, total_lines = 0, 0
    if image is not None:
        if isinstance(image, str):
            layout += [[Image(filename=image)]]
        else:
            layout += [[Image(data=image)]]

    for message in args_to_print:
        # fancy code to check if string and convert if not is not need. Just always convert to string :-)
        # if not isinstance(message, str): message = str(message)
        message = str(message)
        if message.count(
            "\n"
        ):  # if there are line breaks, then wrap each segment separately
            # message_wrapped = message         # used to just do this, but now breaking into smaller pieces
            message_wrapped = ""
            msg_list = message.split(
                "\n"
            )  # break into segments that will each be wrapped
            message_wrapped = "\n".join(
                [textwrap.fill(msg, local_line_width) for msg in msg_list]
            )
        else:
            message_wrapped = textwrap.fill(
                message, local_line_width, drop_whitespace=drop_whitespace
            )
        message_wrapped_lines = message_wrapped.count("\n") + 1
        longest_line_len = max([len(l) for l in message.split("\n")])
        width_used = min(longest_line_len, local_line_width)
        max_line_total = max(max_line_total, width_used)
        # height = _GetNumLinesNeeded(message, width_used)
        height = message_wrapped_lines
        layout += [
            [
                Text(
                    message_wrapped,
                    auto_size_text=True,
                    text_color=text_color,
                    background_color=background_color,
                )
            ]
        ]
        total_lines += height

    if non_blocking:
        PopupButton = (
            DummyButton  # important to use or else button will close other windows too!
        )
    else:
        PopupButton = Button
    # show either an OK or Yes/No depending on paramater
    if custom_text != (None, None):
        if type(custom_text) is not tuple:
            layout += [
                [
                    PopupButton(
                        custom_text,
                        size=(len(custom_text), 1),
                        button_color=button_color,
                        focus=True,
                        bind_return_key=True,
                    )
                ]
            ]
        elif custom_text[1] is None:
            layout += [
                [
                    PopupButton(
                        custom_text[0],
                        size=(len(custom_text[0]), 1),
                        button_color=button_color,
                        focus=True,
                        bind_return_key=True,
                    )
                ]
            ]
        else:
            layout += [
                [
                    PopupButton(
                        custom_text[0],
                        button_color=button_color,
                        focus=True,
                        bind_return_key=True,
                        size=(len(custom_text[0]), 1),
                    ),
                    PopupButton(
                        custom_text[1],
                        button_color=button_color,
                        size=(len(custom_text[1]), 1),
                    ),
                ]
            ]
    elif button_type == POPUP_BUTTONS_YES_NO:
        layout += [
            [
                PopupButton(
                    "Yes",
                    button_color=button_color,
                    focus=True,
                    bind_return_key=True,
                    size=(5, 1),
                ),
                PopupButton("No", button_color=button_color, size=(5, 1)),
            ]
        ]
    elif button_type == POPUP_BUTTONS_CANCELLED:
        layout += [
            [
                PopupButton(
                    "Cancelled",
                    button_color=button_color,
                    focus=True,
                    bind_return_key=True,
                )
            ]
        ]
    elif button_type == POPUP_BUTTONS_ERROR:
        layout += [
            [
                PopupButton(
                    "Error",
                    size=(6, 1),
                    button_color=button_color,
                    focus=True,
                    bind_return_key=True,
                )
            ]
        ]
    elif button_type == POPUP_BUTTONS_OK_CANCEL:
        layout += [
            [
                PopupButton(
                    "OK",
                    size=(6, 1),
                    button_color=button_color,
                    focus=True,
                    bind_return_key=True,
                ),
                PopupButton("Cancel", size=(6, 1), button_color=button_color),
            ]
        ]
    elif button_type == POPUP_BUTTONS_NO_BUTTONS:
        pass
    else:
        layout += [
            [
                PopupButton(
                    "OK",
                    size=(5, 1),
                    button_color=button_color,
                    focus=True,
                    bind_return_key=True,
                )
            ]
        ]
    if button_justification is not None:
        justification = button_justification.lower()[0]
        if justification == "r":
            layout[-1] = [Push()] + layout[-1]
        elif justification == "c":
            layout[-1] = [Push()] + layout[-1] + [Push()]

    window = Window(
        _title,
        layout,
        auto_size_text=True,
        background_color=background_color,
        button_color=button_color,
        auto_close=auto_close,
        auto_close_duration=auto_close_duration,
        icon=icon,
        font=font,
        no_titlebar=no_titlebar,
        grab_anywhere=grab_anywhere,
        keep_on_top=keep_on_top,
        location=location,
        relative_location=relative_location,
        return_keyboard_events=any_key_closes,
        modal=modal,
    )

    if non_blocking:
        button, values = window.read(timeout=0)
    else:
        button, values = window.read()
        window.close()
        del window

    return button


# ==============================  MsgBox============#
# Lazy function. Same as calling Popup with parms   #
# This function WILL Disappear perhaps today        #
# ==================================================#
# MsgBox is the legacy call and should not be used any longer
def MsgBox(*args):
    """
    Do not call this anymore it will raise exception.  Use Popups instead
    """
    raise DeprecationWarning(
        "MsgBox is no longer supported... change your call to Popup"
    )


# ========================  Scrolled Text Box   =====#
# ===================================================#
def popup_scrolled(
    *args,
    title=None,
    button_color=None,
    background_color=None,
    text_color=None,
    yes_no=False,
    no_buttons=False,
    button_justification="l",
    auto_close=False,
    auto_close_duration=None,
    size=(None, None),
    location=(None, None),
    relative_location=(None, None),
    non_blocking=False,
    no_titlebar=False,
    grab_anywhere=False,
    keep_on_top=None,
    font=None,
    image=None,
    icon=None,
    modal=True,
    no_sizegrip=False,
):
    """
    Show a scrolled Popup window containing the user's text that was supplied.  Use with as many items to print as you
    want, just like a print statement.

    :param title:                 Title to display in the window.
    :type title:                  (str)
    :param button_color:          button color (foreground, background)
    :type button_color:           (str, str) | str
    :param yes_no:                If True, displays Yes and No buttons instead of Ok
    :type yes_no:                 (bool)
    :param no_buttons:            If True, no buttons will be shown. User will have to close using the "X"
    :type no_buttons:             (bool)
    :param button_justification:  How buttons should be arranged.  l, c, r for Left, Center or Right justified
    :type button_justification:   (str)
    :param auto_close:            if True window will close itself
    :type auto_close:             (bool)
    :param auto_close_duration:   Older versions only accept int. Time in seconds until window will close
    :type auto_close_duration:    int | float
    :param size:                  (w,h) w=characters-wide, h=rows-high
    :type size:                   (int, int)
    :param location:              Location on the screen to place the upper left corner of the window
    :type location:               (int, int)
    :param relative_location:     (x,y) location relative to the default location of the window, in pixels. Normally the window centers.  This location is relative to the location the window would be created. Note they can be negative.
    :type relative_location:      (int, int)
    :param non_blocking:          if True the call will immediately return rather than waiting on user input
    :type non_blocking:           (bool)
    :param background_color:      color of background
    :type background_color:       (str)
    :param text_color:            color of the text
    :type text_color:             (str)
    :param no_titlebar:           If True no titlebar will be shown
    :type no_titlebar:            (bool)
    :param grab_anywhere:         If True, than can grab anywhere to move the window (Default = False)
    :type grab_anywhere:          (bool)
    :param keep_on_top:           If True the window will remain above all current windows
    :type keep_on_top:            (bool)
    :param font:                  specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:                   (str or (str, int[, str]) or None)
    :param image:                 Image to include at the top of the popup window
    :type image:                  (str) or (bytes)
    :param icon:                  filename or base64 string to be used for the window's icon
    :type icon:                   bytes | str
    :param modal:                 If True then makes the popup will behave like a Modal window... all other windows are non-operational until this one is closed. Default = True
    :type modal:                  bool
    :param no_sizegrip:           If True no Sizegrip will be shown when there is no titlebar. It's only shown if there is no titlebar
    :type no_sizegrip:            (bool)
    :return:                      Returns text of the button that was pressed.  None will be returned if user closed window with X
    :rtype:                       str | None | TIMEOUT_KEY
    """

    if not args:
        return
    width, height = size
    width = width if width else MESSAGE_BOX_LINE_WIDTH

    layout = [[]]

    if image is not None:
        if isinstance(image, str):
            layout += [[Image(filename=image)]]
        else:
            layout += [[Image(data=image)]]
    max_line_total, max_line_width, total_lines, height_computed = 0, 0, 0, 0
    complete_output = ""
    for message in args:
        # fancy code to check if string and convert if not is not need. Just always convert to string :-)
        # if not isinstance(message, str): message = str(message)
        message = str(message)
        longest_line_len = max([len(l) for l in message.split("\n")])
        width_used = min(longest_line_len, width)
        max_line_total = max(max_line_total, width_used)
        max_line_width = width
        lines_needed = _GetNumLinesNeeded(message, width_used)
        height_computed += lines_needed + 1
        complete_output += message + "\n"
        total_lines += lines_needed
    height_computed = (
        MAX_SCROLLED_TEXT_BOX_HEIGHT
        if height_computed > MAX_SCROLLED_TEXT_BOX_HEIGHT
        else height_computed
    )
    if height:
        height_computed = height
    layout += [
        [
            Multiline(
                complete_output,
                size=(max_line_width, height_computed),
                background_color=background_color,
                text_color=text_color,
                expand_x=True,
                expand_y=True,
                k="-MLINE-",
            )
        ]
    ]
    # show either an OK or Yes/No depending on paramater
    button = DummyButton if non_blocking else Button

    if yes_no:
        buttons = [button("Yes"), button("No")]
    elif no_buttons:
        buttons = [button("OK", size=(5, 1), button_color=button_color)]
    else:
        buttons = None

    if buttons is not None:
        if button_justification.startswith("l"):
            layout += [buttons]
        elif button_justification.startswith("c"):
            layout += [[Push()] + buttons + [Push()]]
        else:
            layout += [[Push()] + buttons]

    if no_sizegrip:
        layout[-1] += [Sizegrip()]

    window = Window(
        title or args[0],
        layout,
        auto_size_text=True,
        button_color=button_color,
        auto_close=auto_close,
        auto_close_duration=auto_close_duration,
        location=location,
        relative_location=relative_location,
        resizable=True,
        font=font,
        background_color=background_color,
        no_titlebar=no_titlebar,
        grab_anywhere=grab_anywhere,
        keep_on_top=keep_on_top,
        modal=modal,
        icon=icon,
    )
    if non_blocking:
        button, values = window.read(timeout=0)
    else:
        button, values = window.read()
        window.close()
        del window
    return button


# ============================== sprint ======#
# Is identical to the Scrolled Text Box       #
# Provides a crude 'print' mechanism but in a #
# GUI environment                             #
# This is in addition to the Print function   #
# which routes output to a "Debug Window"     #
# ============================================#


# --------------------------- popup_no_buttons ---------------------------
def popup_no_buttons(
    *args,
    title=None,
    background_color=None,
    text_color=None,
    auto_close=False,
    auto_close_duration=None,
    non_blocking=False,
    icon=None,
    line_width=None,
    font=None,
    no_titlebar=False,
    grab_anywhere=False,
    keep_on_top=None,
    location=(None, None),
    relative_location=(None, None),
    image=None,
    modal=True,
):
    """Show a Popup but without any buttons

    :param keep_on_top:
    :param title:               Title to display in the window.
    :type title:                (str)
    :param background_color:    color of background
    :type background_color:     (str)
    :param text_color:          color of the text
    :type text_color:           (str)
    :param auto_close:          if True window will close itself
    :type auto_close:           (bool)
    :param auto_close_duration: Older versions only accept int. Time in seconds until window will close
    :type auto_close_duration:  int | float
    :param non_blocking:        If True then will immediately return from the function without waiting for the user's input. (Default = False)
    :type non_blocking:         (bool)
    :param icon:                filename or base64 string to be used for the window's icon
    :type icon:                 bytes | str
    :param line_width:          Width of lines in characters
    :type line_width:           (int)
    :param font:                specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:                 (str or (str, int[, str]) or None)
    :param no_titlebar:         If True no titlebar will be shown
    :type no_titlebar:          (bool)
    :param grab_anywhere:       If True, than can grab anywhere to move the window (Default = False)
    :type grab_anywhere:        (bool)
    :param location:            Location of upper left corner of the window
    :type location:             (int, int)
    :param relative_location:   (x,y) location relative to the default location of the window, in pixels. Normally the window centers.  This location is relative to the location the window would be created. Note they can be negative.
    :type relative_location:    (int, int)
    :param image:               Image to include at the top of the popup window
    :type image:                (str) or (bytes)
    :param modal:               If True then makes the popup will behave like a Modal window... all other windows are non-operational until this one is closed. Default = True
    :type modal:                bool
    :return:                    Returns text of the button that was pressed.  None will be returned if user closed window with X
    :rtype:                     str | None | TIMEOUT_KEY"""
    Popup(
        *args,
        title=title,
        background_color=background_color,
        text_color=text_color,
        button_type=POPUP_BUTTONS_NO_BUTTONS,
        auto_close=auto_close,
        auto_close_duration=auto_close_duration,
        non_blocking=non_blocking,
        icon=icon,
        line_width=line_width,
        font=font,
        no_titlebar=no_titlebar,
        grab_anywhere=grab_anywhere,
        keep_on_top=keep_on_top,
        location=location,
        relative_location=relative_location,
        image=image,
        modal=modal,
    )


# --------------------------- popup_non_blocking ---------------------------
def popup_non_blocking(
    *args,
    title=None,
    button_type=POPUP_BUTTONS_OK,
    button_color=None,
    background_color=None,
    text_color=None,
    auto_close=False,
    auto_close_duration=None,
    non_blocking=True,
    icon=None,
    line_width=None,
    font=None,
    no_titlebar=False,
    grab_anywhere=False,
    keep_on_top=None,
    location=(None, None),
    relative_location=(None, None),
    image=None,
    modal=False,
):
    """
    Show Popup window and immediately return (does not block)

    :param keep_on_top:
    :param title:               Title to display in the window.
    :type title:                (str)
    :param button_type:         Determines which pre-defined buttons will be shown (Default value = POPUP_BUTTONS_OK).
    :type button_type:          (int)
    :param button_color:        button color (foreground, background)
    :type button_color:         (str, str) | str
    :param background_color:    color of background
    :type background_color:     (str)
    :param text_color:          color of the text
    :type text_color:           (str)
    :param auto_close:          if True window will close itself
    :type auto_close:           (bool)
    :param auto_close_duration: Older versions only accept int. Time in seconds until window will close
    :type auto_close_duration:  int | float
    :param non_blocking:        if True the call will immediately return rather than waiting on user input
    :type non_blocking:         (bool)
    :param icon:                filename or base64 string to be used for the window's icon
    :type icon:                 bytes | str
    :param line_width:          Width of lines in characters
    :type line_width:           (int)
    :param font:                specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:                 (str or (str, int[, str]) or None)
    :param no_titlebar:         If True no titlebar will be shown
    :type no_titlebar:          (bool)
    :param grab_anywhere:       If True: can grab anywhere to move the window (Default = False)
    :type grab_anywhere:        (bool)
    :param location:            Location of upper left corner of the window
    :type location:             (int, int)
    :param relative_location:   (x,y) location relative to the default location of the window, in pixels. Normally the window centers.  This location is relative to the location the window would be created. Note they can be negative.
    :type relative_location:    (int, int)
    :param image:               Image to include at the top of the popup window
    :type image:                (str) or (bytes)
    :param modal:               If True then makes the popup will behave like a Modal window... all other windows are non-operational until this one is closed. Default = False
    :type modal:                bool
    :return:                    Reason for popup closing
    :rtype:                     str | None
    """

    return popup(
        *args,
        title=title,
        button_color=button_color,
        background_color=background_color,
        text_color=text_color,
        button_type=button_type,
        auto_close=auto_close,
        auto_close_duration=auto_close_duration,
        non_blocking=non_blocking,
        icon=icon,
        line_width=line_width,
        font=font,
        no_titlebar=no_titlebar,
        grab_anywhere=grab_anywhere,
        keep_on_top=keep_on_top,
        location=location,
        relative_location=relative_location,
        image=image,
        modal=modal,
    )


# --------------------------- popup_quick - a NonBlocking, Self-closing Popup  ---------------------------
def popup_quick(
    *args,
    title=None,
    button_type=POPUP_BUTTONS_OK,
    button_color=None,
    background_color=None,
    text_color=None,
    auto_close=True,
    auto_close_duration=2,
    non_blocking=True,
    icon=None,
    line_width=None,
    font=None,
    no_titlebar=False,
    grab_anywhere=False,
    keep_on_top=None,
    location=(None, None),
    relative_location=(None, None),
    image=None,
    modal=False,
):
    """
    Show Popup box that doesn't block and closes itself

    :param title:               Title to display in the window.
    :type title:                (str)
    :param button_type:         Determines which pre-defined buttons will be shown (Default value = POPUP_BUTTONS_OK).
    :type button_type:          (int)
    :param button_color:        button color (foreground, background)
    :type button_color:         (str, str) | str
    :param background_color:    color of background
    :type background_color:     (str)
    :param text_color:          color of the text
    :type text_color:           (str)
    :param auto_close:          if True window will close itself
    :type auto_close:           (bool)
    :param auto_close_duration: Older versions only accept int. Time in seconds until window will close
    :type auto_close_duration:  int | float
    :param non_blocking:        if True the call will immediately return rather than waiting on user input
    :type non_blocking:         (bool)
    :param icon:                filename or base64 string to be used for the window's icon
    :type icon:                 bytes | str
    :param line_width:          Width of lines in characters
    :type line_width:           (int)
    :param font:                specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:                 (str or (str, int[, str]) or None)
    :param no_titlebar:         If True no titlebar will be shown
    :type no_titlebar:          (bool)
    :param grab_anywhere:       If True: can grab anywhere to move the window (Default = False)
    :type grab_anywhere:        (bool)
    :param keep_on_top:         If True the window will remain above all current windows
    :type keep_on_top:          (bool)
    :param location:            Location of upper left corner of the window
    :type location:             (int, int)
    :param relative_location:   (x,y) location relative to the default location of the window, in pixels. Normally the window centers.  This location is relative to the location the window would be created. Note they can be negative.
    :type relative_location:    (int, int)
    :param image:               Image to include at the top of the popup window
    :type image:                (str) or (bytes)
    :param modal:               If True then makes the popup will behave like a Modal window... all other windows are non-operational until this one is closed. Default = False
    :type modal:                bool
    :return:                    Returns text of the button that was pressed.  None will be returned if user closed window with X
    :rtype:                     str | None | TIMEOUT_KEY
    """

    return popup(
        *args,
        title=title,
        button_color=button_color,
        background_color=background_color,
        text_color=text_color,
        button_type=button_type,
        auto_close=auto_close,
        auto_close_duration=auto_close_duration,
        non_blocking=non_blocking,
        icon=icon,
        line_width=line_width,
        font=font,
        no_titlebar=no_titlebar,
        grab_anywhere=grab_anywhere,
        keep_on_top=keep_on_top,
        location=location,
        relative_location=relative_location,
        image=image,
        modal=modal,
    )


# --------------------------- popup_quick_message - a NonBlocking, Self-closing Popup with no titlebar and no buttons ---------------------------
def popup_quick_message(
    *args,
    title=None,
    button_type=POPUP_BUTTONS_NO_BUTTONS,
    button_color=None,
    background_color=None,
    text_color=None,
    auto_close=True,
    auto_close_duration=2,
    non_blocking=True,
    icon=None,
    line_width=None,
    font=None,
    no_titlebar=True,
    grab_anywhere=False,
    keep_on_top=True,
    location=(None, None),
    relative_location=(None, None),
    image=None,
    modal=False,
):
    """
    Show Popup window with no titlebar, doesn't block, and auto closes itself.

    :param title:               Title to display in the window.
    :type title:                (str)
    :param button_type:         Determines which pre-defined buttons will be shown (Default value = POPUP_BUTTONS_OK).
    :type button_type:          (int)
    :param button_color:        button color (foreground, background)
    :type button_color:         (str, str) | str
    :param keep_on_top:         If True the window will remain above all current windows
    :type keep_on_top:          (bool)
    :param background_color:    color of background
    :type background_color:     (str)
    :param text_color:          color of the text
    :type text_color:           (str)
    :param auto_close:          if True window will close itself
    :type auto_close:           (bool)
    :param auto_close_duration: Older versions only accept int. Time in seconds until window will close
    :type auto_close_duration:  int | float
    :param non_blocking:        if True the call will immediately return rather than waiting on user input
    :type non_blocking:         (bool)
    :param icon:                filename or base64 string to be used for the window's icon
    :type icon:                 bytes | str
    :param line_width:          Width of lines in characters
    :type line_width:           (int)
    :param font:                specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:                 (str or (str, int[, str]) or None)
    :param no_titlebar:         If True no titlebar will be shown
    :type no_titlebar:          (bool)
    :param grab_anywhere:       If True: can grab anywhere to move the window (Default = False)
    :type grab_anywhere:        (bool)
    :param location:            Location of upper left corner of the window
    :type location:             (int, int)
    :param relative_location:   (x,y) location relative to the default location of the window, in pixels. Normally the window centers.  This location is relative to the location the window would be created. Note they can be negative.
    :type relative_location:    (int, int)
    :param image:               Image to include at the top of the popup window
    :type image:                (str) or (bytes)
    :param modal:               If True then makes the popup will behave like a Modal window... all other windows are non-operational until this one is closed. Default = False
    :type modal:                bool
    :return:                    Returns text of the button that was pressed.  None will be returned if user closed window with X
    :rtype:                     str | None | TIMEOUT_KEY
    """
    return popup(
        *args,
        title=title,
        button_color=button_color,
        background_color=background_color,
        text_color=text_color,
        button_type=button_type,
        auto_close=auto_close,
        auto_close_duration=auto_close_duration,
        non_blocking=non_blocking,
        icon=icon,
        line_width=line_width,
        font=font,
        no_titlebar=no_titlebar,
        grab_anywhere=grab_anywhere,
        keep_on_top=keep_on_top,
        location=location,
        relative_location=relative_location,
        image=image,
        modal=modal,
    )


# --------------------------- PopupNoTitlebar ---------------------------
def popup_no_titlebar(
    *args,
    title=None,
    button_type=POPUP_BUTTONS_OK,
    button_color=None,
    background_color=None,
    text_color=None,
    auto_close=False,
    auto_close_duration=None,
    non_blocking=False,
    icon=None,
    line_width=None,
    font=None,
    grab_anywhere=True,
    keep_on_top=None,
    location=(None, None),
    relative_location=(None, None),
    image=None,
    modal=True,
):
    """
    Display a Popup without a titlebar.   Enables grab anywhere so you can move it

    :param title:               Title to display in the window.
    :type title:                (str)
    :param button_type:         Determines which pre-defined buttons will be shown (Default value = POPUP_BUTTONS_OK).
    :type button_type:          (int)
    :param button_color:        button color (foreground, background)
    :type button_color:         (str, str) | str
    :param background_color:    color of background
    :type background_color:     (str)
    :param text_color:          color of the text
    :type text_color:           (str)
    :param auto_close:          if True window will close itself
    :type auto_close:           (bool)
    :param auto_close_duration: Older versions only accept int. Time in seconds until window will close
    :type auto_close_duration:  int | float
    :param non_blocking:        if True the call will immediately return rather than waiting on user input
    :type non_blocking:         (bool)
    :param icon:                filename or base64 string to be used for the window's icon
    :type icon:                 bytes | str
    :param line_width:          Width of lines in characters
    :type line_width:           (int)
    :param font:                specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:                 (str or (str, int[, str]) or None)
    :param grab_anywhere:       If True: can grab anywhere to move the window (Default = False)
    :type grab_anywhere:        (bool)
    :param keep_on_top:         If True the window will remain above all current windows
    :type keep_on_top:          (bool)
    :param location:            Location of upper left corner of the window
    :type location:             (int, int)
    :param relative_location:   (x,y) location relative to the default location of the window, in pixels. Normally the window centers.  This location is relative to the location the window would be created. Note they can be negative.
    :type relative_location:    (int, int)
    :param image:               Image to include at the top of the popup window
    :type image:                (str) or (bytes)
    :param modal:               If True then makes the popup will behave like a Modal window... all other windows are non-operational until this one is closed. Default = True
    :type modal:                bool
    :return:                    Returns text of the button that was pressed.  None will be returned if user closed window with X
    :rtype:                     str | None | TIMEOUT_KEY
    """
    return popup(
        *args,
        title=title,
        button_color=button_color,
        background_color=background_color,
        text_color=text_color,
        button_type=button_type,
        auto_close=auto_close,
        auto_close_duration=auto_close_duration,
        non_blocking=non_blocking,
        icon=icon,
        line_width=line_width,
        font=font,
        no_titlebar=True,
        grab_anywhere=grab_anywhere,
        keep_on_top=keep_on_top,
        location=location,
        relative_location=relative_location,
        image=image,
        modal=modal,
    )


# --------------------------- PopupAutoClose ---------------------------
def popup_auto_close(
    *args,
    title=None,
    button_type=POPUP_BUTTONS_OK,
    button_color=None,
    background_color=None,
    text_color=None,
    auto_close=True,
    auto_close_duration=None,
    non_blocking=False,
    icon=None,
    line_width=None,
    font=None,
    no_titlebar=False,
    grab_anywhere=False,
    keep_on_top=None,
    location=(None, None),
    relative_location=(None, None),
    image=None,
    modal=True,
):
    """Popup that closes itself after some time period

    :param title:               Title to display in the window.
    :type title:                (str)
    :param button_type:         Determines which pre-defined buttons will be shown (Default value = POPUP_BUTTONS_OK).
    :type button_type:          (int)
    :param button_color:        button color (foreground, background)
    :type button_color:         (str, str) | str
    :param background_color:    color of background
    :type background_color:     (str)
    :param text_color:          color of the text
    :type text_color:           (str)
    :param auto_close:          if True window will close itself
    :type auto_close:           (bool)
    :param auto_close_duration: Older versions only accept int. Time in seconds until window will close
    :type auto_close_duration:  int | float
    :param non_blocking:        if True the call will immediately return rather than waiting on user input
    :type non_blocking:         (bool)
    :param icon:                filename or base64 string to be used for the window's icon
    :type icon:                 bytes | str
    :param line_width:          Width of lines in characters
    :type line_width:           (int)
    :param font:                specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:                 (str or (str, int[, str]) or None)
    :param no_titlebar:         If True no titlebar will be shown
    :type no_titlebar:          (bool)
    :param grab_anywhere:       If True: can grab anywhere to move the window (Default = False)
    :type grab_anywhere:        (bool)
    :param keep_on_top:         If True the window will remain above all current windows
    :type keep_on_top:          (bool)
    :param location:            Location of upper left corner of the window
    :type location:             (int, int)
    :param relative_location:   (x,y) location relative to the default location of the window, in pixels. Normally the window centers.  This location is relative to the location the window would be created. Note they can be negative.
    :type relative_location:    (int, int)
    :param image:               Image to include at the top of the popup window
    :type image:                (str) or (bytes)
    :param modal:               If True then makes the popup will behave like a Modal window... all other windows are non-operational until this one is closed. Default = True
    :type modal:                bool
    :return:                    Returns text of the button that was pressed.  None will be returned if user closed window with X
    :rtype:                     str | None | TIMEOUT_KEY
    """

    return popup(
        *args,
        title=title,
        button_color=button_color,
        background_color=background_color,
        text_color=text_color,
        button_type=button_type,
        auto_close=auto_close,
        auto_close_duration=auto_close_duration,
        non_blocking=non_blocking,
        icon=icon,
        line_width=line_width,
        font=font,
        no_titlebar=no_titlebar,
        grab_anywhere=grab_anywhere,
        keep_on_top=keep_on_top,
        location=location,
        relative_location=relative_location,
        image=image,
        modal=modal,
    )


# --------------------------- popup_error ---------------------------
def popup_error(
    *args,
    title=None,
    button_color=(None, None),
    background_color=None,
    text_color=None,
    auto_close=False,
    auto_close_duration=None,
    non_blocking=False,
    icon=None,
    line_width=None,
    font=None,
    no_titlebar=False,
    grab_anywhere=False,
    keep_on_top=None,
    location=(None, None),
    relative_location=(None, None),
    image=None,
    modal=True,
):
    """
    Popup with colored button and 'Error' as button text

    :param title:               Title to display in the window.
    :type title:                (str)
    :param button_color:        button color (foreground, background)
    :type button_color:         (str, str) | str
    :param background_color:    color of background
    :type background_color:     (str)
    :param text_color:          color of the text
    :type text_color:           (str)
    :param auto_close:          if True window will close itself
    :type auto_close:           (bool)
    :param auto_close_duration: Older versions only accept int. Time in seconds until window will close
    :type auto_close_duration:  int | float
    :param non_blocking:        if True the call will immediately return rather than waiting on user input
    :type non_blocking:         (bool)
    :param icon:                filename or base64 string to be used for the window's icon
    :type icon:                 bytes | str
    :param line_width:          Width of lines in characters
    :type line_width:           (int)
    :param font:                specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:                 (str or (str, int[, str]) or None)
    :param no_titlebar:         If True no titlebar will be shown
    :type no_titlebar:          (bool)
    :param grab_anywhere:       If True: can grab anywhere to move the window (Default = False)
    :type grab_anywhere:        (bool)
    :param keep_on_top:         If True the window will remain above all current windows
    :type keep_on_top:          (bool)
    :param location:            Location of upper left corner of the window
    :type location:             (int, int)
    :param relative_location:   (x,y) location relative to the default location of the window, in pixels. Normally the window centers.  This location is relative to the location the window would be created. Note they can be negative.
    :type relative_location:    (int, int)
    :param image:               Image to include at the top of the popup window
    :type image:                (str) or (bytes)
    :param modal:               If True then makes the popup will behave like a Modal window... all other windows are non-operational until this one is closed. Default = True
    :type modal:                bool
    :return:                    Returns text of the button that was pressed.  None will be returned if user closed window with X
    :rtype:                     str | None | TIMEOUT_KEY
    """
    tbutton_color = (
        DEFAULT_ERROR_BUTTON_COLOR if button_color == (None, None) else button_color
    )
    return popup(
        *args,
        title=title,
        button_type=POPUP_BUTTONS_ERROR,
        background_color=background_color,
        text_color=text_color,
        non_blocking=non_blocking,
        icon=icon,
        line_width=line_width,
        button_color=tbutton_color,
        auto_close=auto_close,
        auto_close_duration=auto_close_duration,
        font=font,
        no_titlebar=no_titlebar,
        grab_anywhere=grab_anywhere,
        keep_on_top=keep_on_top,
        location=location,
        relative_location=relative_location,
        image=image,
        modal=modal,
    )


# --------------------------- popup_cancel ---------------------------
def popup_cancel(
    *args,
    title=None,
    button_color=None,
    background_color=None,
    text_color=None,
    auto_close=False,
    auto_close_duration=None,
    non_blocking=False,
    icon=None,
    line_width=None,
    font=None,
    no_titlebar=False,
    grab_anywhere=False,
    keep_on_top=None,
    location=(None, None),
    relative_location=(None, None),
    image=None,
    modal=True,
):
    """
    Display Popup with "cancelled" button text

    :param title:               Title to display in the window.
    :type title:                (str)
    :param button_color:        button color (foreground, background)
    :type button_color:         (str, str) | str
    :param background_color:    color of background
    :type background_color:     (str)
    :param text_color:          color of the text
    :type text_color:           (str)
    :param auto_close:          if True window will close itself
    :type auto_close:           (bool)
    :param auto_close_duration: Older versions only accept int. Time in seconds until window will close
    :type auto_close_duration:  int | float
    :param non_blocking:        if True the call will immediately return rather than waiting on user input
    :type non_blocking:         (bool)
    :param icon:                filename or base64 string to be used for the window's icon
    :type icon:                 bytes | str
    :param line_width:          Width of lines in characters
    :type line_width:           (int)
    :param font:                specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:                 (str or (str, int[, str]) or None)
    :param no_titlebar:         If True no titlebar will be shown
    :type no_titlebar:          (bool)
    :param grab_anywhere:       If True: can grab anywhere to move the window (Default = False)
    :type grab_anywhere:        (bool)
    :param keep_on_top:         If True the window will remain above all current windows
    :type keep_on_top:          (bool)
    :param location:            Location of upper left corner of the window
    :type location:             (int, int)
    :param relative_location:   (x,y) location relative to the default location of the window, in pixels. Normally the window centers.  This location is relative to the location the window would be created. Note they can be negative.
    :type relative_location:    (int, int)
    :param image:               Image to include at the top of the popup window
    :type image:                (str) or (bytes)
    :param modal:               If True then makes the popup will behave like a Modal window... all other windows are non-operational until this one is closed. Default = True
    :type modal:                bool
    :return:                    Returns text of the button that was pressed.  None will be returned if user closed window with X
    :rtype:                     str | None | TIMEOUT_KEY
    """
    return popup(
        *args,
        title=title,
        button_type=POPUP_BUTTONS_CANCELLED,
        background_color=background_color,
        text_color=text_color,
        non_blocking=non_blocking,
        icon=icon,
        line_width=line_width,
        button_color=button_color,
        auto_close=auto_close,
        auto_close_duration=auto_close_duration,
        font=font,
        no_titlebar=no_titlebar,
        grab_anywhere=grab_anywhere,
        keep_on_top=keep_on_top,
        location=location,
        relative_location=relative_location,
        image=image,
        modal=modal,
    )


# --------------------------- popup_ok ---------------------------
def popup_ok(
    *args,
    title=None,
    button_color=None,
    background_color=None,
    text_color=None,
    auto_close=False,
    auto_close_duration=None,
    non_blocking=False,
    icon=None,
    line_width=None,
    font=None,
    no_titlebar=False,
    grab_anywhere=False,
    keep_on_top=None,
    location=(None, None),
    relative_location=(None, None),
    image=None,
    modal=True,
):
    """
    Display Popup with OK button only

    :param title:               Title to display in the window.
    :type title:                (str)
    :param button_color:        button color (foreground, background)
    :type button_color:         (str, str) | str
    :param background_color:    color of background
    :type background_color:     (str)
    :param text_color:          color of the text
    :type text_color:           (str)
    :param auto_close:          if True window will close itself
    :type auto_close:           (bool)
    :param auto_close_duration: Older versions only accept int. Time in seconds until window will close
    :type auto_close_duration:  int | float
    :param non_blocking:        if True the call will immediately return rather than waiting on user input
    :type non_blocking:         (bool)
    :param icon:                filename or base64 string to be used for the window's icon
    :type icon:                 bytes | str
    :param line_width:          Width of lines in characters
    :type line_width:           (int)
    :param font:                specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:                 (str or (str, int[, str]) or None)
    :param no_titlebar:         If True no titlebar will be shown
    :type no_titlebar:          (bool)
    :param grab_anywhere:       If True: can grab anywhere to move the window (Default = False)
    :type grab_anywhere:        (bool)
    :param keep_on_top:         If True the window will remain above all current windows
    :type keep_on_top:          (bool)
    :param location:            Location of upper left corner of the window
    :type location:             (int, int)
    :param relative_location:   (x,y) location relative to the default location of the window, in pixels. Normally the window centers.  This location is relative to the location the window would be created. Note they can be negative.
    :type relative_location:    (int, int)
    :param image:               Image to include at the top of the popup window
    :type image:                (str) or (bytes)
    :param modal:               If True then makes the popup will behave like a Modal window... all other windows are non-operational until this one is closed. Default = True
    :type modal:                bool
    :return:                    Returns text of the button that was pressed.  None will be returned if user closed window with X
    :rtype:                     str | None | TIMEOUT_KEY
    """
    return popup(
        *args,
        title=title,
        button_type=POPUP_BUTTONS_OK,
        background_color=background_color,
        text_color=text_color,
        non_blocking=non_blocking,
        icon=icon,
        line_width=line_width,
        button_color=button_color,
        auto_close=auto_close,
        auto_close_duration=auto_close_duration,
        font=font,
        no_titlebar=no_titlebar,
        grab_anywhere=grab_anywhere,
        keep_on_top=keep_on_top,
        location=location,
        relative_location=relative_location,
        image=image,
        modal=modal,
    )


# --------------------------- popup_ok_cancel ---------------------------
def popup_ok_cancel(
    *args,
    title=None,
    button_color=None,
    background_color=None,
    text_color=None,
    auto_close=False,
    auto_close_duration=None,
    non_blocking=False,
    icon=DEFAULT_WINDOW_ICON,
    line_width=None,
    font=None,
    no_titlebar=False,
    grab_anywhere=False,
    keep_on_top=None,
    location=(None, None),
    relative_location=(None, None),
    image=None,
    modal=True,
):
    """
    Display popup with OK and Cancel buttons

    :param title:               Title to display in the window.
    :type title:                (str)
    :param button_color:        button color (foreground, background)
    :type button_color:         (str, str) | str
    :param background_color:    color of background
    :type background_color:     (str)
    :param text_color:          color of the text
    :type text_color:           (str)
    :param auto_close:          if True window will close itself
    :type auto_close:           (bool)
    :param auto_close_duration: Older versions only accept int. Time in seconds until window will close
    :type auto_close_duration:  int | float
    :param non_blocking:        if True the call will immediately return rather than waiting on user input
    :type non_blocking:         (bool)
    :param icon:                filename or base64 string to be used for the window's icon
    :type icon:                 bytes | str
    :param line_width:          Width of lines in characters
    :type line_width:           (int)
    :param font:                specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:                 (str or (str, int[, str]) or None)
    :param no_titlebar:         If True no titlebar will be shown
    :type no_titlebar:          (bool)
    :param grab_anywhere:       If True: can grab anywhere to move the window (Default = False)
    :type grab_anywhere:        (bool)
    :param keep_on_top:         If True the window will remain above all current windows
    :type keep_on_top:          (bool)
    :param location:            Location of upper left corner of the window
    :type location:             (int, int)
    :param relative_location:   (x,y) location relative to the default location of the window, in pixels. Normally the window centers.  This location is relative to the location the window would be created. Note they can be negative.
    :type relative_location:    (int, int)
    :param image:               Image to include at the top of the popup window
    :type image:                (str) or (bytes)
    :param modal:               If True then makes the popup will behave like a Modal window... all other windows are non-operational until this one is closed. Default = True
    :type modal:                bool
    :return:                    clicked button
    :rtype:                     "OK" | "Cancel" | None
    """
    return popup(
        *args,
        title=title,
        button_type=POPUP_BUTTONS_OK_CANCEL,
        background_color=background_color,
        text_color=text_color,
        non_blocking=non_blocking,
        icon=icon,
        line_width=line_width,
        button_color=button_color,
        auto_close=auto_close,
        auto_close_duration=auto_close_duration,
        font=font,
        no_titlebar=no_titlebar,
        grab_anywhere=grab_anywhere,
        keep_on_top=keep_on_top,
        location=location,
        relative_location=relative_location,
        image=image,
        modal=modal,
    )


# --------------------------- popup_yes_no ---------------------------
def popup_yes_no(
    *args,
    title=None,
    button_color=None,
    background_color=None,
    text_color=None,
    auto_close=False,
    auto_close_duration=None,
    non_blocking=False,
    icon=None,
    line_width=None,
    font=None,
    no_titlebar=False,
    grab_anywhere=False,
    keep_on_top=None,
    location=(None, None),
    relative_location=(None, None),
    image=None,
    modal=True,
):
    """
    Display Popup with Yes and No buttons

    :param title:               Title to display in the window.
    :type title:                (str)
    :param button_color:        button color (foreground, background)
    :type button_color:         (str, str) | str
    :param background_color:    color of background
    :type background_color:     (str)
    :param text_color:          color of the text
    :type text_color:           (str)
    :param auto_close:          if True window will close itself
    :type auto_close:           (bool)
    :param auto_close_duration: Older versions only accept int. Time in seconds until window will close
    :type auto_close_duration:  int | float
    :param non_blocking:        if True the call will immediately return rather than waiting on user input
    :type non_blocking:         (bool)
    :param icon:                filename or base64 string to be used for the window's icon
    :type icon:                 bytes | str
    :param line_width:          Width of lines in characters
    :type line_width:           (int)
    :param font:                specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:                 (str or (str, int[, str]) or None)
    :param no_titlebar:         If True no titlebar will be shown
    :type no_titlebar:          (bool)
    :param grab_anywhere:       If True: can grab anywhere to move the window (Default = False)
    :type grab_anywhere:        (bool)
    :param keep_on_top:         If True the window will remain above all current windows
    :type keep_on_top:          (bool)
    :param location:            Location of upper left corner of the window
    :type location:             (int, int)
    :param relative_location:   (x,y) location relative to the default location of the window, in pixels. Normally the window centers.  This location is relative to the location the window would be created. Note they can be negative.
    :type relative_location:    (int, int)
    :param image:               Image to include at the top of the popup window
    :type image:                (str) or (bytes)
    :param modal:               If True then makes the popup will behave like a Modal window... all other windows are non-operational until this one is closed. Default = True
    :type modal:                bool
    :return:                    clicked button
    :rtype:                     "Yes" | "No" | None
    """
    return popup(
        *args,
        title=title,
        button_type=POPUP_BUTTONS_YES_NO,
        background_color=background_color,
        text_color=text_color,
        non_blocking=non_blocking,
        icon=icon,
        line_width=line_width,
        button_color=button_color,
        auto_close=auto_close,
        auto_close_duration=auto_close_duration,
        font=font,
        no_titlebar=no_titlebar,
        grab_anywhere=grab_anywhere,
        keep_on_top=keep_on_top,
        location=location,
        relative_location=relative_location,
        image=image,
        modal=modal,
    )


##############################################################################
#   The popup_get_____ functions - Will return user input                     #
##############################################################################

# --------------------------- popup_get_folder ---------------------------


def popup_get_folder(
    message,
    title=None,
    default_path="",
    no_window=False,
    size=(None, None),
    button_color=None,
    background_color=None,
    text_color=None,
    icon=None,
    font=None,
    no_titlebar=False,
    grab_anywhere=False,
    keep_on_top=None,
    location=(None, None),
    relative_location=(None, None),
    initial_folder=None,
    image=None,
    modal=True,
    history=False,
    history_setting_filename=None,
):
    """
    Display popup with text entry field and browse button so that a folder can be chosen.

    :param message:                  message displayed to user
    :type message:                   (str)
    :param title:                    Window title
    :type title:                     (str)
    :param default_path:             path to display to user as starting point (filled into the input field)
    :type default_path:              (str)
    :param no_window:                if True, no PySimpleGUI window will be shown. Instead just the tkinter dialog is shown
    :type no_window:                 (bool)
    :param size:                     (width, height) of the InputText Element
    :type size:                      (int, int)
    :param button_color:             button color (foreground, background)
    :type button_color:              (str, str) | str
    :param background_color:         color of background
    :type background_color:          (str)
    :param text_color:               color of the text
    :type text_color:                (str)
    :param icon:                     filename or base64 string to be used for the window's icon
    :type icon:                      bytes | str
    :param font:                     specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:                      (str or (str, int[, str]) or None)
    :param no_titlebar:              If True no titlebar will be shown
    :type no_titlebar:               (bool)
    :param grab_anywhere:            If True: can grab anywhere to move the window (Default = False)
    :type grab_anywhere:             (bool)
    :param keep_on_top:              If True the window will remain above all current windows
    :type keep_on_top:               (bool)
    :param location:                 Location of upper left corner of the window
    :type location:                  (int, int)
    :param relative_location:        (x,y) location relative to the default location of the window, in pixels. Normally the window centers.  This location is relative to the location the window would be created. Note they can be negative.
    :type relative_location:         (int, int)
    :param initial_folder:           location in filesystem to begin browsing
    :type initial_folder:            (str)
    :param image:                    Image to include at the top of the popup window
    :type image:                     (str) or (bytes)
    :param modal:                    If True then makes the popup will behave like a Modal window... all other windows are non-operational until this one is closed. Default = True
    :type modal:                     bool
    :param history:                  If True then enable a "history" feature that will display previous entries used. Uses settings filename provided or default if none provided
    :type history:                   bool
    :param history_setting_filename: Filename to use for the User Settings. Will store list of previous entries in this settings file
    :type history_setting_filename:  (str)
    :return:                         string representing the path chosen, None if cancelled or window closed with X
    :rtype:                          str | None
    """

    # First setup the history settings file if history feature is enabled
    if history and history_setting_filename is not None:
        try:
            history_settings = UserSettings(history_setting_filename)
        except Exception as e:
            _error_popup_with_traceback(
                "popup_get_folder - Something is wrong with your supplied history settings filename",
                "Exception: {}".format(e),
            )
            return None
    elif history:
        history_settings_filename = os.path.basename(inspect.stack()[1].filename)
        history_settings_filename = (
            os.path.splitext(history_settings_filename)[0] + ".json"
        )
        history_settings = UserSettings(history_settings_filename)
    else:
        history_settings = None

    # global _my_windows
    if no_window:
        _get_hidden_master_root()
        root = tk.Toplevel()

        try:
            root.attributes(
                "-alpha", 0
            )  # hide window while building it. makes for smoother 'paint'
            # if not running_mac():
            try:
                root.wm_overrideredirect(True)
            except Exception as e:
                print(
                    "* Error performing wm_overrideredirect while hiding the window during creation in get folder *",
                    e,
                )
            root.withdraw()
        except Exception:
            pass
        folder_name = tk.filedialog.askdirectory(
            initialdir=initial_folder
        )  # show the 'get folder' dialog box

        root.destroy()

        return folder_name

    browse_button = FolderBrowse(initial_folder=initial_folder)

    if image is not None:
        if isinstance(image, str):
            layout = [[Image(filename=image)]]
        else:
            layout = [[Image(data=image)]]
    else:
        layout = [[]]

    layout += [
        [
            Text(
                message,
                auto_size_text=True,
                text_color=text_color,
                background_color=background_color,
            )
        ]
    ]

    if not history:
        layout += [
            [
                InputText(default_text=default_path, size=size, key="-INPUT-"),
                browse_button,
            ]
        ]
    else:
        file_list = history_settings.get("-PSG folder list-", [])
        last_entry = file_list[0] if file_list else ""
        layout += [
            [
                Combo(
                    file_list,
                    default_value=last_entry,
                    key="-INPUT-",
                    size=size if size != (None, None) else (80, 1),
                    bind_return_key=True,
                ),
                browse_button,
                Button(
                    "Clear History",
                    tooltip="Clears the list of folders shown in the combobox",
                ),
            ]
        ]

    layout += [
        [Button("Ok", size=(6, 1), bind_return_key=True), Button("Cancel", size=(6, 1))]
    ]

    window = Window(
        title=title or message,
        layout=layout,
        icon=icon,
        auto_size_text=True,
        button_color=button_color,
        font=font,
        background_color=background_color,
        no_titlebar=no_titlebar,
        grab_anywhere=grab_anywhere,
        keep_on_top=keep_on_top,
        location=location,
        relative_location=relative_location,
        modal=modal,
    )

    while True:
        event, values = window.read()
        if event in ("Cancel", WIN_CLOSED):
            break
        elif event == "Clear History":
            history_settings.set("-PSG folder list-", [])
            window["-INPUT-"].update("", [])
            popup_quick_message(
                "History of Previous Choices Cleared",
                background_color="red",
                text_color="white",
                font="_ 20",
                keep_on_top=True,
            )
        elif event in ("Ok", "-INPUT-"):
            if values["-INPUT-"] != "":
                if history_settings is not None:
                    list_of_entries = history_settings.get("-PSG folder list-", [])
                    if values["-INPUT-"] in list_of_entries:
                        list_of_entries.remove(values["-INPUT-"])
                    list_of_entries.insert(0, values["-INPUT-"])
                    history_settings.set("-PSG folder list-", list_of_entries)
            break

    window.close()
    del window
    if event in ("Cancel", WIN_CLOSED):
        return None

    return values["-INPUT-"]


# --------------------------- popup_get_file ---------------------------


def popup_get_file(
    message,
    title=None,
    default_path="",
    default_extension="",
    save_as=False,
    multiple_files=False,
    file_types=FILE_TYPES_ALL_FILES,
    no_window=False,
    size=(None, None),
    button_color=None,
    background_color=None,
    text_color=None,
    icon=None,
    font=None,
    no_titlebar=False,
    grab_anywhere=False,
    keep_on_top=None,
    location=(None, None),
    relative_location=(None, None),
    initial_folder=None,
    image=None,
    files_delimiter=BROWSE_FILES_DELIMITER,
    modal=True,
    history=False,
    show_hidden=True,
    history_setting_filename=None,
):
    """
    Display popup window with text entry field and browse button so that a file can be chosen by user.

    :param message:                  message displayed to user
    :type message:                   (str)
    :param title:                    Window title
    :type title:                     (str)
    :param default_path:             path to display to user as starting point (filled into the input field)
    :type default_path:              (str)
    :param default_extension:        If no extension entered by user, add this to filename (only used in saveas dialogs)
    :type default_extension:         (str)
    :param save_as:                  if True, the "save as" dialog is shown which will verify before overwriting
    :type save_as:                   (bool)
    :param multiple_files:           if True, then allows multiple files to be selected that are returned with ';' between each filename
    :type multiple_files:            (bool)
    :param file_types:               List of extensions to show using wildcards. All files (the default) = (("ALL Files", "*.* *"),).
    :type file_types:                Tuple[Tuple[str,str]]
    :param no_window:                if True, no PySimpleGUI window will be shown. Instead just the tkinter dialog is shown
    :type no_window:                 (bool)
    :param size:                     (width, height) of the InputText Element or Combo element if using history feature
    :type size:                      (int, int)
    :param button_color:             Color of the button (text, background)
    :type button_color:              (str, str) | str
    :param background_color:         background color of the entire window
    :type background_color:          (str)
    :param text_color:               color of the text
    :type text_color:                (str)
    :param icon:                     filename or base64 string to be used for the window's icon
    :type icon:                      bytes | str
    :param font:                     specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:                      (str or (str, int[, str]) or None)
    :param no_titlebar:              If True no titlebar will be shown
    :type no_titlebar:               (bool)
    :param grab_anywhere:            If True: can grab anywhere to move the window (Default = False)
    :type grab_anywhere:             (bool)
    :param keep_on_top:              If True the window will remain above all current windows
    :type keep_on_top:               (bool)
    :param location:                 Location of upper left corner of the window
    :type location:                  (int, int)
    :param relative_location:        (x,y) location relative to the default location of the window, in pixels. Normally the window centers.  This location is relative to the location the window would be created. Note they can be negative.
    :type relative_location:         (int, int)
    :param initial_folder:           location in filesystem to begin browsing
    :type initial_folder:            (str)
    :param image:                    Image to include at the top of the popup window
    :type image:                     (str) or (bytes)
    :param files_delimiter:          String to place between files when multiple files are selected. Normally a ;
    :type files_delimiter:           str
    :param modal:                    If True then makes the popup will behave like a Modal window... all other windows are non-operational until this one is closed. Default = True
    :type modal:                     bool
    :param history:                  If True then enable a "history" feature that will display previous entries used. Uses settings filename provided or default if none provided
    :type history:                   bool
    :param show_hidden:              If True then enables the checkbox in the system dialog to select hidden files to be shown
    :type show_hidden:               bool
    :param history_setting_filename: Filename to use for the User Settings. Will store list of previous entries in this settings file
    :type history_setting_filename:  (str)
    :return:                         string representing the file(s) chosen, None if cancelled or window closed with X
    :rtype:                          str | None
    """

    # First setup the history settings file if history feature is enabled
    if history and history_setting_filename is not None:
        try:
            history_settings = UserSettings(history_setting_filename)
        except Exception as e:
            _error_popup_with_traceback(
                "popup_get_file - Something is wrong with your supplied history settings filename",
                "Exception: {}".format(e),
            )
            return None
    elif history:
        history_settings_filename = os.path.basename(inspect.stack()[1].filename)
        history_settings_filename = (
            os.path.splitext(history_settings_filename)[0] + ".json"
        )
        history_settings = UserSettings(history_settings_filename)
    else:
        history_settings = None

    if icon is None:
        icon = Window._user_defined_icon or DEFAULT_BASE64_ICON
    if no_window:
        _get_hidden_master_root()
        root = tk.Toplevel()

        try:
            root.attributes(
                "-alpha", 0
            )  # hide window while building it. makes for smoother 'paint'
            # if not running_mac():
            try:
                root.wm_overrideredirect(True)
            except Exception as e:
                print("* Error performing wm_overrideredirect in get file *", e)
            root.withdraw()
        except Exception:
            pass

        if not show_hidden:
            try:
                # call a dummy dialog with an impossible option to initialize the file
                # dialog without really getting a dialog window; this will throw a
                # TclError, so we need a try...except :
                try:
                    root.tk.call("tk_getOpenFile", "-foobarbaz")
                except tk.TclError:
                    pass
                # now set the magic variables accordingly
                root.tk.call("set", "::tk::dialog::file::showHiddenBtn", "1")
                root.tk.call("set", "::tk::dialog::file::showHiddenVar", "0")
            except Exception:
                pass

        if root and icon is not None:
            _set_icon_for_tkinter_window(root, icon=icon)
        # for Macs, setting parent=None fixes a warning problem.
        if save_as:
            if running_mac():
                is_all = [
                    (x, y) for (x, y) in file_types if all(ch in "* ." for ch in y)
                ]
                if not len(set(file_types)) > 1 and (
                    len(is_all) != 0 or file_types == FILE_TYPES_ALL_FILES
                ):
                    filename = tk.filedialog.asksaveasfilename(
                        initialdir=initial_folder,
                        initialfile=default_path,
                        defaultextension=default_extension,
                    )  # show the 'get file' dialog box
                else:
                    filename = tk.filedialog.asksaveasfilename(
                        filetypes=file_types,
                        initialdir=initial_folder,
                        initialfile=default_path,
                        defaultextension=default_extension,
                    )  # show the 'get file' dialog box
            else:
                filename = tk.filedialog.asksaveasfilename(
                    filetypes=file_types,
                    initialdir=initial_folder,
                    initialfile=default_path,
                    parent=root,
                    defaultextension=default_extension,
                )  # show the 'get file' dialog box
        elif multiple_files:
            if running_mac():
                is_all = [
                    (x, y) for (x, y) in file_types if all(ch in "* ." for ch in y)
                ]
                if not len(set(file_types)) > 1 and (
                    len(is_all) != 0 or file_types == FILE_TYPES_ALL_FILES
                ):
                    filename = tk.filedialog.askopenfilenames(
                        initialdir=initial_folder,
                        initialfile=default_path,
                        defaultextension=default_extension,
                    )  # show the 'get file' dialog box
                else:
                    filename = tk.filedialog.askopenfilenames(
                        filetypes=file_types,
                        initialdir=initial_folder,
                        initialfile=default_path,
                        defaultextension=default_extension,
                    )  # show the 'get file' dialog box
            else:
                filename = tk.filedialog.askopenfilenames(
                    filetypes=file_types,
                    initialdir=initial_folder,
                    initialfile=default_path,
                    parent=root,
                    defaultextension=default_extension,
                )  # show the 'get file' dialog box
        else:
            if running_mac():
                is_all = [
                    (x, y) for (x, y) in file_types if all(ch in "* ." for ch in y)
                ]
                if not len(set(file_types)) > 1 and (
                    len(is_all) != 0 or file_types == FILE_TYPES_ALL_FILES
                ):
                    filename = tk.filedialog.askopenfilename(
                        initialdir=initial_folder,
                        initialfile=default_path,
                        defaultextension=default_extension,
                    )  # show the 'get files' dialog box
                else:
                    filename = tk.filedialog.askopenfilename(
                        filetypes=file_types,
                        initialdir=initial_folder,
                        initialfile=default_path,
                        defaultextension=default_extension,
                    )  # show the 'get files' dialog box
            else:
                filename = tk.filedialog.askopenfilename(
                    filetypes=file_types,
                    initialdir=initial_folder,
                    initialfile=default_path,
                    parent=root,
                    defaultextension=default_extension,
                )  # show the 'get files' dialog box
        root.destroy()

        if not multiple_files and type(filename) in (tuple, list):
            if len(filename):  # only if not 0 length, otherwise will get an error
                filename = filename[0]
        if not filename:
            return None
        return filename

    if save_as:
        browse_button = SaveAs(
            file_types=file_types,
            initial_folder=initial_folder,
            default_extension=default_extension,
        )
    elif multiple_files:
        browse_button = FilesBrowse(
            file_types=file_types,
            initial_folder=initial_folder,
            files_delimiter=files_delimiter,
        )
    else:
        browse_button = FileBrowse(file_types=file_types, initial_folder=initial_folder)

    if image is not None:
        if isinstance(image, str):
            layout = [[Image(filename=image)]]
        else:
            layout = [[Image(data=image)]]
    else:
        layout = [[]]

    layout += [
        [
            Text(
                message,
                auto_size_text=True,
                text_color=text_color,
                background_color=background_color,
            )
        ]
    ]

    if not history:
        layout += [
            [
                InputText(default_text=default_path, size=size, key="-INPUT-"),
                browse_button,
            ]
        ]
    else:
        file_list = history_settings.get("-PSG file list-", [])
        last_entry = file_list[0] if file_list else ""
        layout += [
            [
                Combo(
                    file_list,
                    default_value=last_entry,
                    key="-INPUT-",
                    size=size if size != (None, None) else (80, 1),
                    bind_return_key=True,
                ),
                browse_button,
                Button(
                    "Clear History",
                    tooltip="Clears the list of files shown in the combobox",
                ),
            ]
        ]

    layout += [
        [Button("Ok", size=(6, 1), bind_return_key=True), Button("Cancel", size=(6, 1))]
    ]

    window = Window(
        title=title or message,
        layout=layout,
        icon=icon,
        auto_size_text=True,
        button_color=button_color,
        font=font,
        background_color=background_color,
        no_titlebar=no_titlebar,
        grab_anywhere=grab_anywhere,
        keep_on_top=keep_on_top,
        location=location,
        relative_location=relative_location,
        modal=modal,
        finalize=True,
    )

    if running_linux() and show_hidden is True:
        window.TKroot.tk.eval(
            "catch {tk_getOpenFile -badoption}"
        )  # dirty hack to force autoloading of Tk's file dialog code
        window.TKroot.setvar(
            "::tk::dialog::file::showHiddenBtn", 1
        )  # enable the "show hidden files" checkbox (it's necessary)
        window.TKroot.setvar(
            "::tk::dialog::file::showHiddenVar", 0
        )  # start with the hidden files... well... hidden

    while True:
        event, values = window.read()
        if event in ("Cancel", WIN_CLOSED):
            break
        elif event == "Clear History":
            history_settings.set("-PSG file list-", [])
            window["-INPUT-"].update("", [])
            popup_quick_message(
                "History of Previous Choices Cleared",
                background_color="red",
                text_color="white",
                font="_ 20",
                keep_on_top=True,
            )
        elif event in ("Ok", "-INPUT-"):
            if values["-INPUT-"] != "":
                if history_settings is not None:
                    list_of_entries = history_settings.get("-PSG file list-", [])
                    if values["-INPUT-"] in list_of_entries:
                        list_of_entries.remove(values["-INPUT-"])
                    list_of_entries.insert(0, values["-INPUT-"])
                    history_settings.set("-PSG file list-", list_of_entries)
            break

    window.close()
    del window
    if event in ("Cancel", WIN_CLOSED):
        return None

    return values["-INPUT-"]


# --------------------------- popup_get_text ---------------------------


def popup_get_text(
    message,
    title=None,
    default_text="",
    password_char="",
    size=(None, None),
    button_color=None,
    background_color=None,
    text_color=None,
    icon=None,
    font=None,
    no_titlebar=False,
    grab_anywhere=False,
    keep_on_top=None,
    location=(None, None),
    relative_location=(None, None),
    image=None,
    history=False,
    history_setting_filename=None,
    modal=True,
):
    """
    Display Popup with text entry field. Returns the text entered or None if closed / cancelled

    :param message:                  message displayed to user
    :type message:                   (str)
    :param title:                    Window title
    :type title:                     (str)
    :param default_text:             default value to put into input area
    :type default_text:              (str)
    :param password_char:            character to be shown instead of actually typed characters. WARNING - if history=True then can't hide passwords
    :type password_char:             (str)
    :param size:                     (width, height) of the InputText Element
    :type size:                      (int, int)
    :param button_color:             Color of the button (text, background)
    :type button_color:              (str, str) | str
    :param background_color:         background color of the entire window
    :type background_color:          (str)
    :param text_color:               color of the message text
    :type text_color:                (str)
    :param icon:                     filename or base64 string to be used for the window's icon
    :type icon:                      bytes | str
    :param font:                     specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:                      (str or (str, int[, str]) or None)
    :param no_titlebar:              If True no titlebar will be shown
    :type no_titlebar:               (bool)
    :param grab_anywhere:            If True can click and drag anywhere in the window to move the window
    :type grab_anywhere:             (bool)
    :param keep_on_top:              If True the window will remain above all current windows
    :type keep_on_top:               (bool)
    :param location:                 (x,y) Location on screen to display the upper left corner of window
    :type location:                  (int, int)
    :param relative_location:        (x,y) location relative to the default location of the window, in pixels. Normally the window centers.  This location is relative to the location the window would be created. Note they can be negative.
    :type relative_location:         (int, int)
    :param image:                    Image to include at the top of the popup window
    :type image:                     (str) or (bytes)
    :param history:                  If True then enable a "history" feature that will display previous entries used. Uses settings filename provided or default if none provided
    :type history:                   bool
    :param history_setting_filename: Filename to use for the User Settings. Will store list of previous entries in this settings file
    :type history_setting_filename:  (str)
    :param modal:                    If True then makes the popup will behave like a Modal window... all other windows are non-operational until this one is closed. Default = True
    :type modal:                     bool
    :return:                         Text entered or None if window was closed or cancel button clicked
    :rtype:                          str | None
    """

    # First setup the history settings file if history feature is enabled
    if history and history_setting_filename is not None:
        try:
            history_settings = UserSettings(history_setting_filename)
        except Exception as e:
            _error_popup_with_traceback(
                "popup_get_file - Something is wrong with your supplied history settings filename",
                "Exception: {}".format(e),
            )
            return None
    elif history:
        history_settings_filename = os.path.basename(inspect.stack()[1].filename)
        history_settings_filename = (
            os.path.splitext(history_settings_filename)[0] + ".json"
        )
        history_settings = UserSettings(history_settings_filename)
    else:
        history_settings = None

    if image is not None:
        if isinstance(image, str):
            layout = [[Image(filename=image)]]
        else:
            layout = [[Image(data=image)]]
    else:
        layout = [[]]

    layout += [
        [
            Text(
                message,
                auto_size_text=True,
                text_color=text_color,
                background_color=background_color,
            )
        ]
    ]
    if not history:
        layout += [
            [
                InputText(
                    default_text=default_text,
                    size=size,
                    key="-INPUT-",
                    password_char=password_char,
                )
            ]
        ]
    else:
        text_list = history_settings.get("-PSG text list-", [])
        last_entry = text_list[0] if text_list else default_text
        layout += [
            [
                Combo(
                    text_list,
                    default_value=last_entry,
                    key="-INPUT-",
                    size=size if size != (None, None) else (80, 1),
                    bind_return_key=True,
                ),
                Button(
                    "Clear History",
                    tooltip="Clears the list of files shown in the combobox",
                ),
            ]
        ]

    layout += [
        [Button("Ok", size=(6, 1), bind_return_key=True), Button("Cancel", size=(6, 1))]
    ]

    window = Window(
        title=title or message,
        layout=layout,
        icon=icon,
        auto_size_text=True,
        button_color=button_color,
        no_titlebar=no_titlebar,
        background_color=background_color,
        grab_anywhere=grab_anywhere,
        keep_on_top=keep_on_top,
        location=location,
        relative_location=relative_location,
        finalize=True,
        modal=modal,
        font=font,
    )

    while True:
        event, values = window.read()
        if event in ("Cancel", WIN_CLOSED):
            break
        elif event == "Clear History":
            history_settings.set("-PSG text list-", [])
            window["-INPUT-"].update("", [])
            popup_quick_message(
                "History of Previous Choices Cleared",
                background_color="red",
                text_color="white",
                font="_ 20",
                keep_on_top=True,
            )
        elif event in ("Ok", "-INPUT-"):
            if values["-INPUT-"] != "":
                if history_settings is not None:
                    list_of_entries = history_settings.get("-PSG text list-", [])
                    if values["-INPUT-"] in list_of_entries:
                        list_of_entries.remove(values["-INPUT-"])
                    list_of_entries.insert(0, values["-INPUT-"])
                    history_settings.set("-PSG text list-", list_of_entries)
            break

    window.close()
    del window
    if event in ("Cancel", WIN_CLOSED):
        return None
    else:
        text = values["-INPUT-"]
        return text


def popup_get_date(
    start_mon=None,
    start_day=None,
    start_year=None,
    begin_at_sunday_plus=0,
    no_titlebar=True,
    title="Choose Date",
    keep_on_top=True,
    location=(None, None),
    relative_location=(None, None),
    close_when_chosen=False,
    icon=None,
    locale=None,
    month_names=None,
    day_abbreviations=None,
    day_font="TkFixedFont 9",
    mon_year_font="TkFixedFont 10",
    arrow_font="TkFixedFont 7",
    modal=True,
):
    """
    Display a calendar window, get the user's choice, return as a tuple (mon, day, year)

    :param start_mon:            The starting month
    :type start_mon:             (int)
    :param start_day:            The starting day - optional. Set to None or 0 if no date to be chosen at start
    :type start_day:             int | None
    :param start_year:           The starting year
    :type start_year:            (int)
    :param begin_at_sunday_plus: Determines the left-most day in the display. 0=sunday, 1=monday, etc
    :type begin_at_sunday_plus:  (int)
    :param icon:                 Same as Window icon parameter. Can be either a filename or Base64 value. For Windows if filename, it MUST be ICO format. For Linux, must NOT be ICO
    :type icon:                  (str | bytes)
    :param location:             (x,y) location on the screen to place the top left corner of your window. Default is to center on screen
    :type location:              (int, int)
    :param relative_location:    (x,y) location relative to the default location of the window, in pixels. Normally the window centers.  This location is relative to the location the window would be created. Note they can be negative.
    :type relative_location:     (int, int)
    :param title:                Title that will be shown on the window
    :type title:                 (str)
    :param close_when_chosen:    If True, the window will close and function return when a day is clicked
    :type close_when_chosen:     (bool)
    :param locale:               locale used to get the day names
    :type locale:                (str)
    :param no_titlebar:          If True no titlebar will be shown
    :type no_titlebar:           (bool)
    :param keep_on_top:          If True the window will remain above all current windows
    :type keep_on_top:           (bool)
    :param month_names:          optional list of month names to use (should be 12 items)
    :type month_names:           List[str]
    :param day_abbreviations:    optional list of abbreviations to display as the day of week
    :type day_abbreviations:     List[str]
    :param day_font:             Font and size to use for the calendar
    :type day_font:              str | tuple
    :param mon_year_font:        Font and size to use for the month and year at the top
    :type mon_year_font:         str | tuple
    :param arrow_font:           Font and size to use for the arrow buttons
    :type arrow_font:            str | tuple
    :param modal:                If True then makes the popup will behave like a Modal window... all other windows are non-operational until this one is closed. Default = True
    :type modal:                 bool
    :return:                     Tuple containing (month, day, year) of chosen date or None if was cancelled
    :rtype:                      None | (int, int, int)
    """

    if month_names is not None and len(month_names) != 12:
        if not SUPPRESS_ERROR_POPUPS:
            popup_error(
                "Incorrect month names list specified. Must have 12 entries.",
                "Your list:",
                month_names,
            )

    if day_abbreviations is not None and len(day_abbreviations) != 7:
        if not SUPPRESS_ERROR_POPUPS:
            popup_error(
                "Incorrect day abbreviation list. Must have 7 entries.",
                "Your list:",
                day_abbreviations,
            )

    now = datetime.datetime.now()
    cur_month, cur_day, cur_year = now.month, now.day, now.year
    cur_month = start_mon or cur_month
    if start_mon is not None:
        cur_day = start_day
    else:
        cur_day = cur_day
    cur_year = start_year or cur_year

    def update_days(window, month, year, begin_at_sunday_plus):
        [window[(week, day)].update("") for day in range(7) for week in range(6)]
        weeks = calendar.monthcalendar(year, month)
        month_days = list(
            itertools.chain.from_iterable(
                [[0 for _ in range(8 - begin_at_sunday_plus)]] + weeks
            )
        )
        if month_days[6] == 0:
            month_days = month_days[7:]
            if month_days[6] == 0:
                month_days = month_days[7:]
        for i, day in enumerate(month_days):
            offset = i
            if offset >= 6 * 7:
                break
            window[(offset // 7, offset % 7)].update(str(day) if day else "")

    def make_days_layout():
        days_layout = []
        for week in range(6):
            row = []
            for day in range(7):
                row.append(
                    T(
                        "",
                        size=(4, 1),
                        justification="c",
                        font=day_font,
                        key=(week, day),
                        enable_events=True,
                        pad=(0, 0),
                    )
                )
            days_layout.append(row)
        return days_layout

    # Create table of month names and week day abbreviations

    if day_abbreviations is None or len(day_abbreviations) != 7:
        fwday = calendar.SUNDAY
        try:
            if locale is not None:
                _cal = calendar.LocaleTextCalendar(fwday, locale)
            else:
                _cal = calendar.TextCalendar(fwday)
            day_names = _cal.formatweekheader(3).split()
        except Exception as e:
            print("Exception building day names from locale", locale, e)
            day_names = ("Sun", "Mon", "Tue", "Wed", "Th", "Fri", "Sat")
    else:
        day_names = day_abbreviations

    mon_names = (
        month_names
        if month_names is not None and len(month_names) == 12
        else [calendar.month_name[i] for i in range(1, 13)]
    )
    days_layout = make_days_layout()

    layout = [
        [
            B(
                "◄◄",
                font=arrow_font,
                border_width=0,
                key="-YEAR-DOWN-",
                pad=((10, 2), 2),
            ),
            B("◄", font=arrow_font, border_width=0, key="-MON-DOWN-", pad=(0, 2)),
            Text(
                "{} {}".format(mon_names[cur_month - 1], cur_year),
                size=(16, 1),
                justification="c",
                font=mon_year_font,
                key="-MON-YEAR-",
                pad=(0, 2),
            ),
            B("►", font=arrow_font, border_width=0, key="-MON-UP-", pad=(0, 2)),
            B("►►", font=arrow_font, border_width=0, key="-YEAR-UP-", pad=(2, 2)),
        ]
    ]
    layout += [
        [
            Col(
                [
                    [
                        T(
                            day_names[i - (7 - begin_at_sunday_plus) % 7],
                            size=(4, 1),
                            font=day_font,
                            background_color=theme_text_color(),
                            text_color=theme_background_color(),
                            pad=(0, 0),
                        )
                        for i in range(7)
                    ]
                ],
                background_color=theme_text_color(),
                pad=(0, 0),
            )
        ]
    ]
    layout += days_layout
    if not close_when_chosen:
        layout += [
            [
                Button("Ok", border_width=0, font="TkFixedFont 8"),
                Button("Cancel", border_width=0, font="TkFixedFont 8"),
            ]
        ]

    window = Window(
        title,
        layout,
        no_titlebar=no_titlebar,
        grab_anywhere=True,
        keep_on_top=keep_on_top,
        font="TkFixedFont 12",
        use_default_focus=False,
        location=location,
        relative_location=relative_location,
        finalize=True,
        icon=icon,
    )

    update_days(window, cur_month, cur_year, begin_at_sunday_plus)

    prev_choice = chosen_mon_day_year = None

    if cur_day:
        chosen_mon_day_year = cur_month, cur_day, cur_year
        for week in range(6):
            for day in range(7):
                if window[(week, day)].DisplayText == str(cur_day):
                    window[(week, day)].update(
                        background_color=theme_text_color(),
                        text_color=theme_background_color(),
                    )
                    prev_choice = (week, day)
                    break

    if modal or DEFAULT_MODAL_WINDOWS_FORCED:
        window.make_modal()

    while True:  # Event Loop
        event, values = window.read()
        if event in (None, "Cancel"):
            chosen_mon_day_year = None
            break
        if event == "Ok":
            break
        if event in ("-MON-UP-", "-MON-DOWN-", "-YEAR-UP-", "-YEAR-DOWN-"):
            cur_month += event == "-MON-UP-"
            cur_month -= event == "-MON-DOWN-"
            cur_year += event == "-YEAR-UP-"
            cur_year -= event == "-YEAR-DOWN-"
            if cur_month > 12:
                cur_month = 1
                cur_year += 1
            elif cur_month < 1:
                cur_month = 12
                cur_year -= 1
            window["-MON-YEAR-"].update(
                "{} {}".format(mon_names[cur_month - 1], cur_year)
            )
            update_days(window, cur_month, cur_year, begin_at_sunday_plus)
            if prev_choice:
                window[prev_choice].update(
                    background_color=theme_background_color(),
                    text_color=theme_text_color(),
                )
        elif type(event) is tuple:
            if window[event].DisplayText != "":
                chosen_mon_day_year = (
                    cur_month,
                    int(window[event].DisplayText),
                    cur_year,
                )
                if prev_choice:
                    window[prev_choice].update(
                        background_color=theme_background_color(),
                        text_color=theme_text_color(),
                    )
                window[event].update(
                    background_color=theme_text_color(),
                    text_color=theme_background_color(),
                )
                prev_choice = event
                if close_when_chosen:
                    break
    window.close()
    return chosen_mon_day_year


# --------------------------- PopupAnimated ---------------------------


def popup_animated(
    image_source,
    message=None,
    background_color=None,
    text_color=None,
    font=None,
    no_titlebar=True,
    grab_anywhere=True,
    keep_on_top=True,
    location=(None, None),
    relative_location=(None, None),
    alpha_channel=None,
    time_between_frames=0,
    transparent_color=None,
    title="",
    icon=None,
    no_buffering=False,
):
    """
     Show animation one frame at a time.  This function has its own internal clocking meaning you can call it at any frequency
     and the rate the frames of video is shown remains constant.  Maybe your frames update every 30 ms but your
     event loop is running every 10 ms.  You don't have to worry about delaying, just call it every time through the
     loop.

    :param image_source:        Either a filename or a base64 string. Use None to close the window.
    :type image_source:         str | bytes | None
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
    :param relative_location:   (x,y) location relative to the default location of the window, in pixels. Normally the window centers.  This location is relative to the location the window would be created. Note they can be negative.
    :type relative_location:    (int, int)
    :param alpha_channel:       Window transparency 0 = invisible 1 = completely visible. Values between are see through
    :type alpha_channel:        (float)
    :param time_between_frames: Amount of time in milliseconds between each frame
    :type time_between_frames:  (int)
    :param transparent_color:   This color will be completely see-through in your window. Can even click through
    :type transparent_color:    (str)
    :param title:               Title that will be shown on the window
    :type title:                (str)
    :param icon:                Same as Window icon parameter. Can be either a filename or Base64 byte string. For Windows if filename, it MUST be ICO format. For Linux, must NOT be ICO
    :type icon:                 str | bytes
    :param no_buffering:        If True then no buffering will be used for the GIF. May work better if you have a large animation
    :type no_buffering:         (bool)
    :return:                    True if the window updated OK. False if the window was closed
    :rtype:                     bool
    """
    if image_source is None:
        for image in Window._animated_popup_dict:
            window = Window._animated_popup_dict[image]
            window.close()
        Window._animated_popup_dict = {}
        return

    if image_source not in Window._animated_popup_dict:
        if type(image_source) is bytes or len(image_source) > 300:
            layout = [
                [
                    Image(
                        data=image_source,
                        background_color=background_color,
                        key="-IMAGE-",
                    )
                ],
            ]
        else:
            layout = [
                [
                    Image(
                        filename=image_source,
                        background_color=background_color,
                        key="-IMAGE-",
                    )
                ],
            ]
        if message:
            layout.append(
                [
                    Text(
                        message,
                        background_color=background_color,
                        text_color=text_color,
                        font=font,
                    )
                ]
            )

        window = Window(
            title,
            layout,
            no_titlebar=no_titlebar,
            grab_anywhere=grab_anywhere,
            keep_on_top=keep_on_top,
            background_color=background_color,
            location=location,
            alpha_channel=alpha_channel,
            element_padding=(0, 0),
            margins=(0, 0),
            transparent_color=transparent_color,
            finalize=True,
            element_justification="c",
            icon=icon,
            relative_location=relative_location,
        )
        Window._animated_popup_dict[image_source] = window
    else:
        window = Window._animated_popup_dict[image_source]
        if no_buffering:
            window["-IMAGE-"].update_animation_no_buffering(
                image_source, time_between_frames=time_between_frames
            )
        else:
            window["-IMAGE-"].update_animation(
                image_source, time_between_frames=time_between_frames
            )
    event, values = window.read(1)
    if event == WIN_CLOSED:
        return False
    # window.refresh() # call refresh instead of Read to save significant CPU time
    return True


# Popup Notify
def popup_notify(
    *args,
    title="",
    icon=SYSTEM_TRAY_MESSAGE_ICON_INFORMATION,
    display_duration_in_ms=SYSTEM_TRAY_MESSAGE_DISPLAY_DURATION_IN_MILLISECONDS,
    fade_in_duration=SYSTEM_TRAY_MESSAGE_FADE_IN_DURATION,
    alpha=0.9,
    location=None,
):
    """
    Displays a "notification window", usually in the bottom right corner of your display.  Has an icon, a title, and a message.  It is more like a "toaster" window than the normal popups.

    The window will slowly fade in and out if desired.  Clicking on the window will cause it to move through the end the current "phase". For example, if the window was fading in and it was clicked, then it would immediately stop fading in and instead be fully visible.  It's a way for the user to quickly dismiss the window.

    The return code specifies why the call is returning (e.g. did the user click the message to dismiss it)

    :param title:                  Text to be shown at the top of the window in a larger font
    :type title:                   (str)
    :param icon:                   A base64 encoded PNG/GIF image or PNG/GIF filename that will be displayed in the window
    :type icon:                    bytes | str
    :param display_duration_in_ms: Number of milliseconds to show the window
    :type display_duration_in_ms:  (int)
    :param fade_in_duration:       Number of milliseconds to fade window in and out
    :type fade_in_duration:        (int)
    :param alpha:                  Alpha channel. 0 - invisible 1 - fully visible
    :type alpha:                   (float)
    :param location:               Location on the screen to display the window
    :type location:                (int, int)
    :return:                       reason for returning
    :rtype:                        (int)
    """

    if not args:
        args_to_print = [""]
    else:
        args_to_print = args
    output = ""
    max_line_total, total_lines, local_line_width = (
        0,
        0,
        SYSTEM_TRAY_MESSAGE_MAX_LINE_LENGTH,
    )
    for message in args_to_print:
        # fancy code to check if string and convert if not is not need. Just always convert to string :-)
        # if not isinstance(message, str): message = str(message)
        message = str(message)
        if message.count("\n"):
            message_wrapped = message
        else:
            message_wrapped = textwrap.fill(message, local_line_width)
        message_wrapped_lines = message_wrapped.count("\n") + 1
        longest_line_len = max([len(l) for l in message.split("\n")])
        width_used = min(longest_line_len, local_line_width)
        max_line_total = max(max_line_total, width_used)
        # height = _GetNumLinesNeeded(message, width_used)
        height = message_wrapped_lines
        output += message_wrapped + "\n"
        total_lines += height

    message = output

    # def __init__(self, menu=None, filename=None, data=None, data_base64=None, tooltip=None, metadata=None):
    return SystemTray.notify(
        title=title,
        message=message,
        icon=icon,
        display_duration_in_ms=display_duration_in_ms,
        fade_in_duration=fade_in_duration,
        alpha=alpha,
        location=location,
    )


def popup_menu(window, element, menu_def, title=None, location=(None, None)):
    """
    Makes a "popup menu"
    This type of menu is what you get when a normal menu or a right click menu is torn off
    The settings for the menu are obtained from the window parameter's Window


    :param window:   The window associated with the popup menu. The theme and right click menu settings for this window will be used
    :type window:    Window
    :param element:  An element in your window to associate the menu to. It can be any element
    :type element:   Element
    :param menu_def: A menu definition. This will be the same format as used for Right Click Menus1
    :type  menu_def: List[List[ List[str] | str ]]
    :param title:    The title that will be shown on the torn off menu window. Defaults to window titlr
    :type title:     str
    :param location: The location on the screen to place the window
    :type location:  (int, int) | (None, None)
    """

    element._popup_menu_location = location
    top_menu = tk.Menu(
        window.TKroot, tearoff=True, tearoffcommand=element._tearoff_menu_callback
    )
    if window.right_click_menu_background_color not in (COLOR_SYSTEM_DEFAULT, None):
        top_menu.config(bg=window.right_click_menu_background_color)
    if window.right_click_menu_text_color not in (COLOR_SYSTEM_DEFAULT, None):
        top_menu.config(fg=window.right_click_menu_text_color)
    if window.right_click_menu_disabled_text_color not in (COLOR_SYSTEM_DEFAULT, None):
        top_menu.config(disabledforeground=window.right_click_menu_disabled_text_color)
    if window.right_click_menu_font is not None:
        top_menu.config(font=window.right_click_menu_font)
    if window.right_click_menu_selected_colors[0] != COLOR_SYSTEM_DEFAULT:
        top_menu.config(activeforeground=window.right_click_menu_selected_colors[0])
    if window.right_click_menu_selected_colors[1] != COLOR_SYSTEM_DEFAULT:
        top_menu.config(activebackground=window.right_click_menu_selected_colors[1])
    top_menu.config(title=window.Title if title is None else title)
    AddMenuItem(top_menu, menu_def[1], element, right_click_menu=True)
    # element.Widget.bind('<Button-3>', element._RightClickMenuCallback)
    top_menu.invoke(0)


def popup_error_with_traceback(title, *messages, emoji=None):
    """
    Show an error message and as many additoinal lines of messages as you want.
    Will show the same error window as PySimpleGUI uses internally.  Has a button to
    take the user to the line of code you called this popup from.
    If you include the Exception information in your messages, then it will be parsed and additional information
    will be in the window about such as the specific line the error itself occurred on.

    :param title:     The title that will be shown in the popup's titlebar and in the first line of the window
    :type title:      str
    :param emoji:     An optional BASE64 Encoded image to shows in the error window
    :type emoji:      bytes
    """

    # For now, call the function that PySimpleGUI uses internally
    _error_popup_with_traceback(str(title), *messages, emoji=emoji)


def _error_popup_with_traceback(title, *args, emoji=None):
    if SUPPRESS_ERROR_POPUPS:
        return
    trace_details = traceback.format_stack()
    error_message = ""
    file_info_pysimplegui = None
    for line in reversed(trace_details):
        if __file__ not in line:
            file_info_pysimplegui = line.split(",")[0]
            error_message = line
            break
    if file_info_pysimplegui is None:
        _error_popup_with_code(
            title, None, None, "Did not find your traceback info", *args, emoji=emoji
        )
        return

    error_parts = None
    if error_message != "":
        error_parts = error_message.split(", ")
        if len(error_parts) < 4:
            error_message = (
                error_parts[0] + "\n" + error_parts[1] + "\n" + "".join(error_parts[2:])
            )
    if error_parts is None:
        print("*** Error popup attempted but unable to parse error details ***")
        print(trace_details)
        return
    filename = error_parts[0][error_parts[0].index("File ") + 5 :]
    line_num = error_parts[1][error_parts[1].index("line ") + 5 :]
    _error_popup_with_code(title, filename, line_num, error_message, *args, emoji=emoji)


def _error_popup_with_code(title, filename, line_num, *args, emoji=None):
    """
    Makes the error popup window

    :param title:     The title that will be shown in the popup's titlebar and in the first line of the window
    :type title:      str
    :param filename:  The filename to show.. may not be the filename that actually encountered the exception!
    :type filename:   str
    :param line_num:  Line number within file with the error
    :type line_num:   int | str
    :param args:      A variable number of lines of messages
    :type args:       *Any
    :param emoji:     An optional BASE64 Encoded image to shows in the error window
    :type emoji:      bytes
    """
    editor_filename = execute_get_editor()
    emoji_data = emoji if emoji is not None else _random_error_emoji()
    layout = [[Text("ERROR"), Text(title)], [Image(data=emoji_data)]]
    lines = []
    for msg in args:
        if isinstance(msg, Exception):
            lines += [
                [
                    "Additional Exception info pased in by PySimpleGUI or user: Error type is: {}".format(
                        type(msg).__name__
                    )
                ]
            ]
            lines += [
                [
                    "In file {} Line number {}".format(
                        __file__, msg.__traceback__.tb_lineno
                    )
                ]
            ]
            lines += [[str(msg)]]
        else:
            lines += [str(msg).split("\n")]
    max_line_len = 0
    for line in lines:
        max_line_len = max(max_line_len, max([len(s) for s in line]))

    layout += [
        [Text("".join(line), size=(min(max_line_len, 90), None))] for line in lines
    ]
    layout += [
        [
            Button("Close"),
            Button("Take me to error", disabled=True if not editor_filename else False),
            Button("Kill Application", button_color="white on red"),
        ]
    ]
    if not editor_filename:
        layout += [
            [
                Text(
                    'Configure editor in the Global settings to enable "Take me to error" feature'
                )
            ]
        ]
    window = Window(title, layout, keep_on_top=True)

    while True:
        event, values = window.read()
        if event in ("Close", WIN_CLOSED):
            break
        if event == "Kill Application":
            window.close()
            popup_quick_message(
                "KILLING APP!  BYE!",
                font="_ 18",
                keep_on_top=True,
                text_color="white",
                background_color="red",
                non_blocking=False,
            )
            sys.exit()
        if (
            event == "Take me to error"
            and filename is not None
            and line_num is not None
        ):
            execute_editor(filename, line_num)

    window.close()


