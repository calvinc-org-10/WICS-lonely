"""
code that's being auditioned
"""

from typing import (Any, )
from datetime import (date, datetime, )

from PySide6.QtCore import (
    Qt, Slot,
    QRect, QPoint, QDate, 
    Signal, 
    )
from PySide6.QtGui import (
    QIcon,
    QPainter, QRegion,
    QImage, 
    QDragEnterEvent, QDropEvent,
    )
from PySide6.QtWidgets import (
    QWidget, QLabel, QProgressBar, QPushButton, QDateEdit,
    QTabWidget, QGridLayout, QBoxLayout, QVBoxLayout,
    QCheckBox, QGroupBox, QScrollArea, QFileDialog,
    )
from PySide6.QtPrintSupport import (
    QPrinter, 
    QPrintDialog, QPrintPreviewDialog,
    )

from sqlalchemy import and_

from openpyxl import load_workbook
from openpyxl.utils.datetime import WINDOWS_EPOCH, from_excel

from qtawesome import icon

from calvincTools.utils import (cSimpleRecordForm, cFileSelectWidget, )

from app.database import (get_app_sessionmaker, Repository, )
from app.models import (
    SAP_SOHRecs, SAPPlants_org, MaterialList,
    )


class UploadSAPSOHSprsht(cSimpleRecordForm):
    _ORMmodel = SAP_SOHRecs
    _formname = "Upload SAP MB52 Spreadsheet"
    _ssnmaker = get_app_sessionmaker()
    fieldDefs = {
        # no fields to edit, everything manually handled
    }


    # __init__ inherited from cSimpleRecordForm
    def __init__(self, *args, **kwargs):
        self.uploadresults: dict[str, Any] = {}

        super().__init__(*args, **kwargs)
    # __init__


    ###########################################################
    ############## Override cSimpleRecordForm UI build methods
    ###########################################################

    @Slot()
    def _placeFields(self, layoutFormPages: QTabWidget, layoutFormFixedTop: QGridLayout | None, layoutFormFixedBottom: QGridLayout | None, lookupsAllowed: bool = True) -> None:
        # no fields to place, everything manually handled
        mainFormPage = self.FormPage(0)
        assert isinstance(mainFormPage, QGridLayout)

        # one day, Ill have the db do this ...
        SAPDates = { dd.uploaded_at for dd in Repository(get_app_sessionmaker(), SAP_SOHRecs).get_all() }        
        self.LastSAPUpload = None if not SAPDates else max(SAPDates)
        anncestrLastDate = "No Previous SAP SOH Upload" if self.LastSAPUpload is None else f"Last SAP MB52 Upload was on: {self.LastSAPUpload.strftime('%Y-%m-%d')}"
        mainFormPage.addWidget(QLabel(anncestrLastDate), 0, 0)

        todaysdate = datetime.now().date()
        self.uplDate = QDateEdit(date=QDate(todaysdate.year, todaysdate.month, todaysdate.day))
        self.uplDate.userDateChanged.connect(self.uplDateChanged)
        uplDateTitle = QLabel("Upload Date (for SAP SOH records):")
        self.uplDateWarning = QLabel(" ")
        self.uplDateWarning.setStyleSheet("color: red; font-weight: bold;")
        mainFormPage.addWidget(uplDateTitle, 1, 0)
        mainFormPage.addWidget(self.uplDate, 1, 1)
        mainFormPage.addWidget(self.uplDateWarning, 1, 2)

        chooseFileWidget = QWidget()
        chooseFileLayout = QGridLayout(chooseFileWidget)
        lblChooseFileLabel = QLabel("Choose or Drop SAP MB52 Spreadsheet File:")
        self.btnChooseFile = cFileSelectWidget(btnText="Choose Spreadsheet File")
        self.btnChooseFile.fileChosen.connect(self.FileChosen)
        chooseFileLayout.addWidget(lblChooseFileLabel, 0, 0)
        chooseFileLayout.addWidget(self.btnChooseFile, 1, 0)
        mainFormPage.addWidget(chooseFileWidget, 2, 0)

        # the status area
        self.wdgtUpdtStatusText = QLabel("")
        self.wdgtUpdtStatusProgBar = QProgressBar()
        assert layoutFormFixedTop is not None, "layoutFormFixedTop is required"
        layoutFormFixedTop.addWidget(self.wdgtUpdtStatusText, 0, 0)
        layoutFormFixedTop.addWidget(self.wdgtUpdtStatusProgBar, 1, 0)
    # _placeFields

    def _addActionButtons(self, layoutButtons: QBoxLayout | None = None, layoutHorizontal: bool = True, NavActions: list[tuple[str, QIcon]] | None = None, CRUDActions: list[tuple[str, QIcon]] | None = None) -> None:
        btnUploadFile = QPushButton(icon('fa5s.file-upload'), "Upload SAP SOH")
        btnUploadFile.clicked.connect(self.uploadFile)
        btnClose = QPushButton(icon('mdi.close-octagon'), "Close Form")
        btnClose.clicked.connect(self.closeForm)

        if layoutButtons is not None:
            layoutButtons.addWidget(btnUploadFile, alignment=Qt.AlignmentFlag.AlignLeft)
            layoutButtons.addStretch(1)
            layoutButtons.addWidget(btnClose, alignment=Qt.AlignmentFlag.AlignRight)
        #endif layoutButtons
    # def _handleActionButton(self, action: str) -> None:
    #     return super()._handleActionButton(action)
    # _add/handleActionButtons

    def initialdisplay(self):
        self.showNewRecordFlag()
        self.showUpdateStatus("")
    # initialdisplay

    ###########################################################
    ############## UI update methods
    ###########################################################

    def showUpdateStatus(self, statusText: str, progressValue: int = 0, progressMax: int = -1) -> None:

        self.wdgtUpdtStatusText.setText(statusText)

        if progressMax < 0:
            self.wdgtUpdtStatusProgBar.setVisible(False)
        else:
            self.wdgtUpdtStatusProgBar.setVisible(True)
            self.wdgtUpdtStatusProgBar.setMaximum(progressMax)
            self.wdgtUpdtStatusProgBar.setValue(progressValue)
        # endif progressMax
    # showUpdateStatus


    ###########################################################
    ############## button responders
    ###########################################################

    @Slot()
    def FileChosen(self):
        # enable the Upload button
        pass

    @Slot()
    def uplDateChanged(self, dateslctd: QDate):
        # Check if SAP SOH records already exist for this date
        UplDate = datetime(dateslctd.year(), dateslctd.month(), dateslctd.day()).date()
        self.uplDateWarning.setText(" ")    # assume no warning
        existingRecs = Repository(get_app_sessionmaker(), SAP_SOHRecs).get_all(SAP_SOHRecs.uploaded_at==UplDate)
        if len(existingRecs) > 0:
            self.uplDateWarning.setText(f"(an existing SAP upload exists for {UplDate.strftime('%Y-%m-%d')}. It will be overwritten!!)")


    @Slot()
    def uploadFile(self):
        # disable most of the form while processing

        self.proc_UpSAPSprsheet_00InitUpld()

        USSName = self.proc_UpSAPSprsheet_00CopySpreadsheet()
        self.proc_UpSAPSprsheet_01ReadSheet(USSName)
        self.done_UpSAPSprsheet_01ReadSheet()      # this triggers most of the rest of the processing chain

        # present results to user
        childScreen = ShowUploadedSAPResults(uploadresults=self.uploadresults)
        childScreen.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        childScreen.show()

        self.proc_UpSAPSprsheet_99_Cleanup()
        self.closeForm()


    @Slot()
    def closeForm(self):
        # TODO: Implement close form logic
        self.close()


    ###########################################################
    ############## "record" status methods
    ###########################################################

    def isNewRecord(self) -> bool:
        return False


    ###########################################################
    ############## other cSimpleRecordForm overrides
    ###########################################################

    def changeInternalVarField(self, wdgt, intVarField: str, wdgt_value: Any) -> None:
        return


    ###########################################################
    ############## Read / process spreadsheet methods
    ###########################################################

    def proc_UpSAPSprsheet_00InitUpld(self) -> None:
        self.showUpdateStatus("Initializing Upload of SAP MB52 Spreadsheet...")

    def proc_UpSAPSprsheet_00CopySpreadsheet(self) -> str:
        return self.btnChooseFile.getFileChosen()

    def proc_UpSAPSprsheet_01ReadSheet(self, fName: str) -> None:
        self.showUpdateStatus("Reading SAP MB52 Spreadsheet...")

        NOTdbFld_flags = ['**NOTdbFld**',]

        wb = load_workbook(filename=fName, read_only=True)
        CountSprshtDateEpoch = wb.epoch
        ws = wb.active
        assert ws is not None, "Spreadsheet has no active worksheet"

        _SStName_Material = 'Material'
        _TblName_Material = 'MaterialPartNum'
        _SStName_Plant = 'Plant'
        _TblName_Plant = 'Plant'
        SprshtcolmnNames = ws[1]
        SprshtcolmnMap = {_TblName_Material: None, _TblName_Plant: None}
        SprshtREQUIREDFLDS = [_TblName_Material, _TblName_Plant, ]
        Sprsht_SSName_TableName_map = {
                _SStName_Material: _TblName_Material,  # Material+org will translate to a Material_id
                _SStName_Plant: _TblName_Plant,
                'Material description': 'Description',
                'Material type': 'MaterialType',
                'Storage location': 'StorageLocation',
                'Base Unit of Measure': 'BaseUnitofMeasure',
                'Unrestricted': 'Amount',
                'Currency': 'Currency',
                'Value Unrestricted': 'ValueUnrestricted',
                'Special Stock': 'SpecialStock',
                'Blocked':'Blocked',
                'Value BlockedStock':'ValueBlocked',
                'Vendor':'Vendor',
                'Batch': 'Batch',
                }
        for col in SprshtcolmnNames:
            if col.value in Sprsht_SSName_TableName_map:
                colkey = Sprsht_SSName_TableName_map[str(col.value)]
                # has this col.value already been mapped?
                if (colkey in SprshtcolmnMap and SprshtcolmnMap[colkey] is not None):
                    # yes, that's a problem
                    self.showUpdateStatus(f"Error: This workbook has a bad header row - More than one column named {col.value}.  See Calvin to fix this.")
                    wb.close()
                    return
                else:
                    SprshtcolmnMap[colkey] = col.column - 1 # type: ignore
                # endif previously mapped
            #endif col.value in SAP_SSName_TableName_map
        #endfor col in SAPcolmnNames

        HeaderGood = all([(reqFld in SprshtcolmnMap) for reqFld in SprshtREQUIREDFLDS])
        if not HeaderGood:
            MissingRequiredFields = [reqFld for reqFld in SprshtREQUIREDFLDS if reqFld not in SprshtcolmnMap]
            self.showUpdateStatus(f"Error: This workbook has a bad header row - missing columns {MissingRequiredFields}.  See Calvin to fix this.")
            wb.close()
            return
        material_col = SprshtcolmnMap[_TblName_Material]
        plants_col = SprshtcolmnMap[_TblName_Plant]
        assert material_col is not None, "Material column mapping failed"
        assert plants_col is not None, "Plant column mapping failed"

        # if SAP SOH records exist for this date, kill them; only one set of SAP SOH records per day
        # (this was signed off on by user before coming here)
        UplDate = self.uplDate.date().toPython()
        Repository(get_app_sessionmaker(), SAP_SOHRecs).removewhere(SAP_SOHRecs.uploaded_at==UplDate)

        SprshtRowNum = 1
        nRowsAdded = 0

        intrval_announce = min(100, int(max(1, ws.max_row // 10)))
        for row in ws.iter_rows(min_row=SprshtRowNum+1, values_only=True):
            SprshtRowNum += 1
            if SprshtRowNum % intrval_announce == 0:
                self.showUpdateStatus(f"Reading Spreadsheet ... record {SprshtRowNum} of {ws.max_row}", SprshtRowNum, ws.max_row)

            if material_col is None or row[material_col] is None:
                MatlNum = ''
            else:
                MatlNum = row[material_col]
            if len(str(MatlNum)):
                plant_val = row[plants_col]
                _org = Repository(get_app_sessionmaker(), SAPPlants_org).get_all(SAPPlants_org.SAPPlant==plant_val)[0].org_id
                try:
                    whereclause = and_(MaterialList.org_id==_org,MaterialList.Material==MatlNum)
                    MatlRec = Repository(get_app_sessionmaker(), MaterialList).get_all(whereclause)[0]
                except (TypeError, IndexError, KeyError):
                    MatlRec = None
                if not MatlRec:
                    self.showUpdateStatus(f'either {MatlNum}  does not exist in MaterialList or incorrect Plant ({plant_val}) given',
                        SprshtRowNum, ws.max_row)
                else:
                    SRec = SAP_SOHRecs(
                            org_id = _org,     # will be going away - or will it???
                            uploaded_at = UplDate,
                            Material_id = MatlRec.id
                            )
                    for fldName, colNum in SprshtcolmnMap.items():
                        assert colNum is not None, f"Column number for field {fldName} is None"
                        if fldName == _TblName_Material:
                            pass    # not continue - we are preserving the incoming MaterialPartNum string
                        setval = '' if row[colNum] is None else row[colNum]
                        setattr(SRec, fldName, setval)
                    # endfor fldName, colNum
                    Repository(get_app_sessionmaker(), SAP_SOHRecs).add(SRec)
                    nRowsAdded += 1
                # endif MatlRec
            # endif len(str(MatlNum))
        # endfor row in ws.iter_rows

        self.uploadresults['nRowsTotal'] = SprshtRowNum
        self.uploadresults['nRowsAdded'] = nRowsAdded
        self.uploadresults['uploadDate'] = UplDate

        # close and kill temp files
        wb.close()

        # self.done_UpSAPSprsheet_01ReadSheet()    # caller will do this
    def done_UpSAPSprsheet_01ReadSheet(self):
        self.showUpdateStatus("Finished Reading Count Entry Spreadsheet.")
        self.proc_UpSAPSprsheet_99_FinalProc()

    def proc_UpSAPSprsheet_99_FinalProc(self) -> None:
        self.showUpdateStatus("Finished Processing Count Entry Spreadsheet...")

    def proc_UpSAPSprsheet_99_Cleanup(self) -> None:
        # nothing to clean up here
        return
# UploadActCountSprsht

class ShowUploadedSAPResults(QWidget):
    """A form to show the Upload SAP SOH Spreadsheet results."""
    _formname = "Upload SAP SOH Spreadsheet - Results"

    def __init__(self, *args, **kwargs):
        uploadresults = kwargs.pop('uploadresults', {})
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

        nRowsRead = uploadresults.get('nRowsTotal', 0)
        nRowsAdded = uploadresults.get('nRowsAdded', 0)
        upldDate = uploadresults.get('uploadDate', None)

        lblSummary = QLabel(
            f"<h4>{ nRowsAdded } SAP SOH (MB52) spreadsheet records successfully uploaded with date { upldDate }!</h4>"
            )
        layoutMainArea.addWidget(lblSummary)
    # __init__
# ShowUploadedSAPResults
