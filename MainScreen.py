# the Main Screen must be in a separate file because it has to be loaded AFTER django support

from PySide6.QtWidgets import (QWidget, QVBoxLayout, )


from sysver import (_appname, sysver, )
from calvincTools.cMenu import cMenu

from menuformname_viewMap import FormNameToURL_Map
from externalWebPageURL_Map import ExternalWebPageURL_Map
from app.database import get_app_sessionmaker

class MainScreen(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        if not self.objectName():
            self.setObjectName("MainWindow")
            
        theMenu = cMenu(
            parent,
            sysver=sysver['DEV'],
            FormNameToURL_Map=FormNameToURL_Map,
            ExternalWebPageURL_Map=ExternalWebPageURL_Map,
            app_sessionmaker=get_app_sessionmaker(),
            )
        # theMenu.loadMenu(3, 5) #FIX cMenu!!
        llayout = QVBoxLayout(self)
        llayout.addWidget(theMenu)
        
        self.setLayout(llayout)
        
        self.setWindowTitle(self.tr(_appname + " " + sysver['DEV']))

        # QMetaObject.connectSlotsByName(self)
    # __init__


