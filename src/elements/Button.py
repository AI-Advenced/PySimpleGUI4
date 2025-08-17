from ..core import Element
from ..constants import *
from .. import utils

# ---------------------------------------------------------------------- #
#                           Button Class                                 #
# ---------------------------------------------------------------------- #
class Button(Element):
    """
    Button Element - Defines all possible buttons. The shortcuts such as Submit, FileBrowse, ... each create a Button
    """

    def __init__(
        self,
        button_text="",
        button_type=BUTTON_TYPE_READ_FORM,
        target=(None, None),
        tooltip=None,
        file_types=FILE_TYPES_ALL_FILES,
        initial_folder=None,
        default_extension="",
        disabled=False,
        change_submits=False,
        enable_events=False,
        image_filename=None,
        image_data=None,
        image_size=(None, None),
        image_subsample=None,
        image_zoom=None,
        image_source=None,
        border_width=None,
        size=(None, None),
        s=(None, None),
        auto_size_button=None,
        button_color=None,
        disabled_button_color=None,
        highlight_colors=None,
        mouseover_colors=(None, None),
        use_ttk_buttons=None,
        font=None,
        bind_return_key=False,
        focus=False,
        pad=None,
        p=None,
        key=None,
        k=None,
        right_click_menu=None,
        expand_x=False,
        expand_y=False,
        visible=True,
        metadata=None,
    ):
        """
        :param button_text:           Text to be displayed on the button
        :type button_text:            (str)
        :param button_type:           You  should NOT be setting this directly. ONLY the shortcut functions set this
        :type button_type:            (int)
        :param target:                key or (row,col) target for the button. Note that -1 for column means 1 element to the left of this one. The constant ThisRow is used to indicate the current row. The Button itself is a valid target for some types of button
        :type target:                 str | (int, int)
        :param tooltip:               text, that will appear when mouse hovers over the element
        :type tooltip:                (str)
        :param file_types:            the filetypes that will be used to match files. To indicate all files: (("ALL Files", "*.* *"),).
        :type file_types:             Tuple[(str, str), ...]
        :param initial_folder:        starting path for folders and files
        :type initial_folder:         (str)
        :param default_extension:     If no extension entered by user, add this to filename (only used in saveas dialogs)
        :type default_extension:      (str)
        :param disabled:              If True button will be created disabled. If BUTTON_DISABLED_MEANS_IGNORE then the button will be ignored rather than disabled using tkinter
        :type disabled:               (bool | str)
        :param change_submits:        DO NOT USE. Only listed for backwards compat - Use enable_events instead
        :type change_submits:         (bool)
        :param enable_events:         Turns on the element specific events. If this button is a target, should it generate an event when filled in
        :type enable_events:          (bool)
        :param image_source:          Image to place on button. Use INSTEAD of the image_filename and image_data. Unifies these into 1 easier to use parm
        :type image_source:           (str | bytes)
        :param image_filename:        image filename if there is a button image. GIFs and PNGs only.
        :type image_filename:         (str)
        :param image_data:            Raw or Base64 representation of the image to put on button. Choose either filename or data
        :type image_data:             bytes | str
        :param image_size:            Size of the image in pixels (width, height)
        :type image_size:             (int, int)
        :param image_subsample:       amount to reduce the size of the image. Divides the size by this number. 2=1/2, 3=1/3, 4=1/4, etc
        :type image_subsample:        (int)
        :param image_zoom:            amount to increase the size of the image. 2=twice size, 3=3 times, etc
        :type image_zoom:             (int)
        :param border_width:          width of border around button in pixels
        :type border_width:           (int)
        :param size:                  (w, h) w=characters-wide, h=rows-high. If an int instead of a tuple is supplied, then height is auto-set to 1
        :type size:                   (int | None, int | None)  | (None, None) | int
        :param s:                     Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
        :type s:                      (int | None, int | None)  | (None, None) | int
        :param auto_size_button:      if True the button size is sized to fit the text
        :type auto_size_button:       (bool)
        :param button_color:          Color of button. default is from theme or the window. Easy to remember which is which if you say "ON" between colors. "red" on "green". Normally a tuple, but can be a simplified-button-color-string "foreground on background". Can be a single color if want to set only the background.
        :type button_color:           (str, str) | str
        :param disabled_button_color: colors to use when button is disabled (text, background). Use None for a color if don't want to change. Only ttk buttons support both text and background colors. tk buttons only support changing text color
        :type disabled_button_color:  (str, str) | str
        :param highlight_colors:      colors to use when button has focus (has focus, does not have focus). None will use colors based on theme. Only used by Linux and only for non-TTK button
        :type highlight_colors:       (str, str)
        :param mouseover_colors:      Important difference between Linux & Windows! Linux - Colors when mouse moved over button.  Windows - colors when button is pressed. The default is to switch the text and background colors (an inverse effect)
        :type mouseover_colors:       (str, str) | str
        :param use_ttk_buttons:       True = use ttk buttons. False = do not use ttk buttons.  None (Default) = use ttk buttons only if on a Mac and not with button images
        :type use_ttk_buttons:        (bool)
        :param font:                  specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
        :type font:                   (str or (str, int[, str]) or None)
        :param bind_return_key:       If True then pressing the return key in an Input or Multiline Element will cause this button to appear to be clicked (generates event with this button's key
        :type bind_return_key:        (bool)
        :param focus:                 if True, initial focus will be put on this button
        :type focus:                  (bool)
        :param pad:                   Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
        :type pad:                    (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
        :param p:                     Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
        :type p:                      (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
        :param key:                   Used with window.find_element and with return values to uniquely identify this element to uniquely identify this element
        :type key:                    str | int | tuple | object
        :param k:                     Same as the Key. You can use either k or key. Which ever is set will be used.
        :type k:                      str | int | tuple | object
        :param right_click_menu:      A list of lists of Menu items to show when this element is right clicked. See user docs for exact format.
        :type right_click_menu:       List[List[ List[str] | str ]]
        :param expand_x:              If True the element will automatically expand in the X direction to fill available space
        :type expand_x:               (bool)
        :param expand_y:              If True the element will automatically expand in the Y direction to fill available space
        :type expand_y:               (bool)
        :param visible:               set visibility state of the element
        :type visible:                (bool)
        :param metadata:              User metadata that can be set to ANYTHING
        :type metadata:               (Any)
        """

        self.AutoSizeButton = auto_size_button
        self.BType = button_type
        if (
            file_types is not None
            and len(file_types) == 2
            and isinstance(file_types[0], str)
            and isinstance(file_types[1], str)
        ):
            warnings.warn(
                "file_types parameter not correctly specified. This parameter is a LIST of TUPLES. You have passed (str,str) rather than ((str, str),). Fixing it for you this time.\nchanging {} to {}\nPlease correct your code".format(
                    file_types, ((file_types[0], file_types[1]),)
                ),
                UserWarning,
            )
            file_types = ((file_types[0], file_types[1]),)
        self.FileTypes = file_types
        self.Widget = self.TKButton = None  # type: tk.Button
        self.Target = target
        self.ButtonText = str(button_text)
        self.RightClickMenu = right_click_menu
        # Button colors can be a tuple (text, background) or a string with format "text on background"
        # bc = button_color
        # if button_color is None:
        #     bc = DEFAULT_BUTTON_COLOR
        # else:
        #     try:
        #         if isinstance(button_color,str):
        #             bc = button_color.split(' on ')
        #     except Exception as e:
        #         print('* cprint warning * you messed up with color formatting', e)
        #     if bc[1] is None:
        #         bc = (bc[0], theme_button_color()[1])
        # self.ButtonColor = bc
        self.ButtonColor = utils.button_color_to_tuple(button_color)

        # experimental code to compute disabled button text color
        # if disabled_button_color is None:
        #     try:
        #         disabled_button_color = (get_complimentary_hex(theme_button_color()[0]), theme_button_color()[1])
        #         # disabled_button_color = disabled_button_color
        #     except Exception:
        #         print('* Problem computing disabled button color *')
        self.DisabledButtonColor = (
            utils.button_color_to_tuple(disabled_button_color)
            if disabled_button_color is not None
            else (None, None)
        )
        if image_source is not None:
            if isinstance(image_source, bytes):
                image_data = image_source
            elif isinstance(image_source, str):
                image_filename = image_source
        self.ImageFilename = image_filename
        self.ImageData = image_data
        self.ImageSize = image_size
        self.ImageSubsample = image_subsample
        self.zoom = int(image_zoom) if image_zoom is not None else None
        self.UserData = None
        self.BorderWidth = (
            border_width if border_width is not None else DEFAULT_BORDER_WIDTH
        )
        self.BindReturnKey = bind_return_key
        self.Focus = focus
        self.TKCal = None
        self.calendar_default_date_M_D_Y = (None, None, None)
        self.calendar_close_when_chosen = False
        self.calendar_locale = None
        self.calendar_format = None
        self.calendar_location = (None, None)
        self.calendar_no_titlebar = True
        self.calendar_begin_at_sunday_plus = 0
        self.calendar_month_names = None
        self.calendar_day_abbreviations = None
        self.calendar_title = ""
        self.calendar_selection = ""
        self.default_button = None
        self.InitialFolder = initial_folder
        self.DefaultExtension = default_extension
        self.Disabled = disabled
        self.ChangeSubmits = change_submits or enable_events
        self.UseTtkButtons = use_ttk_buttons
        self._files_delimiter = BROWSE_FILES_DELIMITER  # used by the file browse button. used when multiple files are selected by user
        if use_ttk_buttons is None and utils.running_mac():
            self.UseTtkButtons = True
        # if image_filename or image_data:
        #     self.UseTtkButtons = False              # if an image is to be displayed, then force the button to not be a TTK Button
        if key is None and k is None:
            _key = self.ButtonText
            if DEFAULT_USE_BUTTON_SHORTCUTS:
                pos = _key.find(MENU_SHORTCUT_CHARACTER)
                if pos != -1:
                    if (
                        pos < len(MENU_SHORTCUT_CHARACTER)
                        or _key[pos - len(MENU_SHORTCUT_CHARACTER)] != "\\"
                    ):
                        _key = _key[:pos] + _key[pos + len(MENU_SHORTCUT_CHARACTER) :]
                    else:
                        _key = _key.replace(
                            "\\" + MENU_SHORTCUT_CHARACTER, MENU_SHORTCUT_CHARACTER
                        )
        else:
            _key = key if key is not None else k
        if highlight_colors is not None:
            self.HighlightColors = highlight_colors
        else:
            self.HighlightColors = self._compute_highlight_colors()

        if mouseover_colors != (None, None):
            self.MouseOverColors = utils.button_color_to_tuple(mouseover_colors)
        elif button_color is not None:
            self.MouseOverColors = (self.ButtonColor[1], self.ButtonColor[0])
        else:
            self.MouseOverColors = (theme_button_color()[1], theme_button_color()[0])
        pad = pad if pad is not None else p
        self.expand_x = expand_x
        self.expand_y = expand_y

        sz = size if size != (None, None) else s
        super().__init__(
            ELEM_TYPE_BUTTON,
            size=sz,
            font=font,
            pad=pad,
            key=_key,
            tooltip=tooltip,
            visible=visible,
            metadata=metadata,
        )
        return

    def _compute_highlight_colors(self):
        """
        Determines the color to use to indicate the button has focus. This setting is only used by Linux.
        :return: Pair of colors. (Highlight, Highlight Background)
        :rtype:  (str, str)
        """
        highlight_color = highlight_background = COLOR_SYSTEM_DEFAULT
        if (
            self.ButtonColor != COLOR_SYSTEM_DEFAULT
            and theme_background_color() != COLOR_SYSTEM_DEFAULT
        ):
            highlight_background = theme_background_color()
        if (
            self.ButtonColor != COLOR_SYSTEM_DEFAULT
            and self.ButtonColor[0] != COLOR_SYSTEM_DEFAULT
        ):
            if self.ButtonColor[0] != theme_background_color():
                highlight_color = self.ButtonColor[0]
            else:
                highlight_color = "red"
        return highlight_color, highlight_background

        # Realtime button release callback

    def ButtonReleaseCallBack(self, parm):
        """
        Not a user callable function.  Called by tkinter when a "realtime" button is released

        :param parm: the event info from tkinter
        :type parm:

        """
        self.LastButtonClickedWasRealtime = False
        self.ParentForm.LastButtonClicked = None

    # Realtime button callback
    def ButtonPressCallBack(self, parm):
        """
        Not a user callable method. Callback called by tkinter when a "realtime" button is pressed

        :param parm: Event info passed in by tkinter
        :type parm:

        """
        self.ParentForm.LastButtonClickedWasRealtime = True
        if self.Key is not None:
            self.ParentForm.LastButtonClicked = self.Key
        else:
            self.ParentForm.LastButtonClicked = self.ButtonText
        # if self.ParentForm.CurrentlyRunningMainloop:
        #     Window._window_that_exited = self.ParentForm
        #     self.ParentForm.TKroot.quit()  # kick out of loop if read was called
        _exit_mainloop(self.ParentForm)

    def _find_target(self):
        target = self.Target
        target_element = None

        if target[0] == ThisRow:
            target = [self.Position[0], target[1]]
            if target[1] < 0:
                target[1] = self.Position[1] + target[1]
        strvar = None
        should_submit_window = False
        if target == (None, None):
            strvar = self.TKStringVar
        else:
            # Need a try-block because if the target is not hashable, the "in" test will raise exception
            try:
                if target in self.ParentForm.AllKeysDict:
                    target_element = self.ParentForm.AllKeysDict[target]
            except Exception:
                pass
            # if target not found or the above try got exception, then keep looking....
            if target_element is None:
                if not isinstance(target, str):
                    if target[0] < 0:
                        target = [self.Position[0] + target[0], target[1]]
                    target_element = self.ParentContainer._GetElementAtLocation(target)
                else:
                    target_element = self.ParentForm.find_element(target)
            try:
                strvar = target_element.TKStringVar
            except Exception:
                pass
            try:
                if target_element.ChangeSubmits:
                    should_submit_window = True
            except Exception:
                pass
        return target_element, strvar, should_submit_window

    # -------  Button Callback  ------- #
    def ButtonCallBack(self):
        """
        Not user callable! Called by tkinter when a button is clicked.  This is where all the fun begins!
        """

        if self.Disabled == BUTTON_DISABLED_MEANS_IGNORE:
            return
        target_element, strvar, should_submit_window = self._find_target()

        filetypes = FILE_TYPES_ALL_FILES if self.FileTypes is None else self.FileTypes

        if self.BType == BUTTON_TYPE_BROWSE_FOLDER:
            if utils.running_mac():  # macs don't like seeing the parent window (go firgure)
                folder_name = tk.filedialog.askdirectory(
                    initialdir=self.InitialFolder
                )  # show the 'get folder' dialog box
            else:
                folder_name = tk.filedialog.askdirectory(
                    initialdir=self.InitialFolder, parent=self.ParentForm.TKroot
                )  # show the 'get folder' dialog box
            if folder_name:
                try:
                    strvar.set(folder_name)
                    self.TKStringVar.set(folder_name)
                except Exception:
                    pass
            else:  # if "cancel" button clicked, don't generate an event
                should_submit_window = False
        elif self.BType == BUTTON_TYPE_BROWSE_FILE:
            if utils.running_mac():
                # Workaround for the "*.*" issue on Mac
                is_all = [
                    (x, y) for (x, y) in filetypes if all(ch in "* ." for ch in y)
                ]
                if not len(set(filetypes)) > 1 and (
                    len(is_all) != 0 or filetypes == FILE_TYPES_ALL_FILES
                ):
                    file_name = tk.filedialog.askopenfilename(
                        initialdir=self.InitialFolder
                    )
                else:
                    file_name = tk.filedialog.askopenfilename(
                        initialdir=self.InitialFolder, filetypes=filetypes
                    )  # show the 'get file' dialog box
                # elif _mac_allow_filetypes():
                # file_name = tk.filedialog.askopenfilename(initialdir=self.InitialFolder, filetypes=filetypes)  # show the 'get file' dialog box
                # else:
                #     file_name = tk.filedialog.askopenfilename(initialdir=self.InitialFolder)  # show the 'get file' dialog box
            else:
                file_name = tk.filedialog.askopenfilename(
                    filetypes=filetypes,
                    initialdir=self.InitialFolder,
                    parent=self.ParentForm.TKroot,
                )  # show the 'get file' dialog box

            if file_name:
                strvar.set(file_name)
                self.TKStringVar.set(file_name)
            else:  # if "cancel" button clicked, don't generate an event
                should_submit_window = False
        elif self.BType == BUTTON_TYPE_COLOR_CHOOSER:
            color = tk.colorchooser.askcolor(
                parent=self.ParentForm.TKroot, color=self.default_color
            )  # show the 'get file' dialog box
            color = color[1]  # save only the #RRGGBB portion
            if color is not None:
                strvar.set(color)
                self.TKStringVar.set(color)
        elif self.BType == BUTTON_TYPE_BROWSE_FILES:
            if utils.running_mac():
                # Workaround for the "*.*" issue on Mac
                is_all = [
                    (x, y) for (x, y) in filetypes if all(ch in "* ." for ch in y)
                ]
                if not len(set(filetypes)) > 1 and (
                    len(is_all) != 0 or filetypes == FILE_TYPES_ALL_FILES
                ):
                    file_name = tk.filedialog.askopenfilenames(
                        initialdir=self.InitialFolder
                    )
                else:
                    file_name = tk.filedialog.askopenfilenames(
                        filetypes=filetypes, initialdir=self.InitialFolder
                    )
                # elif _mac_allow_filetypes():
                #     file_name = tk.filedialog.askopenfilenames(filetypes=filetypes, initialdir=self.InitialFolder)
                # else:
                #     file_name = tk.filedialog.askopenfilenames(initialdir=self.InitialFolder)
            else:
                file_name = tk.filedialog.askopenfilenames(
                    filetypes=filetypes,
                    initialdir=self.InitialFolder,
                    parent=self.ParentForm.TKroot,
                )

            if file_name:
                file_name = self._files_delimiter.join(file_name)  # normally a ';'
                strvar.set(file_name)
                self.TKStringVar.set(file_name)
            else:  # if "cancel" button clicked, don't generate an event
                should_submit_window = False
        elif self.BType == BUTTON_TYPE_SAVEAS_FILE:
            # show the 'get file' dialog box
            if utils.running_mac():
                # Workaround for the "*.*" issue on Mac
                is_all = [
                    (x, y) for (x, y) in filetypes if all(ch in "* ." for ch in y)
                ]
                if not len(set(filetypes)) > 1 and (
                    len(is_all) != 0 or filetypes == FILE_TYPES_ALL_FILES
                ):
                    file_name = tk.filedialog.asksaveasfilename(
                        defaultextension=self.DefaultExtension,
                        initialdir=self.InitialFolder,
                    )
                else:
                    file_name = tk.filedialog.asksaveasfilename(
                        filetypes=filetypes,
                        defaultextension=self.DefaultExtension,
                        initialdir=self.InitialFolder,
                    )
                # elif _mac_allow_filetypes():
                #     file_name = tk.filedialog.asksaveasfilename(filetypes=filetypes, defaultextension=self.DefaultExtension, initialdir=self.InitialFolder)
                # else:
                #     file_name = tk.filedialog.asksaveasfilename(defaultextension=self.DefaultExtension, initialdir=self.InitialFolder)
            else:
                file_name = tk.filedialog.asksaveasfilename(
                    filetypes=filetypes,
                    defaultextension=self.DefaultExtension,
                    initialdir=self.InitialFolder,
                    parent=self.ParentForm.TKroot,
                )

            if file_name:
                strvar.set(file_name)
                self.TKStringVar.set(file_name)
            else:  # if "cancel" button clicked, don't generate an event
                should_submit_window = False
        elif (
            self.BType == BUTTON_TYPE_CLOSES_WIN
        ):  # this is a return type button so GET RESULTS and destroy window
            # first, get the results table built
            # modify the Results table in the parent FlexForm object
            if self.Key is not None:
                self.ParentForm.LastButtonClicked = self.Key
            else:
                self.ParentForm.LastButtonClicked = self.ButtonText
            self.ParentForm.FormRemainedOpen = False
            self.ParentForm._Close()
            _exit_mainloop(self.ParentForm)

            if self.ParentForm.NonBlocking:
                self.ParentForm.TKroot.destroy()
                Window._DecrementOpenCount()
        elif (
            self.BType == BUTTON_TYPE_READ_FORM
        ):  # LEAVE THE WINDOW OPEN!! DO NOT CLOSE
            # This is a PLAIN BUTTON
            # first, get the results table built
            # modify the Results table in the parent FlexForm object
            if self.Key is not None:
                self.ParentForm.LastButtonClicked = self.Key
            else:
                self.ParentForm.LastButtonClicked = self.ButtonText
            self.ParentForm.FormRemainedOpen = True
            _exit_mainloop(self.ParentForm)
        elif (
            self.BType == BUTTON_TYPE_CLOSES_WIN_ONLY
        ):  # special kind of button that does not exit main loop
            self.ParentForm._Close(without_event=True)
            self.ParentForm.TKroot.destroy()  # close the window with tkinter
            Window._DecrementOpenCount()
        elif (
            self.BType == BUTTON_TYPE_CALENDAR_CHOOSER
        ):  # this is a return type button so GET RESULTS and destroy window
            # ------------ new chooser code -------------
            self.ParentForm.LastButtonClicked = (
                self.Key
            )  # key should have been generated already if not set by user
            self.ParentForm.FormRemainedOpen = True
            should_submit_window = False
            _exit_mainloop(self.ParentForm)
        # elif self.BType == BUTTON_TYPE_SHOW_DEBUGGER:
        # **** DEPRICATED *****
        # if self.ParentForm.DebuggerEnabled:
        # show_debugger_popout_window()

        if should_submit_window:
            self.ParentForm.LastButtonClicked = target_element.Key
            self.ParentForm.FormRemainedOpen = True
            _exit_mainloop(self.ParentForm)

        return

    def update(
        self,
        text:str=None,
        button_color=(None, None),
        disabled:bool=None,
        image_source=None,
        image_data=None,
        image_filename=None,
        visible=None,
        image_subsample=None,
        image_zoom=None,
        disabled_button_color=(None, None),
        image_size=None,
    ):
        """
        Changes some of the settings for the Button Element. Must call `Window.Read` or `Window.Finalize` prior

        Changes will not be visible in your window until you call window.read or window.refresh.

        If you change visibility, your element may MOVE. If you want it to remain stationary, use the "layout helper"
        function "pin" to ensure your element is "pinned" to that location in your layout so that it returns there
        when made visible.

        :param text:                  sets button text
        :type text:                   (str)
        :param button_color:          Color of button. default is from theme or the window. Easy to remember which is which if you say "ON" between colors. "red" on "green". Normally a tuple, but can be a simplified-button-color-string "foreground on background". Can be a single color if want to set only the background.
        :type button_color:           (str, str) | str
        :param disabled:              True/False to enable/disable at the GUI level. Use BUTTON_DISABLED_MEANS_IGNORE to ignore clicks (won't change colors)
        :type disabled:               (bool | str)
        :param image_source:          Image to place on button. Use INSTEAD of the image_filename and image_data. Unifies these into 1 easier to use parm
        :type image_source:           (str | bytes)
        :param image_data:            Raw or Base64 representation of the image to put on button. Choose either filename or data
        :type image_data:             bytes | str
        :param image_filename:        image filename if there is a button image. GIFs and PNGs only.
        :type image_filename:         (str)
        :param disabled_button_color: colors to use when button is disabled (text, background). Use None for a color if don't want to change. Only ttk buttons support both text and background colors. tk buttons only support changing text color
        :type disabled_button_color:  (str, str)
        :param visible:               control visibility of element
        :type visible:                (bool)
        :param image_subsample:       amount to reduce the size of the image. Divides the size by this number. 2=1/2, 3=1/3, 4=1/4, etc
        :type image_subsample:        (int)
        :param image_zoom:            amount to increase the size of the image. 2=twice size, 3=3 times, etc
        :type image_zoom:             (int)
        :param image_size:            Size of the image in pixels (width, height)
        :type image_size:             (int, int)
        """

        if (
            not self._widget_was_created()
        ):  # if widget hasn't been created yet, then don't allow
            return

        if self._this_elements_window_closed():
            _error_popup_with_traceback(
                "Error in Button.update - The window was closed"
            )
            return

        if image_source is not None:
            if isinstance(image_source, bytes):
                image_data = image_source
            elif isinstance(image_source, str):
                image_filename = image_source

        if self.UseTtkButtons:
            style_name = (
                self.ttk_style_name
            )  # created when made initial window (in the pack)
            # style_name = str(self.Key) + 'custombutton.TButton'
            button_style = ttk.Style()
        if text is not None:
            btext = text
            if DEFAULT_USE_BUTTON_SHORTCUTS:
                pos = btext.find(MENU_SHORTCUT_CHARACTER)
                if pos != -1:
                    if (
                        pos < len(MENU_SHORTCUT_CHARACTER)
                        or btext[pos - len(MENU_SHORTCUT_CHARACTER)] != "\\"
                    ):
                        btext = (
                            btext[:pos] + btext[pos + len(MENU_SHORTCUT_CHARACTER) :]
                        )
                    else:
                        btext = btext.replace(
                            "\\" + MENU_SHORTCUT_CHARACTER, MENU_SHORTCUT_CHARACTER
                        )
                        pos = -1
                if pos != -1:
                    self.TKButton.config(underline=pos)
            self.TKButton.configure(text=btext)
            self.ButtonText = text
        if button_color != (None, None) and button_color != COLOR_SYSTEM_DEFAULT:
            bc = utils.button_color_to_tuple(button_color, self.ButtonColor)
            # if isinstance(button_color, str):
            #     try:
            #         button_color = button_color.split(' on ')
            #     except Exception as e:
            #         print('** Error in formatting your button color **', button_color, e)
            if self.UseTtkButtons:
                if bc[0] not in (None, COLOR_SYSTEM_DEFAULT):
                    button_style.configure(style_name, foreground=bc[0])
                if bc[1] not in (None, COLOR_SYSTEM_DEFAULT):
                    button_style.configure(style_name, background=bc[1])
            else:
                if bc[0] not in (None, COLOR_SYSTEM_DEFAULT):
                    self.TKButton.config(foreground=bc[0], activebackground=bc[0])
                if bc[1] not in (None, COLOR_SYSTEM_DEFAULT):
                    self.TKButton.config(background=bc[1], activeforeground=bc[1])
            self.ButtonColor = bc
        if disabled:
            self.TKButton["state"] = "disabled"
        elif disabled is False:
            self.TKButton["state"] = "normal"
        elif disabled == BUTTON_DISABLED_MEANS_IGNORE:
            self.TKButton["state"] = "normal"
        self.Disabled = disabled if disabled is not None else self.Disabled

        if image_data is not None:
            image = tk.PhotoImage(data=image_data)
            if image_subsample:
                image = image.subsample(image_subsample)
            if image_zoom is not None:
                image = image.zoom(int(image_zoom))
            if image_size is not None:
                width, height = image_size
            else:
                width, height = image.width(), image.height()
            if self.UseTtkButtons:
                button_style.configure(
                    style_name, image=image, width=width, height=height
                )
            else:
                self.TKButton.config(image=image, width=width, height=height)
            self.TKButton.image = image
        if image_filename is not None:
            image = tk.PhotoImage(file=image_filename)
            if image_subsample:
                image = image.subsample(image_subsample)
            if image_zoom is not None:
                image = image.zoom(int(image_zoom))
            if image_size is not None:
                width, height = image_size
            else:
                width, height = image.width(), image.height()
            if self.UseTtkButtons:
                button_style.configure(
                    style_name, image=image, width=width, height=height
                )
            else:
                self.TKButton.config(
                    highlightthickness=0, image=image, width=width, height=height
                )
            self.TKButton.image = image
        if not visible:
            self._pack_forget_save_settings()
        elif visible:
            self._pack_restore_settings()
        if (
            disabled_button_color != (None, None)
            and disabled_button_color != COLOR_SYSTEM_DEFAULT
        ):
            if not self.UseTtkButtons:
                self.TKButton["disabledforeground"] = disabled_button_color[0]
            else:
                if disabled_button_color[0] is not None:
                    button_style.map(
                        style_name, foreground=[("disabled", disabled_button_color[0])]
                    )
                if disabled_button_color[1] is not None:
                    button_style.map(
                        style_name, background=[("disabled", disabled_button_color[1])]
                    )
            self.DisabledButtonColor = (
                disabled_button_color[0]
                if disabled_button_color[0] is not None
                else self.DisabledButtonColor[0],
                disabled_button_color[1]
                if disabled_button_color[1] is not None
                else self.DisabledButtonColor[1],
            )

        if visible is not None:
            self._visible = visible

    def get_text(self):
        """
        Returns the current text shown on a button

        :return: The text currently displayed on the button
        :rtype:  (str)
        """
        return self.ButtonText

    def click(self):
        """
        Generates a click of the button as if the user clicked the button
        Calls the tkinter invoke method for the button
        """
        try:
            self.TKButton.invoke()
        except Exception:
            print("Exception clicking button")

    Click = click
    GetText = get_text
    Update = update


# -------------------------  Button lazy functions  ------------------------- #
B = Button
Btn = Button


# -------------------------  FOLDER BROWSE Element lazy function  ------------------------- #
def FolderBrowse(
    button_text="Browse",
    target=(ThisRow, -1),
    initial_folder=None,
    tooltip=None,
    size=(None, None),
    s=(None, None),
    auto_size_button=None,
    button_color=None,
    disabled=False,
    change_submits=False,
    enable_events=False,
    font=None,
    pad=None,
    p=None,
    key=None,
    k=None,
    visible=True,
    metadata=None,
    expand_x=False,
    expand_y=False,
):
    """
    :param button_text:      text in the button (Default value = 'Browse')
    :type button_text:       (str)
    :param target:           target for the button (Default value = (ThisRow, -1))
    :type target:            str | (int, int)
    :param initial_folder:   starting path for folders and files
    :type initial_folder:    (str)
    :param tooltip:          text, that will appear when mouse hovers over the element
    :type tooltip:           (str)
    :param size:             (w,h) w=characters-wide, h=rows-high
    :type size:              (int, int)
    :param s:                Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
    :type s:                 (int, int)  | (None, None) | int
    :param auto_size_button: True if button size is determined by button text
    :type auto_size_button:  (bool)
    :param button_color:     button color (foreground, background)
    :type button_color:      (str, str) | str
    :param disabled:         set disable state for element (Default = False)
    :type disabled:          (bool)
    :param change_submits:   If True, pressing Enter key submits window (Default = False)
    :type enable_events:     (bool)
    :param enable_events:    Turns on the element specific events.(Default = False)
    :type enable_events:     (bool)
    :param font:             specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:              (str or (str, int[, str]) or None)
    :param pad:              Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
    :type pad:               (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param p:                Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
    :type p:                 (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param key:              Used with window.find_element and with return values to uniquely identify this element
    :type key:               str | int | tuple | object
    :param k:                Same as the Key. You can use either k or key. Which ever is set will be used.
    :type k:                 str | int | tuple | object
    :param visible:          set initial visibility state of the Button
    :type visible:           (bool)
    :param metadata:         Anything you want to store along with this button
    :type metadata:          (Any)
    :param expand_x:         If True Element will expand in the Horizontal directions
    :type expand_x:          (bool)
    :param expand_y:         If True Element will expand in the Vertical directions
    :type expand_y:          (bool)
    :return:                 The Button created
    :rtype:                  (Button)
    """

    return Button(
        button_text=button_text,
        button_type=BUTTON_TYPE_BROWSE_FOLDER,
        target=target,
        initial_folder=initial_folder,
        tooltip=tooltip,
        size=size,
        s=s,
        auto_size_button=auto_size_button,
        disabled=disabled,
        button_color=button_color,
        change_submits=change_submits,
        enable_events=enable_events,
        font=font,
        pad=pad,
        p=p,
        key=key,
        k=k,
        visible=visible,
        metadata=metadata,
        expand_x=expand_x,
        expand_y=expand_y,
    )


# -------------------------  FILE BROWSE Element lazy function  ------------------------- #
def FileBrowse(
    button_text="Browse",
    target=(ThisRow, -1),
    file_types=FILE_TYPES_ALL_FILES,
    initial_folder=None,
    tooltip=None,
    size=(None, None),
    s=(None, None),
    auto_size_button=None,
    button_color=None,
    change_submits=False,
    enable_events=False,
    font=None,
    disabled=False,
    pad=None,
    p=None,
    key=None,
    k=None,
    visible=True,
    metadata=None,
    expand_x=False,
    expand_y=False,
):
    """

    :param button_text:      text in the button (Default value = 'Browse')
    :type button_text:       (str)
    :param target:           key or (row,col) target for the button (Default value = (ThisRow, -1))
    :type target:            str | (int, int)
    :param file_types:       filter file types Default value = (("ALL Files", "*.* *"),).
    :type file_types:        Tuple[(str, str), ...]
    :param initial_folder:   starting path for folders and files
    :type initial_folder:
    :param tooltip:          text, that will appear when mouse hovers over the element
    :type tooltip:           (str)
    :param size:             (w,h) w=characters-wide, h=rows-high
    :type size:              (int, int)
    :param s:                Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
    :type s:                 (int, int)  | (None, None) | int
    :param auto_size_button: True if button size is determined by button text
    :type auto_size_button:  (bool)
    :param button_color:     button color (foreground, background)
    :type button_color:      (str, str) | str
    :param change_submits:   If True, pressing Enter key submits window (Default = False)
    :type change_submits:    (bool)
    :param enable_events:    Turns on the element specific events.(Default = False)
    :type enable_events:     (bool)
    :param font:             specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:              (str or (str, int[, str]) or None)
    :param disabled:         set disable state for element (Default = False)
    :type disabled:          (bool)
    :param pad:              Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
    :type pad:               (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param p:                Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
    :type p:                 (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param key:              key for uniquely identify this element (for window.find_element)
    :type key:               str | int | tuple | object
    :param k:                Same as the Key. You can use either k or key. Which ever is set will be used.
    :type k:                 str | int | tuple | object
    :param visible:          set initial visibility state of the Button
    :type visible:           (bool)
    :param metadata:         Anything you want to store along with this button
    :type metadata:          (Any)
    :param expand_x:         If True Element will expand in the Horizontal directions
    :type expand_x:          (bool)
    :param expand_y:         If True Element will expand in the Vertical directions
    :type expand_y:          (bool)
    :return:                 returns a button
    :rtype:                  (Button)
    """
    return Button(
        button_text=button_text,
        button_type=BUTTON_TYPE_BROWSE_FILE,
        target=target,
        file_types=file_types,
        initial_folder=initial_folder,
        tooltip=tooltip,
        size=size,
        s=s,
        auto_size_button=auto_size_button,
        change_submits=change_submits,
        enable_events=enable_events,
        disabled=disabled,
        button_color=button_color,
        font=font,
        pad=pad,
        p=p,
        key=key,
        k=k,
        visible=visible,
        metadata=metadata,
        expand_x=expand_x,
        expand_y=expand_y,
    )


# -------------------------  FILES BROWSE Element (Multiple file selection) lazy function  ------------------------- #
def FilesBrowse(
    button_text="Browse",
    target=(ThisRow, -1),
    file_types=FILE_TYPES_ALL_FILES,
    disabled=False,
    initial_folder=None,
    tooltip=None,
    size=(None, None),
    s=(None, None),
    auto_size_button=None,
    button_color=None,
    change_submits=False,
    enable_events=False,
    font=None,
    pad=None,
    p=None,
    key=None,
    k=None,
    visible=True,
    files_delimiter=BROWSE_FILES_DELIMITER,
    metadata=None,
    expand_x=False,
    expand_y=False,
):
    """
    Allows browsing of multiple files. File list is returned as a single list with the delimiter defined using the files_delimiter parameter.

    :param button_text:      text in the button (Default value = 'Browse')
    :type button_text:       (str)
    :param target:           key or (row,col) target for the button (Default value = (ThisRow, -1))
    :type target:            str | (int, int)
    :param file_types:       Default value = (("ALL Files", "*.* *"),).
    :type file_types:        Tuple[(str, str), ...]
    :param disabled:         set disable state for element (Default = False)
    :type disabled:          (bool)
    :param initial_folder:   starting path for folders and files
    :type initial_folder:    (str)
    :param tooltip:          text, that will appear when mouse hovers over the element
    :type tooltip:           (str)
    :param size:             (w,h) w=characters-wide, h=rows-high
    :type size:              (int, int)
    :param s:                Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
    :type s:                 (int, int)  | (None, None) | int
    :param auto_size_button: True if button size is determined by button text
    :type auto_size_button:  (bool)
    :param button_color:     button color (foreground, background)
    :type button_color:      (str, str) | str
    :param change_submits:   If True, pressing Enter key submits window (Default = False)
    :type change_submits:    (bool)
    :param enable_events:    Turns on the element specific events.(Default = False)
    :type enable_events:     (bool)
    :param font:             specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:              (str or (str, int[, str]) or None)
    :param pad:              Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
    :type pad:               (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param p:                Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
    :type p:                 (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param key:              key for uniquely identify this element (for window.find_element)
    :type key:               str | int | tuple | object
    :param k:                Same as the Key. You can use either k or key. Which ever is set will be used.
    :type k:                 str | int | tuple | object
    :param visible:          set initial visibility state of the Button
    :type visible:           (bool)
    :param files_delimiter:  String to place between files when multiple files are selected. Normally a ;
    :type files_delimiter:   str
    :param metadata:         Anything you want to store along with this button
    :type metadata:          (Any)
    :param expand_x:         If True Element will expand in the Horizontal directions
    :type expand_x:          (bool)
    :param expand_y:         If True Element will expand in the Vertical directions
    :type expand_y:          (bool)
    :return:                 returns a button
    :rtype:                  (Button)
    """
    button = Button(
        button_text=button_text,
        button_type=BUTTON_TYPE_BROWSE_FILES,
        target=target,
        file_types=file_types,
        initial_folder=initial_folder,
        change_submits=change_submits,
        enable_events=enable_events,
        tooltip=tooltip,
        size=size,
        s=s,
        auto_size_button=auto_size_button,
        disabled=disabled,
        button_color=button_color,
        font=font,
        pad=pad,
        p=p,
        key=key,
        k=k,
        visible=visible,
        metadata=metadata,
        expand_x=expand_x,
        expand_y=expand_y,
    )
    button._files_delimiter = files_delimiter
    return button


# -------------------------  FILE BROWSE Element lazy function  ------------------------- #
def FileSaveAs(
    button_text="Save As...",
    target=(ThisRow, -1),
    file_types=FILE_TYPES_ALL_FILES,
    initial_folder=None,
    default_extension="",
    disabled=False,
    tooltip=None,
    size=(None, None),
    s=(None, None),
    auto_size_button=None,
    button_color=None,
    change_submits=False,
    enable_events=False,
    font=None,
    pad=None,
    p=None,
    key=None,
    k=None,
    visible=True,
    metadata=None,
    expand_x=False,
    expand_y=False,
):
    """

    :param button_text:       text in the button (Default value = 'Save As...')
    :type button_text:        (str)
    :param target:            key or (row,col) target for the button (Default value = (ThisRow, -1))
    :type target:             str | (int, int)
    :param file_types:        Default value = (("ALL Files", "*.* *"),).
    :type file_types:         Tuple[(str, str), ...]
    :param default_extension: If no extension entered by user, add this to filename (only used in saveas dialogs)
    :type default_extension:  (str)
    :param initial_folder:    starting path for folders and files
    :type initial_folder:     (str)
    :param disabled:          set disable state for element (Default = False)
    :type disabled:           (bool)
    :param tooltip:           text, that will appear when mouse hovers over the element
    :type tooltip:            (str)
    :param size:              (w,h) w=characters-wide, h=rows-high
    :type size:               (int, int)
    :param s:                 Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
    :type s:                  (int, int)  | (None, None) | int
    :param auto_size_button:  True if button size is determined by button text
    :type auto_size_button:   (bool)
    :param button_color:      button color (foreground, background)
    :type button_color:       (str, str) | str
    :param change_submits:    If True, pressing Enter key submits window (Default = False)
    :type change_submits:     (bool)
    :param enable_events:     Turns on the element specific events.(Default = False)
    :type enable_events:      (bool)
    :param font:              specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:               (str or (str, int[, str]) or None)
    :param pad:               Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
    :type pad:                (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param p:                 Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
    :type p:                  (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param key:               key for uniquely identify this element (for window.find_element)
    :type key:                str | int | tuple | object
    :param k:                 Same as the Key. You can use either k or key. Which ever is set will be used.
    :type k:                  str | int | tuple | object
    :param visible:           set initial visibility state of the Button
    :type visible:            (bool)
    :param metadata:          Anything you want to store along with this button
    :type metadata:           (Any)
    :param expand_x:          If True Element will expand in the Horizontal directions
    :type expand_x:           (bool)
    :param expand_y:          If True Element will expand in the Vertical directions
    :type expand_y:           (bool)        :return:                  returns a button
    :rtype:                   (Button)
    """
    return Button(
        button_text=button_text,
        button_type=BUTTON_TYPE_SAVEAS_FILE,
        target=target,
        file_types=file_types,
        initial_folder=initial_folder,
        default_extension=default_extension,
        tooltip=tooltip,
        size=size,
        s=s,
        disabled=disabled,
        auto_size_button=auto_size_button,
        button_color=button_color,
        change_submits=change_submits,
        enable_events=enable_events,
        font=font,
        pad=pad,
        p=p,
        key=key,
        k=k,
        visible=visible,
        metadata=metadata,
        expand_x=expand_x,
        expand_y=expand_y,
    )


# -------------------------  SAVE AS Element lazy function  ------------------------- #
def SaveAs(
    button_text="Save As...",
    target=(ThisRow, -1),
    file_types=FILE_TYPES_ALL_FILES,
    initial_folder=None,
    default_extension="",
    disabled=False,
    tooltip=None,
    size=(None, None),
    s=(None, None),
    auto_size_button=None,
    button_color=None,
    change_submits=False,
    enable_events=False,
    font=None,
    pad=None,
    p=None,
    key=None,
    k=None,
    visible=True,
    metadata=None,
    expand_x=False,
    expand_y=False,
):
    """

    :param button_text:       text in the button (Default value = 'Save As...')
    :type button_text:        (str)
    :param target:            key or (row,col) target for the button (Default value = (ThisRow, -1))
    :type target:             str | (int, int)
    :param file_types:        Default value = (("ALL Files", "*.* *"),).
    :type file_types:         Tuple[(str, str), ...]
    :param default_extension: If no extension entered by user, add this to filename (only used in saveas dialogs)
    :type default_extension:  (str)
    :param initial_folder:    starting path for folders and files
    :type initial_folder:     (str)
    :param disabled:          set disable state for element (Default = False)
    :type disabled:           (bool)
    :param tooltip:           text, that will appear when mouse hovers over the element
    :type tooltip:            (str)
    :param size:              (w,h) w=characters-wide, h=rows-high
    :type size:               (int, int)
    :param s:                 Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
    :type s:                  (int, int)  | (None, None) | int
    :param auto_size_button:  True if button size is determined by button text
    :type auto_size_button:   (bool)
    :param button_color:      button color (foreground, background)
    :type button_color:       (str, str) or str
    :param change_submits:    If True, pressing Enter key submits window (Default = False)
    :type change_submits:     (bool)
    :param enable_events:     Turns on the element specific events.(Default = False)
    :type enable_events:      (bool)
    :param font:              specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:               (str or (str, int[, str]) or None)
    :param pad:               Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
    :type pad:                (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param p:                 Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
    :type p:                  (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int    :param key:               key for uniquely identify this element (for window.find_element)
    :type key:                str | int | tuple | object
    :param k:                 Same as the Key. You can use either k or key. Which ever is set will be used.
    :type k:                  str | int | tuple | object
    :param visible:           set initial visibility state of the Button
    :type visible:            (bool)
    :param metadata:          Anything you want to store along with this button
    :type metadata:           (Any)
    :param expand_x:          If True Element will expand in the Horizontal directions
    :type expand_x:           (bool)
    :param expand_y:          If True Element will expand in the Vertical directions
    :type expand_y:           (bool)
    :return:                  returns a button
    :rtype:                   (Button)
    """
    return Button(
        button_text=button_text,
        button_type=BUTTON_TYPE_SAVEAS_FILE,
        target=target,
        file_types=file_types,
        initial_folder=initial_folder,
        default_extension=default_extension,
        tooltip=tooltip,
        size=size,
        s=s,
        disabled=disabled,
        auto_size_button=auto_size_button,
        button_color=button_color,
        change_submits=change_submits,
        enable_events=enable_events,
        font=font,
        pad=pad,
        p=p,
        key=key,
        k=k,
        visible=visible,
        metadata=metadata,
        expand_x=expand_x,
        expand_y=expand_y,
    )


# -------------------------  SAVE BUTTON Element lazy function  ------------------------- #
def Save(
    button_text="Save",
    size=(None, None),
    s=(None, None),
    auto_size_button=None,
    button_color=None,
    bind_return_key=True,
    disabled=False,
    tooltip=None,
    font=None,
    focus=False,
    pad=None,
    p=None,
    key=None,
    k=None,
    visible=True,
    metadata=None,
    expand_x=False,
    expand_y=False,
):
    """

    :param button_text:      text in the button (Default value = 'Save')
    :type button_text:       (str)
    :param size:             (w,h) w=characters-wide, h=rows-high
    :type size:              (int, int)
    :param s:                Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
    :type s:                 (int, int)  | (None, None) | int
    :param auto_size_button: True if button size is determined by button text
    :type auto_size_button:  (bool)
    :param button_color:     button color (foreground, background)
    :type button_color:      (str, str) | str
    :param bind_return_key:  (Default = True) If True, this button will appear to be clicked when return key is pressed in other elements such as Input and elements with return key options
    :type bind_return_key:   (bool)
    :param disabled:         set disable state for element (Default = False)
    :type disabled:          (bool)
    :param tooltip:          text, that will appear when mouse hovers over the element
    :type tooltip:           (str)
    :param font:             specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:              (str or (str, int[, str]) or None)
    :param focus:            if focus should be set to this
    :type focus:             idk_yetReally
    :param pad:              Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
    :type pad:               (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param p:                Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
    :type p:                 (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param key:              key for uniquely identify this element (for window.find_element)
    :type key:               str | int | tuple | object
    :param k:                Same as the Key. You can use either k or key. Which ever is set will be used.
    :type k:                 str | int | tuple | object
    :param visible:          set initial visibility state of the Button
    :type visible:           (bool)
    :param metadata:         Anything you want to store along with this button
    :type metadata:          (Any)
    :param expand_x:         If True Element will expand in the Horizontal directions
    :type expand_x:          (bool)
    :param expand_y:         If True Element will expand in the Vertical directions
    :type expand_y:          (bool)
    :return:                 returns a button
    :rtype:                  (Button)
    """
    return Button(
        button_text=button_text,
        button_type=BUTTON_TYPE_READ_FORM,
        tooltip=tooltip,
        size=size,
        s=s,
        auto_size_button=auto_size_button,
        button_color=button_color,
        font=font,
        disabled=disabled,
        bind_return_key=bind_return_key,
        focus=focus,
        pad=pad,
        p=p,
        key=key,
        k=k,
        visible=visible,
        metadata=metadata,
        expand_x=expand_x,
        expand_y=expand_y,
    )


# -------------------------  SUBMIT BUTTON Element lazy function  ------------------------- #
def Submit(
    button_text="Submit",
    size=(None, None),
    s=(None, None),
    auto_size_button=None,
    button_color=None,
    disabled=False,
    bind_return_key=True,
    tooltip=None,
    font=None,
    focus=False,
    pad=None,
    p=None,
    key=None,
    k=None,
    visible=True,
    metadata=None,
    expand_x=False,
    expand_y=False,
):
    """

    :param button_text:      text in the button (Default value = 'Submit')
    :type button_text:       (str)
    :param size:             (w,h) w=characters-wide, h=rows-high
    :type size:              (int, int)
    :param s:                Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
    :type s:                 (int, int)  | (None, None) | int
    :param auto_size_button: True if button size is determined by button text
    :type auto_size_button:  (bool)
    :param button_color:     button color (foreground, background)
    :type button_color:      (str, str) | str
    :param disabled:         set disable state for element (Default = False)
    :type disabled:          (bool)
    :param bind_return_key:  (Default = True) If True, this button will appear to be clicked when return key is pressed in other elements such as Input and elements with return key options
    :type bind_return_key:   (bool)
    :param tooltip:          text, that will appear when mouse hovers over the element
    :type tooltip:           (str)
    :param font:             specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:              (str or (str, int[, str]) or None)
    :param focus:            if focus should be set to this
    :type focus:             idk_yetReally
    :param pad:              Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
    :type pad:               (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param p:                Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
    :type p:                 (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param key:              key for uniquely identify this element (for window.find_element)
    :type key:               str | int | tuple | object
    :param k:                Same as the Key. You can use either k or key. Which ever is set will be used.
    :type k:                 str | int | tuple | object
    :param visible:          set initial visibility state of the Button
    :type visible:           (bool)
    :param metadata:         Anything you want to store along with this button
    :type metadata:          (Any)
    :param expand_x:         If True Element will expand in the Horizontal directions
    :type expand_x:          (bool)
    :param expand_y:         If True Element will expand in the Vertical directions
    :type expand_y:          (bool)
    :return:                 returns a button
    :rtype:                  (Button)
    """
    return Button(
        button_text=button_text,
        button_type=BUTTON_TYPE_READ_FORM,
        tooltip=tooltip,
        size=size,
        s=s,
        auto_size_button=auto_size_button,
        button_color=button_color,
        font=font,
        disabled=disabled,
        bind_return_key=bind_return_key,
        focus=focus,
        pad=pad,
        p=p,
        key=key,
        k=k,
        visible=visible,
        metadata=metadata,
        expand_x=expand_x,
        expand_y=expand_y,
    )


# -------------------------  OPEN BUTTON Element lazy function  ------------------------- #
# -------------------------  OPEN BUTTON Element lazy function  ------------------------- #
def Open(
    button_text="Open",
    size=(None, None),
    s=(None, None),
    auto_size_button=None,
    button_color=None,
    disabled=False,
    bind_return_key=True,
    tooltip=None,
    font=None,
    focus=False,
    pad=None,
    p=None,
    key=None,
    k=None,
    visible=True,
    metadata=None,
    expand_x=False,
    expand_y=False,
):
    """

    :param button_text:      text in the button (Default value = 'Open')
    :type button_text:       (str)
    :param size:             (w,h) w=characters-wide, h=rows-high
    :type size:              (int, int)
    :param s:                Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
    :type s:                 (int, int)  | (None, None) | int
    :param auto_size_button: True if button size is determined by button text
    :type auto_size_button:  (bool)
    :param button_color:     button color (foreground, background)
    :type button_color:      (str, str) | str
    :param disabled:         set disable state for element (Default = False)
    :type disabled:          (bool)
    :param bind_return_key:  (Default = True) If True, this button will appear to be clicked when return key is pressed in other elements such as Input and elements with return key options
    :type bind_return_key:   (bool)
    :param tooltip:          text, that will appear when mouse hovers over the element
    :type tooltip:           (str)
    :param font:             specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:              (str or (str, int[, str]) or None)
    :param focus:            if focus should be set to this
    :type focus:             idk_yetReally
    :param pad:              Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
    :type pad:               (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param p:                Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
    :type p:                 (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param key:              key for uniquely identify this element (for window.find_element)
    :type key:               str | int | tuple | object
    :param k:                Same as the Key. You can use either k or key. Which ever is set will be used.
    :type k:                 str | int | tuple | object
    :param visible:          set initial visibility state of the Button
    :type visible:           (bool)
    :param metadata:         Anything you want to store along with this button
    :type metadata:          (Any)
    :param expand_x:         If True Element will expand in the Horizontal directions
    :type expand_x:          (bool)
    :param expand_y:         If True Element will expand in the Vertical directions
    :type expand_y:          (bool)
    :return:                 returns a button
    :rtype:                  (Button)
    """
    return Button(
        button_text=button_text,
        button_type=BUTTON_TYPE_READ_FORM,
        tooltip=tooltip,
        size=size,
        s=s,
        auto_size_button=auto_size_button,
        button_color=button_color,
        font=font,
        disabled=disabled,
        bind_return_key=bind_return_key,
        focus=focus,
        pad=pad,
        p=p,
        key=key,
        k=k,
        visible=visible,
        metadata=metadata,
        expand_x=expand_x,
        expand_y=expand_y,
    )


# -------------------------  OK BUTTON Element lazy function  ------------------------- #
def OK(
    button_text="OK",
    size=(None, None),
    s=(None, None),
    auto_size_button=None,
    button_color=None,
    disabled=False,
    bind_return_key=True,
    tooltip=None,
    font=None,
    focus=False,
    pad=None,
    p=None,
    key=None,
    k=None,
    visible=True,
    metadata=None,
    expand_x=False,
    expand_y=False,
):
    """

    :param button_text:      text in the button (Default value = 'OK')
    :type button_text:       (str)
    :param size:             (w,h) w=characters-wide, h=rows-high
    :type size:              (int, int)
    :param s:                Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
    :type s:                 (int, int)  | (None, None) | int
    :param auto_size_button: True if button size is determined by button text
    :type auto_size_button:  (bool)
    :param button_color:     button color (foreground, background)
    :type button_color:      (str, str) | str
    :param disabled:         set disable state for element (Default = False)
    :type disabled:          (bool)
    :param bind_return_key:  (Default = True) If True, this button will appear to be clicked when return key is pressed in other elements such as Input and elements with return key options
    :type bind_return_key:   (bool)
    :param tooltip:          text, that will appear when mouse hovers over the element
    :type tooltip:           (str)
    :param font:             specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:              (str or (str, int[, str]) or None)
    :param focus:            if focus should be set to this
    :type focus:             idk_yetReally
    :param pad:              Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
    :type pad:               (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param p:                Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
    :type p:                 (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param key:              key for uniquely identify this element (for window.find_element)
    :type key:               str | int | tuple | object
    :param k:                Same as the Key. You can use either k or key. Which ever is set will be used.
    :type k:                 str | int | tuple | object
    :param visible:          set initial visibility state of the Button
    :type visible:           (bool)
    :param metadata:         Anything you want to store along with this button
    :type metadata:          (Any)
    :param expand_x:         If True Element will expand in the Horizontal directions
    :type expand_x:          (bool)
    :param expand_y:         If True Element will expand in the Vertical directions
    :type expand_y:          (bool)
    :return:                 returns a button
    :rtype:                  (Button)
    """
    return Button(
        button_text=button_text,
        button_type=BUTTON_TYPE_READ_FORM,
        tooltip=tooltip,
        size=size,
        s=s,
        auto_size_button=auto_size_button,
        button_color=button_color,
        font=font,
        disabled=disabled,
        bind_return_key=bind_return_key,
        focus=focus,
        pad=pad,
        p=p,
        key=key,
        k=k,
        visible=visible,
        metadata=metadata,
        expand_x=expand_x,
        expand_y=expand_y,
    )


# -------------------------  YES BUTTON Element lazy function  ------------------------- #
def Ok(
    button_text="Ok",
    size=(None, None),
    s=(None, None),
    auto_size_button=None,
    button_color=None,
    disabled=False,
    bind_return_key=True,
    tooltip=None,
    font=None,
    focus=False,
    pad=None,
    p=None,
    key=None,
    k=None,
    visible=True,
    metadata=None,
    expand_x=False,
    expand_y=False,
):
    """

    :param button_text:      text in the button (Default value = 'Ok')
    :type button_text:       (str)
    :param size:             (w,h) w=characters-wide, h=rows-high
    :type size:              (int, int)
    :param s:                Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
    :type s:                 (int, int)  | (None, None) | int
    :param auto_size_button: True if button size is determined by button text
    :type auto_size_button:  (bool)
    :param button_color:     button color (foreground, background)
    :type button_color:      (str, str) | str
    :param disabled:         set disable state for element (Default = False)
    :type disabled:          (bool)
    :param bind_return_key:  (Default = True) If True, this button will appear to be clicked when return key is pressed in other elements such as Input and elements with return key options
    :type bind_return_key:   (bool)
    :param tooltip:          text, that will appear when mouse hovers over the element
    :type tooltip:           (str)
    :param font:             specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:              (str or (str, int[, str]) or None)
    :param focus:            if focus should be set to this
    :type focus:             idk_yetReally
    :param pad:              Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
    :type pad:               (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param p:                Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
    :type p:                 (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param key:              key for uniquely identify this element (for window.find_element)
    :type key:               str | int | tuple | object
    :param k:                Same as the Key. You can use either k or key. Which ever is set will be used.
    :type k:                 str | int | tuple | object
    :param visible:          set initial visibility state of the Button
    :type visible:           (bool)
    :param metadata:         Anything you want to store along with this button
    :type metadata:          (Any)
    :param expand_x:         If True Element will expand in the Horizontal directions
    :type expand_x:          (bool)
    :param expand_y:         If True Element will expand in the Vertical directions
    :type expand_y:          (bool)
    :return:                 returns a button
    :rtype:                  (Button)
    """
    return Button(
        button_text=button_text,
        button_type=BUTTON_TYPE_READ_FORM,
        tooltip=tooltip,
        size=size,
        s=s,
        auto_size_button=auto_size_button,
        button_color=button_color,
        font=font,
        disabled=disabled,
        bind_return_key=bind_return_key,
        focus=focus,
        pad=pad,
        p=p,
        key=key,
        k=k,
        visible=visible,
        metadata=metadata,
        expand_x=expand_x,
        expand_y=expand_y,
    )


# -------------------------  CANCEL BUTTON Element lazy function  ------------------------- #
def Cancel(
    button_text="Cancel",
    size=(None, None),
    s=(None, None),
    auto_size_button=None,
    button_color=None,
    disabled=False,
    tooltip=None,
    font=None,
    bind_return_key=False,
    focus=False,
    pad=None,
    p=None,
    key=None,
    k=None,
    visible=True,
    metadata=None,
    expand_x=False,
    expand_y=False,
):
    """

    :param button_text:      text in the button (Default value = 'Cancel')
    :type button_text:       (str)
    :param size:             (w,h) w=characters-wide, h=rows-high
    :type size:              (int, int)
    :param s:                Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
    :type s:                 (int, int)  | (None, None) | int
    :param auto_size_button: True if button size is determined by button text
    :type auto_size_button:  (bool)
    :param button_color:     button color (foreground, background)
    :type button_color:      (str, str) | str
    :param disabled:         set disable state for element (Default = False)
    :type disabled:          (bool)
    :param tooltip:          text, that will appear when mouse hovers over the element
    :type tooltip:           (str)
    :param font:             specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:              (str or (str, int[, str]) or None)
    :param bind_return_key:  (Default = False) If True, this button will appear to be clicked when return key is pressed in other elements such as Input and elements with return key options
    :type bind_return_key:   (bool)
    :param focus:            if focus should be set to this
    :type focus:
    :param pad:              Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
    :type pad:               (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param p:                Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
    :type p:                 (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param key:              key for uniquely identify this element (for window.find_element)
    :type key:               str | int | tuple | object
    :param k:                Same as the Key. You can use either k or key. Which ever is set will be used.
    :type k:                 str | int | tuple | object
    :param visible:          set initial visibility state of the Button
    :type visible:           (bool)
    :param metadata:         Anything you want to store along with this button
    :type metadata:          (Any)
    :param expand_x:         If True Element will expand in the Horizontal directions
    :type expand_x:          (bool)
    :param expand_y:         If True Element will expand in the Vertical directions
    :type expand_y:          (bool)
    :return:                 returns a button
    :rtype:                  (Button)
    """
    return Button(
        button_text=button_text,
        button_type=BUTTON_TYPE_READ_FORM,
        tooltip=tooltip,
        size=size,
        s=s,
        auto_size_button=auto_size_button,
        button_color=button_color,
        font=font,
        disabled=disabled,
        bind_return_key=bind_return_key,
        focus=focus,
        pad=pad,
        p=p,
        key=key,
        k=k,
        visible=visible,
        metadata=metadata,
        expand_x=expand_x,
        expand_y=expand_y,
    )


# -------------------------  QUIT BUTTON Element lazy function  ------------------------- #
def Quit(
    button_text="Quit",
    size=(None, None),
    s=(None, None),
    auto_size_button=None,
    button_color=None,
    disabled=False,
    tooltip=None,
    font=None,
    bind_return_key=False,
    focus=False,
    pad=None,
    p=None,
    key=None,
    k=None,
    visible=True,
    metadata=None,
    expand_x=False,
    expand_y=False,
):
    """

    :param button_text:      text in the button (Default value = 'Quit')
    :type button_text:       (str)
    :param size:             (w,h) w=characters-wide, h=rows-high
    :type size:              (int, int)
    :param s:                Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
    :type s:                 (int, int)  | (None, None) | int
    :param auto_size_button: True if button size is determined by button text
    :type auto_size_button:  (bool)
    :param button_color:     button color (foreground, background)
    :type button_color:      (str, str) | str
    :param disabled:         set disable state for element (Default = False)
    :type disabled:          (bool)
    :param tooltip:          text, that will appear when mouse hovers over the element
    :type tooltip:           (str)
    :param font:             specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:              (str or (str, int[, str]) or None)
    :param bind_return_key:  (Default = False) If True, this button will appear to be clicked when return key is pressed in other elements such as Input and elements with return key options
    :type bind_return_key:   (bool)
    :param focus:            if focus should be set to this
    :type focus:             (bool)
    :param pad:              Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
    :type pad:               (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param p:                Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
    :type p:                 (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param key:              key for uniquely identify this element (for window.find_element)
    :type key:               str | int | tuple | object
    :param k:                Same as the Key. You can use either k or key. Which ever is set will be used.
    :type k:                 str | int | tuple | object
    :param visible:          set initial visibility state of the Button
    :type visible:           (bool)
    :param metadata:         Anything you want to store along with this button
    :type metadata:          (Any)
    :param expand_x:         If True Element will expand in the Horizontal directions
    :type expand_x:          (bool)
    :param expand_y:         If True Element will expand in the Vertical directions
    :type expand_y:          (bool)
    :return:                 returns a button
    :rtype:                  (Button)
    """
    return Button(
        button_text=button_text,
        button_type=BUTTON_TYPE_READ_FORM,
        tooltip=tooltip,
        size=size,
        s=s,
        auto_size_button=auto_size_button,
        button_color=button_color,
        font=font,
        disabled=disabled,
        bind_return_key=bind_return_key,
        focus=focus,
        pad=pad,
        p=p,
        key=key,
        k=k,
        visible=visible,
        metadata=metadata,
        expand_x=expand_x,
        expand_y=expand_y,
    )


# -------------------------  Exit BUTTON Element lazy function  ------------------------- #
def Exit(
    button_text="Exit",
    size=(None, None),
    s=(None, None),
    auto_size_button=None,
    button_color=None,
    disabled=False,
    tooltip=None,
    font=None,
    bind_return_key=False,
    focus=False,
    pad=None,
    p=None,
    key=None,
    k=None,
    visible=True,
    metadata=None,
    expand_x=False,
    expand_y=False,
):
    """

    :param button_text:      text in the button (Default value = 'Exit')
    :type button_text:       (str)
    :param size:             (w,h) w=characters-wide, h=rows-high
    :type size:              (int, int)
    :param s:                Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
    :type s:                 (int, int)  | (None, None) | int
    :param auto_size_button: True if button size is determined by button text
    :type auto_size_button:  (bool)
    :param button_color:     button color (foreground, background)
    :type button_color:      (str, str) | str
    :param disabled:         set disable state for element (Default = False)
    :type disabled:          (bool)
    :param tooltip:          text, that will appear when mouse hovers over the element
    :type tooltip:           (str)
    :param font:             specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:              (str or (str, int[, str]) or None)
    :param bind_return_key:  (Default = False) If True, this button will appear to be clicked when return key is pressed in other elements such as Input and elements with return key options
    :type bind_return_key:   (bool)
    :param focus:            if focus should be set to this
    :type focus:
    :param pad:              Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
    :type pad:               (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param p:                Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
    :type p:                 (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param key:              key for uniquely identify this element (for window.find_element)
    :type key:               str | int | tuple | object
    :param k:                Same as the Key. You can use either k or key. Which ever is set will be used.
    :type k:                 str | int | tuple | object
    :param visible:          set initial visibility state of the Button
    :type visible:           (bool)
    :param metadata:         Anything you want to store along with this button
    :type metadata:          (Any)
    :param expand_x:         If True Element will expand in the Horizontal directions
    :type expand_x:          (bool)
    :param expand_y:         If True Element will expand in the Vertical directions
    :type expand_y:          (bool)
    :return:                 returns a button
    :rtype:                  (Button)
    """
    return Button(
        button_text=button_text,
        button_type=BUTTON_TYPE_READ_FORM,
        tooltip=tooltip,
        size=size,
        s=s,
        auto_size_button=auto_size_button,
        button_color=button_color,
        font=font,
        disabled=disabled,
        bind_return_key=bind_return_key,
        focus=focus,
        pad=pad,
        p=p,
        key=key,
        k=k,
        visible=visible,
        metadata=metadata,
        expand_x=expand_x,
        expand_y=expand_y,
    )


# -------------------------  YES BUTTON Element lazy function  ------------------------- #
def Yes(
    button_text="Yes",
    size=(None, None),
    s=(None, None),
    auto_size_button=None,
    button_color=None,
    disabled=False,
    tooltip=None,
    font=None,
    bind_return_key=True,
    focus=False,
    pad=None,
    p=None,
    key=None,
    k=None,
    visible=True,
    metadata=None,
    expand_x=False,
    expand_y=False,
):
    """

    :param button_text:      text in the button (Default value = 'Yes')
    :type button_text:       (str)
    :param size:             (w,h) w=characters-wide, h=rows-high
    :type size:              (int, int)
    :param s:                Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
    :type s:                 (int, int)  | (None, None) | int
    :param auto_size_button: True if button size is determined by button text
    :type auto_size_button:  (bool)
    :param button_color:     button color (foreground, background)
    :type button_color:      (str, str) | str
    :param disabled:         set disable state for element (Default = False)
    :type disabled:          (bool)
    :param tooltip:          text, that will appear when mouse hovers over the element
    :type tooltip:           (str)
    :param font:             specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:              (str or (str, int[, str]) or None)
    :param bind_return_key:  (Default = True) If True, this button will appear to be clicked when return key is pressed in other elements such as Input and elements with return key options
    :type bind_return_key:   (bool)
    :param focus:            if focus should be set to this
    :type focus:
    :param pad:              Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
    :type pad:               (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param p:                Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
    :type p:                 (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param key:              key for uniquely identify this element (for window.find_element)
    :type key:               str | int | tuple | object
    :param k:                Same as the Key. You can use either k or key. Which ever is set will be used.
    :type k:                 str | int | tuple | object
    :param visible:          set initial visibility state of the Button
    :type visible:           (bool)
    :param metadata:         Anything you want to store along with this button
    :type metadata:          (Any)
    :param expand_x:         If True Element will expand in the Horizontal directions
    :type expand_x:          (bool)
    :param expand_y:         If True Element will expand in the Vertical directions
    :type expand_y:          (bool)
    :return:                 returns a button
    :rtype:                  (Button)
    """
    return Button(
        button_text=button_text,
        button_type=BUTTON_TYPE_READ_FORM,
        tooltip=tooltip,
        size=size,
        s=s,
        auto_size_button=auto_size_button,
        button_color=button_color,
        font=font,
        disabled=disabled,
        bind_return_key=bind_return_key,
        focus=focus,
        pad=pad,
        p=p,
        key=key,
        k=k,
        visible=visible,
        metadata=metadata,
        expand_x=expand_x,
        expand_y=expand_y,
    )


# -------------------------  NO BUTTON Element lazy function  ------------------------- #
def No(
    button_text="No",
    size=(None, None),
    s=(None, None),
    auto_size_button=None,
    button_color=None,
    disabled=False,
    tooltip=None,
    font=None,
    bind_return_key=False,
    focus=False,
    pad=None,
    p=None,
    key=None,
    k=None,
    visible=True,
    metadata=None,
    expand_x=False,
    expand_y=False,
):
    """

    :param button_text:      text in the button (Default value = 'No')
    :type button_text:       (str)
    :param size:             (w,h) w=characters-wide, h=rows-high
    :type size:              (int, int)
    :param s:                Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
    :type s:                 (int, int)  | (None, None) | int
    :param auto_size_button: True if button size is determined by button text
    :type auto_size_button:  (bool)
    :param button_color:     button color (foreground, background)
    :type button_color:      (str, str) | str
    :param disabled:         set disable state for element (Default = False)
    :type disabled:          (bool)
    :param tooltip:          text, that will appear when mouse hovers over the element
    :type tooltip:           (str)
    :param font:             specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:              (str or (str, int[, str]) or None)
    :param bind_return_key:  (Default = False) If True, then the return key will cause a the Listbox to generate an event
    :type bind_return_key:   (bool)
    :param focus:            if focus should be set to this
    :type focus:
    :param pad:              Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
    :type pad:               (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param p:                Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
    :type p:                 (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param key:              key for uniquely identify this element (for window.find_element)
    :type key:               str | int | tuple | object
    :param k:                Same as the Key. You can use either k or key. Which ever is set will be used.
    :type k:                 str | int | tuple | object
    :param visible:          set initial visibility state of the Button
    :type visible:           (bool)
    :param metadata:         Anything you want to store along with this button
    :type metadata:          (Any)
    :param expand_x:         If True Element will expand in the Horizontal directions
    :type expand_x:          (bool)
    :param expand_y:         If True Element will expand in the Vertical directions
    :type expand_y:          (bool)
    :return:                 returns a button
    :rtype:                  (Button)
    """
    return Button(
        button_text=button_text,
        button_type=BUTTON_TYPE_READ_FORM,
        tooltip=tooltip,
        size=size,
        s=s,
        auto_size_button=auto_size_button,
        button_color=button_color,
        font=font,
        disabled=disabled,
        bind_return_key=bind_return_key,
        focus=focus,
        pad=pad,
        p=p,
        key=key,
        k=k,
        visible=visible,
        metadata=metadata,
        expand_x=expand_x,
        expand_y=expand_y,
    )


# -------------------------  NO BUTTON Element lazy function  ------------------------- #
def Help(
    button_text="Help",
    size=(None, None),
    s=(None, None),
    auto_size_button=None,
    button_color=None,
    disabled=False,
    font=None,
    tooltip=None,
    bind_return_key=False,
    focus=False,
    pad=None,
    p=None,
    key=None,
    k=None,
    visible=True,
    metadata=None,
    expand_x=False,
    expand_y=False,
):
    """

    :param button_text:      text in the button (Default value = 'Help')
    :type button_text:       (str)
    :param size:             (w,h) w=characters-wide, h=rows-high
    :type size:              (int, int)
    :param s:                Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
    :type s:                 (int, int)  | (None, None) | int
    :param auto_size_button: True if button size is determined by button text
    :type auto_size_button:  (bool)
    :param button_color:     button color (foreground, background)
    :type button_color:      (str, str) | str
    :param disabled:         set disable state for element (Default = False)
    :type disabled:          (bool)
    :param font:             specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:              (str or (str, int[, str]) or None)
    :param tooltip:          text, that will appear when mouse hovers over the element
    :type tooltip:           (str)
    :param bind_return_key:  (Default = False) If True, this button will appear to be clicked when return key is pressed in other elements such as Input and elements with return key options
    :type bind_return_key:   (bool)
    :param focus:            if focus should be set to this
    :type focus:
    :param pad:              Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
    :type pad:               (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param p:                Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
    :type p:                 (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param key:              key for uniquely identify this element (for window.find_element)
    :type key:               str | int | tuple | object
    :param k:                Same as the Key. You can use either k or key. Which ever is set will be used.
    :type k:                 str | int | tuple | object
    :param visible:          set initial visibility state of the Button
    :type visible:           (bool)
    :param metadata:         Anything you want to store along with this button
    :type metadata:          (Any)
    :param expand_x:         If True Element will expand in the Horizontal directions
    :type expand_x:          (bool)
    :param expand_y:         If True Element will expand in the Vertical directions
    :type expand_y:          (bool)
    :return:                 returns a button
    :rtype:                  (Button)
    """
    return Button(
        button_text=button_text,
        button_type=BUTTON_TYPE_READ_FORM,
        tooltip=tooltip,
        size=size,
        s=s,
        auto_size_button=auto_size_button,
        button_color=button_color,
        font=font,
        disabled=disabled,
        bind_return_key=bind_return_key,
        focus=focus,
        pad=pad,
        p=p,
        key=key,
        k=k,
        visible=visible,
        metadata=metadata,
        expand_x=expand_x,
        expand_y=expand_y,
    )


# -------------------------  NO BUTTON Element lazy function  ------------------------- #
def Debug(
    button_text="",
    size=(None, None),
    s=(None, None),
    auto_size_button=None,
    button_color=None,
    disabled=False,
    font=None,
    tooltip=None,
    bind_return_key=False,
    focus=False,
    pad=None,
    p=None,
    key=None,
    k=None,
    visible=True,
    metadata=None,
    expand_x=False,
    expand_y=False,
):
    """
    This Button has been changed in how it works!!
    Your button has been replaced with a normal button that has the PySimpleGUI Debugger buggon logo on it.
    In your event loop, you will need to check for the event of this button and then call:
            show_debugger_popout_window()
    :param button_text:      text in the button (Default value = '')
    :type button_text:       (str)
    :param size:             (w,h) w=characters-wide, h=rows-high
    :type size:              (int, int)
    :param s:                Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
    :type s:                 (int, int)  | (None, None) | int
    :param auto_size_button: True if button size is determined by button text
    :type auto_size_button:  (bool)
    :param button_color:     button color (foreground, background)
    :type button_color:      (str, str) | str
    :param disabled:         set disable state for element (Default = False)
    :type disabled:          (bool)
    :param font:             specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:              (str or (str, int[, str]) or None)
    :param tooltip:          text, that will appear when mouse hovers over the element
    :type tooltip:           (str)
    :param bind_return_key:  (Default = False) If True, this button will appear to be clicked when return key is pressed in other elements such as Input and elements with return key options
    :type bind_return_key:   (bool)
    :param focus:            if focus should be set to this
    :type focus:
    :param pad:              Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
    :type pad:               (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param p:                Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
    :type p:                 (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param key:              key for uniquely identify this element (for window.find_element)
    :type key:               str | int | tuple | object
    :param k:                Same as the Key. You can use either k or key. Which ever is set will be used.
    :type k:                 str | int | tuple | object
    :param visible:          set initial visibility state of the Button
    :type visible:           (bool)
    :param metadata:         Anything you want to store along with this button
    :type metadata:          (Any)
    :param expand_x:         If True Element will expand in the Horizontal directions
    :type expand_x:          (bool)
    :param expand_y:         If True Element will expand in the Vertical directions
    :type expand_y:          (bool)
    :return:                 returns a button
    :rtype:                  (Button)
    """

    user_key = key if key is not None else k if k is not None else button_text

    return Button(
        button_text="",
        button_type=BUTTON_TYPE_READ_FORM,
        tooltip=tooltip,
        size=size,
        s=s,
        auto_size_button=auto_size_button,
        button_color=theme_button_color(),
        font=font,
        disabled=disabled,
        bind_return_key=bind_return_key,
        focus=focus,
        pad=pad,
        p=p,
        key=user_key,
        k=k,
        visible=visible,
        image_data=PSG_DEBUGGER_LOGO,
        image_subsample=2,
        border_width=0,
        metadata=metadata,
        expand_x=expand_x,
        expand_y=expand_y,
    )


# -------------------------  GENERIC BUTTON Element lazy function  ------------------------- #
def SimpleButton(
    button_text,
    image_filename=None,
    image_data=None,
    image_size=(None, None),
    image_subsample=None,
    border_width=None,
    tooltip=None,
    size=(None, None),
    s=(None, None),
    auto_size_button=None,
    button_color=None,
    font=None,
    bind_return_key=False,
    disabled=False,
    focus=False,
    pad=None,
    p=None,
    key=None,
    k=None,
    metadata=None,
    expand_x=False,
    expand_y=False,
):
    """
    DEPIRCATED

    This Button should not be used.

    :param border_width:
    :param button_text:      text in the button
    :type button_text:       (str)
    :param image_filename:   image filename if there is a button image
    :type image_filename:    image filename if there is a button image
    :param image_data:       in-RAM image to be displayed on button
    :type image_data:        in-RAM image to be displayed on button
    :param image_size:       image size (O.K.)
    :type image_size:        (Default = (None))
    :param image_subsample:  amount to reduce the size of the image
    :type image_subsample:   amount to reduce the size of the image
    :param tooltip:          text, that will appear when mouse hovers over the element
    :type tooltip:           (str)
    :param size:             (w,h) w=characters-wide, h=rows-high
    :type size:              (int, int)
    :param s:                Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
    :type s:                 (int, int)  | (None, None) | int
    :param auto_size_button: True if button size is determined by button text
    :type auto_size_button:  (bool)
    :param button_color:     button color (foreground, background)
    :type button_color:      (str, str) | str
    :param font:             specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:              (str or (str, int[, str]) or None)
    :param bind_return_key:  (Default = False) If True, this button will appear to be clicked when return key is pressed in other elements such as Input and elements with return key options
    :type bind_return_key:   (bool)
    :param disabled:         set disable state for element (Default = False)
    :type disabled:          (bool)
    :param focus:            if focus should be set to this
    :type focus:             idk_yetReally
    :param pad:              Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
    :type pad:               (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param p:                Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
    :type p:                 (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param key:              key for uniquely identify this element (for window.find_element)
    :type key:               str | int | tuple | object
    :param k:                Same as the Key. You can use either k or key. Which ever is set will be used.
    :type k:                 str | int | tuple | object
    :param metadata:         Anything you want to store along with this button
    :type metadata:          (Any)
    :param expand_x:         If True Element will expand in the Horizontal directions
    :type expand_x:          (bool)
    :param expand_y:         If True Element will expand in the Vertical directions
    :type expand_y:          (bool)
    :return:                 returns a button
    :rtype:                  (Button)
    """
    return Button(
        button_text=button_text,
        button_type=BUTTON_TYPE_CLOSES_WIN,
        image_filename=image_filename,
        image_data=image_data,
        image_size=image_size,
        image_subsample=image_subsample,
        border_width=border_width,
        tooltip=tooltip,
        disabled=disabled,
        size=size,
        s=s,
        auto_size_button=auto_size_button,
        button_color=button_color,
        font=font,
        bind_return_key=bind_return_key,
        focus=focus,
        pad=pad,
        p=p,
        key=key,
        k=k,
        metadata=metadata,
        expand_x=expand_x,
        expand_y=expand_y,
    )


# -------------------------  CLOSE BUTTON Element lazy function  ------------------------- #
def CloseButton(
    button_text,
    image_filename=None,
    image_data=None,
    image_size=(None, None),
    image_subsample=None,
    border_width=None,
    tooltip=None,
    size=(None, None),
    s=(None, None),
    auto_size_button=None,
    button_color=None,
    font=None,
    bind_return_key=False,
    disabled=False,
    focus=False,
    pad=None,
    p=None,
    key=None,
    k=None,
    metadata=None,
    expand_x=False,
    expand_y=False,
):
    """
    DEPRICATED

    This button should not be used.  Instead explicitly close your windows by calling window.close() or by using
    the close parameter in window.read

    :param border_width:
    :param button_text:      text in the button
    :type button_text:       (str)
    :param image_filename:   image filename if there is a button image
    :type image_filename:    image filename if there is a button image
    :param image_data:       in-RAM image to be displayed on button
    :type image_data:        in-RAM image to be displayed on button
    :param image_size:       image size (O.K.)
    :type image_size:        (Default = (None))
    :param image_subsample:  amount to reduce the size of the image
    :type image_subsample:   amount to reduce the size of the image
    :param tooltip:          text, that will appear when mouse hovers over the element
    :type tooltip:           (str)
    :param size:             (w,h) w=characters-wide, h=rows-high
    :type size:              (int, int)
    :param s:                Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
    :type s:                 (int, int)  | (None, None) | int
    :param auto_size_button: True if button size is determined by button text
    :type auto_size_button:  (bool)
    :param button_color:     button color (foreground, background)
    :type button_color:      (str, str) | str
    :param font:             specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:              (str or (str, int[, str]) or None)
    :param bind_return_key:  (Default = False) If True, this button will appear to be clicked when return key is pressed in other elements such as Input and elements with return key options
    :type bind_return_key:   (bool)
    :param disabled:         set disable state for element (Default = False)
    :type disabled:          (bool)
    :param focus:            if focus should be set to this
    :type focus:             idk_yetReally
    :param pad:              Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
    :type pad:               (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param p:                Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
    :type p:                 (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param key:              key for uniquely identify this element (for window.find_element)
    :type key:               str | int | tuple | object
    :param k:                Same as the Key. You can use either k or key. Which ever is set will be used.
    :type k:                 str | int | tuple | object
    :param metadata:         Anything you want to store along with this button
    :type metadata:          (Any)
    :param expand_x:         If True Element will expand in the Horizontal directions
    :type expand_x:          (bool)
    :param expand_y:         If True Element will expand in the Vertical directions
    :type expand_y:          (bool)
    :return:                 returns a button
    :rtype:                  (Button)
    """
    return Button(
        button_text=button_text,
        button_type=BUTTON_TYPE_CLOSES_WIN,
        image_filename=image_filename,
        image_data=image_data,
        image_size=image_size,
        image_subsample=image_subsample,
        border_width=border_width,
        tooltip=tooltip,
        disabled=disabled,
        size=size,
        s=s,
        auto_size_button=auto_size_button,
        button_color=button_color,
        font=font,
        bind_return_key=bind_return_key,
        focus=focus,
        pad=pad,
        p=p,
        key=key,
        k=k,
        metadata=metadata,
        expand_x=expand_x,
        expand_y=expand_y,
    )


CButton = CloseButton


# -------------------------  GENERIC BUTTON Element lazy function  ------------------------- #
def ReadButton(
    button_text,
    image_filename=None,
    image_data=None,
    image_size=(None, None),
    image_subsample=None,
    border_width=None,
    tooltip=None,
    size=(None, None),
    s=(None, None),
    auto_size_button=None,
    button_color=None,
    font=None,
    bind_return_key=False,
    disabled=False,
    focus=False,
    pad=None,
    p=None,
    key=None,
    k=None,
    metadata=None,
    expand_x=False,
    expand_y=False,
):
    """
    :param button_text:      text in the button
    :type button_text:       (str)
    :param image_filename:   image filename if there is a button image
    :type image_filename:    image filename if there is a button image
    :param image_data:       in-RAM image to be displayed on button
    :type image_data:        in-RAM image to be displayed on button
    :param image_size:       image size (O.K.)
    :type image_size:        (Default = (None))
    :param image_subsample:  amount to reduce the size of the image
    :type image_subsample:   amount to reduce the size of the image
    :param tooltip:          text, that will appear when mouse hovers over the element
    :type tooltip:           (str)
    :param size:             (w,h) w=characters-wide, h=rows-high
    :type size:              (int, int)
    :param s:                Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
    :type s:                 (int, int)  | (None, None) | int
    :param auto_size_button: True if button size is determined by button text
    :type auto_size_button:  (bool)
    :param button_color:     button color (foreground, background)
    :type button_color:      (str, str) | str
    :param font:             specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:              (str or (str, int[, str]) or None)
    :param bind_return_key:  (Default = False) If True, this button will appear to be clicked when return key is pressed in other elements such as Input and elements with return key options
    :type bind_return_key:   (bool)
    :param disabled:         set disable state for element (Default = False)
    :type disabled:          (bool)
    :param focus:            if focus should be set to this
    :type focus:             idk_yetReally
    :param pad:              Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
    :type pad:               (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param p:                Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
    :type p:                 (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param key:              key for uniquely identify this element (for window.find_element)
    :type key:               str | int | tuple | object
    :param k:                Same as the Key. You can use either k or key. Which ever is set will be used.
    :type k:                 str | int | tuple | object
    :param border_width:     width of border around element
    :type border_width:      (int)
    :param metadata:         Anything you want to store along with this button
    :type metadata:          (Any)
    :param expand_x:         If True Element will expand in the Horizontal directions
    :type expand_x:          (bool)
    :param expand_y:         If True Element will expand in the Vertical directions
    :type expand_y:          (bool)
    :return:                 Button created
    :rtype:                  (Button)
    """

    return Button(
        button_text=button_text,
        button_type=BUTTON_TYPE_READ_FORM,
        image_filename=image_filename,
        image_data=image_data,
        image_size=image_size,
        image_subsample=image_subsample,
        border_width=border_width,
        tooltip=tooltip,
        size=size,
        s=s,
        disabled=disabled,
        auto_size_button=auto_size_button,
        button_color=button_color,
        font=font,
        bind_return_key=bind_return_key,
        focus=focus,
        pad=pad,
        p=p,
        key=key,
        k=k,
        metadata=metadata,
        expand_x=expand_x,
        expand_y=expand_y,
    )


ReadFormButton = ReadButton
RButton = ReadFormButton


# -------------------------  Realtime BUTTON Element lazy function  ------------------------- #
def RealtimeButton(
    button_text,
    image_filename=None,
    image_data=None,
    image_size=(None, None),
    image_subsample=None,
    border_width=None,
    tooltip=None,
    size=(None, None),
    s=(None, None),
    auto_size_button=None,
    button_color=None,
    font=None,
    disabled=False,
    bind_return_key=False,
    focus=False,
    pad=None,
    p=None,
    key=None,
    k=None,
    visible=True,
    metadata=None,
    expand_x=False,
    expand_y=False,
):
    """

    :param button_text:      text in the button
    :type button_text:       (str)
    :param image_filename:   image filename if there is a button image
    :type image_filename:    image filename if there is a button image
    :param image_data:       in-RAM image to be displayed on button
    :type image_data:        in-RAM image to be displayed on button
    :param image_size:       image size (O.K.)
    :type image_size:        (Default = (None))
    :param image_subsample:  amount to reduce the size of the image
    :type image_subsample:   amount to reduce the size of the image
    :param border_width:     width of border around element
    :type border_width:      (int)
    :param tooltip:          text, that will appear when mouse hovers over the element
    :type tooltip:           (str)
    :param size:             (w,h) w=characters-wide, h=rows-high
    :type size:              (int, int)
    :param s:                Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
    :type s:                 (int, int)  | (None, None) | int
    :param auto_size_button: True if button size is determined by button text
    :type auto_size_button:  (bool)
    :param button_color:     button color (foreground, background)
    :type button_color:      (str, str) | str
    :param font:             specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:              (str or (str, int[, str]) or None)
    :param disabled:         set disable state for element (Default = False)
    :type disabled:          (bool)
    :param bind_return_key:  (Default = False) If True, this button will appear to be clicked when return key is pressed in other elements such as Input and elements with return key options
    :type bind_return_key:   (bool)
    :param focus:            if focus should be set to this
    :type focus:             (bool)
    :param pad:              Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
    :type pad:               (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param p:                Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
    :type p:                 (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param key:              key for uniquely identify this element (for window.find_element)
    :type key:               str | int | tuple | object
    :param k:                Same as the Key. You can use either k or key. Which ever is set will be used.
    :type k:                 str | int | tuple | object
    :param visible:          set initial visibility state of the Button
    :type visible:           (bool)
    :param metadata:         Anything you want to store along with this button
    :type metadata:          (Any)
    :param expand_x:         If True Element will expand in the Horizontal directions
    :type expand_x:          (bool)
    :param expand_y:         If True Element will expand in the Vertical directions
    :type expand_y:          (bool)
    :return:                 Button created
    :rtype:                  (Button)
    """
    return Button(
        button_text=button_text,
        button_type=BUTTON_TYPE_REALTIME,
        image_filename=image_filename,
        image_data=image_data,
        image_size=image_size,
        image_subsample=image_subsample,
        border_width=border_width,
        tooltip=tooltip,
        disabled=disabled,
        size=size,
        s=s,
        auto_size_button=auto_size_button,
        button_color=button_color,
        font=font,
        bind_return_key=bind_return_key,
        focus=focus,
        pad=pad,
        p=p,
        key=key,
        k=k,
        visible=visible,
        metadata=metadata,
        expand_x=expand_x,
        expand_y=expand_y,
    )


# -------------------------  Dummy BUTTON Element lazy function  ------------------------- #
def DummyButton(
    button_text,
    image_filename=None,
    image_data=None,
    image_size=(None, None),
    image_subsample=None,
    border_width=None,
    tooltip=None,
    size=(None, None),
    s=(None, None),
    auto_size_button=None,
    button_color=None,
    font=None,
    disabled=False,
    bind_return_key=False,
    focus=False,
    pad=None,
    p=None,
    key=None,
    k=None,
    visible=True,
    metadata=None,
    expand_x=False,
    expand_y=False,
):
    """
    This is a special type of Button.

    It will close the window but NOT send an event that the window has been closed.

    It's used in conjunction with non-blocking windows to silently close them.  They are used to
    implement the non-blocking popup windows. They're also found in some Demo Programs, so look there for proper use.

    :param button_text:      text in the button
    :type button_text:       (str)
    :param image_filename:   image filename if there is a button image
    :type image_filename:    image filename if there is a button image
    :param image_data:       in-RAM image to be displayed on button
    :type image_data:        in-RAM image to be displayed on button
    :param image_size:       image size (O.K.)
    :type image_size:        (Default = (None))
    :param image_subsample:  amount to reduce the size of the image
    :type image_subsample:   amount to reduce the size of the image
    :param border_width:     width of border around element
    :type border_width:      (int)
    :param tooltip:          text, that will appear when mouse hovers over the element
    :type tooltip:           (str)
    :param size:             (w,h) w=characters-wide, h=rows-high
    :type size:              (int, int)
    :param s:                Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
    :type s:                 (int, int)  | (None, None) | int
    :param auto_size_button: True if button size is determined by button text
    :type auto_size_button:  (bool)
    :param button_color:     button color (foreground, background)
    :type button_color:      (str, str) | str
    :param font:             specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:              (str or (str, int[, str]) or None)
    :param disabled:         set disable state for element (Default = False)
    :type disabled:          (bool)
    :param bind_return_key:  (Default = False) If True, this button will appear to be clicked when return key is pressed in other elements such as Input and elements with return key options
    :type bind_return_key:   (bool)
    :param focus:            if focus should be set to this
    :type focus:             (bool)
    :param pad:              Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
    :type pad:               (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param p:                Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
    :type p:                 (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param key:              key for uniquely identify this element (for window.find_element)
    :type key:               str | int | tuple | object
    :param k:                Same as the Key. You can use either k or key. Which ever is set will be used.
    :type k:                 str | int | tuple | object
    :param visible:          set initial visibility state of the Button
    :type visible:           (bool)
    :param metadata:         Anything you want to store along with this button
    :type metadata:          (Any)
    :param expand_x:         If True Element will expand in the Horizontal directions
    :type expand_x:          (bool)
    :param expand_y:         If True Element will expand in the Vertical directions
    :type expand_y:          (bool)
    :return:                 returns a button
    :rtype:                  (Button)
    """
    return Button(
        button_text=button_text,
        button_type=BUTTON_TYPE_CLOSES_WIN_ONLY,
        image_filename=image_filename,
        image_data=image_data,
        image_size=image_size,
        image_subsample=image_subsample,
        border_width=border_width,
        tooltip=tooltip,
        size=size,
        s=s,
        auto_size_button=auto_size_button,
        button_color=button_color,
        font=font,
        disabled=disabled,
        bind_return_key=bind_return_key,
        focus=focus,
        pad=pad,
        p=p,
        key=key,
        k=k,
        visible=visible,
        metadata=metadata,
        expand_x=expand_x,
        expand_y=expand_y,
    )


# -------------------------  Calendar Chooser Button lazy function  ------------------------- #
def CalendarButton(
    button_text,
    target=(ThisRow, -1),
    close_when_date_chosen=True,
    default_date_m_d_y=(None, None, None),
    image_filename=None,
    image_data=None,
    image_size=(None, None),
    image_subsample=None,
    tooltip=None,
    border_width=None,
    size=(None, None),
    s=(None, None),
    auto_size_button=None,
    button_color=None,
    disabled=False,
    font=None,
    bind_return_key=False,
    focus=False,
    pad=None,
    p=None,
    enable_events=None,
    key=None,
    k=None,
    visible=True,
    locale=None,
    format="%Y-%m-%d %H:%M:%S",
    begin_at_sunday_plus=0,
    month_names=None,
    day_abbreviations=None,
    title="Choose Date",
    no_titlebar=True,
    location=(None, None),
    metadata=None,
    expand_x=False,
    expand_y=False,
):
    """
    Button that will show a calendar chooser window.  Fills in the target element with result

    :param enable_events:
    :param button_text:            text in the button
    :type button_text:             (str)
    :param target:                 Key or "coordinate" (see docs) of target element
    :type target:                  (int, int) | Any
    :param close_when_date_chosen: (Default = True)
    :type close_when_date_chosen:  bool
    :param default_date_m_d_y:     Beginning date to show
    :type default_date_m_d_y:      (int, int or None, int)
    :param image_filename:         image filename if there is a button image
    :type image_filename:          image filename if there is a button image
    :param image_data:             in-RAM image to be displayed on button
    :type image_data:              in-RAM image to be displayed on button
    :param image_size:             image size (O.K.)
    :type image_size:              (Default = (None))
    :param image_subsample:        amount to reduce the size of the image
    :type image_subsample:         amount to reduce the size of the image
    :param tooltip:                text, that will appear when mouse hovers over the element
    :type tooltip:                 (str)
    :param border_width:           width of border around element
    :type border_width:            width of border around element
    :param size:                   (w,h) w=characters-wide, h=rows-high
    :type size:                    (int, int)
    :param s:                      Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
    :type s:                       (int, int)  | (None, None) | int
    :param auto_size_button:       True if button size is determined by button text
    :type auto_size_button:        (bool)
    :param button_color:           button color (foreground, background)
    :type button_color:            (str, str) | str
    :param disabled:               set disable state for element (Default = False)
    :type disabled:                (bool)
    :param font:                   specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:                    (str or (str, int[, str]) or None)
    :param bind_return_key:  (Default = False) If True, this button will appear to be clicked when return key is pressed in other elements such as Input and elements with return key options
    :type bind_return_key:         bool
    :param focus:                  if focus should be set to this
    :type focus:                   bool
    :param pad:                    Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
    :type pad:                     (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param p:                      Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
    :type p:                       (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param key:                    key for uniquely identify this element (for window.find_element)
    :type key:                     str | int | tuple | object
    :param k:                      Same as the Key. You can use either k or key. Which ever is set will be used.
    :type k:                       str | int | tuple | object
    :param locale:                 defines the locale used to get day names
    :type locale:                  str
    :param format:                 formats result using this strftime format
    :type format:                  str
    :param begin_at_sunday_plus:   Determines the left-most day in the display. 0=sunday, 1=monday, etc
    :type begin_at_sunday_plus:    (int)
    :param month_names:            optional list of month names to use (should be 12 items)
    :type month_names:             List[str]
    :param day_abbreviations:      optional list of abbreviations to display as the day of week
    :type day_abbreviations:       List[str]
    :param title:                  Title shown on the date chooser window
    :type title:                   (str)
    :param no_titlebar:            if True no titlebar will be shown on the date chooser window
    :type no_titlebar:             bool
    :param location:               Location on the screen (x,y) to show the calendar popup window
    :type location:                (int, int)
    :param visible:                set initial visibility state of the Button
    :type visible:                 (bool)
    :param metadata:               Anything you want to store along with this button
    :type metadata:                (Any)
    :param expand_x:               If True Element will expand in the Horizontal directions
    :type expand_x:                (bool)
    :param expand_y:               If True Element will expand in the Vertical directions
    :type expand_y:                (bool)
    :return:                       returns a button
    :rtype:                        (Button)
    """
    button = Button(
        button_text=button_text,
        button_type=BUTTON_TYPE_CALENDAR_CHOOSER,
        target=target,
        image_filename=image_filename,
        image_data=image_data,
        image_size=image_size,
        image_subsample=image_subsample,
        border_width=border_width,
        tooltip=tooltip,
        size=size,
        s=s,
        auto_size_button=auto_size_button,
        button_color=button_color,
        font=font,
        disabled=disabled,
        enable_events=enable_events,
        bind_return_key=bind_return_key,
        focus=focus,
        pad=pad,
        p=p,
        key=key,
        k=k,
        visible=visible,
        metadata=metadata,
        expand_x=expand_x,
        expand_y=expand_y,
    )
    button.calendar_close_when_chosen = close_when_date_chosen
    button.calendar_default_date_M_D_Y = default_date_m_d_y
    button.calendar_locale = locale
    button.calendar_format = format
    button.calendar_no_titlebar = no_titlebar
    button.calendar_location = location
    button.calendar_begin_at_sunday_plus = begin_at_sunday_plus
    button.calendar_month_names = month_names
    button.calendar_day_abbreviations = day_abbreviations
    button.calendar_title = title

    return button


# -------------------------  Calendar Chooser Button lazy function  ------------------------- #
def ColorChooserButton(
    button_text,
    target=(ThisRow, -1),
    image_filename=None,
    image_data=None,
    image_size=(None, None),
    image_subsample=None,
    tooltip=None,
    border_width=None,
    size=(None, None),
    s=(None, None),
    auto_size_button=None,
    button_color=None,
    disabled=False,
    font=None,
    bind_return_key=False,
    focus=False,
    pad=None,
    p=None,
    key=None,
    k=None,
    default_color=None,
    visible=True,
    metadata=None,
    expand_x=False,
    expand_y=False,
):
    """

    :param button_text:      text in the button
    :type button_text:       (str)
    :param target:           key or (row,col) target for the button. Note that -1 for column means 1 element to the left of this one. The constant ThisRow is used to indicate the current row. The Button itself is a valid target for some types of button
    :type target:            str | (int, int)
    :type image_filename:    (str)
    :param image_filename:   image filename if there is a button image. GIFs and PNGs only.
    :type image_filename:    (str)
    :param image_data:       Raw or Base64 representation of the image to put on button. Choose either filename or data
    :type image_data:        bytes | str
    :param image_size:       Size of the image in pixels (width, height)
    :type image_size:        (int, int)
    :param image_subsample:  amount to reduce the size of the image. Divides the size by this number. 2=1/2, 3=1/3, 4=1/4, etc
    :type image_subsample:   (int)
    :param tooltip:          text, that will appear when mouse hovers over the element
    :type tooltip:           (str)
    :param border_width:     width of border around element
    :type border_width:      (int)
    :param size:             (w,h) w=characters-wide, h=rows-high
    :type size:              (int, int)
    :param s:                Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
    :type s:                 (int, int)  | (None, None) | int
    :param auto_size_button: True if button size is determined by button text
    :type auto_size_button:  (bool)
    :param button_color:     button color (foreground, background)
    :type button_color:      (str, str) | str
    :param disabled:         set disable state for element (Default = False)
    :type disabled:          (bool)
    :param font:             specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:              (str or (str, int[, str]) or None)
    :param bind_return_key:  (Default = False) If True, this button will appear to be clicked when return key is pressed in other elements such as Input and elements with return key options
    :type bind_return_key:   (bool)
    :param focus:            Determines if initial focus should go to this element.
    :type focus:             (bool)
    :param pad:              Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
    :type pad:               (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param p:                Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
    :type p:                 (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param key:              key for uniquely identify this element (for window.find_element)
    :type key:               str | int | tuple | object
    :param k:                Same as the Key. You can use either k or key. Which ever is set will be used.
    :type k:                 str | int | tuple | object
    :param default_color:    Color to be sent to tkinter to use as the default color
    :type default_color:     str
    :param visible:          set initial visibility state of the Button
    :type visible:           (bool)
    :param metadata:         User metadata that can be set to ANYTHING
    :type metadata:          (Any)
    :param expand_x:         If True Element will expand in the Horizontal directions
    :type expand_x:          (bool)
    :param expand_y:         If True Element will expand in the Vertical directions
    :type expand_y:          (bool)
    :return:                 returns a button
    :rtype:                  (Button)
    """
    button = Button(
        button_text=button_text,
        button_type=BUTTON_TYPE_COLOR_CHOOSER,
        target=target,
        image_filename=image_filename,
        image_data=image_data,
        image_size=image_size,
        image_subsample=image_subsample,
        border_width=border_width,
        tooltip=tooltip,
        size=size,
        s=s,
        auto_size_button=auto_size_button,
        button_color=button_color,
        font=font,
        disabled=disabled,
        bind_return_key=bind_return_key,
        focus=focus,
        pad=pad,
        p=p,
        key=key,
        k=k,
        visible=visible,
        metadata=metadata,
        expand_x=expand_x,
        expand_y=expand_y,
    )
    button.default_color = default_color
    return button


#####################################  -----  BUTTON Functions   ------ ##################################################
