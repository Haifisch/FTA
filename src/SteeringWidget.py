from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QBoxLayout, QGridLayout, QLabel, QApplication, QGraphicsDropShadowEffect
import math

class SteeringWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(250, 250)
        self.currentSteeringValue = 0.0

    def GetSteeringAngle(self, angle, x):
        percentSteeringAngle = (angle + 127.0) / 255.0
        return percentSteeringAngle * 2 * math.pi * (321.25 / 360) + x

    def paintEvent(self, event):
        paint = QtGui.QPainter()
        paint.begin(self)
        paint.setRenderHint(QtGui.QPainter.Antialiasing)
        #paint.setPen(QtCore.Qt.yellow)
        #paint.setBrush(QtCore.Qt.yellow)
        #paint.drawEllipse(QtCore.QRect(35, 35, 200, 200))
        paint.setPen(QtCore.Qt.red)
        paint.setBrush(QtCore.Qt.white)
        #print(str(self.currentSteeringValue))
        paint.drawArc(0, 0, 200, 200, -120, 120)
        paint.rotate(self.currentSteeringValue);
        paint.end()

    def UpdateSteering(self, value):
        self.currentSteeringValue = value
