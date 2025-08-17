from ..core import Element
from ..constants import *

# ---------------------------------------------------------------------- #
#                       TKProgressBar                                    #
#  Emulate the TK ProgressBar using canvas and rectangles
# ---------------------------------------------------------------------- #


class TKProgressBar:
    uniqueness_counter = 0

    def __init__(
        self,
        root,
        max,
        length=400,
        width=DEFAULT_PROGRESS_BAR_SIZE[1],
        ttk_theme=DEFAULT_TTK_THEME,
        style_name="",
        relief=DEFAULT_PROGRESS_BAR_RELIEF,
        border_width=DEFAULT_PROGRESS_BAR_BORDER_WIDTH,
        orientation="horizontal",
        BarColor=(None, None),
        key=None,
    ):
        """
        :param root:         The root window bar is to be shown in
        :type root:          tk.Tk | tk.TopLevel
        :param max:          Maximum value the bar will be measuring
        :type max:           (int)
        :param length:       length in pixels of the bar
        :type length:        (int)
        :param width:        width in pixels of the bar
        :type width:         (int)
        :param style_name:   Progress bar style to use.  Set in the packer function
        :type style_name:    (str)
        :param ttk_theme:    Progress bar style defined as one of these 'default', 'winnative', 'clam', 'alt', 'classic', 'vista', 'xpnative'
        :type ttk_theme:     (str)
        :param relief:       relief style. Values are same as progress meter relief values.  Can be a constant or a string: `RELIEF_RAISED RELIEF_SUNKEN RELIEF_FLAT RELIEF_RIDGE RELIEF_GROOVE RELIEF_SOLID` (Default value = DEFAULT_PROGRESS_BAR_RELIEF)
        :type relief:        (str)
        :param border_width: The amount of pixels that go around the outside of the bar
        :type border_width:  (int)
        :param orientation:  'horizontal' or 'vertical' ('h' or 'v' work) (Default value = 'vertical')
        :type orientation:   (str)
        :param BarColor:     The 2 colors that make up a progress bar. One is the background, the other is the bar
        :type BarColor:      (str, str)
        :param key:          Used with window.find_element and with return values to uniquely identify this element to uniquely identify this element
        :type key:           str | int | tuple | object
        """

        self.Length = length
        self.Width = width
        self.Max = max
        self.Orientation = orientation
        self.Count = None
        self.PriorCount = 0
        self.style_name = style_name

        TKProgressBar.uniqueness_counter += 1

        if orientation.lower().startswith("h"):
            s = ttk.Style()
            _change_ttk_theme(s, ttk_theme)

            # self.style_name = str(key) + str(TKProgressBar.uniqueness_counter) + "my.Horizontal.TProgressbar"
            if BarColor != COLOR_SYSTEM_DEFAULT and BarColor[0] != COLOR_SYSTEM_DEFAULT:
                s.configure(
                    self.style_name,
                    background=BarColor[0],
                    troughcolor=BarColor[1],
                    troughrelief=relief,
                    borderwidth=border_width,
                    thickness=width,
                )
            else:
                s.configure(
                    self.style_name,
                    troughrelief=relief,
                    borderwidth=border_width,
                    thickness=width,
                )

            self.TKProgressBarForReal = ttk.Progressbar(
                root,
                maximum=self.Max,
                style=self.style_name,
                length=length,
                orient=tk.HORIZONTAL,
                mode="determinate",
            )
        else:
            s = ttk.Style()
            _change_ttk_theme(s, ttk_theme)
            # self.style_name = str(key) + str(TKProgressBar.uniqueness_counter) + "my.Vertical.TProgressbar"
            if BarColor != COLOR_SYSTEM_DEFAULT and BarColor[0] != COLOR_SYSTEM_DEFAULT:
                s.configure(
                    self.style_name,
                    background=BarColor[0],
                    troughcolor=BarColor[1],
                    troughrelief=relief,
                    borderwidth=border_width,
                    thickness=width,
                )
            else:
                s.configure(
                    self.style_name,
                    troughrelief=relief,
                    borderwidth=border_width,
                    thickness=width,
                )

            self.TKProgressBarForReal = ttk.Progressbar(
                root,
                maximum=self.Max,
                style=self.style_name,
                length=length,
                orient=tk.VERTICAL,
                mode="determinate",
            )

    def Update(self, count=None, max=None):
        """
        Update the current value of the bar and/or update the maximum value the bar can reach
        :param count: current value
        :type count:  (int)
        :param max:   the maximum value
        :type max:    (int)
        """
        if max is not None:
            self.Max = max
            try:
                self.TKProgressBarForReal.config(maximum=max)
            except Exception:
                return False
        if count is not None:
            try:
                self.TKProgressBarForReal["value"] = count
            except Exception:
                return False
        return True

