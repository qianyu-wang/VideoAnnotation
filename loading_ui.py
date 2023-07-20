# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'loading.ui'
##
## Created by: Qt User Interface Compiler version 6.5.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QProgressBar, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_LoadingDialog(object):
    def setupUi(self, LoadingDialog):
        if not LoadingDialog.objectName():
            LoadingDialog.setObjectName(u"LoadingDialog")
        LoadingDialog.resize(400, 300)
        self.verticalLayout = QVBoxLayout(LoadingDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.progressBar = QProgressBar(LoadingDialog)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)

        self.verticalLayout.addWidget(self.progressBar)


        self.retranslateUi(LoadingDialog)

        QMetaObject.connectSlotsByName(LoadingDialog)
    # setupUi

    def retranslateUi(self, LoadingDialog):
        LoadingDialog.setWindowTitle(QCoreApplication.translate("LoadingDialog", u"Loading Dialog", None))
    # retranslateUi

