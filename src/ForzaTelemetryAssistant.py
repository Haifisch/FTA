import pyqtgraph as pg
import pyqtgraph.exporters
import os
import signal
import socket
import sys
import time
import datetime
from PyQt5 import QtGui, QtCore
from PyQt5 import QtWidgets
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QBoxLayout, QApplication, QGridLayout, QLCDNumber, QScrollArea, QLabel, QTableWidget, QTableWidgetItem, QMessageBox, QShortcut
from pyqtgraph import PlotWidget, plot
from numpy import *
from ForzaDataPacket import ForzaDataPacket
from ColorHelper import RandomPenColor
from MiscConstants import MaxPointsOnGraph

# ui defined elsewhere
from TimeAxisItem import TimeAxisItem
from WheelGraphsWindow import WheelGraphsWindow
from RaceWidget import Ui_RaceWidget
from VideoTools import Ui_VideoTools
from DriverInputWidget import Ui_DriverInputWidget
from AccelerationTest import Ui_AccelerationTest
from AutoshifterWidget import Ui_AutoshifterWidget
from SimpleReport import *

def sigint_handler(*args):
    """Handler for the SIGINT signal."""
    sys.stderr.write('\r')
    if QMessageBox.question(None, '', "Are you sure you want to quit?",
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No) == QMessageBox.Yes:
        QApplication.quit()

class DataCollectThread(QtCore.QThread):
    telemetry_packet = QtCore.pyqtSignal(object)

    _RunThread = False

    def __init__(self):
        QtCore.QThread.__init__(self)

    def run(self):
        self._RunThread = True
        # Listen for incoming datagrams
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(('10.16.0.13', 4141))
        while self._RunThread:
            # datastream to object
            message, address = server_socket.recvfrom(512)
            frame = ForzaDataPacket(message, "fh4")
            frame_dict = frame.to_dict()
            self.telemetry_packet.emit(frame_dict)

    def stop(self):
        if self._RunThread:
            self._RunThread = False

class MainWindow(QtWidgets.QMainWindow):
    global MaxPointsOnGraph

    zeroFrameTimer = 0
    recievedPacketCount = 0

    # stuff we dont really track on a curve
    Max_RPM = 0
    Max_RPM_Data = linspace(0, 0, MaxPointsOnGraph)

    # stuff we track on a curve
    X_Data = linspace(0, 0, MaxPointsOnGraph)
    Timestamp_Data = linspace(0, 0, MaxPointsOnGraph)
    RPM_Data = linspace(0, 0, MaxPointsOnGraph)
    Torque_Data = linspace(0, 0, MaxPointsOnGraph)
    Power_Data = linspace(0, 0, MaxPointsOnGraph)
    Boost_Data = linspace(0, 0, MaxPointsOnGraph)
    Gear_Data = linspace(0, 0, MaxPointsOnGraph)
    Speed_Data = linspace(0, 0, MaxPointsOnGraph)
    Accel_Data = linspace(0, 0, MaxPointsOnGraph)
    Brake_Data = linspace(0, 0, MaxPointsOnGraph)

    EngineRPMGraph = None
    EngineTorqueGraph = None

    Starting_Timestamp = 0

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Forza Telemetry Assistant")
        self.setStyleSheet("background-color: black; color: white;")
        self.randomPenColor = RandomPenColor()
        self.simpleReportBuilder = None
        # session timer
        self.SessionTimer = QtCore.QTime()
        self.SessionTimer.start()
        # graph reset shortcut
        self.ResetGraphsShortcut = QShortcut(QKeySequence("Ctrl+Shift+C"), self)
        self.ResetGraphsShortcut.activated.connect(self.ResetGraphs)
        # init driver input widget
        self.driverInputWidget = Ui_DriverInputWidget()
        # rpm
        self.EngineRPMGraph = pg.PlotWidget(title="RPM", axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.EngineRPMGraph.enableAutoRange()
        self.EngineRPMGraph.showButtons()
        self.EngineRPMGraph.resize(900, 400)
        self.EngineRPMGraph.showGrid(x=True, y=True)
        self.EngineRPMGraph.addLegend()
        # torque
        self.EngineTorqueGraph = pg.PlotWidget(title="Torque", axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.EngineTorqueGraph.enableAutoRange()
        self.EngineTorqueGraph.showButtons()
        self.EngineTorqueGraph.addLegend()
        self.EngineTorqueGraph.showGrid(x=True, y=True)
        # gear
        self.EngineGearGraph = pg.PlotWidget(title="Gear", axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.EngineGearGraph.enableAutoRange()
        self.EngineGearGraph.showButtons()
        self.EngineGearGraph.addLegend()
        self.EngineGearGraph.showGrid(x=True, y=True)
        # speed
        self.SpeedGraph = pg.PlotWidget(title="Speed", axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.SpeedGraph.enableAutoRange()
        self.SpeedGraph.showButtons()
        self.SpeedGraph.addLegend()
        self.SpeedGraph.showGrid(x=True, y=True)
        # top graph layout
        self.hlayout = QHBoxLayout()
        self.hlayout.addWidget(self.EngineRPMGraph)
        self.hlayout.addWidget(self.EngineTorqueGraph)
        # mid graph layout
        self.hlayout2 = QHBoxLayout()
        self.hlayout2.addWidget(self.EngineGearGraph)
        self.hlayout2.addWidget(self.SpeedGraph)
        # bot graph layout
        self.hlayout3 = QHBoxLayout()
        self.hlayout3.addWidget(self.driverInputWidget)
        # quick export graphs button
        self.exportButton = QPushButton('Export Plots', self)
        self.exportButton.clicked.connect(self.ExportButton_OnClick)
        # show race info button
        self.raceInfoButton = QPushButton("Race Info")
        self.raceInfoButton.clicked.connect(self.ShowRaceInfoWindow)
        # show suspension info button
        self.suspensionInfoButton = QPushButton("Wheels & Suspension")
        self.suspensionInfoButton.clicked.connect(self.ShowSuspensionInfoWindow)
        self.suspensionInfoButton.setStyleSheet("QPushButton {background-color: blue; color: white;}")
        # show video utils button
        self.videoToolsButton = QPushButton("Video Utilities")
        self.videoToolsButton.clicked.connect(self.ShowKeyableWheelsWindow)
        self.videoToolsButton.setStyleSheet("QPushButton {background-color: grey; color: white;}")
        # drag test
        self.accelerationTestButton = QPushButton("Drag Tester")
        self.accelerationTestButton.clicked.connect(self.ShowAccelerationTestWindow)
        self.accelerationTestButton.setStyleSheet("QPushButton {background-color: purple; color: white;}")
        # drag test
        self.autoshifterButton = QPushButton("Autoshifter")
        self.autoshifterButton.clicked.connect(self.ShowAutoshifterWindow)
        self.autoshifterButton.setStyleSheet("QPushButton {background-color: magenta; color: white;}")

        # button group
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.exportButton)
        self.buttonLayout.addWidget(self.raceInfoButton)
        self.buttonLayout.addWidget(self.suspensionInfoButton)
        self.buttonLayout.addWidget(self.videoToolsButton)
        self.buttonLayout.addWidget(self.accelerationTestButton)
        self.buttonLayout.addWidget(self.autoshifterButton)
        # collection layout
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.hlayout3)
        self.mainLayout.addLayout(self.hlayout)
        self.mainLayout.addLayout(self.hlayout2)
        self.mainLayout.addLayout(self.buttonLayout)
        # primary widget
        self.mainWidget = QWidget()
        self.mainWidget.setFixedSize(1800, 900)
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)
        # plot initial data
        self.RPMCurve = self.EngineRPMGraph.plot(self.Timestamp_Data, self.RPM_Data, name="RPM", pen=QtGui.QPen(self.randomPenColor.GetColor()))
        self.RedLineRPMCurve = self.EngineRPMGraph.plot(self.Timestamp_Data, self.RPM_Data, name="Max RPM", pen=QtGui.QPen(self.randomPenColor.GetColor()))
        self.TorqueCurve = self.EngineTorqueGraph.plot(self.Timestamp_Data, self.Torque_Data, name="Torque", pen=QtGui.QPen(self.randomPenColor.GetColor()))
        self.PowerCurve = self.EngineRPMGraph.plot(self.Timestamp_Data, self.Power_Data, name="Power", pen=QtGui.QPen(self.randomPenColor.GetColor()))
        self.GearCurve = self.EngineGearGraph.plot(self.Timestamp_Data, self.Gear_Data, name="Gear", pen=QtGui.QPen(self.randomPenColor.GetColor()))
        self.SpeedCurve = self.SpeedGraph.plot(self.Timestamp_Data, self.Speed_Data, name="Speed", pen=QtGui.QPen(self.randomPenColor.GetColor()))
        # graph update timer, updating this in time with the amount of packets recieved from fh5 just like obliterates qt and crashes w/o error
        # i dont really care much about it being 1:1 in updating with packets recieved so a short wait time is sufficient to avoid crashing
        self.UpdateGraphTimer = QtCore.QTimer()
        self.UpdateGraphTimer.timeout.connect(self.UpdatePlotCurves)
        self.UpdateGraphTimer.start(500)
        # start telemetry listener
        self.telemetryCollector = DataCollectThread()
        self.telemetryCollector.telemetry_packet.connect(self.OnTelemetryData)
        self.telemetryCollector.telemetry_packet.connect(self.driverInputWidget.OnTelemetryData)
        self.telemetryCollector.start()

    def UpdatePlotCurves(self):
        self.RedLineRPMCurve.setData(self.X_Data, self.Max_RPM_Data)
        self.RedLineRPMCurve.setPos(self.recievedPacketCount, 0)
        self.RPMCurve.setData(self.X_Data, self.RPM_Data)
        self.RPMCurve.setPos(self.recievedPacketCount, 0)
        self.TorqueCurve.setData(self.X_Data, self.Torque_Data)
        self.TorqueCurve.setPos(self.recievedPacketCount, 0)
        self.PowerCurve.setData(self.X_Data, self.Power_Data)
        self.PowerCurve.setPos(self.recievedPacketCount, 0)
        self.GearCurve.setData(self.X_Data, self.Gear_Data)
        self.GearCurve.setPos(self.recievedPacketCount, 0)
        self.SpeedCurve.setData(self.X_Data, self.Speed_Data)
        self.SpeedCurve.setPos(self.recievedPacketCount, 0) 

    def ResetGraphs(self):
        print("resetting graph data")
        self.SessionTimer.restart()
        self.Starting_Timestamp = 0
        self.X_Data = linspace(0, 0, MaxPointsOnGraph)
        self.Timestamp_Data = linspace(0, 0, MaxPointsOnGraph)
        self.RPM_Data = linspace(0, 0, MaxPointsOnGraph)
        self.Torque_Data = linspace(0, 0, MaxPointsOnGraph)
        self.Power_Data = linspace(0, 0, MaxPointsOnGraph)
        self.Boost_Data = linspace(0, 0, MaxPointsOnGraph)
        self.Gear_Data = linspace(0, 0, MaxPointsOnGraph)
        self.Speed_Data = linspace(0, 0, MaxPointsOnGraph)
        self.Accel_Data = linspace(0, 0, MaxPointsOnGraph)
        self.Brake_Data = linspace(0, 0, MaxPointsOnGraph)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to close the window?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
            if self.telemetryCollector != None:
                self.telemetryCollector.stop()
            exit()
        else:
            event.ignore()

    def ShowAutoshifterWindow(self):
        self.autoshifterWidget = Ui_AutoshifterWidget()
        self.telemetryCollector.telemetry_packet.connect(self.autoshifterWidget.OnTelemetryData)
        self.autoshifterWidget.show()

    def ShowRaceInfoWindow(self):
        self.raceInfo = Ui_RaceWidget()
        self.telemetryCollector.telemetry_packet.connect(self.raceInfo.OnTelemetryData)
        self.raceInfo.show()

    def ShowSuspensionInfoWindow(self):
        self.wheelGraphsWindow = WheelGraphsWindow(self.SessionTimer)
        self.telemetryCollector.telemetry_packet.connect(self.wheelGraphsWindow.OnTelemetryData)
        self.wheelGraphsWindow.show()

    def ShowReportWinow(self):
        self.simpleReportBuilder = SimpleReportBuilder()

    def ShowKeyableWheelsWindow(self):
        self.wheelGraphsWindow = WheelGraphsWindow(makeWindowKeyable=True)
        self.telemetryCollector.telemetry_packet.connect(self.wheelGraphsWindow.OnTelemetryData)
        self.wheelGraphsWindow.show()

    def ShowVideoToolsWindow(self):
        self.videoToolsWindow = Ui_VideoTools(self.telemetryCollector)
        self.videoToolsWindow.show()

    def ShowAccelerationTestWindow(self):
        self.accelerationTestWindow = Ui_AccelerationTest()
        self.telemetryCollector.telemetry_packet.connect(self.accelerationTestWindow.OnTelemetryData)
        self.accelerationTestWindow.show()

    def Add_RPM(self, value):
        self.RPM_Data[:-1] = self.RPM_Data[1:]
        self.RPM_Data[-1] = float(value)        

    def Add_Torque(self, value):
        self.Torque_Data[:-1] = self.Torque_Data[1:]
        self.Torque_Data[-1] = float(value)

    def Add_Power(self, value):
        self.Power_Data[:-1] = self.Power_Data[1:]
        self.Power_Data[-1] = float(value) 

    def Add_Gear(self, value):
        self.Gear_Data[:-1] = self.Gear_Data[1:]
        self.Gear_Data[-1] = float(value)

    def Add_Speed(self, value):
        self.Speed_Data[:-1] = self.Speed_Data[1:]
        self.Speed_Data[-1] = float(value)

    def Add_X_Old(self, value):
        diff = 0
        if self.Starting_Timestamp == 0:
            self.Starting_Timestamp = datetime.now()
        else:
            Current_Timestamp = datetime.now()
            diff = (Current_Timestamp - self.Starting_Timestamp).total_seconds()
        self.X_Data[:-1] = self.X_Data[1:]
        self.X_Data[-1] = int(diff)

    def Add_X(self, value):
        self.X_Data[:-1] = self.X_Data[1:]
        self.X_Data[-1] = int(value)

    def OnTelemetryData(self, data):
        if data['is_race_on'] == 1.0:
            # update data
            if data['engine_max_rpm'] > 0 or self.Max_RPM != int(data['engine_max_rpm']):
                self.Max_RPM = int(data['engine_max_rpm'])
            if self.simpleReportBuilder is not None:
                self.simpleReportBuilder.Analyze(data)
            self.Timestamp_Data[:-1] = self.Timestamp_Data[1:]
            self.Timestamp_Data[-1] = int(data['timestamp_ms'])
            self.Add_X(self.SessionTimer.elapsed())
            self.Max_RPM_Data = full(MaxPointsOnGraph, self.Max_RPM)
            self.Add_RPM(int(data['current_engine_rpm']))
            self.Add_Torque(int(data['torque'] * 0.73756))
            self.Add_Power(int(data['power'] / 745.699872))
            self.Add_Gear(data['gear'])
            self.Add_Speed(int(float(data['speed'] * 2.236936)))
            self.recievedPacketCount += 1
            if self.simpleReportBuilder is not None:
                if int(float(data['timestamp_ms'] / 1000.0)) % 10 == 0:
                    self.simpleReportBuilder.ProcessToWindow()
        #print(data)

    def SavePlot(self, targetPlot, endSuffix):
        isExist = os.path.exists('exports/')
        if not isExist:
            os.makedirs('exports/')
        # eh the svg export isnt too bad but the stroke width that the result has is very smol
        # png is very bleh but the lines are usually consistent.
        # this entirely makes me not want to use plotgraph so if anyone has a better plotting solution hmu
        exporter = pg.exporters.ImageExporter(targetPlot.scene())
        #exporter = pg.exporters.SVGExporter(targetPlot.scene())
        exporter.parameters()['width'] = 1200
        exporter.parameters()['height'] = 600
        #exporter.parameters()['scaling stroke'] = True
        exporter.export('exports/'+str(int(time.time()))+'_'+endSuffix+'.png')

    @QtCore.pyqtSlot()
    def ExportButton_OnClick(self):
        self.SavePlot(self.EngineRPMGraph, "rpm_and_power")
        self.SavePlot(self.EngineTorqueGraph, "torque")
        self.SavePlot(self.EngineGearGraph, "gear")
        self.SavePlot(self.SpeedGraph, "speed")
        self.SavePlot(self.AccelBrakeGraph, "accel_brake_boost")

try:
    import OpenGL
    pg.setConfigOption('useOpenGL', True)
    pg.setConfigOption('enableExperimental', True)
    pg.setConfigOption('useCupy', True)
    pg.setConfigOption('antialias', True)
except Exception as e:
    print(f"Enabling OpenGL failed with {e}. Will result in slow rendering. Try installing PyOpenGL.")

if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint_handler)
    
    QtWidgets.QApplication.setAttribute(QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet("QMessageBox QPushButton {background-color: grey; color: white;}")
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())