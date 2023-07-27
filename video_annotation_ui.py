# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'video_annotation.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QSpacerItem, QStatusBar,
    QVBoxLayout, QWidget)

from anno_label import AnnoLabel

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.text_file = QLineEdit(self.centralwidget)
        self.text_file.setObjectName(u"text_file")

        self.horizontalLayout_2.addWidget(self.text_file)

        self.button_select_file = QPushButton(self.centralwidget)
        self.button_select_file.setObjectName(u"button_select_file")

        self.horizontalLayout_2.addWidget(self.button_select_file)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_5)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.combo_type = QComboBox(self.centralwidget)
        self.combo_type.addItem("")
        self.combo_type.addItem("")
        self.combo_type.addItem("")
        self.combo_type.addItem("")
        self.combo_type.setObjectName(u"combo_type")

        self.horizontalLayout.addWidget(self.combo_type)

        self.label_4 = QLabel(self.centralwidget)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout.addWidget(self.label_4)

        self.label_color = QLabel(self.centralwidget)
        self.label_color.setObjectName(u"label_color")
        self.label_color.setMinimumSize(QSize(20, 20))
        self.label_color.setStyleSheet(u"background:white")
        self.label_color.setFrameShape(QFrame.Box)

        self.horizontalLayout.addWidget(self.label_color)

        self.button_change_color = QPushButton(self.centralwidget)
        self.button_change_color.setObjectName(u"button_change_color")

        self.horizontalLayout.addWidget(self.button_change_color)

        self.button_copy_to_all = QPushButton(self.centralwidget)
        self.button_copy_to_all.setObjectName(u"button_copy_to_all")

        self.horizontalLayout.addWidget(self.button_copy_to_all)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_4)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_6)

        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_5.addWidget(self.label_3)

        self.combo_anno_provider = QComboBox(self.centralwidget)
        self.combo_anno_provider.setObjectName(u"combo_anno_provider")

        self.horizontalLayout_5.addWidget(self.combo_anno_provider)

        self.button_run_provider = QPushButton(self.centralwidget)
        self.button_run_provider.setObjectName(u"button_run_provider")

        self.horizontalLayout_5.addWidget(self.button_run_provider)

        self.button_run_provider_all = QPushButton(self.centralwidget)
        self.button_run_provider_all.setObjectName(u"button_run_provider_all")

        self.horizontalLayout_5.addWidget(self.button_run_provider_all)

        self.button_reload_provider = QPushButton(self.centralwidget)
        self.button_reload_provider.setObjectName(u"button_reload_provider")

        self.horizontalLayout_5.addWidget(self.button_reload_provider)

        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_7)


        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_2)

        self.button_undo = QPushButton(self.centralwidget)
        self.button_undo.setObjectName(u"button_undo")

        self.horizontalLayout_4.addWidget(self.button_undo)

        self.button_previous = QPushButton(self.centralwidget)
        self.button_previous.setObjectName(u"button_previous")

        self.horizontalLayout_4.addWidget(self.button_previous)

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_4.addWidget(self.label_2)

        self.text_current = QLineEdit(self.centralwidget)
        self.text_current.setObjectName(u"text_current")

        self.horizontalLayout_4.addWidget(self.text_current)

        self.label_total = QLabel(self.centralwidget)
        self.label_total.setObjectName(u"label_total")

        self.horizontalLayout_4.addWidget(self.label_total)

        self.button_next = QPushButton(self.centralwidget)
        self.button_next.setObjectName(u"button_next")

        self.horizontalLayout_4.addWidget(self.button_next)

        self.button_redo = QPushButton(self.centralwidget)
        self.button_redo.setObjectName(u"button_redo")

        self.horizontalLayout_4.addWidget(self.button_redo)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.horizontalLayout_4.setStretch(0, 1)
        self.horizontalLayout_4.setStretch(8, 1)

        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.button_export = QPushButton(self.centralwidget)
        self.button_export.setObjectName(u"button_export")

        self.horizontalLayout_3.addWidget(self.button_export)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.label_anno = AnnoLabel(self.centralwidget)
        self.label_anno.setObjectName(u"label_anno")
        self.label_anno.setEnabled(False)
        self.label_anno.setMouseTracking(True)
        self.label_anno.setTabletTracking(True)
        self.label_anno.setFocusPolicy(Qt.ClickFocus)
        self.label_anno.setContextMenuPolicy(Qt.NoContextMenu)
        self.label_anno.setStyleSheet(u"background:white")
        self.label_anno.setScaledContents(True)
        self.label_anno.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label_anno)

        self.verticalLayout.setStretch(5, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Video Annotation", None))
        self.button_select_file.setText(QCoreApplication.translate("MainWindow", u"select video", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"annotation type", None))
        self.combo_type.setItemText(0, QCoreApplication.translate("MainWindow", u"rectangle", None))
        self.combo_type.setItemText(1, QCoreApplication.translate("MainWindow", u"text", None))
        self.combo_type.setItemText(2, QCoreApplication.translate("MainWindow", u"circle", None))
        self.combo_type.setItemText(3, QCoreApplication.translate("MainWindow", u"point", None))

        self.label_4.setText(QCoreApplication.translate("MainWindow", u"color", None))
        self.label_color.setText("")
        self.button_change_color.setText(QCoreApplication.translate("MainWindow", u"change color", None))
        self.button_copy_to_all.setText(QCoreApplication.translate("MainWindow", u"copy last annotation to all frames", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"annotation provider", None))
        self.button_run_provider.setText(QCoreApplication.translate("MainWindow", u"run provider", None))
        self.button_run_provider_all.setText(QCoreApplication.translate("MainWindow", u"run provider for all frames", None))
        self.button_reload_provider.setText(QCoreApplication.translate("MainWindow", u"reload provider list", None))
        self.button_undo.setText(QCoreApplication.translate("MainWindow", u"undo", None))
        self.button_previous.setText(QCoreApplication.translate("MainWindow", u"previous image", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Progress:", None))
        self.label_total.setText(QCoreApplication.translate("MainWindow", u"/0", None))
        self.button_next.setText(QCoreApplication.translate("MainWindow", u"next image", None))
        self.button_redo.setText(QCoreApplication.translate("MainWindow", u"redo", None))
        self.button_export.setText(QCoreApplication.translate("MainWindow", u"export", None))
        self.label_anno.setText("")
    # retranslateUi

