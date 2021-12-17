from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt
import sys, random

class PositionDrawingWidget(QWidget):
    playerPositionPoints = []

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 300, 190)
        self.setWindowTitle('Points')
        self.show()

    def AddPoint(self, newPos):
        print(newPos)
        self.playerPositionPoints.append([newPos[0], newPos[1]])
        self.update()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawPoints(qp)
        qp.end()

    def drawPoints(self, qp):
        qp.setPen(Qt.red)
        size = self.size()

        if size.height() <= 1 or size.height() <= 1:
            return
        if len(self.playerPositionPoints) > 0:
            for playerPoint in self.playerPositionPoints:
                qp.drawPoint(playerPoint[0], playerPoint[1])