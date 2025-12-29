"""
code that's being auditioned
"""

from PySide6.QtCore import (
    Qt, QRect, QPoint,
    Signal, 
    )
from PySide6.QtGui import (
    QPainter, QRegion,
    QImage, 
    QDragEnterEvent, QDropEvent,
    )
from PySide6.QtWidgets import (
    QWidget,
    QCheckBox, QGroupBox, QScrollArea, QFileDialog,
    )
from PySide6.QtPrintSupport import (
    QPrinter, 
    QPrintDialog, QPrintPreviewDialog,
    )