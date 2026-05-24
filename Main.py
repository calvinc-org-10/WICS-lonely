import sys
from PySide6.QtCore import (QCoreApplication, )
from PySide6.QtWidgets import (
    QApplication, 
    QWidget, QVBoxLayout, 
    )
from PySide6.QtGui import QPixmap

from calvincTools import calvincTools

from sysver import (_appname, sysver, )
from app_secrets import (sysver_key, usr_auth_required, )

from menuformname_viewMap import FormNameToURL_Map
from externalWebPageURL_Map import ExternalWebPageURL_Map
from app.database import get_app_sessionmaker

class MainScreen(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        if not self.objectName():
            self.setObjectName("MainWindow")

        pixsize=100
        # applogo = QPixmap("F:/calvincTools/calvincTools/assets/cTools.png").scaled(pixsize, pixsize, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation),
        applogo = QPixmap()
        cTools = calvincTools(
            app_sessionmaker=get_app_sessionmaker(),
            FormNameToURL_Map=FormNameToURL_Map,
            ExternalWebPageURL_Map=ExternalWebPageURL_Map,
            appname=_appname,
            logo=applogo,
            appver=sysver[sysver_key],
            usr_auth=usr_auth_required,
            )

        llayout = QVBoxLayout(self)
        stack = cTools.main_window_stack()
        if stack is not None:
            llayout.addWidget(stack)
        self.setLayout(llayout)

        self.setWindowTitle(QCoreApplication.translate("MainWindow", _appname, None))

        cTools.login()
        
    # __init__
# MainScreen
    def end_of_class(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)

    topscreen = MainScreen()
    topscreen.show()

    sys.exit(app.exec())


