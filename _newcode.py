from typing import (Any, )

from PySide6.QtCore import (
    Qt, Slot, 
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

from qtawesome import icon

from calvincTools.utils import (cSimpleRecordForm, )

from app.database import (
    get_app_sessionmaker, 
    Repository 
    )
from app.models import (
    tmpMaterialListUpdate, 
    )



class cFileSelectWidget(QWidget):
    """A QPushButton that accepts file drops and opens a QFileDialog
    with the dropped file pre-selected.
    """
    _btnChooseFile: QPushButton = QPushButton()
    _lblFileChosen: QLabel = QLabel("No file chosen")
    
    def __init__(self, btnIcon=None, btnText="Pick or Drop File Here", *args, **kwargs):
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
        btnChooseFile = cFileSelectWidget(btnText="Choose Spreadsheet File")
        btnChooseFile.clicked.connect(self.chooseFile)
        chooseFileLayout.addWidget(lblChooseFileLabel, 0, 0)
        chooseFileLayout.addWidget(btnChooseFile, 1, 0)
        
        PhaseWidget = QWidget()
        PhaseLayout = QHBoxLayout(PhaseWidget)
        lblShowPhaseTitle = QLabel("Phase:")
        lblShowPhase = QLabel("No file chosen")
        PhaseLayout.addWidget(lblShowPhaseTitle)
        PhaseLayout.addWidget(lblShowPhase, alignment=Qt.AlignmentFlag.AlignLeft)
        
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
        
        mainFormPage.addWidget(chooseFileWidget, 0, 0)
        mainFormPage.addWidget(PhaseWidget, 2, 0)
        mainFormPage.addWidget(grpbxUpdtOptions, 0, 1, 2, 1)
        mainFormPage.addWidget(chkDoNotDelete, 2, 1)
        
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
        return
    def _handleActionButton(self, action: str) -> None:
        return super()._handleActionButton(action)
    
    def initialdisplay(self):
        self.showNewRecordFlag()
    
    def isNewRecord(self) -> bool:
        return False
    
    @Slot()
    def chooseFile(self):
        # TODO: Implement file chooser logic
        print("Choose File button clicked")
        pass
    
    @Slot()
    def uploadFile(self):
        # TODO: Implement file upload logic
        pass
    
    @Slot()
    def closeForm(self):
        # TODO: Implement close form logic
        pass
    

