class SeqStyle:
    """ Initialize sequence diagram rendering style """

    def __init__(self):
        self.axes_width = 2
        self.axes_color = (0, 0, 0)
        self.axes_ticks = False
        self.axes_overlayed = True

        self.color = (0, 0, 0)
        self.color_fill = (0.5, 0.5, 0.5, 0.2)
        self.width = 2
        self.font_size = 20
        self.font_color = (0, 0, 0)
        self.zorder = 1

        self.arrow_length = 0.1
