# the Main Screen must be in a separate file because it has to be loaded AFTER django support

from PySide6.QtWidgets import (QWidget, QVBoxLayout, )  # type: ignore

from sysver import (_appname, sysver)
from cMenu.cMenu import cMenu


class MainScreen(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        if not self.objectName():
            self.setObjectName("MainWindow")
            
        theMenu = cMenu(parent)
        # theMenu.loadMenu(3, 5) #FIX cMenu!!
        llayout = QVBoxLayout(self)
        llayout.addWidget(theMenu)
        
        self.setLayout(llayout)
        
        self.setWindowTitle(self.tr(_appname + " " + sysver['DEV']))

        # QMetaObject.connectSlotsByName(self)
    # __init__


