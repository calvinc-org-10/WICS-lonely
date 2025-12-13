# pylint: disable=f-string-without-interpolation

import re as regex
from typing import (Any, )
from datetime import datetime

from PySide6.QtCore import (
    Qt, Slot, 
    QMimeData, QUrl, 
    )
from PySide6.QtGui import (
    QDragEnterEvent, QDropEvent, 
    QIcon, 
    )
from PySide6.QtWidgets import (
    QBoxLayout,
    QWidget, 
    QPushButton, QLabel, QCheckBox, QProgressBar, 
    QGroupBox, 
    QGridLayout, QHBoxLayout, QVBoxLayout, QTabWidget,
    QFileDialog,
    )

from sqlalchemy import (delete, update, select, insert, func, literal_column, text, )

from openpyxl import load_workbook

from qtawesome import icon

from calvincTools.utils import (cSimpleRecordForm, )

from app.database import (
    get_app_sessionmaker, get_app_session,
    Repository 
    )
from app.models import (
    tmpMaterialListUpdate, SAPPlants_org, MaterialList,
    ActualCounts, CountSchedule, SAP_SOHRecs,
    )


class cFileSelectWidget(QWidget):
    """A QPushButton that accepts file drops and opens a QFileDialog
    with the dropped file pre-selected.
    """
    _btnChooseFile: QPushButton = QPushButton()
    _lblFileChosen: QLabel = QLabel("No file chosen")
    
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
            "All Files (*)",                     # Filter
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
            # Here you can handle the selected file as needed
            # print(f"User confirmed selection: {selected_file}")
        else:
            pass
            # print("Dialog closed without confirming the selection.")
        #endif selected_file
    # open_file_dialog_with_file
# cFileDropButton
            
class UpdateMatlListfromSAP(cSimpleRecordForm):
    _ORMmodel = tmpMaterialListUpdate
    _formname = "Update Material List from SAP MM60 or ZMSQV001 Spreadsheet"
    _ssnmaker = get_app_sessionmaker()
    fieldDefs = {
        # no fields to edit, everything manually handled
    }
    
    # __init__ inherited from cSimpleRecordForm
    
    @Slot()
    def _placeFields(self, layoutFormPages: QTabWidget, layoutFormFixedTop: QGridLayout | None, layoutFormFixedBottom: QGridLayout | None, lookupsAllowed: bool = True) -> None:
        # return super()._placeFields(layoutFormPages, layoutFormFixedTop, layoutFormFixedBottom, lookupsAllowed)
        
        mainFormPage = self.FormPage(0)
        assert isinstance(mainFormPage, QGridLayout)
        
        chooseFileWidget = QWidget()
        chooseFileLayout = QGridLayout(chooseFileWidget)
        lblChooseFileLabel = QLabel("Choose or Drop SAP Material List Spreadsheet File:")
        self.btnChooseFile = cFileSelectWidget(btnText="Choose Spreadsheet File")
        self.btnChooseFile.clicked.connect(self.chooseFile)
        chooseFileLayout.addWidget(lblChooseFileLabel, 0, 0)
        chooseFileLayout.addWidget(self.btnChooseFile, 1, 0)
        
        # PhaseWidget = QWidget()
        # PhaseLayout = QHBoxLayout(PhaseWidget)
        # lblShowPhaseTitle = QLabel("Phase:")
        # lblShowPhase = QLabel("No file chosen")
        # PhaseLayout.addWidget(lblShowPhaseTitle)
        # PhaseLayout.addWidget(lblShowPhase, alignment=Qt.AlignmentFlag.AlignLeft)
        
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
        
        self.chkDoNotDelete = QCheckBox("Do Not Delete Records Not in Spreadsheet")
        
        mainFormPage.addWidget(chooseFileWidget, 0, 0)
        # mainFormPage.addWidget(PhaseWidget, 2, 0)
        mainFormPage.addWidget(grpbxUpdtOptions, 0, 1, 2, 1)
        mainFormPage.addWidget(self.chkDoNotDelete, 2, 1)
        
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

    def initialdisplay(self):
        self.showNewRecordFlag()
        self.showUpdateStatus("")
    
    def isNewRecord(self) -> bool:
        return False
    
    @Slot()
    def chooseFile(self):
        # TODO: Implement file chooser logic
        print("Choose File button clicked")
    
    @Slot()
    def uploadFile(self):
        reqid = 'unique-request-id'  # Generate or obtain a unique request ID

        # disable most of the form while processing
        
        self.proc_MatlListSAPSprsheet_00InitUMLasync_comm(reqid)

        # UMLSSName = self.proc_MatlListSAPSprsheet_00CopyUMLSpreadsheet(reqid)     # needed in a client-server environment, not for standalone
        UMLSSName = self.btnChooseFile.getFileChosen()
        self.proc_MatlListSAPSprsheet_01ReadSpreadsheet(reqid, UMLSSName)
        self.done_MatlListSAPSprsheet_01ReadSpreadsheet(reqid)      # this trigger most of the rest of the processing chain
        
        # present results to user
        
        self.proc_MatlListSAPSprsheet_99_Cleanup(reqid)
        self.closeForm()
        
    # uploadFile

    @Slot()
    def closeForm(self):
        # TODO: Implement close form logic
        pass

    def changeInternalVarField(self, wdgt, intVarField: str, wdgt_value: Any) -> None:
        return

    def proc_MatlListSAPSprsheet_00InitUMLasync_comm(self, reqid):
        self.showUpdateStatus('Initializing ...')
    # proc_MatlListSAPSprsheet_00InitUMLasync_comm

    # not needed in standalone version
    # def proc_MatlListSAPSprsheet_00CopyUMLSpreadsheet(self, reqid):
    #     ...

    def proc_MatlListSAPSprsheet_01ReadSpreadsheet(self, reqid, fName):
        # tmpMaterialListUpdate.objects.using(dbToUse).all().delete() - from client-server Django version
        # Repository.removeRecs_withcondition not implemented yet
        # So we do it manually here
        Repository(get_app_sessionmaker(), tmpMaterialListUpdate).removewhere(lambda rec: True)
        # with get_app_session() as session:
        #     stmt = delete(tmpMaterialListUpdate)
        #     session.execute(stmt)
        #     session.commit()
        # endwith

        self.showUpdateStatus('Reading Spreadsheet')

        wb = load_workbook(filename=fName, read_only=True)
        ws = wb.active
        assert ws is not None, "Failed to load active worksheet from spreadsheet."
        SAPcolmnNames = ws[1]
        SAPcol = {'Plant':None,'Material': None}
        SAP_SSName_TableName_map = {
                'Material': 'Material',
                'Material description': 'Description',
                'Plant': 'Plant', 'Plnt': 'Plant',
                'Material type': 'SAPMaterialType',  'MTyp': 'SAPMaterialType',
                'Material Group': 'SAPMaterialGroup', 'Matl Group': 'SAPMaterialGroup',
                'Manufact.': 'SAPManuf', 
                'MPN': 'SAPMPN', 
                'ABC': 'SAPABC', 
                'Price': 'Price', 'Standard price': 'Price',
                'Price unit': 'PriceUnit', 'per': 'PriceUnit',
                'Currency':'Currency',
                }
        dict_SAPPlants = {rec.SAPPlant: rec.org_id  for rec in Repository(get_app_sessionmaker(), SAPPlants_org).get_all()}  # preload SAPPlants_org cache
        for col in SAPcolmnNames:
            if col.value in SAP_SSName_TableName_map:
                SAPcol[SAP_SSName_TableName_map[col.value]] = col.column - 1 # type: ignore
        if (SAPcol['Material'] == None or SAPcol['Plant'] == None):
            self.showUpdateStatus('SAP Spreadsheet has bad header row. Plant and/or Material is missing.  See Calvin to fix this.', 0, -1)

            wb.close()
            return      # need to do more than this, but for now, just exit
        # endif bad header row

        numrows = ws.max_row
        nRows = 0
        intrval_announce = min(100, int(max(1, numrows // 10)))
        for row in ws.iter_rows(min_row=2, values_only=True):
            nRows += 1
            if nRows % intrval_announce == 0:
                self.showUpdateStatus(f'Reading Spreadsheet ... record {nRows} of {numrows}', nRows, numrows)

            if row[SAPcol['Material']]==None: MatNum = ''
            else: MatNum = row[SAPcol['Material']]
            validTmpRec = False
            ## create a blank tmpMaterialListUpdate record,
            newrec = tmpMaterialListUpdate()
            if regex.match(".*[\n\t\xA0].*",str(MatNum)):
                validTmpRec = True
                ## refuse to work with special chars embedded in the MatNum
                newrec.recStatus = 'err-MatlNum'
                newrec.errmsg = f'error: {MatNum!a} is an unusable part number. It contains invalid characters and cannot be added to WICS'
            elif len(str(MatNum)):
                validTmpRec = True
                newrec.org_id = dict_SAPPlants.get(str(row[SAPcol['Plant']]), 0)
            # endif invalid Material
            if validTmpRec:
                ## populate by looping through SAPcol,
                ## then save
                for dbColName, ssColNum in SAPcol.items():
                    setattr(newrec,dbColName,row[ssColNum]) # type: ignore
                Repository(get_app_sessionmaker(), tmpMaterialListUpdate).add(newrec)
        # endfor

        wb.close()
        return      # need to do more than this, but for now, just exit

    # proc_MatlListSAPSprsheet_01ReadSpreadsheet

    def done_MatlListSAPSprsheet_01ReadSpreadsheet(self, reqid):
        # handle fatal err if occurred during reading
        # statecode = async_comm.objects.using(dbToUse).get(pk=reqid).statecode
        # if statecode != 'fatalerr':
        #     set_async_comm_state(
        #         dbToUse,
        #         reqid,
        #         statecode = 'done-rdng-sprsht',
        #         statetext = f'Finished Reading Spreadsheet',
        #         )
        
        self.proc_MatlListSAPSprsheet_02_identifyexistingMaterial(reqid)
    # done_MatlListSAPSprsheet_01ReadSpreadsheet

    def proc_MatlListSAPSprsheet_02_identifyexistingMaterial(self, reqid):
        self.showUpdateStatus('Identifying Existing Materials ...')
        # UpdMaterialLinkSQL = 'UPDATE WICS_tmpmateriallistupdate, (select id, org_id, Material from WICS_materiallist) as MasterMaterials'
        # UpdMaterialLinkSQL += ' set WICS_tmpmateriallistupdate.MaterialLink_id = MasterMaterials.id, '
        # UpdMaterialLinkSQL += "     WICS_tmpmateriallistupdate.recStatus = 'FOUND' "
        # UpdMaterialLinkSQL += ' where WICS_tmpmateriallistupdate.org_id = MasterMaterials.org_id '
        # UpdMaterialLinkSQL += '   and WICS_tmpmateriallistupdate.Material = MasterMaterials.Material '
        # with connections[dbToUse].cursor() as cursor:
        #     cursor.execute(UpdMaterialLinkSQL)
        # this is a little too wild for the Repository pattern, so we do it manually here
        with get_app_session() as session:
            stmt = (
                update(tmpMaterialListUpdate)
                .values(
                    MaterialLink_id=select(MaterialList.id)
                        .where(
                            tmpMaterialListUpdate.org_id == MaterialList.org_id,
                            tmpMaterialListUpdate.Material == MaterialList.Material
                        )
                        .correlate(tmpMaterialListUpdate)
                        .scalar_subquery(),
                    recStatus='FOUND'
                )
                .where(
                    select(MaterialList.id)
                        .where(
                            tmpMaterialListUpdate.org_id == MaterialList.org_id,
                            tmpMaterialListUpdate.Material == MaterialList.Material
                        )
                        .correlate(tmpMaterialListUpdate)
                        .exists()
                )
            )

            session.execute(stmt)
            session.commit()
        # endwith

        self.showUpdateStatus('Identifying WICS Materials no longer in SAP MM60 Materials')
        # MustKeepMatlsSelCond = ''
        # MustKeepMatlsSelCond += ' AND ' if MustKeepMatlsSelCond else ''
        # MustKeepMatlsSelCond += 'id NOT IN (SELECT DISTINCT tmucopy.MaterialLink_id AS Material_id FROM WICS_tmpmateriallistupdate tmucopy WHERE tmucopy.MaterialLink_id IS NOT NULL)'
        # MustKeepMatlsSelCond += ' AND ' if MustKeepMatlsSelCond else ''
        # MustKeepMatlsSelCond += 'id NOT IN (SELECT DISTINCT Material_id FROM WICS_actualcounts)'
        # MustKeepMatlsSelCond += ' AND ' if MustKeepMatlsSelCond else ''
        # MustKeepMatlsSelCond += 'id NOT IN (SELECT DISTINCT Material_id FROM WICS_countschedule)'
        # MustKeepMatlsSelCond += ' AND ' if MustKeepMatlsSelCond else ''
        # MustKeepMatlsSelCond += 'id NOT IN (SELECT DISTINCT Material_id FROM WICS_sap_sohrecs)'

        # DeleteMatlsSelectSQL = "INSERT INTO WICS_tmpmateriallistupdate (recStatus, delMaterialLink, MaterialLink_id, org_id, Material, Description, Plant "
        # DeleteMatlsSelectSQL += ", SAPMaterialType, SAPMaterialGroup, Currency  ) "    # these can go once I set null=True on these fields
        # DeleteMatlsSelectSQL += " SELECT  concat('DEL ',FORMAT(id,0)), id, NULL, org_id, Material, Description, Plant "
        # DeleteMatlsSelectSQL += ", SAPMaterialType, SAPMaterialGroup, Currency  "    # these can go once I set null=True on these fields
        # DeleteMatlsSelectSQL += " FROM WICS_materiallist"
        # DeleteMatlsSelectSQL += f" WHERE ({MustKeepMatlsSelCond})"
        with get_app_session() as session:
            # Build the NOT IN subqueries
            not_in_tmp = select(tmpMaterialListUpdate.MaterialLink).where(
                tmpMaterialListUpdate.MaterialLink.is_not(None)
            ).distinct()

            not_in_actual = select(ActualCounts.Material_id).distinct()
            not_in_schedule = select(CountSchedule.Material_id).distinct()
            not_in_sap = select(SAP_SOHRecs.Material_id).distinct()

            # Build the SELECT statement for materials to delete
            select_stmt = select(
                ('DEL ' + func.format(MaterialList.id, 0)).label('recStatus'),
                MaterialList.id.label('delMaterialLink'),
                literal_column('NULL').label('MaterialLink'),
                MaterialList.org_id,
                MaterialList.Material,
                MaterialList.Description,
                MaterialList.Plant,
                MaterialList.SAPMaterialType,
                MaterialList.SAPMaterialGroup,
                MaterialList.Currency
            ).where(
                MaterialList.id.not_in(not_in_tmp),
                MaterialList.id.not_in(not_in_actual),
                MaterialList.id.not_in(not_in_schedule),
                MaterialList.id.not_in(not_in_sap)
            )

            # INSERT ... SELECT
            stmt = insert(tmpMaterialListUpdate).from_select(
                ['recStatus', 'delMaterialLink', 'MaterialLink', 'org_id', 'Material',
                'Description', 'Plant', 'SAPMaterialType', 'SAPMaterialGroup', 'Currency'],
                select_stmt
            )

            session.execute(stmt)
            session.commit()

        self.showUpdateStatus('Identifying SAP MM60 Materials new to WICS')
        # MarkAddMatlsSelectSQL = "UPDATE WICS_tmpmateriallistupdate"
        # MarkAddMatlsSelectSQL += " SET recStatus = 'ADD'"
        # MarkAddMatlsSelectSQL += " WHERE (MaterialLink_id IS NULL) AND (recStatus is NULL)"
        Repository(get_app_sessionmaker(), tmpMaterialListUpdate).updatewhere(
            lambda rec: rec.MaterialLink_id is None and (rec.recStatus is None),
            {'recStatus': 'ADD'}
        )

        self.done_MatlListSAPSprsheet_02_identifyexistingMaterial(reqid)
    # proc_MatlListSAPSprsheet_02_identifyexistingMaterial
    def done_MatlListSAPSprsheet_02_identifyexistingMaterial(self, reqid):
        self.showUpdateStatus('Finished Linking SAP MM60 list to existing WICS Materials ...')   
        
        self.proc_MatlListSAPSprsheet_03_UpdateExistingRecs(reqid)
    # done_MatlListSAPSprsheet_02_identifyexistingMaterial

    def proc_MatlListSAPSprsheet_03_UpdateExistingRecs(self, reqid):
        def setstate_MatlListSAPSprsheet_03_UpdateExistingRecs(fldName):
            self.showUpdateStatus(f'Updating _{fldName}_ Field in Existing Records')
        # setstate_MatlListSAPSprsheet_03_UpdateExistingRecs

        setstate_MatlListSAPSprsheet_03_UpdateExistingRecs('')

        # (Form Name, db fld Name, zero/blank value)
        # NOTE: SAPPrice updates three fields: Price, PriceUnit, Currency - that's why I don't use a simple dict here
        FormTodbFld_map = [
            ('Description','Description','""'),
            ('SAPMatlType','SAPMaterialType','""'),
            ('SAPMatlGroup','SAPMaterialGroup','""'),
            ('SAPManuf','SAPManuf','""'),
            ('SAPMPN','SAPMPN','""'),
            ('SAPABC','SAPABC','""'),
            ('SAPPrice','Price',0),
            ('SAPPrice','PriceUnit',0),
            ('SAPPrice','Currency','""'),
        ]

        UpdateExistFldSet = {
            key for key, chkbox in self.dict_chkUpdtOption.items() 
                if chkbox.isChecked()
        }

        if UpdateExistFldSet:
            MatlList_tbl = MaterialList.__tablename__
            tmpMatlListUpd_tbl = tmpMaterialListUpdate.__tablename__
            for formName, dbName, zeroVal in FormTodbFld_map:
                if formName in UpdateExistFldSet:
                    setstate_MatlListSAPSprsheet_03_UpdateExistingRecs(dbName)
                    # UPDATE this field
                    # for SQLite, the SQLAlchemy way is complex, so we do it manually here
                    UpdSQLSetStmt = f"{MatlList_tbl}.{dbName}={tmpMatlListUpd_tbl}.{dbName}"
                    UpdSQLWhereStmt = f"(IFNULL({tmpMatlListUpd_tbl}.{dbName},{zeroVal}) != {zeroVal} AND IFNULL({MatlList_tbl}.{dbName},{zeroVal})!=IFNULL({tmpMatlListUpd_tbl}.{dbName},{zeroVal}))"

                    UpdSQLStmt = f"UPDATE {MatlList_tbl}"
                    UpdSQLStmt += f" SET {UpdSQLSetStmt}"
                    UpdSQLStmt += f" FROM {tmpMatlListUpd_tbl}"
                    UpdSQLStmt += f" WHERE ({tmpMatlListUpd_tbl}.MaterialLink_id={MatlList_tbl}.id) AND {UpdSQLWhereStmt}"
                    UpdSQLStmt += ";"
                    
                    with get_app_session() as session:
                        session.execute(text(UpdSQLStmt))
                        session.commit()
                #endif formName in UpdateExistFldList
            #endfor
        # endif UpdateExistFldList not empty
        self.done_MatlListSAPSprsheet_03_UpdateExistingRecs(reqid)
    # proc_MatlListSAPSprsheet_03_UpdateExistingRecs
    def done_MatlListSAPSprsheet_03_UpdateExistingRecs(self, reqid):
        self.showUpdateStatus('Finished Updating Existing Records to MM60 values')
        
        self.proc_MatlListSAPSprsheet_04_Remove(reqid)
    # done_MatlListSAPSprsheet_03_UpdateExistingRecs

    def proc_MatlListSAPSprsheet_04_Remove(self, reqid):
        if self.chkDoNotDelete.isChecked():
            self.done_MatlListSAPSprsheet_04_Remove(reqid)
            return

        self.showUpdateStatus('Removing WICS Materials no longer in SAP MM60 Materials')
        
        # do the Removals
        with get_app_session() as session:
            # SQLAlchemy delete with subquery
            subq = select(tmpMaterialListUpdate.delMaterialLink).where(tmpMaterialListUpdate.recStatus.like('DEL%'))
            stmt = delete(MaterialList).where(MaterialList.id.in_(subq))
            session.execute(stmt)
            session.commit()
            
        self.done_MatlListSAPSprsheet_04_Remove(reqid)
    # proc_MatlListSAPSprsheet_04_Remove
    def done_MatlListSAPSprsheet_04_Remove(self,reqid):
        self.showUpdateStatus('Finished Removing WICS Materials no longer in SAP MM60 Materials')

        self.proc_MatlListSAPSprsheet_04_Add(reqid)
    # done_MatlListSAPSprsheet_04_Remove

    def proc_MatlListSAPSprsheet_04_Add(self, reqid):
        self.showUpdateStatus('Adding New WICS Materials from SAP MM60 Materials')
        
        # do the Additions
        with get_app_session() as session:
             # Select compatible columns from tmp where recStatus is 'ADD'
            select_stmt = select(
                tmpMaterialListUpdate.org_id,
                tmpMaterialListUpdate.Material,
                tmpMaterialListUpdate.Description,
                tmpMaterialListUpdate.Plant,
                tmpMaterialListUpdate.SAPMaterialType,
                tmpMaterialListUpdate.SAPMaterialGroup,
                tmpMaterialListUpdate.SAPManuf,
                tmpMaterialListUpdate.SAPMPN,
                tmpMaterialListUpdate.SAPABC,
                tmpMaterialListUpdate.Price,
                tmpMaterialListUpdate.PriceUnit,
                tmpMaterialListUpdate.Currency
            ).where(
                tmpMaterialListUpdate.recStatus.like('ADD')
            )
            
            # Insert into MaterialList
            stmt = insert(MaterialList).from_select(
                ['org_id', 'Material', 'Description', 'Plant', 
                 'SAPMaterialType', 'SAPMaterialGroup', 'SAPManuf', 
                 'SAPMPN', 'SAPABC', 'Price', 'PriceUnit', 'Currency'],
                select_stmt
            )
            
            session.execute(stmt)
            session.commit()
            
        self.done_MatlListSAPSprsheet_04_Add(reqid)
    # proc_MatlListSAPSprsheet_04_Add
    def done_MatlListSAPSprsheet_04_Add(self, reqid):
        self.showUpdateStatus('Finished Adding WICS Materials from SAP MM60 Materials') 

        self.proc_MatlListSAPSprsheet_99_FinalProc(reqid)
    # done_MatlListSAPSprsheet_04_Add

    def proc_MatlListSAPSprsheet_99_FinalProc(self, reqid):
        self.showUpdateStatus('Finished Processing Spreadsheet')
    # proc_MatlListSAPSprsheet_99_FinalProc

    def proc_MatlListSAPSprsheet_99_Cleanup(self, reqid):   # pylint: disable=unused-argument
        # kill async_comm[reqid] object

        Repository(get_app_sessionmaker(), tmpMaterialListUpdate).removewhere(lambda rec: True)
    # proc_MatlListSAPSprsheet_99_Cleanup
    
# UpdateMatlListfromSAP
