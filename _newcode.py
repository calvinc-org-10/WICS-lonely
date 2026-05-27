"""
code that's being auditioned
"""

from typing import (Any, List, Dict, )
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

from calvincTools.utils import (
    cSRFSingleRecordForm, cFileSelectWidget,
    cExcelFile, 
    )

from app.database import (get_app_sessionmaker, Repository, )
from app.models import (
    SAP_SOHRecs, SAPPlants_org, MaterialList,
    )
from calvincTools.utils.forms.definitions.cQFormFieldDef import cQFormFieldDef


class UploadSAPSOHSprsht(cSRFSingleRecordForm):
    _ORMmodel = SAP_SOHRecs
    _formname = "Upload SAP MB52 Spreadsheet"
    _ssnmaker = get_app_sessionmaker()

    LastSAPUpload = None
    uplDate = None
    uplDateWarning = None
    btnChooseFile = None
    wdgtUpdtStatusText = None
    wdgtUpdtStatusProgBar = None
    

    # __init__ inherited from cSimpleRecordForm
    def __init__(self, *args, **kwargs):
        self.uploadresults: dict[str, Any] = {}

        super().__init__(*args, **kwargs)
    # __init__

    def defineFields(self) -> List[cQFormFieldDef] | None:
        # no fields to edit, everything manually handled
        return []


    ###########################################################
    ############## Override cSimpleRecordForm UI build methods
    ###########################################################

    @Slot()
    def _build_fields(self) -> None:
    # def _placeFields(self, layoutFormPages: QTabWidget, layoutFormFixedTop: QGridLayout | None, layoutFormFixedBottom: QGridLayout | None, lookupsAllowed: bool = True) -> None:
        # no fields to place, everything manually handled
        mainFormPage = self.FormPage(0)
        assert isinstance(mainFormPage, QGridLayout)

        layoutFormFixedTop = self._layouts.fixed_top
        
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


    def _addActionButtons(self, ActionButtons) -> None:     # pylint:disable=signature-differs
        layoutButtons = self._layouts.buttons

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

        assert self.wdgtUpdtStatusText is not None, "wdgtUpdtStatusText is not defined"
        assert self.wdgtUpdtStatusProgBar is not None, "wdgtUpdtStatusProgBar is not defined"
        
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
        assert self.uplDateWarning is not None, "uplDateWarning widget is not defined"
        
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

    def changeInternalVarField(self, wdgt, intVarField: str, wdgt_value: Any) -> None:      # pylint:disable=unused-argument
        return


    ###########################################################
    ############## Read / process spreadsheet methods
    ###########################################################

    def proc_UpSAPSprsheet_00InitUpld(self) -> None:
        self.showUpdateStatus("Initializing Upload of SAP MB52 Spreadsheet...")

    def proc_UpSAPSprsheet_00CopySpreadsheet(self) -> str:
        assert self.btnChooseFile is not None, "btnChooseFile widget is not defined"
        return self.btnChooseFile.getFileChosen()

    def proc_UpSAPSprsheet_01ReadSheet(self, fName: str) -> None:
        self.showUpdateStatus("Reading SAP MB52 Spreadsheet...")

        # NOTdbFld_flags = ['**NOTdbFld**',]
        
        _SStName_Material = 'Material'
        _TblName_Material = 'MaterialPartNum'
        _SStName_Plant = 'Plant'
        _TblName_Plant = 'Plant'

        def SAPFldDescMap() -> Dict[str,cExcelFile.SprdsheetFldDescriptor]:
            Sprsht_SSName_TableName_map = {
                    # Material+org will translate to a Material_id
                    _SStName_Material: {'ModelFldName': _TblName_Material},
                    _SStName_Plant: {'ModelFldName': _TblName_Plant},
                    'OrgID': {'ModelFldName': 'org_id', 'CalculatedFld': True, 'CleanProc': SAPCalcFldProc, 'AllowedTypes': (int, )},
                    'MatlID': {'ModelFldName': 'Material_id', 'CalculatedFld': True, 'CleanProc': SAPCalcFldProc, 'AllowedTypes': (int, )},
                    'UpldAt': {'ModelFldName': 'uploaded_at', 'CalculatedFld': True, 'CleanProc': SAPCalcFldProc, 'AllowedTypes': (date, )},
                    'Material description': {'ModelFldName': 'Description'},
                    'Material type': {'ModelFldName': 'MaterialType'},
                    'Storage location': {'ModelFldName': 'StorageLocation'},
                    'Base Unit of Measure': {'ModelFldName': 'BaseUnitofMeasure'},
                    'Unrestricted': {'ModelFldName': 'Amount', 'CleanProc': SAPFldCleanProc, 'AllowedTypes': (float, int, )},
                    'Currency': {'ModelFldName': 'Currency'},
                    'Value Unrestricted': {'ModelFldName': 'ValueUnrestricted', 'CleanProc': SAPFldCleanProc, 'AllowedTypes': (float, int, )},
                    'Special Stock': {'ModelFldName': 'SpecialStock'},
                    'Blocked':{'ModelFldName': 'Blocked', 'CleanProc': SAPFldCleanProc, 'AllowedTypes': (float, int, )},
                    'Value BlockedStock':{'ModelFldName': 'ValueBlocked', 'CleanProc': SAPFldCleanProc, 'AllowedTypes': (float, int, )},
                    'Vendor':{'ModelFldName': 'Vendor'},
                    'Batch': {'ModelFldName': 'Batch'},
                    }
            retDict = {ssName: cExcelFile.SprdsheetFldDescriptor(**fldDescArgs)
                for ssName, fldDescArgs in Sprsht_SSName_TableName_map.items()}
            return retDict
        # SAPFldDescMap

        def SAPFldCleanProc(fldName:str, fldVal:Any, row, dbFld_to_SsprshtCol, **kwargs) -> Any:        # pylint:disable=unused-argument
            if fldVal is None:
                return None
            if fldName in ['Amount', 'ValueUnrestricted', 'ValueBlocked', 'Blocked']:
                try:
                    return float(fldVal)
                except ValueError:
                    return 0.0
            # endif numeric fields
            return fldVal
        # SAPFldCleanProc
        
        def SAPCalcFldProc(fldName:str, val, row, dbFld_to_SsprshtCol, **kwargs) -> Any:    # pylint:disable=unused-argument
            if fldName == 'org_id':
                plant_val = row[dbFld_to_SsprshtCol[_TblName_Plant]]
                org_id = Repository(get_app_sessionmaker(), SAPPlants_org).get_all(SAPPlants_org.SAPPlant==plant_val)[0].org_id
                return org_id
            elif fldName == 'Material_id':
                plant_val = row[dbFld_to_SsprshtCol[_TblName_Plant]]
                _org = Repository(get_app_sessionmaker(), SAPPlants_org).get_all(SAPPlants_org.SAPPlant==plant_val)[0].org_id
                MatlNum = row[dbFld_to_SsprshtCol[_TblName_Material]]
                try:
                    whereclause = and_(MaterialList.org_id==_org, MaterialList.Material==MatlNum)
                    MatlRec = Repository(get_app_sessionmaker(), MaterialList).get_all(whereclause)[0]
                    return MatlRec.id
                except (TypeError, IndexError, KeyError):
                    return None
            elif fldName == 'uploaded_at':
                assert self.uplDate is not None, "uplDate is not defined"
                return self.uplDate.date().toPython()
            # endif calculated fields
            return None
        # SAPCalcFldProc

        def UplSAPProgressAnnounceCallback(currentRowNum, totalRows):        
            self.showUpdateStatus(f"Reading Spreadsheet ... record {currentRowNum} of {totalRows}", currentRowNum, totalRows)

        # if SAP SOH records exist for this date, kill them; only one set of SAP SOH records per day
        # (this was signed off on by user before coming here)
        assert self.uplDate is not None, "uplDate is not defined"
        UplDate = self.uplDate.date().toPython()
        Repository(get_app_sessionmaker(), SAP_SOHRecs).removewhere(SAP_SOHRecs.uploaded_at==UplDate)

        # wb = load_workbook(filename=fName, read_only=True)
        wb = cExcelFile.load_from_file(filename=fName, read_only=True)
        assert wb is not None, "Failed to load spreadsheet file"
        # CountSprshtDateEpoch = wb.epoch
        
        wb.save_to_SQLAlchemyModel(
            ssnmaker=self._ssnmaker,
            TargetModel=SAP_SOHRecs,
            WksheetName=None,   # default to active sheet
            SprdsheetFlds=SAPFldDescMap(),
            required_columns=[_TblName_Material, _TblName_Plant, ],
            progress_interval=100,
            progress_callback=UplSAPProgressAnnounceCallback,
            )
        
        self.uploadresults['nRowsTotal'] = wb.num_rows
        self.uploadresults['nRowsAdded'] = wb.nRows
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
    def end_of_class(self):
        pass

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

        # nRowsRead = uploadresults.get('nRowsTotal', 0)
        nRowsAdded = uploadresults.get('nRowsAdded', 0)
        upldDate = uploadresults.get('uploadDate', None)

        lblSummary = QLabel(
            f"<h4>{ nRowsAdded } SAP SOH (MB52) spreadsheet records successfully uploaded with date { upldDate }!</h4>"
            )
        layoutMainArea.addWidget(lblSummary)
    # __init__
# ShowUploadedSAPResults
    def end_of_class(self):
        pass

