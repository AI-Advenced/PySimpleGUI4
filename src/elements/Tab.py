from ..core import Element
from ..constants import *

# ---------------------------------------------------------------------- #
#                           Tab                                          #
# ---------------------------------------------------------------------- #
class Tab(Element):
    """
    Tab Element is another "Container" element that holds a layout and displays a tab with text. Used with TabGroup only
    Tabs are never placed directly into a layout.  They are always "Contained" in a TabGroup layout
    """

    def __init__(
        self,
        title,
        layout,
        title_color=None,
        background_color=None,
        font=None,
        pad=None,
        p=None,
        disabled=False,
        border_width=None,
        key=None,
        k=None,
        tooltip=None,
        right_click_menu=None,
        expand_x=False,
        expand_y=False,
        visible=True,
        element_justification="left",
        image_source=None,
        image_subsample=None,
        image_zoom=None,
        metadata=None,
    ):
        """
        :param title:                 text to show on the tab
        :type title:                  (str)
        :param layout:                The element layout that will be shown in the tab
        :type layout:                 List[List[Element]]
        :param title_color:           color of the tab text (note not currently working on tkinter)
        :type title_color:            (str)
        :param background_color:      color of background of the entire layout
        :type background_color:       (str)
        :param font:                  NOT USED in the tkinter port
        :type font:                   (str or (str, int[, str]) or None)
        :param pad:                   Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
        :type pad:                    (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
        :param p:                     Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
        :type p:                      (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
        :param disabled:              If True button will be created disabled
        :type disabled:               (bool)
        :param border_width:          NOT USED in tkinter port
        :type border_width:           (int)
        :param key:                   Value that uniquely identifies this element from all other elements. Used when Finding an element or in return values. Must be unique to the window
        :type key:                    str | int | tuple | object
        :param k:                     Same as the Key. You can use either k or key. Which ever is set will be used.
        :type k:                      str | int | tuple | object
        :param tooltip:               text, that will appear when mouse hovers over the element
        :type tooltip:                (str)
        :param right_click_menu:      A list of lists of Menu items to show when this element is right clicked. See user docs for exact format.
        :type right_click_menu:       List[List[ List[str] | str ]]
        :param expand_x:              If True the element will automatically expand in the X direction to fill available space
        :type expand_x:               (bool)
        :param expand_y:              If True the element will automatically expand in the Y direction to fill available space
        :type expand_y:               (bool)
        :param visible:               set visibility state of the element
        :type visible:                (bool)
        :param element_justification: All elements inside the Tab will have this justification 'left', 'right', 'center' are valid values
        :type element_justification:  (str)
        :param image_source:          A filename or a base64 bytes of an image to place on the Tab
        :type image_source:            str | bytes | None
        :param image_subsample:       amount to reduce the size of the image. Divides the size by this number. 2=1/2, 3=1/3, 4=1/4, etc
        :type image_subsample:        (int)
        :param image_zoom:            amount to increase the size of the image. 2=twice size, 3=3 times, etc
        :type image_zoom:             (int)
        :param metadata:              User metadata that can be set to ANYTHING
        :type metadata:               (Any)
        """

        filename = data = None
        if image_source is not None:
            if isinstance(image_source, bytes):
                data = image_source
            elif isinstance(image_source, str):
                filename = image_source
            else:
                warnings.warn(
                    "Image element - source is not a valid type: {}".format(
                        type(image_source)
                    ),
                    UserWarning,
                )

        self.Filename = filename
        self.Data = data
        self.ImageSubsample = image_subsample
        self.zoom = int(image_zoom) if image_zoom is not None else None
        self.UseDictionary = False
        self.ReturnValues = None
        self.ReturnValuesList = []
        self.ReturnValuesDictionary = {}
        self.DictionaryKeyCounter = 0
        self.ParentWindow = None
        self.Rows = []
        self.TKFrame = None
        self.Widget = None  # type: tk.Frame
        self.Title = title
        self.BorderWidth = border_width
        self.Disabled = disabled
        self.ParentNotebook = None
        self.TabID = None
        self.BackgroundColor = (
            background_color
            if background_color is not None
            else DEFAULT_BACKGROUND_COLOR
        )
        self.RightClickMenu = right_click_menu
        self.ContainerElemementNumber = Window._GetAContainerNumber()
        self.ElementJustification = element_justification
        key = key if key is not None else k
        pad = pad if pad is not None else p
        self.expand_x = expand_x
        self.expand_y = expand_y

        self.Layout(layout)

        super().__init__(
            ELEM_TYPE_TAB,
            background_color=background_color,
            text_color=title_color,
            font=font,
            pad=pad,
            key=key,
            tooltip=tooltip,
            visible=visible,
            metadata=metadata,
        )
        return

    def add_row(self, *args):
        """
        Not recommended use call.  Used to add rows of Elements to the Frame Element.

        """
        NumRows = len(self.Rows)  # number of existing rows is our row number
        CurrentRowNumber = NumRows  # this row's number
        CurrentRow = []  # start with a blank row and build up
        # -------------------------  Add the elements to a row  ------------------------- #
        for i, element in enumerate(
            args
        ):  # Loop through list of elements and add them to the row
            if type(element) == list:
                popup_error_with_traceback(
                    "Error creating Tab layout",
                    "Layout has a LIST instead of an ELEMENT",
                    "This sometimes means you have a badly placed ]",
                    "The offensive list is:",
                    element,
                    "This list will be stripped from your layout",
                )
                continue
            elif callable(element) and not isinstance(element, Element):
                popup_error_with_traceback(
                    "Error creating Tab layout",
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
                popup_error_with_traceback(
                    "Error creating Tab layout",
                    "The layout specified has already been used",
                    'You MUST start witha "clean", unused layout every time you create a window',
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
            if element.Key is not None:
                self.UseDictionary = True
        # -------------------------  Append the row to list of Rows  ------------------------- #
        self.Rows.append(CurrentRow)

    def layout(self, rows):
        """
        Not user callable.  Use layout parameter instead. Creates the layout using the supplied rows of Elements

        :param rows: List[List[Element]] The list of rows
        :type rows:  List[List[Element]]
        :return:     (Tab) used for chaining
        :rtype:
        """

        for row in rows:
            try:
                iter(row)
            except TypeError:
                PopupError(
                    "Error creating Tab layout",
                    "Your row is not an iterable (e.g. a list)",
                    "Instead of a list, the type found was {}".format(type(row)),
                    "The offensive row = ",
                    row,
                    "This item will be stripped from your layout",
                    keep_on_top=True,
                    image=_random_error_emoji(),
                )
                continue
            self.AddRow(*row)
        return self

    def update(self, title=None, disabled=None, visible=None):
        """
        Changes some of the settings for the Tab Element. Must call `Window.Read` or `Window.Finalize` prior

        Changes will not be visible in your window until you call window.read or window.refresh.

        If you change visibility, your element may MOVE. If you want it to remain stationary, use the "layout helper"
        function "pin" to ensure your element is "pinned" to that location in your layout so that it returns there
        when made visible.

        :param title:    tab title
        :type title:     (str)
        :param disabled: disable or enable state of the element
        :type disabled:  (bool)
        :param visible:  control visibility of element
        :type visible:   (bool)
        """
        if (
            not self._widget_was_created()
        ):  # if widget hasn't been created yet, then don't allow
            return

        if self._this_elements_window_closed():
            _error_popup_with_traceback("Error in Tab.update - The window was closed")
            return

        state = "normal"
        if disabled is not None:
            self.Disabled = disabled
            if disabled:
                state = "disabled"
        if not visible:
            state = "hidden"
        if visible is not None:
            self._visible = visible

        self.ParentNotebook.tab(self.TabID, state=state)

        if title is not None:
            self.Title = str(title)
            self.ParentNotebook.tab(self.TabID, text=self.Title)
            # self.ParentNotebook.tab(self.ContainerElemementNumber-1, text=self.Title)

        # if visible is False:
        #     self.ParentNotebook.pack_forget()
        # elif visible is True:
        #     self.ParentNotebook.pack()
        return self

    def _GetElementAtLocation(self, location):
        """
        Not user callable. Used to find the Element at a row, col position within the layout

        :param location: (row, column) position of the element to find in layout
        :type location:  (int, int)
        :return:         The element found at the location
        :rtype:          (Element)
        """

        (row_num, col_num) = location
        row = self.Rows[row_num]
        element = row[col_num]
        return element

    def select(self):
        """
        Create a tkinter event that mimics user clicking on a tab. Must have called window.Finalize / Read first!

        """
        # Use a try in case the window has been destoyed
        try:
            self.ParentNotebook.select(self.TabID)
        except Exception as e:
            print("Exception Selecting Tab {}".format(e))

    AddRow = add_row
    Layout = layout
    Select = select
    Update = update

