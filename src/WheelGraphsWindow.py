from PyQt5 import QtGui, QtCore
from PyQt5 import QtWidgets
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QBoxLayout, QGridLayout, QLabel, QShortcut
from pyqtgraph import PlotWidget, plot
from numpy import *
import pyqtgraph as pg
from MiscConstants import MaxPointsOnGraph
from ColorHelper import RandomPenColor
from WheelsWidget import Ui_WheelsWidget
from SteeringWidget import SteeringWidget
from TimeAxisItem import TimeAxisItem

class WheelGraphsWindow(QWidget):
    recievedPacketCount = 0
    X_Data = linspace(0, 0, MaxPointsOnGraph)
    Timestamp_Data = linspace(0, 0, MaxPointsOnGraph)

    WheelSlip_FL = linspace(0, 0, MaxPointsOnGraph)
    WheelSlip_FR = linspace(0, 0, MaxPointsOnGraph)
    WheelSlip_RL = linspace(0, 0, MaxPointsOnGraph)
    WheelSlip_RR = linspace(0, 0, MaxPointsOnGraph)

    WheelTemperature_FL = linspace(0, 0, MaxPointsOnGraph)
    WheelTemperature_FR = linspace(0, 0, MaxPointsOnGraph)
    WheelTemperature_RL = linspace(0, 0, MaxPointsOnGraph)
    WheelTemperature_RR = linspace(0, 0, MaxPointsOnGraph)

    rgb = [0, 0, 0]

    lastData = None
    WheelGraphSessionTimer = None

    def __init__(self, SessionTimer, makeWindowKeyable=False):
        super().__init__()
        # graph reset shortcut
        self.ResetWheelGraphsShortcut = QShortcut(QKeySequence("Ctrl+Shift+C"), self)
        self.ResetWheelGraphsShortcut.activated.connect(self.ResetGraphs)

        self.WheelGraphSessionTimer = SessionTimer
        self.setWindowTitle("FTA Wheels")
        if makeWindowKeyable is not True:
            self.setStyleSheet("background-color: black; color: white;")
        else:
            self.setStyleSheet("background-color: #FF00FF; color: white;")
        self.wheelWidget = Ui_WheelsWidget()
        self.slipLayout = QHBoxLayout(self)
        # add graphs to layout
        self.vertSlipLayout = QVBoxLayout()
        self.vertSlipLayout.addWidget(self.wheelWidget)
        if makeWindowKeyable is not True:  
            # slip
            self.WheelSlipGraph = pg.PlotWidget(title="Combined Slip", axisItems={'bottom': TimeAxisItem(orientation='bottom')})
            self.WheelSlipGraph.enableAutoRange()
            self.WheelSlipGraph.showButtons()
            self.WheelSlipGraph.showGrid(x=True, y=True)
            self.WheelSlipGraph.addLegend()
            # init curves
            self.InitCurves()
        self.slipLayout.addLayout(self.vertSlipLayout)
        self.setLayout(self.slipLayout)
        if makeWindowKeyable is not True:
            self.slipLayout.addWidget(self.WheelSlipGraph)
            self.setFixedSize(1500, 600)
            # setup graph update timer
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.UpdatePlotCurves)
            self.timer.start(600)
        else:
            self.setFixedSize(300, 360)
        self.WheelWidgetTimer = QtCore.QTimer()
        self.WheelWidgetTimer.timeout.connect(self.UpdateWheelWidget)
        self.WheelWidgetTimer.start(200)

    def ResetGraphs(self):
        print("resetting graph data")
        self.X_Data = linspace(0, 0, MaxPointsOnGraph)
        self.Timestamp_Data = linspace(0, 0, MaxPointsOnGraph)
        self.WheelSlip_FL = linspace(0, 0, MaxPointsOnGraph)
        self.WheelSlip_FR = linspace(0, 0, MaxPointsOnGraph)
        self.WheelSlip_RL = linspace(0, 0, MaxPointsOnGraph)
        self.WheelSlip_RR = linspace(0, 0, MaxPointsOnGraph)

    def InitCurves(self):
        self.randomPenColor = RandomPenColor()
        # slip
        self.Curve_CombinedSlipFL = self.WheelSlipGraph.plot(self.Timestamp_Data, self.WheelSlip_FL, name="FL", pen=QtGui.QPen(self.randomPenColor.GetColor()))
        self.Curve_CombinedSlipFR = self.WheelSlipGraph.plot(self.Timestamp_Data, self.WheelSlip_FL, name="FR", pen=QtGui.QPen(self.randomPenColor.GetColor()))
        self.Curve_CombinedSlipRL = self.WheelSlipGraph.plot(self.Timestamp_Data, self.WheelSlip_FL, name="RL", pen=QtGui.QPen(self.randomPenColor.GetColor()))
        self.Curve_CombinedSlipRR = self.WheelSlipGraph.plot(self.Timestamp_Data, self.WheelSlip_FL, name="RR", pen=QtGui.QPen(self.randomPenColor.GetColor()))

    def Add_X(self, value):
        self.X_Data[:-1] = self.X_Data[1:]
        self.X_Data[-1] = int(value)

    def Add_WheelSlip(self, value, wheel):
        if wheel == "FL":
            self.WheelSlip_FL[:-1] = self.WheelSlip_FL[1:]
            self.WheelSlip_FL[-1] = float(value)
        elif wheel == "FR":
            self.WheelSlip_FR[:-1] = self.WheelSlip_FR[1:]
            self.WheelSlip_FR[-1] = float(value)
        elif wheel == "RL":
            self.WheelSlip_RL[:-1] = self.WheelSlip_RL[1:]
            self.WheelSlip_RL[-1] = float(value)
        elif wheel == "RR":
            self.WheelSlip_RR[:-1] = self.WheelSlip_RR[1:]
            self.WheelSlip_RR[-1] = float(value)

    def OnTelemetryData(self, data):
        if bool(int(data['is_race_on'])) == True:
            self.lastData = data
            self.Add_X(self.WheelGraphSessionTimer.elapsed())
            # update wheel slip
            self.Add_WheelSlip(data['tire_combined_slip_FL'], "FL")
            self.Add_WheelSlip(data['tire_combined_slip_FR'], "FR")
            self.Add_WheelSlip(data['tire_combined_slip_RL'], "RL")
            self.Add_WheelSlip(data['tire_combined_slip_RR'], "RR")           
            self.recievedPacketCount += 1

    def UpdatePlotCurves(self):
        # slip
        self.Curve_CombinedSlipFL.setData(self.X_Data, self.WheelSlip_FL)
        self.Curve_CombinedSlipFL.setPos(self.recievedPacketCount, 0)
        self.Curve_CombinedSlipFR.setData(self.X_Data, self.WheelSlip_FR)
        self.Curve_CombinedSlipFR.setPos(self.recievedPacketCount, 0)
        self.Curve_CombinedSlipRL.setData(self.X_Data, self.WheelSlip_RL)
        self.Curve_CombinedSlipRL.setPos(self.recievedPacketCount, 0)
        self.Curve_CombinedSlipRR.setData(self.X_Data, self.WheelSlip_RR)
        self.Curve_CombinedSlipRR.setPos(self.recievedPacketCount, 0)

    def UpdateWheelWidget(self):
        if self.lastData != None:
            self.wheelWidget.UpdateForData(self.lastData)