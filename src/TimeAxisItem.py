import pyqtgraph as pg
import time 

class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        # PySide's QTime() initialiser fails miserably and dismisses args/kwargs
        return [time.strftime('%H:%M:%S', time.gmtime(int(value/1000))) for value in values]