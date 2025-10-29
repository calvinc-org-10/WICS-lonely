import sys
from PySide6.QtCore import (QCoreApplication, QMetaObject,  )
from PySide6.QtWidgets import QApplication, QWidget

from django_support.load_ORM_only import setup_django_ORM


if __name__ == "__main__":
    setup_django_ORM()  # must happen before MainScreen imported
    app = QApplication(sys.argv)
    from MainScreen import MainScreen
    topscreen = MainScreen()
    # topscreen = testforms.Test02()
    topscreen.show()
    sys.exit(app.exec())


