from PyQt5 import QtGui, QtCore
import random
import colorsys
from colour import Color

class RandomPenColor:
    
    def __init__(self):
        super().__init__()
        self.ColorsUsed = [[255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255]]

    def GetColor(self):
        h,s,l = random.random(), 0.5 + random.random()/2.0, 0.4 + random.random()/5.0
        r,g,b = [int(256*i) for i in colorsys.hls_to_rgb(h,l,s)]
        self.ColorsUsed[:-1] = self.ColorsUsed[1:]
        self.ColorsUsed[-1] = [r, g, b]
        #print(self.ColorsUsed)
        return QtGui.QColor(r, g, b)


def ColorInterpolate(temp, coldColor, neutralColor, warmColor, hotColor, coldLower, coldUpper, warmLower, warmUpper, hotLower, hotUpper):
    if temp < warmLower and temp > warmUpper:
        return Color(neutralColor).hex_l
    elif (temp >= hotLower):
        x = min(1, max(0, (temp - hotLower) / (hotUpper - hotLower)))
        colorList = list(Color(warmColor).range_to(Color(hotColor), 3))
        mid = int(len(colorList) / 2)
        return colorList[mid].hex_l
    elif (temp >= warmLower): 
        x = min(1, max(0, (temp - warmLower) / (warmUpper - warmLower)))
        colorList = list(Color(neutralColor).range_to(Color(warmColor), 3))
        mid = int(len(colorList) / 2)
        return colorList[mid].hex_l
    else:
        x = min(1, max(0, (temp - coldLower) / (coldUpper - coldLower)))
        colorList = list(Color(coldColor).range_to(Color(neutralColor), 3))
        mid = int(len(colorList) / 2)
        return colorList[mid].hex_l