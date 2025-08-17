from ..core import Element
from ..constants import *

# ---------------------------------------------------------------------- #
#                           Horizontal Separator                           #
# ---------------------------------------------------------------------- #
class HorizontalSeparator(Element):
    """
    Horizontal Separator Element draws a Horizontal line at the given location.
    """

    def __init__(self, color=None, pad=None, p=None, key=None, k=None):
        """
        :param color: Color of the line. Defaults to theme's text color. Can be name or #RRGGBB format
        :type color:  (str)
        :param pad:   Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
        :type pad:    (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
        :param p:     Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
        :type p:      (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
        :param key:   Value that uniquely identifies this element from all other elements. Used when Finding an element or in return values. Must be unique to the window
        :type key:    str | int | tuple | object
        :param k:     Same as the Key. You can use either k or key. Which ever is set will be used.
        :type k:      str | int | tuple | object
        """

        self.Orientation = "horizontal"  # for now only vertical works
        self.color = color if color is not None else theme_text_color()
        self.expand_x = True
        self.expand_y = None
        key = key if key is not None else k
        pad = pad if pad is not None else p

        super().__init__(ELEM_TYPE_SEPARATOR, pad=pad, key=key)


HSeparator = HorizontalSeparator
HSep = HorizontalSeparator

