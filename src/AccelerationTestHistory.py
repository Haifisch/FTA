# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\designer\AccelerationTestHistory.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QBoxLayout, QApplication, QGridLayout, QLCDNumber, QScrollArea, QLabel, QTableWidget, QTableWidgetItem, QMessageBox, QShortcut


class Ui_AccelerationTestHistory(QWidget):

    def MakeNewItem(self, row, col, itemData):
        newItem = QTableWidgetItem(itemData)
        newItem.setTextAlignment(Qt.AlignCenter)
        self.tableView.setItem(row, col, newItem)

    def __init__(self, tableData):
        super().__init__()
        self.setFixedSize(800, 300)
        self.setStyleSheet("background-color: black; color: white;")
        self.setObjectName("AccelerationTestHistory")
        self.verticalLayoutWidget = QtWidgets.QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 700, 400))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        header_labels = ['Time', 'Car ID', 'Class', '0-60', '0-100', '0-200']  
        self.tableView = QtWidgets.QTableWidget(len(tableData), len(header_labels))
        self.tableView.setHorizontalHeaderLabels(header_labels)
        self.tableView.setObjectName("tableView")
        self.tableView.setStyleSheet('QHeaderView::section { background-color: black; color: white; } QTableWidget QTableCornerButton::section {background-color: rgba(0,0,0,0); }')
        self.verticalLayout.addWidget(self.tableView)
        self.widget = QtWidgets.QWidget(self.verticalLayoutWidget)
        self.widget.setMinimumSize(QtCore.QSize(0, 60))
        self.widget.setObjectName("widget")
        self.verticalLayout.addWidget(self.widget)
        self.setWindowTitle("Acceleration Test History")
        QtCore.QMetaObject.connectSlotsByName(self)
        self.tableView.setColumnWidth(0, 100)
        self.tableView.setColumnWidth(1, 80)
        self.tableView.setColumnWidth(2, 80)
        self.tableView.setColumnWidth(3, 80)
        self.tableView.setColumnWidth(4, 80)
        self.tableView.setColumnWidth(5, 80)
        self.tableView.setRowCount(len(tableData))
        row = 0
        for testData in tableData:
            print(testData)
            self.MakeNewItem(row, 0, testData['time'])
            self.MakeNewItem(row, 1, testData['car_ordinal'])
            self.MakeNewItem(row, 2, testData['performance_class'])
            self.MakeNewItem(row, 3, testData['0-to-60'])
            self.MakeNewItem(row, 4, testData['0-to-100'])
            self.MakeNewItem(row, 5, testData['0-to-200'])
            row = row+1   
        