# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\designer\VideoTools.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QBoxLayout, QGridLayout, QLabel, QApplication, QGraphicsDropShadowEffect
from WheelGraphsWindow import WheelGraphsWindow

class Ui_VideoTools(QWidget):

    def __init__(self, _telemetryCollector):
        super().__init__()
        self.telemetryCollectorInstance = _telemetryCollector
        self.setFixedSize(250, 300)
        self.setupUi(self)

    def setupUi(self, VideoTools):
        VideoTools.setObjectName("VideoTools")
        self.gridLayoutWidget = QtWidgets.QWidget(VideoTools)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(-1, -1, 251, 301))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.KeyableWheelWindowButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.KeyableWheelWindowButton.setFlat(False)
        self.KeyableWheelWindowButton.setObjectName("KeyableWheelWindowButton")
        self.KeyableWheelWindowButton.clicked.connect(self.ShowKeyableWheelWindow)
        self.gridLayout.addWidget(self.KeyableWheelWindowButton, 0, 0, 1, 1)

        self.retranslateUi(VideoTools)
        QtCore.QMetaObject.connectSlotsByName(VideoTools)

    def retranslateUi(self, VideoTools):
        _translate = QtCore.QCoreApplication.translate
        VideoTools.setWindowTitle(_translate("VideoTools", "Video Utilities"))
        self.KeyableWheelWindowButton.setText(_translate("VideoTools", "Show Keyable Wheel Window"))

    def ShowKeyableWheelWindow(self):
        self.wheelGraphsWindow = WheelGraphsWindow(makeWindowKeyable=True)
        self.telemetryCollectorInstance.telemetry_packet.connect(self.wheelGraphsWindow.OnTelemetryData)
        self.wheelGraphsWindow.show()
