from PyQt5 import QtGui, QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from MiscConstants import MaxPointsOnGraph
from enum import Enum
import time
# at the moment only detects rpm redlining 

class SimpleReportWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Telemetry Report'
        self.left = 0
        self.top = 0
        self.width = 600
        self.height = 300
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.createTable()
        # Add box layout, add table to box layout and add box layout to widget
        self.reportLayout = QVBoxLayout()
        self.reportLayout.addWidget(self.tableWidget) 
        self.setLayout(self.reportLayout)

    def createTable(self):
       # Create table
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(1)
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setItem(0,0, QTableWidgetItem("No issues yet :)"))
        self.tableWidget.move(0,0)
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)

    def UpdateReport(self, reportArray):
        if len(reportArray) <= 0:
            return
        self.tableWidget.setRowCount(len(reportArray))
        itemCount = 0
        for reportItem in reportArray:
            self.tableWidget.setItem(0,itemCount, QTableWidgetItem(reportItem))
            itemCount += 1

class SteeringAngle(Enum):
    NEUTRAL = 0
    HARD_LEFT = 1
    HARD_RIGHT = 2

class ReportObject:
    def __init__(self, reportType, reportReadableDescription):
        super().__init__()
        self.ReportType = reportType
        self.HumanDescription = reportReadableDescription

class SimpleReportBuilder:
    reportTableLines = 0
    steeringAngle = SteeringAngle.NEUTRAL

    reportList = []
    lastReportObject = None

    lastReportTime = time.time()
    reportDelay = 10

    def __init__(self):
        super().__init__()
        self.simpleReportWindow = SimpleReportWindow()
        self.redlines = []
        self.suspensionIssues = []

    def Analyze(self, data):
        ReadyToTakeReport = False
        timeNow = time.time()
        reportTimeDifference = int(timeNow - self.lastReportTime)
        if reportTimeDifference > self.reportDelay:
            ReadyToTakeReport = True
        if ReadyToTakeReport:
            if int(data['current_engine_rpm']) >= int(data['engine_max_rpm']):
                self.AddDetectedRedline(self.recievedPacketCount, data['current_engine_rpm'], data['engine_max_rpm'], int(float(data['speed'] * 2.236936)), data['gear'])
            if data['steer'] > 0.0:
                self.steeringAngle = SteeringAngle.HARD_RIGHT
            elif data['steer'] < 0.0:
                self.steeringAngle = SteeringAngle.HARD_LEFT
            elif data['steer'] == 0.0:
                self.steeringAngle = SteeringAngle.NEUTRAL
            self.DetectWheelSlipInTurn(data)

    def DetectWheelSlipInTurn(self, data):
        # current_engine_rpm
        isWheelInPuddle, WheelsInPuddle = self.CheckForWheelInPuddle(data)
        isTurning = (self.steeringAngle != SteeringAngle.NEUTRAL)
        if isTurning == False:
            return
        SlippingWheels = self.FindWheelsWithLowestGrip(data)
        #print(SlippingWheels)
        # wheel slip in puddle?
        if isTurning and isWheelInPuddle:
            for SlippingWheel in SlippingWheels:
                for WheelInPuddle in WheelsInPuddle:
                    if WheelInPuddle == SlippingWheel:
                        #print("!!! slipping in puddle !!!\n"+SlippingWheel)
                        break
        # wheel slip on dry road?
        if isTurning and isWheelInPuddle == False:
            for SlippingWheel in SlippingWheels:
                #print("!!! slipping on dry medium !!!\n"+SlippingWheel)
                pass

    def CheckForWheelInPuddle(self, data):
        WheelInPuddle = False
        WheelLocations = []
        if data['wheel_in_puddle_FL'] > 0.0:
            WheelInPuddle = True
            WheelLocations.append('wheel_in_puddle_FL')
        elif data['wheel_in_puddle_FR'] > 0.0:
            WheelInPuddle = True
            WheelLocations.append('wheel_in_puddle_FR')
        elif data['wheel_in_puddle_RL'] > 0.0:
            WheelInPuddle = True
            WheelLocations.append('wheel_in_puddle_RL')
        elif data['wheel_in_puddle_RR'] > 0.0:
            WheelInPuddle = True
            WheelLocations.append('wheel_in_puddle_RR')
        return WheelInPuddle, WheelLocations

    def FindWheelsWithLowestGrip(self, data):
        # tire_slip_ratio_FL
        wheels = []
        if data['tire_slip_ratio_FL'] > 1.0:
            wheels.append('tire_slip_ratio_FL')
        elif data['tire_slip_ratio_FR'] > 1.0:
            wheels.append('tire_slip_ratio_FR')
        elif data['tire_slip_ratio_RL'] > 1.0:
            wheels.append('tire_slip_ratio_RL')
        elif data['tire_slip_ratio_RR'] > 1.0:
            wheels.append('tire_slip_ratio_RR')
        return wheels

    def AddDetectedRedline(self, xTime, rpm, rpmMax, speed, gear):
        #print("!!! RPM RED LINE !!!")
        if len(self.redlines) > 0:
            if ((xTime - self.redlines[-1]['time']) > 500):
                self.redlines.append({"time":xTime, "rpm":rpm, "max":rpmMax, "speed":speed, "gear":gear})
        else:
            self.redlines.append({"time":xTime, "rpm":rpm, "max":rpmMax, "speed":speed, "gear":gear})

    def RedLines(self):
        return self.redlines

    def ProcessToWindow(self):
        tempReport = []
        for redline in self.redlines:
            tempReport.append("RPM Red Line X = "+str(int(redline['time']))+" RPM was "+str(int(redline['rpm']))+" max was "+str(int(redline['max']))+ " gear set @ "+str(redline['gear'])+" speed "+str(redline['speed']))
        self.simpleReportWindow.UpdateReport(tempReport)