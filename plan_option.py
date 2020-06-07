# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plan_option.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(201, 151)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout_2.setSpacing(5)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.extra = QtWidgets.QCheckBox(self.frame)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.extra.setFont(font)
        self.extra.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.extra.setChecked(False)
        self.extra.setObjectName("extra")
        self.verticalLayout_2.addWidget(self.extra)
        self.more_exp = QtWidgets.QCheckBox(self.frame)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.more_exp.setFont(font)
        self.more_exp.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.more_exp.setObjectName("more_exp")
        self.verticalLayout_2.addWidget(self.more_exp)
        self.more_gold = QtWidgets.QCheckBox(self.frame)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.more_gold.setFont(font)
        self.more_gold.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.more_gold.setObjectName("more_gold")
        self.verticalLayout_2.addWidget(self.more_gold)
        self.verticalLayout.addWidget(self.frame)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "规划"))
        self.extra.setText(_translate("Dialog", "考虑合成副产物"))
        self.more_exp.setText(_translate("Dialog", "大量需求经验"))
        self.more_gold.setText(_translate("Dialog", "大量需求龙门币"))
