# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'detection_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_TargetDet(object):
    def setupUi(self, TargetDet):
        TargetDet.setObjectName("TargetDet")
        TargetDet.resize(738, 228)
        self.layoutWidget = QtWidgets.QWidget(TargetDet)
        self.layoutWidget.setGeometry(QtCore.QRect(250, 180, 195, 30))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.okButton = QtWidgets.QPushButton(self.layoutWidget)
        self.okButton.setObjectName("okButton")
        self.horizontalLayout.addWidget(self.okButton)
        self.cancelButton = QtWidgets.QPushButton(self.layoutWidget)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.layoutWidget1 = QtWidgets.QWidget(TargetDet)
        self.layoutWidget1.setGeometry(QtCore.QRect(20, 30, 691, 131))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget1)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.pthButton = QtWidgets.QPushButton(self.layoutWidget1)
        self.pthButton.setObjectName("pthButton")
        self.gridLayout.addWidget(self.pthButton, 1, 2, 1, 1)
        self.lineEdit_inputpath = QtWidgets.QLineEdit(self.layoutWidget1)
        self.lineEdit_inputpath.setObjectName("lineEdit_inputpath")
        self.gridLayout.addWidget(self.lineEdit_inputpath, 0, 1, 1, 1)
        self.lineEdit_outputpath = QtWidgets.QLineEdit(self.layoutWidget1)
        self.lineEdit_outputpath.setObjectName("lineEdit_outputpath")
        self.gridLayout.addWidget(self.lineEdit_outputpath, 2, 1, 1, 1)
        self.output_Button = QtWidgets.QPushButton(self.layoutWidget1)
        self.output_Button.setObjectName("output_Button")
        self.gridLayout.addWidget(self.output_Button, 2, 2, 1, 1)
        self.label = QtWidgets.QLabel(self.layoutWidget1)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.input_Button = QtWidgets.QPushButton(self.layoutWidget1)
        self.input_Button.setObjectName("input_Button")
        self.gridLayout.addWidget(self.input_Button, 0, 2, 1, 1)
        self.lineEdit_pthpath = QtWidgets.QLineEdit(self.layoutWidget1)
        self.lineEdit_pthpath.setObjectName("lineEdit_pthpath")
        self.gridLayout.addWidget(self.lineEdit_pthpath, 1, 1, 1, 1)

        self.retranslateUi(TargetDet)
        QtCore.QMetaObject.connectSlotsByName(TargetDet)

    def retranslateUi(self, TargetDet):
        _translate = QtCore.QCoreApplication.translate
        TargetDet.setWindowTitle(_translate("TargetDet", "目标检测"))
        self.okButton.setText(_translate("TargetDet", "确定"))
        self.cancelButton.setText(_translate("TargetDet", "取消"))
        self.label_2.setText(_translate("TargetDet", "权重文件"))
        self.pthButton.setText(_translate("TargetDet", "浏览"))
        self.output_Button.setText(_translate("TargetDet", "浏览"))
        self.label.setText(_translate("TargetDet", "输入影像"))
        self.label_3.setText(_translate("TargetDet", "输出文件夹"))
        self.input_Button.setText(_translate("TargetDet", "浏览"))
