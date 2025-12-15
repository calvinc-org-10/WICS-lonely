# pylint: disable=f-string-without-interpolation

from typing import (Any, )
from datetime import datetime

from PySide6.QtCore import (
    Slot, Signal,
    QMimeData, QUrl, 
    )
from PySide6.QtGui import (
    QDragEnterEvent, QDropEvent, 
    )
from PySide6.QtWidgets import (
    QWidget, 
    QPushButton, QLabel, QHBoxLayout, QFileDialog,
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
            
