
from PySide6.QtCore import (
    Slot, 
    QMimeData, QUrl, 
    )
from PySide6.QtGui import (
    QDragEnterEvent, QDropEvent, 
    QDesktopServices, QIcon, 
    )
from PySide6.QtWidgets import (
    QBoxLayout,
    QWidget, 
    QPushButton, QLabel, QCheckBox,
    QGroupBox, 
    QGridLayout, QHBoxLayout, QVBoxLayout, QTabWidget,
    QFileDialog,
    )

from calvincTools.utils import (cSimpleRecordForm, )

from app.database import (
    get_app_sessionmaker, 
    Repository 
    )
from app.models import (
    tmpMaterialListUpdate, 
    )



class cFileDropButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 1. Essential: Tell the widget it accepts drops
        self.setAcceptDrops(True)
        self.setText("Drop File Here")
    # __init__

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

    def open_file_dialog_with_file(self, file_path: str):
        """Opens a QFileDialog pre-selecting the dropped file."""
        
        # Determine the directory and file name
        from PySide6.QtCore import QFileInfo
        file_info = QFileInfo(file_path)
        directory = file_info.dir().path()
        file_name = file_info.fileName()

        # You can use getOpenFileName to open the dialog
        # The third argument sets the initial directory
        # The fourth argument sets the filter (e.g., "All Files (*)")
        selected_file, _ = QFileDialog.getOpenFileName(
            self,                               # Parent
            "File Dropped! Verify Selection",    # Dialog Title
            directory,                           # Initial Directory
            "All Files (*)"                      # Filter
        )

        # QFileDialog.getOpenFileName does not automatically pre-select
        # the file name when given only a directory. 
        # To truly pre-select, the path needs to be passed, but the dialog 
        # needs to be *aware* of it. A simple solution is often to just
        # show the user the path they dropped and confirm.
        
        # A workaround to truly pre-select the file in some systems/dialog styles:
        selected_file, _ = QFileDialog.getOpenFileName(
            self, "File Dropped! Verify Selection", file_path, "All Files (*)"
        )

        if selected_file:
            print(f"User confirmed selection: {selected_file}")
        else:
            print("Dialog closed without confirming the selection.")
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
        btnChooseFile = cFileDropButton("Choose Spreadsheet File")
        btnChooseFile.clicked.connect(self.chooseFile)
        lblFileChosen = QLabel("No file chosen")
        chooseFileLayout.addWidget(lblChooseFileLabel, 0, 0, 1, 2)
        chooseFileLayout.addWidget(btnChooseFile, 1, 0)
        chooseFileLayout.addWidget(lblFileChosen, 1, 1)
        
        PhaseWidget = QWidget()
        PhaseLayout = QHBoxLayout(PhaseWidget)
        PhaseLayout.setContentsMargins(0, 0, 0, 0)
        lblShowPhaseTitle = QLabel("Phase:")
        lblShowPhase = QLabel("No file chosen")
        PhaseLayout.addWidget(lblShowPhaseTitle)
        PhaseLayout.addWidget(lblShowPhase)
        
        dict_chkUpdtOption = {}
        dict_chkUpdtOption['Desc'] = QCheckBox("Description")
        dict_chkUpdtOption['SAPMatlType'] = QCheckBox("SAP Material Type")
        dict_chkUpdtOption['SAPMatlGroup'] = QCheckBox("SAP Material Group")
        dict_chkUpdtOption['SAPMfr'] = QCheckBox("SAP Manufacturer")
        dict_chkUpdtOption['SAPMPN'] = QCheckBox("SAP Manufacturer Part Number")
        dict_chkUpdtOption['SAPABC'] = QCheckBox("SAP ABC Designation")
        dict_chkUpdtOption['Price'] = QCheckBox("Price, Price Unit and Currency")
        grpbxUpdtOptions = QGroupBox('Update Existing Material Records for these Fields:')
        layoutUpdtOptions = QVBoxLayout(grpbxUpdtOptions)
        for chk in dict_chkUpdtOption.values():
            layoutUpdtOptions.addWidget(chk)
        
        
        chkDoNotDelete = QCheckBox("Do Not Delete Records Not in Spreadsheet")
        
        btnUploadFile = QPushButton("Upload Data from Spreadsheet")
        btnUploadFile.clicked.connect(self.uploadFile)
        btnClose = QPushButton("Close Form")
        btnClose.clicked.connect(self.closeForm)
        
        mainFormPage.addWidget(chooseFileWidget, 0, 0)
        mainFormPage.addWidget(PhaseWidget, 2, 0)
        mainFormPage.addWidget(grpbxUpdtOptions, 0, 1, 2, 1)
        mainFormPage.addWidget(chkDoNotDelete, 2, 1)
        
    # _placeFields
    
    def _addActionButtons(self, layoutButtons: QBoxLayout | None = None, layoutHorizontal: bool = True, NavActions: list[tuple[str, QIcon]] | None = None, CRUDActions: list[tuple[str, QIcon]] | None = None) -> None:
        # no action buttons here
        return
    
    def initialdisplay(self):
        self.showNewRecordFlag()
    
    def isNewRecord(self) -> bool:
        return False
    
    @Slot()
    def chooseFile(self):
        # TODO: Implement file chooser logic
        pass
    
    @Slot()
    def uploadFile(self):
        # TODO: Implement file upload logic
        pass
    
    @Slot()
    def closeForm(self):
        # TODO: Implement close form logic
        pass
    

