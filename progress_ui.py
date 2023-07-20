# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'progress.ui'
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
    QWidget)

class Ui_ProgressDialog(object):
    def setupUi(self, ProgressDialog):
        if not ProgressDialog.objectName():
            ProgressDialog.setObjectName(u"ProgressDialog")
        ProgressDialog.setMinimumSize(QSize(300, 100))
        ProgressDialog.setMaximumSize(QSize(300, 100))
        self.progress_bar = QProgressBar(ProgressDialog)
        self.progress_bar.setObjectName(u"progress_bar")
        self.progress_bar.setGeometry(QRect(10, 10, 280, 23))
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)

        self.retranslateUi(ProgressDialog)

        QMetaObject.connectSlotsByName(ProgressDialog)
    # setupUi

    def retranslateUi(self, ProgressDialog):
        ProgressDialog.setWindowTitle(QCoreApplication.translate("ProgressDialog", u"Progress", None))
    # retranslateUi

