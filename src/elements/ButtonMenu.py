from ..core import Element
from ..constants import *


# ---------------------------------------------------------------------- #
#                           ButtonMenu Class                             #
# ---------------------------------------------------------------------- #
class ButtonMenu(Element):
    """
    The Button Menu Element.  Creates a button that when clicked will show a menu similar to right click menu
    """

    def __init__(
        self,
        button_text,
        menu_def,
        tooltip=None,
        disabled=False,
        image_source=None,
        image_filename=None,
        image_data=None,
        image_size=(None, None),
        image_subsample=None,
        image_zoom=None,
        border_width=None,
        size=(None, None),
        s=(None, None),
        auto_size_button=None,
        button_color=None,
        text_color=None,
        background_color=None,
        disabled_text_color=None,
        font=None,
        item_font=None,
        pad=None,
        p=None,
        expand_x=False,
        expand_y=False,
        key=None,
        k=None,
        tearoff=False,
        visible=True,
        metadata=None,
    ):
        """
        :param button_text:               Text to be displayed on the button
        :type button_text:                (str)
        :param menu_def:                  A list of lists of Menu items to show when this element is clicked. See docs for format as they are the same for all menu types
        :type menu_def:                   List[List[str]]
        :param tooltip:                   text, that will appear when mouse hovers over the element
        :type tooltip:                    (str)
        :param disabled:                  If True button will be created disabled
        :type disabled:                   (bool)
        :param image_source:              Image to place on button. Use INSTEAD of the image_filename and image_data. Unifies these into 1 easier to use parm
        :type image_source:               (str | bytes)
        :param image_filename:            image filename if there is a button image. GIFs and PNGs only.
        :type image_filename:             (str)
        :param image_data:                Raw or Base64 representation of the image to put on button. Choose either filename or data
        :type image_data:                 bytes | str
        :param image_size:                Size of the image in pixels (width, height)
        :type image_size:                 (int, int)
        :param image_subsample:           amount to reduce the size of the image. Divides the size by this number. 2=1/2, 3=1/3, 4=1/4, etc
        :type image_subsample:            (int)
        :param image_zoom:                amount to increase the size of the image. 2=twice size, 3=3 times, etc
        :type image_zoom:                 (int)
        :param border_width:              width of border around button in pixels
        :type border_width:               (int)
        :param size:                      (w, h) w=characters-wide, h=rows-high. If an int instead of a tuple is supplied, then height is auto-set to 1
        :type size:                       (int, int)  | (None, None) | int
        :param s:                         Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
        :type s:                          (int, int)  | (None, None) | int
        :param auto_size_button:          if True the button size is sized to fit the text
        :type auto_size_button:           (bool)
        :param button_color:              of button. Easy to remember which is which if you say "ON" between colors. "red" on "green"
        :type button_color:               (str, str) | str
        :param background_color:          color of the background
        :type background_color:           (str)
        :param text_color:                element's text color. Can be in #RRGGBB format or a color name "black"
        :type text_color:                 (str)
        :param disabled_text_color:       color to use for text when item is disabled. Can be in #RRGGBB format or a color name "black"
        :type disabled_text_color:        (str)
        :param font:                      specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
        :type font:                       (str or (str, int[, str]) or None)
        :param item_font:                 specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike, for the menu items
        :type item_font:                  (str or (str, int[, str]) or None)
        :param pad:                       Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
        :type pad:                        (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
        :param p:                         Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
        :type p:                          (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
        :param expand_x:                  If True the element will automatically expand in the X direction to fill available space
        :type expand_x:                   (bool)
        :param expand_y:                  If True the element will automatically expand in the Y direction to fill available space
        :type expand_y:                   (bool)
        :param key:                       Used with window.find_element and with return values to uniquely identify this element to uniquely identify this element
        :type key:                        str | int | tuple | object
        :param k:                         Same as the Key. You can use either k or key. Which ever is set will be used.
        :type k:                          str | int | tuple | object
        :param tearoff:                   Determines if menus should allow them to be torn off
        :type tearoff:                    (bool)
        :param visible:                   set visibility state of the element
        :type visible:                    (bool)
        :param metadata:                  User metadata that can be set to ANYTHING
        :type metadata:                   (Any)
        """

        self.MenuDefinition = copy.deepcopy(menu_def)

        self.AutoSizeButton = auto_size_button
        self.ButtonText = button_text
        self.ButtonColor = button_color_to_tuple(button_color)
        # self.TextColor = self.ButtonColor[0]
        # self.BackgroundColor = self.ButtonColor[1]
        self.BackgroundColor = (
            background_color
            if background_color is not None
            else theme_input_background_color()
        )
        self.TextColor = (
            text_color if text_color is not None else theme_input_text_color()
        )
        self.DisabledTextColor = (
            disabled_text_color
            if disabled_text_color is not None
            else COLOR_SYSTEM_DEFAULT
        )
        self.ItemFont = item_font
        self.BorderWidth = (
            border_width if border_width is not None else DEFAULT_BORDER_WIDTH
        )
        if image_source is not None:
            if isinstance(image_source, str):
                image_filename = image_source
            elif isinstance(image_source, bytes):
                image_data = image_source
            else:
                warnings.warn(
                    "ButtonMenu element - image_source is not a valid type: {}".format(
                        type(image_source)
                    ),
                    UserWarning,
                )

        self.ImageFilename = image_filename
        self.ImageData = image_data
        self.ImageSize = image_size
        self.ImageSubsample = image_subsample
        self.zoom = int(image_zoom) if image_zoom is not None else None
        self.Disabled = disabled
        self.IsButtonMenu = True
        self.MenuItemChosen = None
        self.Widget = self.TKButtonMenu = None  # type: tk.Menubutton
        self.TKMenu = None  # type: tk.Menu
        self.part_of_custom_menubar = False
        self.custom_menubar_key = None
        # self.temp_size = size if size != (NONE, NONE) else
        key = key if key is not None else k
        sz = size if size != (None, None) else s
        pad = pad if pad is not None else p
        self.expand_x = expand_x
        self.expand_y = expand_y

        super().__init__(
            ELEM_TYPE_BUTTONMENU,
            size=sz,
            font=font,
            pad=pad,
            key=key,
            tooltip=tooltip,
            text_color=self.TextColor,
            background_color=self.BackgroundColor,
            visible=visible,
            metadata=metadata,
        )
        self.Tearoff = tearoff

    def _MenuItemChosenCallback(
        self, item_chosen
    ):  # ButtonMenu Menu Item Chosen Callback
        """
        Not a user callable function.  Called by tkinter when an item is chosen from the menu.

        :param item_chosen: The menu item chosen.
        :type item_chosen:  (str)
        """
        # print('IN MENU ITEM CALLBACK', item_chosen)
        self.MenuItemChosen = item_chosen
        self.ParentForm.LastButtonClicked = self.Key
        self.ParentForm.FormRemainedOpen = True
        # if self.ParentForm.CurrentlyRunningMainloop:
        #     self.ParentForm.TKroot.quit()  # kick the users out of the mainloop
        _exit_mainloop(self.ParentForm)

    def update(
        self,
        menu_definition=None,
        visible=None,
        image_source=None,
        image_size=(None, None),
        image_subsample=None,
        image_zoom=None,
        button_text=None,
        button_color=None,
    ):
        """
        Changes some of the settings for the ButtonMenu Element. Must call `Window.Read` or `Window.Finalize` prior

        Changes will not be visible in your window until you call window.read or window.refresh.

        If you change visibility, your element may MOVE. If you want it to remain stationary, use the "layout helper"
        function "pin" to ensure your element is "pinned" to that location in your layout so that it returns there
        when made visible.

        :param menu_definition: (New menu definition (in menu definition format)
        :type menu_definition:  List[List]
        :param visible:         control visibility of element
        :type visible:          (bool)
        :param image_source:    new image if image is to be changed. Can be a filename or a base64 encoded byte-string
        :type image_source:     (str | bytes)
        :param image_size:      Size of the image in pixels (width, height)
        :type image_size:       (int, int)
        :param image_subsample: amount to reduce the size of the image. Divides the size by this number. 2=1/2, 3=1/3, 4=1/4, etc
        :type image_subsample:  (int)
        :param image_zoom:      amount to increase the size of the image. 2=twice size, 3=3 times, etc
        :type image_zoom:       (int)
        :param button_text:     Text to be shown on the button
        :type button_text:      (str)
        :param button_color:    Normally a tuple, but can be a simplified-button-color-string "foreground on background". Can be a single color if want to set only the background.
        :type button_color:     (str, str) | str
        """

        if (
            not self._widget_was_created()
        ):  # if widget hasn't been created yet, then don't allow
            return

        if self._this_elements_window_closed():
            _error_popup_with_traceback(
                "Error in ButtonMenu.update - The window was closed"
            )
            return

        if menu_definition is not None:
            self.MenuDefinition = copy.deepcopy(menu_definition)
            top_menu = self.TKMenu = tk.Menu(
                self.TKButtonMenu,
                tearoff=self.Tearoff,
                font=self.ItemFont,
                tearoffcommand=self._tearoff_menu_callback,
            )

            if self.BackgroundColor not in (COLOR_SYSTEM_DEFAULT, None):
                top_menu.config(bg=self.BackgroundColor)
            if self.TextColor not in (COLOR_SYSTEM_DEFAULT, None):
                top_menu.config(fg=self.TextColor)
            if self.DisabledTextColor not in (COLOR_SYSTEM_DEFAULT, None):
                top_menu.config(disabledforeground=self.DisabledTextColor)
            if self.ItemFont is not None:
                top_menu.config(font=self.ItemFont)
            AddMenuItem(self.TKMenu, self.MenuDefinition[1], self)
            self.TKButtonMenu.configure(menu=self.TKMenu)
        if image_source is not None:
            filename = data = None
            if image_source is not None:
                if isinstance(image_source, bytes):
                    data = image_source
                elif isinstance(image_source, str):
                    filename = image_source
                else:
                    warnings.warn(
                        "ButtonMenu element - image_source is not a valid type: {}".format(
                            type(image_source)
                        ),
                        UserWarning,
                    )
            image = None
            if filename is not None:
                image = tk.PhotoImage(file=filename)
                if image_subsample is not None:
                    image = image.subsample(image_subsample)
                if image_zoom is not None:
                    image = image.zoom(int(image_zoom))
            elif data is not None:
                # if type(data) is bytes:
                try:
                    image = tk.PhotoImage(data=data)
                    if image_subsample is not None:
                        image = image.subsample(image_subsample)
                    if image_zoom is not None:
                        image = image.zoom(int(image_zoom))
                except Exception as e:
                    image = data

            if image is not None:
                if type(image) is not bytes:
                    width, height = (
                        image_size[0] if image_size[0] is not None else image.width(),
                        image_size[1] if image_size[1] is not None else image.height(),
                    )
                else:
                    width, height = image_size

                self.TKButtonMenu.config(
                    image=image, compound=tk.CENTER, width=width, height=height
                )
                self.TKButtonMenu.image = image
        if button_text is not None:
            self.TKButtonMenu.configure(text=button_text)
            self.ButtonText = button_text
        if not visible:
            self._pack_forget_save_settings()
        elif visible:
            self._pack_restore_settings()
        if visible is not None:
            self._visible = visible
        if button_color != (None, None) and button_color != COLOR_SYSTEM_DEFAULT:
            bc = button_color_to_tuple(button_color, self.ButtonColor)
            if bc[0] not in (None, COLOR_SYSTEM_DEFAULT):
                self.TKButtonMenu.config(foreground=bc[0], activeforeground=bc[0])
            if bc[1] not in (None, COLOR_SYSTEM_DEFAULT):
                self.TKButtonMenu.config(background=bc[1], activebackground=bc[1])
            self.ButtonColor = bc

    def click(self):
        """
        Generates a click of the button as if the user clicked the button
        Calls the tkinter invoke method for the button
        """
        try:
            self.TKMenu.invoke(1)
        except Exception:
            print("Exception clicking button")

    Update = update
    Click = click


BMenu = ButtonMenu
BM = ButtonMenu
