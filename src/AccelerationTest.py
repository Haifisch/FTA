# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\designer\AccelerationTest.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.
import json
import os.path
from os import path
import datetime
import time
from AccelerationTestHistory import Ui_AccelerationTestHistory
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QBoxLayout, QApplication, QGridLayout, QLCDNumber, QScrollArea, QLabel, QTableWidget, QTableWidgetItem, QMessageBox, QShortcut
from enum import Enum

class TestState(Enum):
    WaitingForStart = 0
    StartingCountdown = 1
    PlayerAcceleration = 2
    FirstMark = 3
    SecondMark = 4
    ThirdMark = 5
    FinishedTest = 6

class Ui_AccelerationTest(QWidget):
    TestRunning = False
    TestStartTime = None
    TestEndTime = None
    TestTimer = None

    State = TestState.WaitingForStart

    ZeroToSixty_Time = 0
    ZeroToHundred_Time = 0
    ZeroToTwoHundred_Time = 0

    StartingCountdown_Time = None
    StartingCountdown_Time_Left = 0

    TestCar_Ordinal = 0
    TestCar_Class = 0
    TestCar_Performance_Index = 0

    def __init__(self):
        super().__init__()
        self.TestTimer = QtCore.QTime()
        self.setFixedSize(500, 320)
        self.setStyleSheet("background-color: black; color: white;")
        self.setupUi(self)
        self.UpdateTimer = QtCore.QTimer()
        self.UpdateTimer.timeout.connect(self.UpdateStateLabels)
        self.UpdateTimer.start(500)


    def UpdateStateLabels(self):
        if self.State == TestState.WaitingForStart:
            self.label.setText("STATE = WAITING FOR START")
        elif self.State == TestState.StartingCountdown:
            self.label.setText("STATE = GET READY... "+str(int(self.StartingCountdown_Time_Left)))
        elif self.State == TestState.PlayerAcceleration:
            self.label.setText("STATE = WAITING FOR PLAYER ACCEL")
        elif self.State == TestState.FirstMark:
            self.label.setText("STATE = WAITING FOR 0-60 MARK")
        elif self.State == TestState.SecondMark:
            self.label.setText("STATE = WAITING FOR 0-100 MARK")
        elif self.State == TestState.ThirdMark:
            self.label.setText("STATE = WAITING FOR 0-200 MARK")
        elif self.State == TestState.FinishedTest:
            self.label.setText("STATE = FINISHED TEST")
        if self.ZeroToSixty_Time > 0:
            self.ZeroToSixtyLabel.setText(datetime.datetime.fromtimestamp(self.ZeroToSixty_Time).strftime('%S.%f'))
        if self.ZeroToHundred_Time > 0:
            self.ZeroToOnehundredLabel.setText(datetime.datetime.fromtimestamp(self.ZeroToHundred_Time).strftime('%S.%f'))
        if self.ZeroToTwoHundred_Time > 0:
            self.ZeroToTwohundredLabel.setText(datetime.datetime.fromtimestamp(self.ZeroToTwoHundred_Time).strftime('%S.%f'))

    def StartTest(self):
        self.TestRunning = True
        self.TestTimer.start()
        self.State = TestState.StartingCountdown
        pass

    def ResetTest(self):
        self.TestStartTime = None
        self.TestRunning = False
        self.State = TestState.WaitingForStart
        pass

    def CarClassFromNumber(self, classNum):
        if classNum == 0:
            return 'D'
        elif classNum == 1:
            return 'C'
        elif classNum == 2:
            return 'B'
        elif classNum == 3:
            return 'A'
        elif classNum == 4:
            return 'S1'
        elif classNum == 5:
            return 'S2'
        elif classNum == 6:
            return 'X'

    def ViewTestsForCar(self):
        if self.TestCar_Class > 0 and self.TestCar_Ordinal > 0 and self.TestCar_Performance_Index > 0:
            DragTestFileName = str(int(self.TestCar_Ordinal))+'_'+str(int(self.TestCar_Class))+'_'+str(int(self.TestCar_Performance_Index))+'.json'
            if path.exists('./drag_tests/'+DragTestFileName) is True:
                f = open('./drag_tests/'+DragTestFileName)
                data = json.load(f)
                with open('./drag_tests/'+DragTestFileName, 'w') as f:
                    json.dump(data, f)
                self.accelerationTestHistory = Ui_AccelerationTestHistory(data)
                self.accelerationTestHistory.show()
        else:
            QMessageBox.question(self, 'Missing Information', "Keep this window open in the background and tab back into Forza, the test car's performance class and ID need collection. Drive around for 5 seconds and come back and hit the history button again.", QMessageBox.Ok)

    def SaveTest(self, carUniqueId, carClass, carPerformanceIndex):        
        saveData = {
            'time':str(int(time.time())), 
            'car_ordinal':str(int(carUniqueId)),
            'performance_class':self.CarClassFromNumber(carClass)+' '+str(int(carPerformanceIndex)),
            '0-to-60': str(round(self.ZeroToSixty_Time, 4)),
            '0-to-100': str(round(self.ZeroToHundred_Time, 4)),
            '0-to-200': str(round(self.ZeroToTwoHundred_Time, 4))
        }
        isExist = path.exists('./drag_tests/')
        if not isExist:
            os.makedirs('./drag_tests/')
        DragTestFileName = str(int(carUniqueId))+'_'+str(int(carClass))+'_'+str(int(carPerformanceIndex))+'.json'
        if path.exists('./drag_tests/'+DragTestFileName) is True:
            f = open('./drag_tests/'+DragTestFileName)
            data = json.load(f)
            data.append(saveData)
            with open('./drag_tests/'+DragTestFileName, 'w') as f:
                json.dump(data, f)
            self.accelerationTestHistory = Ui_AccelerationTestHistory(data)
            self.accelerationTestHistory.show()
        else:
            with open('./drag_tests/'+DragTestFileName, 'w') as f:
                json.dump([saveData], f)
            self.accelerationTestHistory = Ui_AccelerationTestHistory([saveData])
            self.accelerationTestHistory.show()

    def OnTelemetryData(self, data):
        if data['is_race_on'] == 1.0:
            # update data
            self.TestCar_Class = data['car_class'];
            self.TestCar_Ordinal = data['car_ordinal'];
            self.TestCar_Performance_Index = data['car_performance_index'];
            if self.TestRunning is True:
                if self.State == TestState.StartingCountdown:
                    if self.StartingCountdown_Time is None:
                        self.StartingCountdown_Time = time.time()
                    self.StartingCountdown_Time_Left = 3.0 - (time.time() - self.StartingCountdown_Time)
                    if self.StartingCountdown_Time_Left < 0.0:
                        self.State = TestState.PlayerAcceleration
                else:
                    currentSpeed = int(float(data['speed'] * 2.236936))
                    currentAccel = float((data['accel'] / 255) * 100)
                    if self.State == TestState.PlayerAcceleration:
                        if currentSpeed > 0 and currentAccel > 0:
                            self.TestStartTime = time.time()
                            self.State = TestState.FirstMark
                    if currentSpeed >= 200 and self.State == TestState.ThirdMark:
                        t1 = time.time()
                        self.ZeroToTwoHundred_Time = t1 - self.TestStartTime
                        self.TestEndTime = t1
                        self.TestRunning = False
                        self.State = TestState.FinishedTest
                        self.SaveTest(data['car_ordinal'], data['car_class'], data['car_performance_index'])
                        return
                    elif currentSpeed >= 100 and self.State == TestState.SecondMark:
                        self.ZeroToHundred_Time = time.time() - self.TestStartTime
                        self.State = TestState.ThirdMark
                    elif currentSpeed >= 60 and self.State == TestState.FirstMark:
                        self.ZeroToSixty_Time = time.time() - self.TestStartTime
                        self.State = TestState.SecondMark

    def setupUi(self, AccelerationTest):
        AccelerationTest.setObjectName("AccelerationTest")
        AccelerationTest.resize(500, 320)
        self.verticalLayoutWidget = QtWidgets.QWidget(AccelerationTest)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(-1, -1, 501, 321))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget = QtWidgets.QWidget(self.verticalLayoutWidget)
        self.widget.setMinimumSize(QtCore.QSize(0, 190))
        self.widget.setObjectName("widget")
        self.label = QtWidgets.QLabel(self.widget)
        self.label.setGeometry(QtCore.QRect(-4, 0, 511, 51))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.widget)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(0, 50, 501, 141))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.label_3 = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.label_4 = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_3.addWidget(self.label_4)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.ZeroToSixtyLabel = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Roboto")
        font.setPointSize(22)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)
        self.ZeroToSixtyLabel.setFont(font)
        self.ZeroToSixtyLabel.setTextFormat(QtCore.Qt.PlainText)
        self.ZeroToSixtyLabel.setScaledContents(False)
        self.ZeroToSixtyLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.ZeroToSixtyLabel.setObjectName("ZeroToSixtyLabel")
        self.horizontalLayout_2.addWidget(self.ZeroToSixtyLabel)
        self.ZeroToOnehundredLabel = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Roboto")
        font.setPointSize(22)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)
        self.ZeroToOnehundredLabel.setFont(font)
        self.ZeroToOnehundredLabel.setTextFormat(QtCore.Qt.PlainText)
        self.ZeroToOnehundredLabel.setScaledContents(False)
        self.ZeroToOnehundredLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.ZeroToOnehundredLabel.setObjectName("ZeroToOnehundredLabel")
        self.horizontalLayout_2.addWidget(self.ZeroToOnehundredLabel)
        self.ZeroToTwohundredLabel = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Roboto")
        font.setPointSize(22)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)
        self.ZeroToTwohundredLabel.setFont(font)
        self.ZeroToTwohundredLabel.setTextFormat(QtCore.Qt.PlainText)
        self.ZeroToTwohundredLabel.setScaledContents(False)
        self.ZeroToTwohundredLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.ZeroToTwohundredLabel.setObjectName("ZeroToTwohundredLabel")
        self.horizontalLayout_2.addWidget(self.ZeroToTwohundredLabel)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addWidget(self.widget)
        self.label_5 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.label_5.setWordWrap(True)
        #self.label_5.setFixedWidth(300)
        self.verticalLayout.addWidget(self.label_5)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.StartTestButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.StartTestButton.setMinimumSize(QtCore.QSize(100, 50))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.StartTestButton.setFont(font)
        self.StartTestButton.clicked.connect(self.StartTest)
        self.StartTestButton.setStyleSheet("QPushButton {background-color: green; color: white;}")
        self.StartTestButton.setFlat(False)
        self.StartTestButton.setObjectName("StartTestButton")
        self.horizontalLayout.addWidget(self.StartTestButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.TestResetButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.TestResetButton.clicked.connect(self.ResetTest)
        self.TestResetButton.setMinimumSize(QtCore.QSize(100, 50))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.TestResetButton.setFont(font)
        self.TestResetButton.setStyleSheet("QPushButton {background-color: red; color: black;}")
        self.TestResetButton.setObjectName("TestResetButton")
        self.horizontalLayout.addWidget(self.TestResetButton)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)

        self.ViewHistoricalTestsButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.ViewHistoricalTestsButton.clicked.connect(self.ViewTestsForCar)
        self.ViewHistoricalTestsButton.setMinimumSize(QtCore.QSize(100, 50))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.ViewHistoricalTestsButton.setFont(font)
        self.ViewHistoricalTestsButton.setStyleSheet("QPushButton {background-color: blue; color: white;}")
        self.ViewHistoricalTestsButton.setObjectName("ViewHistoricalTestsButton")
        self.horizontalLayout.addWidget(self.ViewHistoricalTestsButton)
        spacerItem3 = QtWidgets.QSpacerItem(40, 30, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(AccelerationTest)
        QtCore.QMetaObject.connectSlotsByName(AccelerationTest)

    def retranslateUi(self, AccelerationTest):
        _translate = QtCore.QCoreApplication.translate
        AccelerationTest.setWindowTitle(_translate("AccelerationTest", "Acceleration Test"))
        self.label.setText(_translate("AccelerationTest", "TEST STATE = WAITING FOR START"))
        self.label_2.setText(_translate("AccelerationTest", "0-60 mph"))
        self.label_3.setText(_translate("AccelerationTest", "0-100 mph"))
        self.label_4.setText(_translate("AccelerationTest", "0-200 mph"))
        self.ZeroToSixtyLabel.setText(_translate("AccelerationTest", "00.0"))
        self.ZeroToOnehundredLabel.setText(_translate("AccelerationTest", "00.0"))
        self.ZeroToTwohundredLabel.setText(_translate("AccelerationTest", "00.0"))
        self.label_5.setText(_translate("AccelerationTest", "Start from the car standing still then hit START to begin, jump back into forza, wait for the timer to countdown to 0, then hit the gas until all marks are hit."))
        self.StartTestButton.setText(_translate("AccelerationTest", "START"))
        self.TestResetButton.setText(_translate("AccelerationTest", "RESET"))
        self.ViewHistoricalTestsButton.setText("HISTORY")