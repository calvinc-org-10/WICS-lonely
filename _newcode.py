"""
code that's being auditioned
"""
from typing import (Any, )

from PySide6.QtCore import (
    Slot, Signal,
    QMimeData, QUrl,
    )
from PySide6.QtGui import (
    QDragEnterEvent, QDropEvent,
    )
from PySide6.QtWidgets import (
    QWidget,
    QPushButton, QLabel, QCheckBox, QGroupBox, QScrollArea,
    QHBoxLayout, QVBoxLayout, QFileDialog,
    )




from app.database import (Repository, get_app_sessionmaker, )
from app.models import (
    UploadSAPResults,
    )



class  RESTARTHERE_rptCountSummary(QWidget):
    """A form to show the Update Material List from SAP MM60 or ZMSQV001 Spreadsheet form."""
    _formname = "Upload Count Spreadsheet - Results"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(self._formname)
        myLayout = QVBoxLayout(self)
        lblResultsTitle = QLabel(self._formname)
        myLayout.addWidget(lblResultsTitle)

        wdgtMainArea = QWidget()
        layoutMainArea = QVBoxLayout(wdgtMainArea)
        wdgtScrollArea = QScrollArea()
        wdgtScrollArea.setWidgetResizable(True)
        wdgtScrollArea.setWidget(wdgtMainArea)
        myLayout.addWidget(wdgtScrollArea)

        statusVal = Repository(get_app_sessionmaker(), UploadSAPResults).get_all(
            UploadSAPResults.errState == 'nRowsTotal'
        )
        nRowsRead = statusVal[0].rowNum - 1 if statusVal else 0     # -1 because header doesn't count
        statusVal = Repository(get_app_sessionmaker(), UploadSAPResults).get_all(
            UploadSAPResults.errState == 'nRowsAdded'
        )
        nRowsAdded = statusVal[0].rowNum if statusVal else 0
        statusVal = Repository(get_app_sessionmaker(), UploadSAPResults).get_all(
            UploadSAPResults.errState == 'nRowsErrors'
        )
        nRowsErrors = statusVal[0].rowNum if statusVal else 0
        statusVal = Repository(get_app_sessionmaker(), UploadSAPResults).get_all(
            UploadSAPResults.errState == 'nRowsIgnored'
        )
        nRowsNoMaterial = statusVal[0].rowNum if statusVal else 0
        
        UplResults = Repository(get_app_sessionmaker(), UploadSAPResults).get_all(
            UploadSAPResults.errState.notin_(['nRowsAdded','nRowsTotal','nRowsErrors','nRowsIgnored'])
        )
        lblSummary = QLabel(f"Upload Summary: {nRowsRead} rows read, {nRowsAdded} rows added, {nRowsErrors} rows with errors, {nRowsNoMaterial} rows ignored (no material).")
        layoutMainArea.addWidget(lblSummary)
        
        for res in UplResults:
            rstr = f"{res.errState}: {res.errmsg}" if 'error' in res.errState else f"Count Record {res.errmsg} added"
            lblrslt = QLabel(rstr)
            layoutMainArea.addWidget(lblrslt)
    # __init__
# ShowUpdateMatlListfromSAPForm
