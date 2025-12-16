# pylint: disable=f-string-without-interpolation

from typing import (Any, )
from datetime import (datetime, date, )

from PySide6.QtCore import (
    Qt,
    Slot, Signal,
    QMimeData, QUrl, 
    )
from PySide6.QtGui import (
    QIcon,
    QDragEnterEvent, QDropEvent, 
    )
from PySide6.QtWidgets import (
    QWidget, 
    QPushButton, QLabel, QCheckBox, QProgressBar,
    QGroupBox, 
    QBoxLayout, QHBoxLayout, QVBoxLayout, QGridLayout, QTabWidget, 
    QFileDialog,
    )

from mathematical_expressions_parser.eval import evaluate 

from app.database import (Repository, get_app_sessionmaker, )
from app.models import (
    UploadSAPResults, MaterialList, ActualCounts,
    )

from openpyxl import load_workbook
from openpyxl.utils.datetime import from_excel, WINDOWS_EPOCH
from qtawesome import icon

from calvincTools.utils import (
    cSimpleRecordForm,
    calvindate, 
    )





# TODO: Refactor this into a reusable component in calvincTools
class cFileSelectWidget(QWidget):
    """A QPushButton that accepts file drops and opens a QFileDialog
    with the dropped file pre-selected.
    """
    _btnChooseFile: QPushButton = QPushButton()
    _lblFileChosen: QLabel = QLabel("No file chosen")
    fileChosen: Signal = Signal()
    
    def __init__(self, *args, btnIcon=None, btnText="Pick or Drop File Here", **kwargs):
        # TODO: add parameters for initial directory, file filters, etc.
        # TODO: TFacceptMultiFiles: bool = False
        
        super().__init__(*args, **kwargs)
        if btnIcon is not None:
            self._btnChooseFile.setIcon(btnIcon)
        self._btnChooseFile.setText(btnText)
        self._btnChooseFile.setToolTip("Click to choose a file or drag and drop a file onto this button.")
        self._btnChooseFile.clicked.connect(self.open_file_dialog_with_file)

        # 1. Essential: Tell the widget it accepts drops
        self.setAcceptDrops(True)
        
        # Layout
        layout = QHBoxLayout(self)
        layout.addWidget(self._btnChooseFile)
        layout.addWidget(self._lblFileChosen)
        
    # __init__

    def getFileChosen(self) -> str:
        """Returns the currently chosen file path."""
        return self._lblFileChosen.text()
    # getFileChosen
    
    # most method calls are actually for the push button inside
    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the contained widget."""
        return getattr(self._btnChooseFile, name, None)

    def dragEnterEvent(self, event: QDragEnterEvent):
        # 2. Check if the dragged data contains a list of URIs (files)
        if event.mimeData().hasUrls():
            # Accept the drag event
            event.acceptProposedAction()
        else:
            # Ignore the drag event
            event.ignore()
        #endif mimeData.hasUrls()
    # dragEnterEvent

    def dropEvent(self, event: QDropEvent):
        # 3. Handle the drop action
        mime_data: QMimeData = event.mimeData()
        
        if mime_data.hasUrls():
            # Get the list of URLs (QUrls)
            urls: list[QUrl] = mime_data.urls()
            
            if urls:
                # We only care about the first dropped file
                first_url: QUrl = urls[0]
                
                # Convert the QUrl to a local file path
                file_path = first_url.toLocalFile()
                
                # Check if it's a valid file path
                if file_path:
                    # 4. Open the QFileDialog with the dropped file chosen
                    self.open_file_dialog_with_file(file_path)
            
            event.acceptProposedAction()
        else:
            event.ignore()
        #endif mime_data.hasUrls()
    # dropEvent

    @Slot()
    def open_file_dialog_with_file(self, file_path: str = ''):
        """Opens a QFileDialog pre-selecting the dropped file."""
        
        # Determine the directory and file name
        from PySide6.QtCore import QFileInfo
        if not file_path:
            file_info = QFileInfo()
        else:
            file_info = QFileInfo(file_path)
        #endif file_path
        directory = file_info.dir().path()
        file_name = file_info.fileName()

        # You can use getOpenFileName to open the dialog
        # The third argument sets the initial directory
        # The fourth argument sets the filter (e.g., "All Files (*)")
        selected_file, _ = QFileDialog.getOpenFileName(
            self,                               # Parent
            "File Dropped! Verify Selection",    # Dialog Title
            directory,                           # Initial Directory
            f"All Files (*);;{file_name}",                     # Filter
            file_name,                           # Pre-selected File Name
        )

        # QFileDialog.getOpenFileName does not automatically pre-select
        # the file name when given only a directory. 
        # To truly pre-select, the path needs to be passed, but the dialog 
        # needs to be *aware* of it. A simple solution is often to just
        # show the user the path they dropped and confirm.
        
        # A workaround to truly pre-select the file in some systems/dialog styles:
        # selected_file, _ = QFileDialog.getOpenFileName(
        #     self, "File Dropped! Verify Selection", file_path, "All Files (*)"
        # )

        if selected_file:
            self._lblFileChosen.setText(selected_file)
            self.fileChosen.emit()
            # Here you can handle the selected file as needed
            # print(f"User confirmed selection: {selected_file}")
        else:
            pass
            # print("Dialog closed without confirming the selection.")
        #endif selected_file
    # open_file_dialog_with_file
# cFileDropButton


class UploadActCountSprsht(cSimpleRecordForm):
    _ORMmodel = None
    _formname = "Upload Count Entry Spreadsheet"
    _ssnmaker = None
    fieldDefs = {
        # no fields to edit, everything manually handled
    }


    # __init__ inherited from cSimpleRecordForm


    ###########################################################
    ############## Override cSimpleRecordForm UI build methods
    ###########################################################

    @Slot()
    def _placeFields(self, layoutFormPages: QTabWidget, layoutFormFixedTop: QGridLayout | None, layoutFormFixedBottom: QGridLayout | None, lookupsAllowed: bool = True) -> None:
        # no fields to place, everything manually handled
        mainFormPage = self.FormPage(0)
        assert isinstance(mainFormPage, QGridLayout)

        chooseFileWidget = QWidget()
        chooseFileLayout = QGridLayout(chooseFileWidget)
        lblChooseFileLabel = QLabel("Choose or Drop SAP Material List Spreadsheet File:")
        self.btnChooseFile = cFileSelectWidget(btnText="Choose Spreadsheet File")
        self.btnChooseFile.fileChosen.connect(self.FileChosen)
        chooseFileLayout.addWidget(lblChooseFileLabel, 0, 0)
        chooseFileLayout.addWidget(self.btnChooseFile, 1, 0)

        self.dict_chkUpdtOption = {}
        self.dict_chkUpdtOption['Description'] = QCheckBox("Description")
        self.dict_chkUpdtOption['SAPMatlType'] = QCheckBox("SAP Material Type")
        self.dict_chkUpdtOption['SAPMatlGroup'] = QCheckBox("SAP Material Group")
        self.dict_chkUpdtOption['SAPManuf'] = QCheckBox("SAP Manufacturer")
        self.dict_chkUpdtOption['SAPMPN'] = QCheckBox("SAP Manufacturer Part Number")
        self.dict_chkUpdtOption['SAPABC'] = QCheckBox("SAP ABC Designation")
        self.dict_chkUpdtOption['SAPPrice'] = QCheckBox("Price, Price Unit and Currency")
        grpbxUpdtOptions = QGroupBox('Update Existing Material Records for these Fields:')
        layoutUpdtOptions = QVBoxLayout(grpbxUpdtOptions)
        for chk in self.dict_chkUpdtOption.values():
            layoutUpdtOptions.addWidget(chk)

        self.chkDeleteIfNotinSprsht = QCheckBox("Delete Records Not in Spreadsheet")

        mainFormPage.addWidget(chooseFileWidget, 0, 0)
        # mainFormPage.addWidget(PhaseWidget, 2, 0)
        mainFormPage.addWidget(grpbxUpdtOptions, 0, 1, 2, 1)
        mainFormPage.addWidget(self.chkDeleteIfNotinSprsht, 2, 1)

        self.wdgtUpdtStatusText = QLabel("")
        self.wdgtUpdtStatusProgBar = QProgressBar()
        assert layoutFormFixedTop is not None, "layoutFormFixedTop is required"
        layoutFormFixedTop.addWidget(self.wdgtUpdtStatusText, 0, 0)
        layoutFormFixedTop.addWidget(self.wdgtUpdtStatusProgBar, 1, 0)
    # _placeFields
    
    def _addActionButtons(self, layoutButtons: QBoxLayout | None = None, layoutHorizontal: bool = True, NavActions: list[tuple[str, QIcon]] | None = None, CRUDActions: list[tuple[str, QIcon]] | None = None) -> None:
        btnUploadFile = QPushButton(icon('fa5s.file-upload'), "Upload Data from Spreadsheet")
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
    def uploadFile(self):
        # disable most of the form while processing

        self.proc_UpActCountSprsheet_00InitUpld()

        USSName = self.proc_UpActCountSprsheet_00CopySpreadsheet()
        self.proc_UpActCountSprsheet_01ReadSheet(USSName)
        self.done_UpActCountSprsheet_01ReadSheet()      # this triggers most of the rest of the processing chain

        # present results to user
        childScreen = ShowUpdateMatlListfromSAPForm()
        childScreen.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        childScreen.show()


        self.proc_UpActCountSprsheet_99_Cleanup()
        self.closeForm()
    # uploadFile
    # do I still need this?
        # elif client_phase=='wantresults':
        #     QS = UploadSAPResults.objects.filter(errState = 'nRowsTotal')
        #     if QS.exists(): SprshtRowNum = QS[0].rowNum
        #     else: SprshtRowNum = 0
        #     QS = UploadSAPResults.objects.filter(errState = 'nRowsAdded')
        #     if QS.exists(): nRowsAdded = QS[0].rowNum
        #     else: nRowsAdded = 0
        #     QS = UploadSAPResults.objects.filter(errState = 'nRowsErrors')
        #     if QS.exists(): nRowsErrors = QS[0].rowNum
        #     else: nRowsErrors = 0
        #     QS = UploadSAPResults.objects.filter(errState = 'nRowsIgnored')
        #     if QS.exists(): nRowsNoMaterial = QS[0].rowNum
        #     else: nRowsNoMaterial = 0
        #     UplResults = UploadSAPResults.objects.exclude(errState__in = ['nRowsAdded','nRowsTotal','nRowsErrors','nRowsIgnored']).order_by('rowNum')
        #     cntext = {'UplResults':UplResults, 
        #             'ResultStats': {
        #                     'nRowsRead': SprshtRowNum - 1,      
        #                         # -1 because header doesn't count
        #                     'nRowsAdded': nRowsAdded ,
        #                     'nRowsNoMaterial': nRowsNoMaterial,
        #                     'nRowsErrors': nRowsErrors,
        #                 },
        #             }


    @Slot()
    def closeForm(self):
        # TODO: Implement close form logic
        self.close()
        pass


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
    
    def cleanupfld(self, fld, val, CountSprshtDateEpoch = WINDOWS_EPOCH):
        """
        fld is the name of the field in the ActualCount or MaterialList table
        val is the value to be cleaned for insertion into the fld
        Returns  {'usefld':usefld, 'cleanval': cleanval}
            usefld is a boolean indicating that val could/not be cleaned to the correct type
            cleanval is val in the correct type (if usefld==True)
        """
        cleanval = None

        if   fld == 'CountDate': 
            if isinstance(val,(calvindate, date, datetime)):
                usefld = True
                cleanval = calvindate(val).as_datetime()
            elif isinstance(val,int):
                usefld = True
                cleanval = from_excel(val,CountSprshtDateEpoch)
            else:
                try:
                    cleanval = calvindate(val).as_datetime()
                    usefld = True
                except ValueError:
                    usefld = False
                #endtry
            #endif val type
        elif fld in \
            ['CTD_QTY_Expr', 
                ]:
            if isinstance(val,str):
                if val[0] == '=':
                    val = val[1:]
            try:
                v = evaluate(str(val))
            except (SyntaxError, NameError, TypeError, ZeroDivisionError):
                v = "-- INVALID --"
            usefld = (v!="-- INVALID --")
            cleanval = str(val) if (v != "--INVALID--") else None
        elif fld in \
            ['org_id', 
                'LocationOnly',
                'FLAG_PossiblyNotRecieved', 
                'FLAG_MovementDuringCount',
                ]:
            try:
                cleanval = int(val)
                usefld = True
            except:
                usefld = False
        elif fld in \
            ['Material', 
                'Counter', 
                'LOCATION', 
                'Notes', 
                'TypicalContainerQty', 
                'TypicalPalletQty',
                'PKGID_Desc',	
                'TAGQTY',
                ]:
            usefld = (val is not None)
            if usefld: cleanval = str(val)
        else:
            usefld = True
            cleanval = val
        
        return {'usefld':usefld, 'cleanval': cleanval}
    #end def cleanupfld

    def proc_UpActCountSprsheet_00InitUpld(self) -> None:
        self.showUpdateStatus("Initializing Upload of Count Entry Spreadsheet...")
        Repository(get_app_sessionmaker(), UploadSAPResults).removewhere(True)

    def proc_UpActCountSprsheet_00CopySpreadsheet(self) -> str:
        return self.btnChooseFile.getFileChosen()

    def proc_UpActCountSprsheet_01ReadSheet(self, fName: str) -> None:
        self.showUpdateStatus("Reading Count Entry Spreadsheet...")

        NOTdbFld_flags = ['**NOTdbFld**',]

        wb = load_workbook(filename=fName, read_only=True)
        CountSprshtDateEpoch = wb.epoch
        if 'Counts' in wb:
            ws = wb['Counts']
        else:
            self.showUpdateStatus("Error: This workbook does not contain a sheet named Counts in the correct format")
            wb.close()
            return
        #endif 'Counts' in wb

        SprshtcolmnNames = ws[1]
        SprshtREQUIREDFLDS = ['Material','CountDate','Counter','LOCATION']     
            # LocationOnly/CTD_QTY_Expr handled separately since at least one must be present and both can be
        SprshtcolmnMap = {}
        Sprsht_SSName_TableName_map = {
                'CountDate': 'CountDate',
                'Counter': 'Counter',
                'LOCATION': 'LOCATION',
                'org_id': 'org_id',
                'Material': 'Material',
                'LocationOnly': 'LocationOnly',
                'CTD_QTY_Expr': 'CTD_QTY_Expr',
                'Typ Cntner Qty': 'TypicalContainerQty',
                'Typ Plt Qty': 'TypicalPalletQty',
                'Notes': 'Notes',
                'PKGID_Desc': 'PKGID_Desc',
                'TAGQTY': 'TAGQTY',
                'Poss Not Rcvd': 'FLAG_PossiblyNotRecieved',
                'Mvmt Dur Ct': 'FLAG_MovementDuringCount',
                'WICSignore': NOTdbFld_flags[0],
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

        SprshtRowNum=1
        nRowsAdded = 0
        nRowsNoMaterial = 0
        nRowsErrors = 0

        intrval_announce = min(100, int(max(1, ws.max_row // 10)))
        for row in ws.iter_rows(min_row=SprshtRowNum+1, values_only=True):
            SprshtRowNum += 1
            if SprshtRowNum % intrval_announce == 0:
                self.showUpdateStatus(f"Reading Spreadsheet ... record {SprshtRowNum} of {ws.max_row}", SprshtRowNum, ws.max_row)

            ignoreline = ( ( (NOTdbFld_flags[0] in SprshtcolmnMap) and (row[SprshtcolmnMap[NOTdbFld_flags[0]]]) )
                        or (row[SprshtcolmnMap['Material']] is None)
                        )
            if not ignoreline:
                matlnum = self.cleanupfld('Material', row[SprshtcolmnMap['Material']])['cleanval']
                # if no org given, check that Material unique.
                if Sprsht_SSName_TableName_map['org_id'] not in SprshtcolmnMap:
                    spshtorg = None
                else:
                    spshtorg = self.cleanupfld('org_id', row[SprshtcolmnMap['org_id']])['cleanval']
                matlorglist = Repository(get_app_sessionmaker(), MaterialList).get_all(MaterialList.Material==matlnum)
                MatlKount = len(matlorglist)
                MatObj = None
                err_already_handled = False
                if MatlKount == 1:
                    MatObj = matlorglist[0]
                    spshtorg = MatObj.org_id
                if MatlKount > 1:
                    if spshtorg is None:
                        r = UploadSAPResults(
                            errState = 'error',
                            errmsg = f"{matlnum} in multiple org_id's {tuple(matlorglist)}, but no org_id given", 
                            rowNum = SprshtRowNum
                            )
                        Repository(get_app_sessionmaker(), UploadSAPResults).add(r)
                        nRowsErrors += 1
                        err_already_handled = True
                    else:
                        for mat in matlorglist:
                            if mat.org_id == spshtorg:
                                MatObj = mat
                                break
                    if MatObj is None and not err_already_handled:
                        r = UploadSAPResults(
                            errState = 'error',
                            errmsg = f"{matlnum} in in multiple org_id's {tuple(matlorglist)}, but org_id given ({spshtorg}) is not one of them", 
                            rowNum = SprshtRowNum
                            )
                        Repository(get_app_sessionmaker(), UploadSAPResults).add(r)
                        nRowsErrors += 1
                        err_already_handled = True
                    #endif spshtorg is None
                #endif MatKount > 1

                if not MatObj:
                    if not err_already_handled:
                        nRowsErrors += 1
                        r = UploadSAPResults(
                            errState = 'error',
                            errmsg = f'either {matlnum} does not exist in MaterialList or incorrect org_id ({str(spshtorg)}) given', 
                            rowNum = SprshtRowNum
                            )
                        Repository(get_app_sessionmaker(), UploadSAPResults).add(r)
                else:
                    rowErrs = False
                    requiredFields = {reqFld: False for reqFld in SprshtREQUIREDFLDS}
                    requiredFields['Both LocationOnly and CTD_QTY'] = False

                    MatChanged = False
                    SRec = ActualCounts()
                    for fldName, colNum in SprshtcolmnMap.items():
                        if fldName in NOTdbFld_flags: continue
                        # check/correct problematic data types
                        usefld, V = self.cleanupfld(fldName, row[colNum], CountSprshtDateEpoch=CountSprshtDateEpoch).values()
                        if (V is not None):
                            if usefld:
                                if   fldName == 'CountDate': 
                                    setattr(SRec, fldName, V) 
                                    requiredFields['CountDate'] = True
                                elif fldName == 'Material': 
                                    setattr(SRec, fldName, MatObj)
                                    requiredFields['Material'] = True
                                elif fldName == 'Counter': 
                                    setattr(SRec, fldName, V)
                                    requiredFields['Counter'] = True
                                elif fldName == 'LOCATION': 
                                    setattr(SRec, fldName, V)
                                    requiredFields['LOCATION'] = True
                                elif fldName == 'LocationOnly': 
                                    setattr(SRec, fldName, True if V else False)
                                    requiredFields['Both LocationOnly and CTD_QTY'] = True
                                elif fldName == 'CTD_QTY_Expr': 
                                    setattr(SRec, fldName, V)
                                    requiredFields['Both LocationOnly and CTD_QTY'] = True
                                elif fldName == 'TypicalContainerQty' \
                                or fldName == 'TypicalPalletQty':
                                    if V == '' or V == None: V = 0
                                    if V != 0 and V != getattr(MatObj,fldName,0): 
                                        setattr(MatObj, fldName, V)
                                        MatChanged = True
                                else:
                                    if hasattr(SRec, fldName): setattr(SRec, fldName, V)
                                # endif fldname
                            else:
                                if fldName!='CTD_QTY_Expr':
                                    # we have to suspend judgement on CTD_QTY_Expr until last, because this could be a LocationOnly count
                                    rowErrs = True
                                    r = UploadSAPResults(
                                        errState = 'error',
                                        errmsg = f'{str(V)} is invalid for {fldName}', 
                                        rowNum = SprshtRowNum
                                        )
                                    Repository(get_app_sessionmaker(), UploadSAPResults).add(r)
                            #endif usefld
                        #endif (V is not None)
                    # for each column
                    
                    # now we determine if one of LocationOnly or CTD_QTY was given
                    if not requiredFields['Both LocationOnly and CTD_QTY']:
                        fldName = 'CTD_QTY_Expr'
                        V = row[SprshtcolmnMap[fldName]]
                        rowErrs = True
                        r = UploadSAPResults(
                            errState = 'error',
                            errmsg = f'record is not marked LocationOnly and {str(V)} is invalid for {fldName}', 
                            rowNum = SprshtRowNum
                            )
                        Repository(get_app_sessionmaker(), UploadSAPResults).add(r)

                    # are all required fields present?
                    AllRequiredPresent = True
                    for keyname, Prsnt in requiredFields.items():
                        AllRequiredPresent = AllRequiredPresent and Prsnt
                        if not Prsnt:
                            rowErrs = True
                            r = UploadSAPResults(
                                errState = 'error',
                                errmsg = f'{keyname} missing', 
                                rowNum = SprshtRowNum
                                )
                            Repository(get_app_sessionmaker(), UploadSAPResults).add(r)
                    # endfor requiredFields

                    if not rowErrs:
                        Repository(get_app_sessionmaker(), ActualCounts).add(SRec)
                        if MatChanged: Repository(get_app_sessionmaker(), MaterialList).update(MatObj)
                        resultString = str(SRec)
                        resultString += ' / LOCATION ONLY'  if SRec.LocationOnly else f' / Qty= {SRec.CTD_QTY_Expr}'
                        resultString += ' (Typ Cont Qty/Typ Plt Qty also changed)' if MatChanged else ''
                        r = UploadSAPResults(
                            errState = 'success',
                            errmsg = resultString, 
                            rowNum = SprshtRowNum
                            )
                        Repository(get_app_sessionmaker(), UploadSAPResults).add(r)
                        nRowsAdded += 1
                    else:
                        nRowsErrors += 1
                    #endif not rowErrs
                # endif MatObj/not MatObj
            else:
                nRowsNoMaterial += 1
            #endif not ignoreline
        # endfor row in ws.iter_rows

        r = UploadSAPResults(
            errState = 'nRowsTotal',
            errmsg = '', 
            rowNum = SprshtRowNum
            )
        Repository(get_app_sessionmaker(), UploadSAPResults).add(r)
        r = UploadSAPResults(
            errState = 'nRowsAdded',
            errmsg = '', 
            rowNum = nRowsAdded
            )
        Repository(get_app_sessionmaker(), UploadSAPResults).add(r)
        r = UploadSAPResults(
            errState = 'nRowsErrors',
            errmsg = '', 
            rowNum = nRowsErrors
            )
        Repository(get_app_sessionmaker(), UploadSAPResults).add(r)
        r = UploadSAPResults(
            errState = 'nRowsIgnored',
            errmsg = '', 
            rowNum = nRowsNoMaterial
            )
        Repository(get_app_sessionmaker(), UploadSAPResults).add(r)

        # close and kill temp files
        wb.close()
        
        # self.done_UpActCountSprsheet_01ReadSheet()    # caller will do this
    def done_UpActCountSprsheet_01ReadSheet(self):
        self.showUpdateStatus("Finished Reading Count Entry Spreadsheet.")
        self.proc_UpActCountSprsheet_99_FinalProc()
        #endif stateocde != 'fatalerr'

    def proc_UpActCountSprsheet_99_FinalProc(self) -> None:
        self.showUpdateStatus("Finished Processing Count Entry Spreadsheet...")

    def proc_UpActCountSprsheet_99_Cleanup(self) -> None:
        # delete the temporary table
        Repository(get_app_sessionmaker(), UploadSAPResults).removewhere(True)

# UploadActCountSprsht
