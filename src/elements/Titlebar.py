from .elements import Column,Image,Text
from ..constants import *

def Titlebar(
    title="",
    icon=None,
    text_color=None,
    background_color=None,
    font=None,
    key=None,
    k=None,
):
    """
    A custom titlebar that replaces the OS provided titlebar, thus giving you control
    the is not possible using the OS provided titlebar such as the color.

    NOTE LINUX USERS - at the moment the minimize function is not yet working.  Windows users
    should have no problem and it should function as a normal window would.

    This titlebar is created from a row of elements that is then encapsulated into a
    one Column element which is what this Titlebar function returns to you.

    A custom titlebar removes the margins from your window.  If you want the  remainder
    of your Window to have margins, place the layout after the Titlebar into a Column and
    set the pad of that Column to the dimensions you would like your margins to have.

    The Titlebar is a COLUMN element.  You can thus call the update method for the column and
    perform operations such as making the column visible/invisible

    :param icon:             Can be either a filename or Base64 byte string of a PNG or GIF. This is used in an Image element to create the titlebar
    :type icon:              str or bytes or None
    :param title:            The "title" to show in the titlebar
    :type title:             str
    :param text_color:       Text color for titlebar
    :type text_color:        str | None
    :param background_color: Background color for titlebar
    :type background_color:  str | None
    :param font:             Font to be used for the text and the symbols
    :type font:              (str or (str, int[, str]) or None)
    :param key:              Identifies an Element. Should be UNIQUE to this window.
    :type key:               str | int | tuple | object | None
    :param k:                Exactly the same as key.  Choose one of them to use
    :type k:                 str | int | tuple | object | None
    :return:                 A single Column element that has eveything in 1 element
    :rtype:                  Column
    """
    bc = background_color or CUSTOM_TITLEBAR_BACKGROUND_COLOR or theme_button_color()[1]
    tc = text_color or CUSTOM_TITLEBAR_TEXT_COLOR or theme_button_color()[0]
    font = font or CUSTOM_TITLEBAR_FONT or ("Helvetica", 12)
    key = k or key

    if isinstance(icon, bytes):
        icon_and_text_portion = [
            Image(data=icon, background_color=bc, key=TITLEBAR_IMAGE_KEY)
        ]
    elif icon == TITLEBAR_DO_NOT_USE_AN_ICON:
        icon_and_text_portion = []
    elif icon is not None:
        icon_and_text_portion = [
            Image(filename=icon, background_color=bc, key=TITLEBAR_IMAGE_KEY)
        ]
    elif CUSTOM_TITLEBAR_ICON is not None:
        if isinstance(CUSTOM_TITLEBAR_ICON, bytes):
            icon_and_text_portion = [
                Image(
                    data=CUSTOM_TITLEBAR_ICON,
                    background_color=bc,
                    key=TITLEBAR_IMAGE_KEY,
                )
            ]
        else:
            icon_and_text_portion = [
                Image(
                    filename=CUSTOM_TITLEBAR_ICON,
                    background_color=bc,
                    key=TITLEBAR_IMAGE_KEY,
                )
            ]
    else:
        icon_and_text_portion = [
            Image(
                data=DEFAULT_BASE64_ICON_16_BY_16,
                background_color=bc,
                key=TITLEBAR_IMAGE_KEY,
            )
        ]

    icon_and_text_portion += [
        T(
            title,
            text_color=tc,
            background_color=bc,
            font=font,
            grab=True,
            key=TITLEBAR_TEXT_KEY,
        )
    ]

    return Column(
        [
            [
                Column([icon_and_text_portion], pad=(0, 0), background_color=bc),
                Column(
                    [
                        [
                            T(
                                SYMBOL_TITLEBAR_MINIMIZE,
                                text_color=tc,
                                background_color=bc,
                                enable_events=True,
                                font=font,
                                key=TITLEBAR_MINIMIZE_KEY,
                            ),
                            Text(
                                SYMBOL_TITLEBAR_MAXIMIZE,
                                text_color=tc,
                                background_color=bc,
                                enable_events=True,
                                font=font,
                                key=TITLEBAR_MAXIMIZE_KEY,
                            ),
                            Text(
                                SYMBOL_TITLEBAR_CLOSE,
                                text_color=tc,
                                background_color=bc,
                                font=font,
                                enable_events=True,
                                key=TITLEBAR_CLOSE_KEY,
                            ),
                        ]
                    ],
                    element_justification="r",
                    expand_x=True,
                    grab=True,
                    pad=(0, 0),
                    background_color=bc,
                ),
            ]
        ],
        expand_x=True,
        grab=True,
        background_color=bc,
        pad=(0, 0),
        metadata=TITLEBAR_METADATA_MARKER,
        key=key,
    )

