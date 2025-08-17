from ..core import Element
from ..constants import *




def MenubarCustom(
    menu_definition,
    disabled_text_color=None,
    bar_font=None,
    font=None,
    tearoff=False,
    pad=0,
    p=None,
    background_color=None,
    text_color=None,
    bar_background_color=None,
    bar_text_color=None,
    key=None,
    k=None,
):
    """
    A custom Menubar that replaces the OS provided Menubar

    Why?
    Two reasons - 1. they look great (see custom titlebar) 2. if you have a custom titlebar, then you have to use a custom menubar if you want a menubar

    :param menu_definition:      The Menu definition specified using lists (docs explain the format)
    :type menu_definition:       List[List[Tuple[str, List[str]]]
    :param disabled_text_color:  color to use for text when item is disabled. Can be in #RRGGBB format or a color name "black"
    :type disabled_text_color:   (str)
    :param bar_font:             specifies the font family, size to be used for the chars in the bar itself
    :type bar_font:              (str or (str, int[, str]) or None)
    :param font:                 specifies the font family, size to be used for the menu items
    :type font:                  (str or (str, int[, str]) or None)
    :param tearoff:              if True, then can tear the menu off from the window ans use as a floating window. Very cool effect
    :type tearoff:               (bool)
    :param pad:                  Amount of padding to put around element in pixels (left/right, top/bottom) or ((left, right), (top, bottom)) or an int. If an int, then it's converted into a tuple (int, int).  TIP - 0 will make flush with titlebar
    :type pad:                   (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param p:                    Same as pad parameter.  It's an alias. If EITHER of them are set, then the one that's set will be used. If BOTH are set, pad will be used
    :type p:                     (int, int) or ((int, int),(int,int)) or (int,(int,int)) or  ((int, int),int) | int
    :param background_color:     color to use for background of the menus that are displayed after making a section. Can be in #RRGGBB format or a color name "black". Defaults to the color of the bar text
    :type background_color:      (str)
    :param text_color:           color to use for the text of the many items in the displayed menus. Can be in #RRGGBB format or a color name "black". Defaults to the bar background
    :type text_color:            (str)
    :param bar_background_color: color to use for the menubar. Can be in #RRGGBB format or a color name "black". Defaults to theme's button text color
    :type bar_background_color:  (str)
    :param bar_text_color:       color to use for the menu items text when item is disabled. Can be in #RRGGBB format or a color name "black". Defaults to theme's button background color
    :type bar_text_color:        (str)
    :param key:                  Value that uniquely identifies this element from all other elements. Used when Finding an element or in return values. Must be unique to the window
    :type key:                   str | int | tuple | object
    :param k:                    Same as the Key. You can use either k or key. Which ever is set will be used.
    :type k:                     str | int | tuple | object
    :returns:                    A Column element that has a series of ButtonMenu elements
    :rtype:                      Column
    """

    # 设置菜单背景色、文本色和内边距的默认值
    bar_bg = bar_background_color or theme_button_color()[0]
    bar_text = bar_text_color or theme_button_color()[1]
    menu_bg = background_color or bar_text
    menu_text = text_color or bar_bg
    pad = pad or p

    row = []
    for menu in menu_definition:
        text = menu[0]
        if MENU_SHORTCUT_CHARACTER in text:
            text = text.replace(MENU_SHORTCUT_CHARACTER, "")
        if text.startswith(MENU_DISABLED_CHARACTER):
            disabled = True
            text = text[len(MENU_DISABLED_CHARACTER) :]
        else:
            disabled = False

        button_menu = ButtonMenu(
            text,
            menu,
            border_width=0,
            button_color=(bar_text, bar_bg),
            key=text,
            pad=(0, 0),
            disabled=disabled,
            font=bar_font,
            item_font=font,
            disabled_text_color=disabled_text_color,
            text_color=menu_text,
            background_color=menu_bg,
            tearoff=tearoff,
        )
        button_menu.part_of_custom_menubar = True
        button_menu.custom_menubar_key = key if key is not None else k
        row += [button_menu]
    return Column(
        [row],
        pad=pad,
        background_color=bar_bg,
        expand_x=True,
        key=key if key is not None else k,
    )

