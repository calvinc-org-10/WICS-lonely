"""
code that's being auditioned
"""


from PySide6.QtCore import (
    QRect, QPoint, Signal, 
    )
from PySide6.QtGui import (
    QIcon,
    QPainter, QRegion,
    QImage, 
    QDragEnterEvent, QDropEvent,
    )
from PySide6.QtWidgets import (
    QTabWidget, QBoxLayout, QCheckBox, QGroupBox, QFileDialog,
    )
from PySide6.QtPrintSupport import (
    QPrinter, 
    QPrintDialog, QPrintPreviewDialog,
    )


from openpyxl import load_workbook
from openpyxl.utils.datetime import WINDOWS_EPOCH, from_excel






