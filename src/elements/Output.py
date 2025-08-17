from ..core import Element
from ..constants import *
from . import Multiline

# ---------------------------------------------------------------------- #
#                           Output                                       #
#  Routes stdout, stderr to a scrolled window                            #
# ---------------------------------------------------------------------- #
class Output(Multiline):
    """
    Output Element - a multi-lined text area to where stdout, stderr, cprint are rerouted.

    The Output Element is now based on the Multiline Element.  When you make an Output Element, you're
    creating a Multiline Element with some specific settings set:
        auto_refresh = True
        auto_scroll = True
        reroute_stdout = True
        reroute_stderr = True
        reroute_cprint = True
        write_only = True

    If you choose to use a Multiline element to replace an Output element, be sure an turn on the write_only paramter in the Multiline
    so that an item is not included in the values dictionary on every window.read call
    """

    def __init__(
        self,
        size=(None, None),
        s=(None, None),
        background_color=None,
        text_color=None,
        pad=None,
        p=None,
        autoscroll_only_at_bottom=False,
        echo_stdout_stderr=False,
        font=None,
        tooltip=None,
        key=None,
        k=None,
        right_click_menu=None,
        expand_x=False,
        expand_y=False,
        visible=True,
        metadata=None,
        wrap_lines=None,
        horizontal_scroll=None,
        sbar_trough_color=None,
        sbar_background_color=None,
        sbar_arrow_color=None,
        sbar_width=None,
        sbar_arrow_width=None,
        sbar_frame_color=None,
        sbar_relief=None,
    ):
        """
        :param size:                        (w, h) w=characters-wide, h=rows-high. If an int instead of a tuple is supplied, then height is auto-set to 1
        :type size:                         (int, int)  | (None, None) | int
        :param s:                           Same as size parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, size will be used
        :type s:                            (int, int)  | (None, None) | int
        :param background_color:            color of background
        :type background_color:             (str)
        :param text_color:                  color of the text
        :type text_color:                   (str)
        :param pad:                         Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int)
        :type pad:                          (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
        :param p:                           Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
        :type p:                            (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
        :param autoscroll_only_at_bottom:   If True the contents of the element will automatically scroll only if the scrollbar is at the bottom of the multiline
        :type autoscroll_only_at_bottom:    (bool)
        :param echo_stdout_stderr:          If True then output to stdout will be output to this element AND also to the normal console location
        :type echo_stdout_stderr:           (bool)
        :param font:                        specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
        :type font:                         (str or (str, int[, str]) or None)
        :param tooltip:                     text, that will appear when mouse hovers over the element
        :type tooltip:                      (str)
        :param key:                         Used with window.find_element and with return values to uniquely identify this element to uniquely identify this element
        :type key:                          str | int | tuple | object
        :param k:                           Same as the Key. You can use either k or key. Which ever is set will be used.
        :type k:                            str | int | tuple | object
        :param right_click_menu:            A list of lists of Menu items to show when this element is right clicked. See user docs for exact format.
        :type right_click_menu:             List[List[ List[str] | str ]]
        :param expand_x:                    If True the element will automatically expand in the X direction to fill available space
        :type expand_x:                     (bool)
        :param expand_y:                    If True the element will automatically expand in the Y direction to fill available space
        :type expand_y:                     (bool)
        :param visible:                     set visibility state of the element
        :type visible:                      (bool)
        :param metadata:                    User metadata that can be set to ANYTHING
        :type metadata:                     (Any)
        :param wrap_lines:                  If True, the lines will be wrapped automatically. Other parms affect this setting, but this one will override them all. Default is it does nothing and uses previous settings for wrapping.
        :type wrap_lines:                   (bool)
        :param horizontal_scroll:           Controls if a horizontal scrollbar should be shown. If True, then line wrapping will be off by default
        :type horizontal_scroll:            (bool)
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

        super().__init__(
            size=size,
            s=s,
            background_color=background_color,
            autoscroll_only_at_bottom=autoscroll_only_at_bottom,
            text_color=text_color,
            pad=pad,
            p=p,
            echo_stdout_stderr=echo_stdout_stderr,
            font=font,
            tooltip=tooltip,
            wrap_lines=wrap_lines,
            horizontal_scroll=horizontal_scroll,
            key=key,
            k=k,
            right_click_menu=right_click_menu,
            write_only=True,
            reroute_stdout=True,
            reroute_stderr=True,
            reroute_cprint=True,
            autoscroll=True,
            auto_refresh=True,
            expand_x=expand_x,
            expand_y=expand_y,
            visible=visible,
            metadata=metadata,
            sbar_trough_color=sbar_trough_color,
            sbar_background_color=sbar_background_color,
            sbar_arrow_color=sbar_arrow_color,
            sbar_width=sbar_width,
            sbar_arrow_width=sbar_arrow_width,
            sbar_frame_color=sbar_frame_color,
            sbar_relief=sbar_relief,
        )

