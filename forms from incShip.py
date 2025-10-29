import decimal
from typing import Any, Dict, List, Tuple, NamedTuple
from collections import namedtuple

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect, QSize,
    QTime, QUrl, Qt, Slot)
from PySide6.QtGui import (QBrush, QColor, QColorConstants, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QWidget, QScrollArea, QMessageBox, QInputDialog,
    QGridLayout, QSpacerItem, QVBoxLayout, QHBoxLayout,
    QListView, QListWidget, QColumnView, QListWidgetItem, QTableView, QHeaderView,
    QComboBox, QDateEdit, QFrame, QCheckBox,
    QLabel, QLineEdit, 
    QPushButton,
    QSizePolicy, QTabWidget, QTextEdit,
    )

from django.apps import apps
from django.db.models import Q, Model
from cMenu.utils import cDataList, cDictModel, cComboBoxFromDict, cQRecordsetView

from incShip.models import (
    HBL, ShippingForms, PO, Invoices, Containers, 
    references as refs,
    Origins, Companies, Organizations, FreightTypes,
    QModelContainers, QModelInvoices, 
    QModelrefs, 
    )


_DATE_FORMAT = 'yyyy-MM-dd'

fontFormTitle = QFont()
fontFormTitle.setFamilies([u"Copperplate Gothic"])
fontFormTitle.setPointSize(24)


##########################################################
##########################################################

def pleaseWriteMe(parent, addlmessage):
    msg = QMessageBox(parent)
    msg.setWindowTitle('Please Write Me')
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.setText(f'Calvin needs to get up off his butt and write some code\n{addlmessage}')
    msg.open()

##########################################################
##########################################################

# standard window and related sizes
std_windowsize = QSize(1024,640)
std_popdialogsize=QSize(400,300)

##########################################################
##########################################################

# many, many choices for these tables - construct the choice list only once or spend forever waiting
Nochoice = {'---': None}    # only needed for combo boxes, not datalists
choices_HBL = {rec.pk: str(rec) for rec in HBL.objects.only('pk')}
choices_Inv = {rec.pk: str(rec) for rec in Invoices.objects.only('pk')}
choices_PO  = {rec.pk: str(rec) for rec in PO.objects.only('pk')}
choices_ShFm = {rec.pk: str(rec) for rec in ShippingForms.objects.only('pk')}
choices_Container = {rec.pk: str(rec) for rec in Containers.objects.only('pk')}

class IncShipAppchoiceWidgets:
    class chooseHBL(cDataList):
        def __init__(self, initval = '', parent = None):
            choices = choices_HBL
            super().__init__(choices, initval, parent)
    class chooseInvoice(cDataList):
        def __init__(self, initval = '', parent = None):
            choices = choices_Inv
            super().__init__(choices, initval, parent)
    class choosePO(cDataList):
        def __init__(self, initval = '', parent = None):
            choices = choices_PO
            super().__init__(choices, initval, parent)
    class chooseShipForm(cDataList):
        def __init__(self, initval = '', parent = None):
            choices = choices_ShFm
            super().__init__(choices, initval, parent)
    class chooseContainer(cDataList):
        def __init__(self, initval = '', parent = None):
            choices = choices_Container
            super().__init__(choices, initval, parent)
    class chooseCompany(cComboBoxFromDict):
        def __init__(self, parent = None):
            dict = Nochoice | { str(x): x.pk for x in Companies.objects.all() }
            super().__init__(dict, parent)
    class chooseOrganization(cComboBoxFromDict):
        def __init__(self, parent = None):
            dict = Nochoice | { str(x): x.pk for x in Organizations.objects.all() }
            super().__init__(dict, parent)
    class chooseFreightType(cComboBoxFromDict):
        def __init__(self, parent = None):
            dict = Nochoice | { str(x): x.pk for x in FreightTypes.objects.all() }
            super().__init__(dict, parent)
    class chooseOrigin(cComboBoxFromDict):
        def __init__(self, parent = None):
            dict = Nochoice | { str(x): x.pk for x in Origins.objects.all() }
            super().__init__(dict, parent)
    # Quote choice classes
    class chooseSmOffInvStatus(cComboBoxFromDict):
        def __init__(self, parent = None):
            dict = { x.name: x.value for x in Invoices.SmOffStatusCodes }
            super().__init__(dict, parent)
    class chooserefTable(cComboBoxFromDict):
        def __init__(self, parent = None):
            dict = Nochoice | { x.name: x.value for x in refs.refTblChoices }
            super().__init__(dict, parent)


class HBLForm(QWidget):
    _linkedTables = ['ShippingForms', 'PO', 'Invoices', 'Containers', 'reference_ties']

    currRec:HBL = HBL()
    linkedRecs:Dict[str, Any] = { tbl: None for tbl in _linkedTables}
    formFields:Dict[str, Tuple[QWidget, Any]] = {}

    
    def __init__(self, parent:QWidget = None):
        super().__init__(parent)

        if not self.objectName():
            self.setObjectName(u"Form")
        # self.resize(std_windowsize)
        self.resize(std_windowsize.width(), std_windowsize.height()+150) # this is a temporary fix
        font = QFont()
        font.setPointSize(12)
        self.setFont(font)
        
        self.layoutForm = QVBoxLayout(self)
        
        thisWindowsize = self.size()

        self.layoutwidgetFormHdr = QWidget()
        self.layoutFormHdr = QGridLayout(self.layoutwidgetFormHdr)
        
        self.lblFormName = QLabel(self)
        wdgt = self.lblFormName
        wdgt.setObjectName(u"lblFormName")
        wdgt.setFont(fontFormTitle)
        wdgt.setFrameShape(QFrame.Shape.Panel)
        wdgt.setFrameShadow(QFrame.Shadow.Raised)
        wdgt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        wdgt.setWordWrap(True)
        self.layoutFormHdr.addWidget(wdgt,0,0)
        
        self.gotoHBL = IncShipAppchoiceWidgets.chooseHBL(parent=self)
        wdgt = self.gotoHBL
        wdgt.setObjectName(u"gotoHBL")
        wdgt.setFrame(True)
        wdgt.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        wdgt.setPlaceholderText('Enter a HBL')
        wdgt.setProperty('field', 'id')
        self.formFields['id'] = (wdgt, None)
        wdgt.setEnabled(True)       # shouldn't be necessary
        wdgt.editingFinished.connect(self.getRecordFromGoto)
        self.lblHBLNotFound = QLabel(self)
        wdgtNF = self.lblHBLNotFound
        palette = QPalette()
        brush = QBrush(QColorConstants.Red)
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
        wdgtNF.setPalette(palette)
        self.layoutFormHdr.addWidget(wdgt,1,0)
        self.layoutFormHdr.addWidget(wdgtNF,2,0)

        self.layoutForm.addWidget(self.layoutwidgetFormHdr)
        self.layoutForm.addSpacing(10)

        self.layoutwidgetFormMain = QWidget(self)
        wdgt = self.layoutwidgetFormMain
        wdgt.setObjectName(u"gridLayoutWidget")
        wdgt.setGeometry(QRect(20, 160, thisWindowsize.width()-40, 360))
        self.layoutFormMain = QGridLayout(self.layoutwidgetFormMain)
        self.layoutFormMain.setObjectName(u"layoutForm")
        self.layoutFormMain.setContentsMargins(0, 0, 0, 0)

        self.lblRecID = QLabel(self.layoutwidgetFormMain)
        wdgt = self.lblRecID
        wdgt.setObjectName(u"label_3")
        self.layoutFormMain.addWidget(wdgt, 0, 6)

        self.comboCompany = IncShipAppchoiceWidgets.chooseCompany(self.layoutwidgetFormMain); self.lblCompany = QLabel(self.layoutwidgetFormMain)
        wdgt = self.comboCompany; wdgtlbl = self.lblCompany
        wdgtlbl.setObjectName(u"lblCompany")
        self.layoutFormMain.addWidget(wdgtlbl, 0, 0)
        wdgt.setObjectName(u"comboCompany")
        wdgt.setProperty('field', 'Company')
        self.formFields['Company'] = (wdgt, None)
        wdgt.currentIndexChanged.connect(lambda indx: self.changeField(self.comboCompany))
        self.layoutFormMain.addWidget(wdgt, 1, 0)

        self.lnedHBLNumber = QLineEdit(self.layoutwidgetFormMain); self.lblHBLNumber = QLabel(self.layoutwidgetFormMain)
        wdgt = self.lnedHBLNumber; wdgtlbl = self.lblHBLNumber
        wdgtlbl.setObjectName(u"lblHBLNumber")
        self.layoutFormMain.addWidget(wdgtlbl, 0, 1)
        wdgt.setObjectName(u"lnedHBLNumber")
        wdgt.setProperty('field', 'HBLNumber')
        self.formFields['HBLNumber'] = (wdgt, None)
        #TODO: write Slot to check if HBL exists
        wdgt.editingFinished.connect(lambda: self.changeField(self.lnedHBLNumber))
        self.layoutFormMain.addWidget(wdgt, 1, 1)

        self.comboFreightType = IncShipAppchoiceWidgets.chooseFreightType(self.layoutwidgetFormMain); self.lblFreightType = QLabel(self.layoutwidgetFormMain)
        wdgt = self.comboFreightType; wdgtlbl = self.lblFreightType
        wdgtlbl.setObjectName(u"lblFreightType")
        self.layoutFormMain.addWidget(wdgtlbl, 0, 2)
        wdgt.setObjectName(u"comboFreightType")
        wdgt.setProperty('field', 'FreightType')
        self.formFields['FreightType'] = (wdgt, None)
        wdgt.currentIndexChanged.connect(lambda indx: self.changeField(self.comboFreightType))
        self.layoutFormMain.addWidget(wdgt, 1, 2)

        self.comboOrigin = IncShipAppchoiceWidgets.chooseOrigin(self.layoutwidgetFormMain); self.lblOrigin = QLabel(self.layoutwidgetFormMain)
        wdgt = self.comboOrigin; wdgtlbl = self.lblOrigin
        wdgtlbl.setObjectName(u"lblOrigin")
        self.layoutFormMain.addWidget(wdgtlbl, 0, 3)
        wdgt.setObjectName(u"comboOrigin")
        wdgt.setProperty('field', 'Origin')
        self.formFields['Origin'] = (wdgt, None)
        wdgt.currentIndexChanged.connect(lambda indx: self.changeField(self.comboOrigin))
        self.layoutFormMain.addWidget(wdgt, 1, 3)

        self.lnedtIncoterm = QLineEdit(self.layoutwidgetFormMain); self.lblIncoTerm = QLabel(self.layoutwidgetFormMain)
        wdgt = self.lnedtIncoterm; wdgtlbl = self.lblIncoTerm
        wdgtlbl.setObjectName(u"lblIncoTerm")
        self.layoutFormMain.addWidget(wdgtlbl, 0, 4)
        wdgt.setObjectName(u"lnedtIncoterm")
        wdgt.setProperty('field', 'incoterm')
        self.formFields['incoterm'] = (wdgt, None)
        wdgt.editingFinished.connect(lambda: self.changeField(self.lnedtIncoterm))
        self.layoutFormMain.addWidget(wdgt, 1, 4)

        self.dtedtETA = QDateEdit(self.layoutwidgetFormMain); self.lblETA = QLabel(self.layoutwidgetFormMain)
        wdgt = self.dtedtETA; wdgtlbl = self.lblETA
        wdgtlbl.setObjectName(u"lblETA")
        self.layoutFormMain.addWidget(wdgtlbl, 2, 0)
        wdgt.setObjectName(u"dtedtETA")
        wdgt.setDisplayFormat(_DATE_FORMAT)
        wdgt.setSpecialValueText('---')
        wdgt.setProperty('field', 'ETA')
        self.formFields['ETA'] = (wdgt, None)
        wdgt.userDateChanged.connect(lambda: self.changeField(self.dtedtETA))
        self.layoutFormMain.addWidget(wdgt, 3, 0)

        self.dtedtLFD = QDateEdit(self.layoutwidgetFormMain); self.lblLFD = QLabel(self.layoutwidgetFormMain)
        wdgt = self.dtedtLFD; wdgtlbl = self.lblLFD
        wdgtlbl.setObjectName(u"lblLFD")
        self.layoutFormMain.addWidget(wdgtlbl, 2, 1)
        wdgt.setObjectName(u"dtedtLFD")
        wdgt.setDisplayFormat(_DATE_FORMAT)
        wdgt.setProperty('field', 'LFD')
        self.formFields['LFD'] = (wdgt, None)
        wdgt.userDateChanged.connect(lambda: self.changeField(self.dtedtLFD))
        self.layoutFormMain.addWidget(wdgt, 3, 1)

        self.lnedtChgWt = QLineEdit(self.layoutwidgetFormMain); self.lblChgWt = QLabel(self.layoutwidgetFormMain)
        wdgt = self.lnedtChgWt; wdgtlbl = self.lblChgWt
        wdgtlbl.setObjectName(u"lblChgWt")
        self.layoutFormMain.addWidget(wdgtlbl, 2, 2)
        wdgt.setObjectName(u"lnedtChgWt")
        wdgt.setProperty('field', 'ChargeableWeight')
        self.formFields['ChargeableWeight'] = (wdgt, None)
        wdgt.editingFinished.connect(lambda: self.changeField(self.lnedtChgWt))
        self.layoutFormMain.addWidget(wdgt, 3, 2)

        self.lnedtPcs = QLineEdit(self.layoutwidgetFormMain); self.lblPcs = QLabel(self.layoutwidgetFormMain)
        wdgt = self.lnedtPcs; wdgtlbl = self.lblPcs
        wdgtlbl.setObjectName(u"lblPcs")
        self.layoutFormMain.addWidget(wdgtlbl, 2, 3)
        wdgt.setObjectName(u"lnedtPcs")
        wdgt.setProperty('field', 'Pieces')
        self.formFields['Pieces'] = (wdgt, None)
        wdgt.editingFinished.connect(lambda: self.changeField(self.lnedtPcs))
        self.layoutFormMain.addWidget(wdgt, 3, 3)

        self.lnedtVolume = QLineEdit(self.layoutwidgetFormMain); self.lblVolume = QLabel(self.layoutwidgetFormMain)
        wdgt = self.lnedtVolume; wdgtlbl = self.lblVolume
        wdgtlbl.setObjectName(u"lblVolume")
        self.layoutFormMain.addWidget(wdgtlbl, 2, 4)
        wdgt.setObjectName(u"lnedtVolume")
        wdgt.setProperty('field', 'Volume')
        self.formFields['Volume'] = (wdgt, None)
        wdgt.editingFinished.connect(lambda: self.changeField(self.lnedtVolume))
        self.layoutFormMain.addWidget(wdgt, 3, 4)

        self.txtedtNotes = QTextEdit(self.layoutwidgetFormMain); self.lblNotes = QLabel(self.layoutwidgetFormMain)
        wdgt = self.txtedtNotes; wdgtlbl = self.lblNotes
        wdgtlbl.setObjectName(u"lblNotes")
        wdgt.setObjectName(u"txtedtNotes")
        wdgt.setProperty('field', 'notes')
        self.formFields['notes'] = (wdgt, None)
        wdgt.textChanged.connect(lambda: self.changeField(self.txtedtNotes))
        self.layoutFormMain.addWidget(wdgtlbl, 4, 1, Qt.AlignmentFlag.AlignBottom)
        self.layoutFormMain.addWidget(wdgt, 5, 1, 3, 4)

        self.listWidgetPO = QListWidget(self.layoutwidgetFormMain)
        wdgt = self.listWidgetPO
        wdgt.setObjectName(u"listWidgetPO")
        wdgt.setProperty('field', 'POList')
        self.formFields['POList'] = (wdgt, None)
        wdgt.itemClicked.connect(lambda item: pleaseWriteMe(self, 'PO clicks'))
        wdgt.itemDoubleClicked.connect(lambda item: pleaseWriteMe(self, 'PO doubleclicks'))
        self.btnAddPO = QPushButton(self.layoutwidgetFormMain)
        wdgtadd = self.btnAddPO
        wdgtadd.setObjectName(u"btnAddPO")
        wdgtadd.clicked.connect(lambda: self.addPOToHBL())
        self.layoutFormMain.addWidget(wdgt, 1, 5, 5, 1)
        self.layoutFormMain.addWidget(wdgtadd, 3, 6)

        self.listWidgetShpFms = QListWidget(self.layoutwidgetFormMain)
        wdgt = self.listWidgetShpFms
        wdgt.setObjectName(u"listWidgetShpFms")
        wdgt.setProperty('field', 'ShippingForms')
        self.formFields['ShippingForms'] = (wdgt, None)
        wdgt.itemClicked.connect(lambda item: pleaseWriteMe(self, 'ShpFms clicks'))
        wdgt.itemDoubleClicked.connect(lambda item: pleaseWriteMe(self, 'ShpFms doubleclicks'))
        self.btnAddShpFms = QPushButton(self.layoutwidgetFormMain)
        wdgtadd = self.btnAddShpFms
        wdgtadd.setObjectName(u"btnAddShpFms")
        wdgtadd.clicked.connect(lambda: self.addShipFmToHBL())
        self.layoutFormMain.addWidget(wdgt, 7, 5)
        self.layoutFormMain.addWidget(wdgtadd, 7, 6)

        self.verticalSpacer1 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.layoutFormMain.addItem(self.verticalSpacer1, 4, 0)
        # second spacer not needed, for now
        # self.verticalSpacer2 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        # self.layoutForm.addItem(self.verticalSpacer2, 8, 0)

        self.layoutForm.addWidget(self.layoutwidgetFormMain)
        self.layoutForm.addSpacing(10)

        self.layoutwidgetFormMainBtm = QWidget(self)
        self.layoutFormMainBtm = QVBoxLayout(self.layoutwidgetFormMainBtm)
        self.tabsetHBLInfo = QTabWidget(self)
        self.tabsetHBLInfo.setObjectName(u"tabsetHBLInfo")
        # self.tabsetHBLInfo.setGeometry(QRect(20, 524, thisWindowsize.width()-40, 280))

        self.tabInvoices = QWidget()
        self.tabInvoices.setObjectName(u"tab1")
        self.tblViewInvoices = QTableView(self.tabInvoices)
        self.tblViewInvoices.setObjectName(u"tblViewInvoices")
        self.tblViewInvoices.verticalHeader().setHidden(True)
        # to a proc?
        header = self.tblViewInvoices.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        # Apply stylesheet to control text wrapping
        self.tblViewInvoices.setStyleSheet("""
        QHeaderView::section {
            padding: 5px;
            font-size: 12px;
            text-align: center;
            white-space: normal;  /* Allow text to wrap */
        }
        """)
        #
        self.tblViewInvoices.setGeometry(QRect(70, 40, thisWindowsize.width()-140, 192))
        self.tabsetHBLInfo.addTab(self.tabInvoices, "")

        self.tabInvoiceDetail = QWidget()
        self.tabInvoiceDetail.setObjectName(u"tab4")
        self.InvcRecSet = cQRecordsetView(newwidget_fn=self.newInvWidgetThisHBL, parent=self.tabInvoiceDetail)
        self.InvcRecSet.setGeometry(10, 10, thisWindowsize.width()-25-170, 250)
        self.tabsetHBLInfo.addTab(self.tabInvoiceDetail,"")
        # button to add new invoice
    
        # self.btnAddInv = QPushButton(self.tabInvoiceDetail)
        # wdgt = self.btnAddInv
        # wdgt.setObjectName('btnAddInv')
        # wdgt.clicked.connect(lambda: pleaseWriteMe(self, 'add Invoice clicks'))
        # wdgt.setGeometry(10+thisWindowsize.width()-55-120, 30, 90, 90)

        self.tabContainers = QWidget()
        self.tabContainers.setObjectName(u"tab2")
        self.tblViewContainers = QTableView(self.tabContainers)
        self.tblViewContainers.setObjectName(u"tblViewContainers")
        self.tblViewContainers.verticalHeader().setHidden(True)
        self.tblViewContainers.setGeometry(QRect(10, 10, thisWindowsize.width()-200, 250))
        self.tabsetHBLInfo.addTab(self.tabContainers, "")
        # button to add new Container
        self.btnAddContainer = QPushButton(self.tabContainers)
        wdgt = self.btnAddContainer
        wdgt.setObjectName('btnAddContainer')
        wdgt.clicked.connect(lambda: self.addContainerToHBL())
        wdgt.setGeometry(10+thisWindowsize.width()-175, 30, 90, 90)

        self.tabrefs = QWidget()
        self.tabrefs.setObjectName(u"tab3")
        self.tblViewrefs = QTableView(self.tabrefs)
        self.tblViewrefs.setObjectName(u"tblViewrefs")
        self.tblViewrefs.verticalHeader().setHidden(True)
        self.tblViewrefs.setGeometry(QRect(20, 20, thisWindowsize.width()-40, 192))
        self.tabsetHBLInfo.addTab(self.tabrefs, "")
        
        self.layoutFormMainBtm.addWidget(self.tabsetHBLInfo)
        self.layoutForm.addWidget(self.layoutwidgetFormMainBtm)

        self.btnCommit = QPushButton(self.layoutwidgetFormHdr)
        self.btnCommit.setObjectName(u"btnCommit")
        self.btnCommit.clicked.connect(lambda: self.writeRecord())
        # self.btnCommit.setGeometry(QRect(820, 60, 101, 61))
        self.layoutFormHdr.addWidget(self.btnCommit,0,1,2,1)

#if QT_CONFIG(shortcut)
        self.lblOrigin.setBuddy(self.comboOrigin)
        self.lblChgWt.setBuddy(self.lnedtChgWt)
        self.lblIncoTerm.setBuddy(self.lnedtIncoterm)
        self.lblVolume.setBuddy(self.lnedtVolume)
        self.lblLFD.setBuddy(self.dtedtLFD)
        self.lblFreightType.setBuddy(self.comboFreightType)
        self.lblPcs.setBuddy(self.lnedtPcs)
        self.lblETA.setBuddy(self.dtedtETA)
        self.lblCompany.setBuddy(self.comboCompany)
        self.lblHBLNumber.setBuddy(self.lnedHBLNumber)
        self.lblNotes.setBuddy(self.txtedtNotes)
#endif // QT_CONFIG(shortcut)

        QWidget.setTabOrder(self.comboCompany, self.lnedHBLNumber)
        QWidget.setTabOrder(self.lnedHBLNumber, self.comboFreightType)
        QWidget.setTabOrder(self.comboFreightType, self.comboOrigin)
        QWidget.setTabOrder(self.comboOrigin, self.lnedtIncoterm)
        QWidget.setTabOrder(self.lnedtIncoterm, self.dtedtETA)
        QWidget.setTabOrder(self.dtedtETA, self.dtedtLFD)
        QWidget.setTabOrder(self.dtedtLFD, self.lnedtChgWt)
        QWidget.setTabOrder(self.lnedtChgWt, self.lnedtPcs)
        QWidget.setTabOrder(self.lnedtPcs, self.lnedtVolume)
        QWidget.setTabOrder(self.lnedtVolume, self.txtedtNotes)
        
        QWidget.setTabOrder(self.txtedtNotes, self.listWidgetPO)
        QWidget.setTabOrder(self.listWidgetPO, self.listWidgetShpFms)
        QWidget.setTabOrder(self.listWidgetShpFms, self.tabsetHBLInfo)
        
        # track if form dirty
        # self.setFormDirty(self, False)
        # make this a new record
        self.currRec = self.createNewHBLRec()
        self.setFormDirty(self,False)

        self.retranslateUi()

        #TODO: play weith this and get it to work
        # self.windowScroller = QScrollArea(self)
        # self.windowScroller.setWidget(self)
        # self.windowScroller.setWidgetResizable(True)
        
    # __init__

    def retranslateUi(self):
        self.setWindowTitle(QCoreApplication.translate("Form", u"HBL", None))

        self.lblOrigin.setText(QCoreApplication.translate("Form", u"Origin", None))
        self.lblChgWt.setText(QCoreApplication.translate("Form", u"Chgbl Weight", None))
        self.lblIncoTerm.setText(QCoreApplication.translate("Form", u"incoterm", None))
        self.lblVolume.setText(QCoreApplication.translate("Form", u"Volume", None))
        self.lblLFD.setText(QCoreApplication.translate("Form", u"LFD", None))
        self.lblFreightType.setText(QCoreApplication.translate("Form", u"Freight Type", None))
        self.lblPcs.setText(QCoreApplication.translate("Form", u"Pieces", None))
        self.lblETA.setText(QCoreApplication.translate("Form", u"ETA", None))
        self.lblCompany.setText(QCoreApplication.translate("Form", u"Company", None))
        self.lblHBLNumber.setText(QCoreApplication.translate("Form", u"HBL Number", None))
        self.lblNotes.setText(QCoreApplication.translate("Form", u"Notes", None))
        self.lblFormName.setText(QCoreApplication.translate("Form", u"HBL", None))

        self.btnCommit.setText(QCoreApplication.translate('Form','Commit\nChanges',None))
        self.btnAddPO.setText(QCoreApplication.translate('Form','Add PO',None))
        self.btnAddShpFms.setText(QCoreApplication.translate('Form','Add Shp\nFms',None))
        # self.btnAddInv.setText(QCoreApplication.translate('Form','Add Invoice',None))
        self.btnAddContainer.setText(QCoreApplication.translate('Form','Add Containr',None))

        self.tabsetHBLInfo.setTabText(self.tabsetHBLInfo.indexOf(self.tabInvoices), QCoreApplication.translate("Form", u"Invoices", None))
        self.tabsetHBLInfo.setTabText(self.tabsetHBLInfo.indexOf(self.tabContainers), QCoreApplication.translate("Form", u"Containers", None))
        self.tabsetHBLInfo.setTabText(self.tabsetHBLInfo.indexOf(self.tabrefs), QCoreApplication.translate("Form", u"references", None))
        self.tabsetHBLInfo.setTabText(self.tabsetHBLInfo.indexOf(self.tabInvoiceDetail), QCoreApplication.translate("Form", u"Invoice Detail", None))
   # retranslateUi

    def newInvWidgetThisHBL(self) -> QWidget:
        return Invoice_singleForm(HBLRec=self.currRec)

    def getRecordFromGoto(self) -> None:
        #TODO: check if dirty

        slctd = self.gotoHBL.selectedItem()
        HBLNumber = slctd['text']
        # id = wdgt.currentData()
        id = slctd['keys'][0] if len(slctd['keys']) else None
        self.lblHBLNotFound.setText('')
        if not id and HBLNumber:
            self.lblHBLNotFound.setText(f'{HBLNumber} not found')
            self.gotoHBL.undo()

            # create new HBL record
            ans = QMessageBox.question(
                self, 
                "Create HBL?", f'HBL {HBLNumber} does not exist. Create it?',
                QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
                )
            if ans == QMessageBox.StandardButton.No:
                self.gotoHBL.undo()
                self.gotoHBL.setFocus()
                return
            else:
                HBLrec = self.createNewHBLRec(
                    HBLNumber=str(HBLNumber),     
                    saverec= True
                )
                id = HBLrec.pk
                # add this new HBL to the dlist
                self.gotoHBL.addChoices({id: HBLNumber})
            #endif ans == QMessageBox.StandardButton.No
        # endif not id
        
        if id:
            self.getRecordfromdb(id)
    # getRecordFromGoto

    def addPOToHBL(self):
        PO_str, ok = QInputDialog.getText(self,
            'Enter POs', 'Enter POs to add, separated by commas',
            )
        if not ok:
            return
        PO_list = ''.join(PO_str.split()).split(',')
        for p in PO_list:
            pRec = PO.objects.filter(PONumber=p).first()
            # check if not exists
            if not pRec:
                # offer to add
                ans = QMessageBox.question(
                    self, 
                    "Create PO?", f'PO {p} does not exist. Create it?\n(if you do, don\'t forget to set org and Buyer)',
                    QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                    )
                if ans == QMessageBox.StandardButton.No:
                    continue
                else:
                    pRec = PO.objects.create(PONumber=p, notes='')
                #endif ans == No
            # endif not pRec
            
            # add p to HBL
            self.currRec.POList.add(pRec)
        
        # rebuild PO list
        self.fillFormFromlinkedPO()
    # addPOToHBL

    def addShipFmToHBL(self):
        ShpFm_str, ok = QInputDialog.getText(self,
            'Enter Ship Formss', 'Enter Shipping Form numbers to add, separated by commas\n(warning: no exception checking)',
            )
        if not ok:
            return
        ShpFm_list = [int(x) for x in ''.join(ShpFm_str.split()).split(',')]
        for s in ShpFm_list:
            sfRec = ShippingForms.objects.filter(id_SmOffFormNum=s).first()
            # check if not exists
            if not sfRec:
                # offer to add
                ans = QMessageBox.question(
                    self, 
                    "Create Shp Fm?", f'Shipping Form {s} does not exist. Create it?\n(if you do, don\'t forget to edit it)',
                    QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                    )
                if ans == QMessageBox.StandardButton.No:
                    continue
                else:
                    sfRec = ShippingForms.objects.create(id_SmOffFormNum=s, incoterm='', notes='')
                #endif ans == No
            # endif not sfRec
            
            # add sf to HBL
            self.currRec.ShippingForms.add(sfRec)
        
        # rebuild PO list
        self.fillFormFromlinkedShipForms()
    # addShipFmToHBL

    def addContainerToHBL(self):
        Contnr_str, ok = QInputDialog.getText(self,
            'Enter Containers', 'Enter Container Numbers to add, separated by commas\n(warning: no exception checking)',
            )
        if not ok:
            return
        Contnr_list = ''.join(Contnr_str.split()).split(',')
        for s in Contnr_list:
            cntrRec = Containers.objects.filter(ContainerNumber=s).first()
            # check if not exists
            if not cntrRec:
                # offer to add
                ans = QMessageBox.question(
                    self, 
                    "Create Container?", f'Container {s} does not exist. Create it?\n(if you do, don\'t forget to edit it)',
                    QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                    )
                if ans == QMessageBox.StandardButton.No:
                    continue
                else:
                    cntrRec = Containers.objects.create(ContainerNumber=s, HBL=self.currRec, notes='')
                #endif ans == No
            # endif not sfRec
            
        # rebuild PO list
        self.fillFormFromlinkedContainers()
    # addShipFmToHBL


    ##########################################
    ########    Create

    def createNewHBLRec(self, HBLNumber:str = None, saverec:bool = False) -> HBL:
        newRec = HBL(
            incoterm = '',
            notes = '',
            )
        if HBLNumber: newRec.HBLNumber = HBLNumber
        
        if saverec:
            newRec.save()
        
        return newRec


    ##########################################
    ########    Read

    def getRecordfromdb(self, recid:int, createFlag:bool = False) -> int:
        self.currRec = HBL.objects.get(pk=recid)
        self.fillFormFromcurrRec()
        
        return self.currRec.pk
    # getRecordfromdb

    def fillFormFromcurrRec(self):
        cRec = self.currRec
    
        # set pk display
        self.lblRecID.setText(str(cRec.pk))

        for field in cRec._meta.get_fields():
            # special cases: ShippingForms, POList, containers, invoices:
            if field.name in ['ShippingForms', 'POList', 'Invoices', 'Containers', 'reference_ties']:
                continue

            field_value = getattr(cRec, field.name, None)
            field_valueStr = field_value
            # transform values for foreign keys and lookups
            forgnKeys = {
                'id': cRec,
                'Company': cRec.Company,
                'FreightType': cRec.FreightType,
                'Origin': cRec.Origin,
                'Quote': cRec.Quote,
                }
            if field.name in forgnKeys:
                field_valueStr = str(forgnKeys[field.name])
            
            for wdgt in self.findChildren(QWidget):
                if wdgt.property('field') == field.name:
                    # set wdgt value to field_value
                    # must set value per widget type
                    if any([wdgt.inherits(tp) for tp in ['QLineEdit', ]]):
                        wdgt.setText(field_valueStr)
                    elif any([wdgt.inherits(tp) for tp in ['QTextEdit', ]]):
                        wdgt.setPlainText(field_valueStr)
                    elif any([wdgt.inherits(tp) for tp in ['QComboBox', ]]):
                        chNum = wdgt.findData(field_valueStr)
                        if chNum == -1: 
                            wdgt.setCurrentText(field_valueStr)
                        else:
                            wdgt.setCurrentIndex(chNum)
                        #endif findData valid
                    elif any([wdgt.inherits(tp) for tp in ['QDateEdit', ]]):
                        wdgt.setDate(field_value)
                    # endif widget type test

                    break   # we found the widget for this field; we don't need to test other widgets
                            # move on to the next field
                # endif wdgt field = field.name
            # endfor wdgt in self.children()
        #endfor field in cRec
        
        if cRec.pk is None:
            # there are no linked recs yet, and most of the below will bomb
            self.setFormDirty(self, False)
            return
        
        # get linked recs
        # _linkedTables = ['ShippingForms', 'PO', 'Invoices', 'Containers', 'reference_ties']
        self.fillFormFromlinkedShipForms()
        
        self.fillFormFromlinkedPO()
        
        self.fillFormFromlinkedInvoices()

        self.fillFormFromlinkedContainers()

        self.fillFormFromlinkedrefs()
        
        self.setFormDirty(self, False)
    # fillFormFromcurrRec

    def fillFormFromlinkedPO(self):
        cRec = self.currRec
        self.linkedRecs['PO'] = cRec.POList.all()
        self.listWidgetPO.clear()
        self.listWidgetPO.addItems( [rec.PONumber for rec in self.linkedRecs['PO']] )
    
    def fillFormFromlinkedContainers(self):
        cRec = self.currRec
        # self.linkedRecs['Containers'] = Containers.objects.filter(HBL=cRec)
        self.linkedRecs['Containers'] = cRec.containers_set.all()
        qmodel = QModelContainers({'HBL': cRec})
        self.tblViewContainers.setModel(qmodel)
    
    def fillFormFromlinkedShipForms(self):
        cRec = self.currRec
        self.linkedRecs['ShippingForms'] = cRec.ShippingForms.all()
        self.listWidgetShpFms.clear()
        self.listWidgetShpFms.addItems( [str(rec.id_SmOffFormNum) for rec in self.linkedRecs['ShippingForms']] )
    
    def fillFormFromlinkedInvoices(self):
        cRec = self.currRec
        # self.linkedRecs['Invoices'] = Invoices.objects.filter(HBL=cRec)
        self.linkedRecs['Invoices'] = cRec.invoices_set.all()
        qmodel = QModelInvoices({'HBL': cRec})
        self.tblViewInvoices.setModel(qmodel)
        self.InvcRecSet.init_recSet()
        for rec in self.linkedRecs['Invoices']:
            wdgtInv = Invoice_singleForm(InvRec=rec)
            self.InvcRecSet.addWidget(wdgtInv)
    
    def fillFormFromlinkedrefs(self):
        cRec = self.currRec
        # fill references
        Q1 = Q(Container__in=self.linkedRecs['Containers'].values_list('pk'))
        Q2 = Q(HBL=cRec.pk)
        Q3 = Q(Invoice__in=self.linkedRecs['Invoices'].values_list('pk'))
        Q4 = Q(ShippingForm__in=self.linkedRecs['ShippingForms'].values_list('pk'))
        reflist = refs.objects.filter(Q1 | Q2 | Q3 | Q4)
        self.linkedRecs['reference_ties'] = reflist
        qmodel = QModelrefs(reflist)
        self.tblViewrefs.setModel(qmodel)
    
    
    ##########################################
    ########    Update

    @Slot()
    def changeField(self, wdgt:QWidget) -> bool:
        forgnKeys = {   
            'Company',
            'FreightType',
            'Origin',
            'Quote',
            }
        cRec = self.currRec
        dbField = wdgt.property('field')
        
        wdgt_value = None
        
        #TODO: write cUtil getQWidgetValue(wdgt), setQWidgetValue(wdgt)
        #widgtype = wdgt.staticMetaObject.className()
        if any([wdgt.inherits(tp) for tp in ['cDataList', ]]):  # I hope I hope I hope
            wdgt_value = wdgt.selectedItem()['keys'][0]
        if any([wdgt.inherits(tp) for tp in ['QLineEdit', ]]):
            wdgt_value = wdgt.text()
        elif any([wdgt.inherits(tp) for tp in ['QTextEdit', ]]):
            wdgt_value = wdgt.toPlainText()
        elif any([wdgt.inherits(tp) for tp in ['QComboBox', ]]):
            wdgt_value = wdgt.currentData()
        elif any([wdgt.inherits(tp) for tp in ['QDateEdit', ]]):
            wdgt_value = wdgt.date().toPython()
        elif any([wdgt.inherits(tp) for tp in ['QCheckBox', ]]):
            wdgt_value = wdgt.isChecked()
        # endif widget type test

        if dbField in forgnKeys:
            # forgnModel:Model = getattr(cRec,dbField).related_model
            # print(forgnModel)   #debugging
            # wdgt_value = forgnModel.objects.get(pk=wdgt_value)
            dbField += '_id'
        
        if wdgt_value:
            setattr(cRec, dbField, wdgt_value)
            self.setFormDirty(wdgt, True)
            return True
        else:
            return False
        # endif wdgt_value
    # changeField
    
    def writeRecord(self):
        if not self.isFormDirty():
            return
        
        cRec = self.currRec
        newrec = (cRec is None)
        
        # There MUST be a HBLNumber, and it can't belong to another record
        if not cRec.HBLNumber:
            QMessageBox(QMessageBox.Icon.Critical, 'Must provide HBL Number','You must provide a HBL Number!',
                QMessageBox.StandardButton.Ok, self).show()
            self.lnedHBLNumber.setFocus()
            return
        existingrec = [R.pk for R in HBL.objects.filter(HBLNumber=cRec.HBLNumber)]
        if len(existingrec) and cRec.pk not in existingrec:
            QMessageBox(QMessageBox.Icon.Critical, 'HBL Number Exists', f'HBL {cRec.HBLNumber} exists in another record!',
                QMessageBox.StandardButton.Ok, self).show()
            self.lnedHBLNumber.clear()
            self.lnedHBLNumber.setFocus()
            return

        # check other traps later
        
        cRec.save()
        pk = cRec.pk
        self.lblRecID.setText(str(pk))
        
        self.gotoHBL.setText(cRec.HBLNumber)

        if newrec:
            # add this record to self.gotoHBL.completer().model()
            self.gotoHBL.addChoices({pk: str(cRec.HBLNumber)})
            
        self.setFormDirty(self, False)


    ##########################################
    ########    Delete


    ##########################################
    ########    CRUD support

    @Slot()
    def setFormDirty(self, wdgt:QWidget, dirty:bool = True):
        wdgt.setProperty('dirty', dirty)
        # if wdgt === self, set all children dirty
        if wdgt is not self:
            if dirty: self.setProperty('dirty',True)
        else:
            for W in self.children():
                if any([W.inherits(tp) for tp in ['QLineEdit', 'QTextEdit', 'QCheckBox', 'QComboBox', 'QDateEdit']]):
                    W.setProperty('dirty', dirty)
        
        # enable btnCommit if anything dirty
        self.btnCommit.setEnabled(self.property('dirty'))
    
    def isFormDirty(self) -> bool:
        return self.property('dirty')


##################################################
##################################################
##################################################

class Invoice_singleForm(QWidget):
    def __init__(self, InvRec:Invoices = None, HBLRec:HBL = None, parent = None):
        super().__init__(parent)
        
        if InvRec: 
            self.currRec = InvRec
        else:
            self.currRec = self.createNewRec(InvNumber=None,HBLref=HBLRec)
        #endif
        
        self.resize(780, 190)
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)

        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        
        self.lblRecID = QLabel(self)
        wdgt = self.lblRecID
        wdgt.setObjectName(u"label_3")
        self.gridLayout.addWidget(wdgt, 0, 0)

        self.lblSmOffForm = QLabel(self)
        self.lnedtSmOffFm = QLineEdit(self)
        wdgt = self.lnedtSmOffFm; wdgtlbl = self.lblSmOffForm
        wdgtlbl.setObjectName(u"label")
        wdgt.setObjectName(u"lineEdit")
        wdgt.setProperty('field', 'id_SmOffFormNum')
        wdgt.editingFinished.connect(lambda: self.changeField(self.lnedtSmOffFm))
        self.gridLayout.addWidget(wdgtlbl, 1, 1)
        self.gridLayout.addWidget(wdgt, 1, 2)

        self.lblSmOffStat = QLabel(self)
        self.cmbSmOffStat = IncShipAppchoiceWidgets.chooseSmOffInvStatus(self)
        wdgt = self.cmbSmOffStat; wdgtlbl = self.lblSmOffStat
        wdgtlbl.setObjectName(u"label_2")
        wdgt.setObjectName(u"comboBox")
        wdgt.setProperty('field', 'SmOffStatus')
        wdgt.currentIndexChanged.connect(lambda indx: self.changeField(self.cmbSmOffStat))
        self.gridLayout.addWidget(wdgtlbl, 1, 3)
        self.gridLayout.addWidget(wdgt, 1, 4)

        self.lblCompany = QLabel(self)
        self.cmbCompany = IncShipAppchoiceWidgets.chooseCompany(self)
        wdgt = self.cmbCompany; wdgtlbl = self.lblCompany
        wdgtlbl.setObjectName(u"label_4")
        wdgt.setObjectName(u"comboBox_2")
        wdgt.setProperty('field', 'Company')
        wdgt.currentIndexChanged.connect(lambda indx: self.changeField(self.cmbCompany))
        self.gridLayout.addWidget(wdgtlbl, 2, 1)
        self.gridLayout.addWidget(wdgt, 2, 2)

        self.lblInvNum = QLabel(self)
        self.lnedtInvNum = QLineEdit(self)
        wdgt = self.lnedtInvNum; wdgtlbl = self.lblInvNum
        wdgtlbl.setObjectName(u"label_5")
        wdgt.setObjectName(u"lineEdit_2")
        wdgt.setProperty('field', 'InvoiceNumber')
        wdgt.editingFinished.connect(lambda: self.changeField(self.lnedtInvNum))
        self.gridLayout.addWidget(wdgtlbl, 2, 3)
        self.gridLayout.addWidget(wdgt, 2, 4)

        self.lblInvDt = QLabel(self)
        self.dtedtInvDt = QDateEdit(self)
        wdgt = self.dtedtInvDt; wdgtlbl = self.lblInvDt
        wdgtlbl.setObjectName(u"label_6")
        wdgt.setObjectName(u"dateEdit")
        wdgt.setDisplayFormat(_DATE_FORMAT)
        wdgt.setProperty('field', 'InvoiceDate')
        wdgt.userDateChanged.connect(lambda indx: self.changeField(self.dtedtInvDt))
        self.gridLayout.addWidget(wdgtlbl, 2, 5)
        self.gridLayout.addWidget(wdgt, 2, 6)

        self.lblAmount = QLabel(self)
        self.lnedtAmount = QLineEdit(self)
        wdgt = self.lnedtAmount; wdgtlbl = self.lblAmount
        wdgtlbl.setObjectName(u"label_7")
        wdgt.setObjectName(u"lineEdit_3")
        wdgt.setProperty('field', 'InvoiceAmount')
        wdgt.editingFinished.connect(lambda: self.changeField(self.lnedtAmount))
        self.gridLayout.addWidget(wdgtlbl, 2, 7)
        self.gridLayout.addWidget(wdgt, 2, 8)

        self.lblHBL = QLabel(self)
        self.dlistHBL = IncShipAppchoiceWidgets.chooseHBL(str(InvRec.HBL) if InvRec else '', self)
        wdgt = self.dlistHBL; wdgtlbl = self.lblHBL
        wdgtlbl.setObjectName(u"label_8")
        wdgt.setObjectName(u"lineEdit_4")
        wdgt.setProperty('field', 'HBL')
        wdgt.editingFinished.connect(lambda: self.changeField(self.dlistHBL))
        self.gridLayout.addWidget(wdgtlbl, 3, 1)
        self.gridLayout.addWidget(wdgt, 3, 2)

        self.lblAddlBillInv = QLabel(self)
        self.dlistAddlBillInv = IncShipAppchoiceWidgets.chooseInvoice(str(InvRec.AddlBillingForInv) if InvRec else '', self)
        wdgt = self.dlistAddlBillInv; wdgtlbl = self.lblAddlBillInv
        wdgtlbl.setObjectName(u"label_10")
        wdgt.setObjectName(u"lineEdit_5")
        wdgt.setProperty('field', 'AddlBillingForInv')
        wdgt.editingFinished.connect(lambda: self.changeField(self.dlistAddlBillInv))
        self.gridLayout.addWidget(wdgtlbl, 3, 4)
        self.gridLayout.addWidget(wdgt, 3, 5, 1, 2)

        self.lblnotes = QLabel(self)
        self.txtedtnotes = QTextEdit(self)
        wdgt = self.txtedtnotes; wdgtlbl = self.lblnotes
        wdgtlbl.setObjectName(u"label_9")
        wdgt.setObjectName(u"textEdit")
        wdgt.setProperty('field', 'notes')
        wdgt.textChanged.connect(lambda: self.changeField(self.txtedtnotes))
        self.gridLayout.addWidget(wdgtlbl, 4, 0)
        self.gridLayout.addWidget(wdgt, 4, 1, 1, 8)

        self.chkbxVerified = QCheckBox(self)
        wdgt = self.chkbxVerified
        wdgt.setObjectName(u"checkBox")
        wdgt.setProperty('field', 'verifiedForFii')
        wdgt.checkStateChanged.connect(lambda newstate: self.changeField(self.chkbxVerified))
        self.gridLayout.addWidget(wdgt, 0, 1, 1, 2)

        self.chkbxInvDL = QCheckBox(self)
        wdgt = self.chkbxInvDL
        wdgt.setObjectName(u"checkBox_2")
        wdgt.setProperty('field', 'inv_downloaded')
        wdgt.checkStateChanged.connect(lambda newstate: self.changeField(self.chkbxInvDL))
        self.gridLayout.addWidget(wdgt, 0, 4, 1, 2)
        
        self.btnCommit = QPushButton(self)
        wdgt = self.btnCommit
        wdgt.setObjectName(u"btnCommit")
        wdgt.clicked.connect(lambda: self.writeRecord())
        self.gridLayout.addWidget(wdgt, 0, 7)

        # set tab order
        
        self.retranslateUi()
        
        self.fillFormFromcurrRec()
    # setupUi

    def retranslateUi(self):
        self.lblSmOffStat.setText(QCoreApplication.translate("Frame", u"SmOff Status", None))
        self.chkbxVerified.setText(QCoreApplication.translate("Frame", u"verified for fii?", None))
        self.lblCompany.setText(QCoreApplication.translate("Frame", u"Company", None))
        self.chkbxInvDL.setText(QCoreApplication.translate("Frame", u"Inv dl?", None))
        self.lblAmount.setText(QCoreApplication.translate("Frame", u"Inv Amount", None))
        self.lblInvNum.setText(QCoreApplication.translate("Frame", u"Inv #", None))
        self.lblnotes.setText(QCoreApplication.translate("Frame", u"notes", None))
        self.lblAddlBillInv.setText(QCoreApplication.translate("Frame", u"Addl Billing For Invoice", None))
        self.lblInvDt.setText(QCoreApplication.translate("Frame", u"Inv Date", None))
        self.lblHBL.setText(QCoreApplication.translate("Frame", u"HBL", None))
        self.lblSmOffForm.setText(QCoreApplication.translate("Frame", u"SmOff FmNum", None))
        self.btnCommit.setText(QCoreApplication.translate('Form','Save Changes',None))
    # retranslateUi

    ##########################################
    ########    Create

    def createNewRec(self, InvNumber:str = None, HBLref:str|HBL|None = None) -> Invoices:
        # HBLNumber - pass in str or a record or an id? or handle any of those?
        newRec = Invoices(
            SmOffStatus = Invoices.SmOffStatusCodes.NOTENT,
            inv_downloaded = False,
            verifiedForFii = False,
            notes = '',
            )
        if InvNumber: newRec.InvoiceNumber = InvNumber
        if HBLref: 
            if isinstance(HBLref, str|int):
                newRec.HBL = HBL.objects.get_or_create(
                    HBLNumber=str(HBLref), 
                    defaults={
                        'incoterm': '',
                        'notes': '',
                })
            elif isinstance(HBLref, HBL):
                newRec.HBL = HBLref
            #endif HBLref type
        
        return newRec
        

    ##########################################
    ########    Read

    def fillFormFromcurrRec(self):
        cRec:Invoices = self.currRec
        
        # set pk display
        self.lblRecID.setText(str(cRec.pk))
        
        # move to class var?
        forgnKeys = {
            'id': cRec if cRec else '',
            'Company': cRec.Company if cRec else '',
            'HBL': cRec.HBL if cRec.HBL_id else '',
            }
        # move to class var?
        valu_transform_flds = {
            'InvoiceAmount': (
                str, 
                lambda value: decimal.Decimal(value.replace("$", "").replace(",", "").replace(" ",""))
                ),
            'SmOffStatus': (
                lambda code: Invoices.SmOffStatusCodes.__call__(code).label if code in Invoices.SmOffStatusCodes else None,
                lambda code: code
                ),
            'AddlBillingForInv': (
                lambda value: str(value) if value else '',
                lambda value: value,
            ),
        }
        for field in cRec._meta.get_fields():
            field_value = getattr(cRec, field.name, None)
            field_valueStr = str(field_value)
            if field.name in forgnKeys:
                field_valueStr = str(forgnKeys[field.name])
            if field.name in valu_transform_flds:
                field_valueStr = valu_transform_flds[field.name][0](field_value)
            
            for wdgt in self.findChildren(QWidget):
                if wdgt.property('field') == field.name:
                    # set wdgt value to field_value
                    # must set value per widget type
                    if any([wdgt.inherits(tp) for tp in ['QLineEdit', ]]):
                        wdgt.setText(field_valueStr)
                    elif any([wdgt.inherits(tp) for tp in ['QTextEdit', ]]):
                        wdgt.setPlainText(field_valueStr)
                    elif any([wdgt.inherits(tp) for tp in ['QComboBox', ]]):
                        chNum = wdgt.findData(field_valueStr)
                        if chNum == -1: 
                            wdgt.setCurrentText(field_valueStr)
                        else:
                            wdgt.setCurrentIndex(chNum)
                        #endif findData valid
                    elif any([wdgt.inherits(tp) for tp in ['QDateEdit', ]]):
                        wdgt.setDate(field_value)
                    elif any([wdgt.inherits(tp) for tp in ['QCheckBox', ]]):
                        wdgt.setChecked(field_value)
                    # endif widget type test

                    break   # we found the widget for this field; we don't need to keep testing widgets
                # endif widget field = field.name
            # endfor wdgt in self.children()
        #endfor field in cRec
            
        self.setFormDirty(self, False)
    # fillFormFromRec


    ##########################################
    ########    Update

    @Slot()
    def changeField(self, wdgt:QWidget) -> bool:
        # move to class var?
        forgnKeys = {   
            'Company',
            'HBL',
            'AddlBillingForInv',
            }
        # move to class var?
        valu_transform_flds = {
            'InvoiceAmount': (
                str, 
                lambda value: decimal.Decimal(value.replace("$", "").replace(",", "").replace(" ",""))
                ),
            'SmOffStatus': (
                lambda code: Invoices.SmOffStatusCodes.__call__(code).label if code in Invoices.SmOffStatusCodes else None,
                lambda code: code
                ),
            'AddlBillingForInv': (
                lambda value: str(value) if value else '',
                lambda value: value,
            ),
        }
        cRec:Invoices = self.currRec
        dbField = wdgt.property('field')

        wdgt_value = None

        #TODO: write cUtil getQWidgetValue(wdgt), setQWidgetValue(wdgt)
        #widgtype = wdgt.staticMetaObject.className()
        if any([wdgt.inherits(tp) for tp in ['cDataList', ]]):  # I hope I hope I hope
            kees = wdgt.selectedItem()['keys']
            wdgt_value = kees[0] if kees else wdgt.text()
        elif any([wdgt.inherits(tp) for tp in ['QLineEdit', ]]):
            wdgt_value = wdgt.text()
        elif any([wdgt.inherits(tp) for tp in ['QTextEdit', ]]):
            wdgt_value = wdgt.toPlainText()
        elif any([wdgt.inherits(tp) for tp in ['QComboBox', ]]):
            wdgt_value = wdgt.currentData()
        elif any([wdgt.inherits(tp) for tp in ['QDateEdit', ]]):
            wdgt_value = wdgt.date().toPython()
        elif any([wdgt.inherits(tp) for tp in ['QCheckBox', ]]):
            wdgt_value = wdgt.isChecked()
        # endif widget type test

        if dbField in forgnKeys:
            dbField += '_id'
        if dbField in valu_transform_flds:
            wdgt_value = valu_transform_flds[dbField][1](wdgt_value)

        # offer to add HBL if nonexistent
        if dbField == "HBL_id" and wdgt_value:
            wdgt_value_asnum = -1
            try:
                wdgt_value_asnum = int(wdgt_value)
            except ValueError:
                pass
            #end try
            if not HBL.objects.filter(pk=wdgt_value_asnum).exists():
                ans = QMessageBox.question(
                    self, 
                    "Create HBL?", f'HBL {wdgt_value} does not exist. Create it?',
                    QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                    )
                if ans == QMessageBox.StandardButton.No:
                    self.dlistHBL.clear()
                    self.dlistHBL.setFocus()
                    return
                else:
                    HBLrec = HBL.objects.create(
                        HBLNumber=str(wdgt.text()),      # str(wdgt.selectedItem()['text']), 
                        incoterm = '',
                        notes = '',
                    )
                    wdgt_value = HBLrec.pk
                    # add this new HBL to the dlist
                    self.dlistHBL.addChoices({wdgt_value: wdgt.text()})
                #endif ans == QMessageBox.StandardButton.No
            # endif HBL not exists
        # endif dbField == "HBL"

        if wdgt_value:
            setattr(cRec, dbField, wdgt_value)
            self.setFormDirty(wdgt, True)
            return True
        else:
            return False
        # endif wdgt_value
    # changeField
    
    def writeRecord(self):
        if not self.isFormDirty():
            return
        
        cRec:Invoices = self.currRec
        newrec = (cRec is None)
        
        #TODO: There must also be a Company, and it's (Company, InvoiceNumber) that needs to be unique
        # There MUST be a InvoiceNumber, and it can't belong to another record
        if not cRec.InvoiceNumber:
            QMessageBox(QMessageBox.Icon.Critical, 'Must provide Invoice Number','You must provide a Invoice Number!',
                QMessageBox.StandardButton.Ok, self).show()
            self.lnedtInvNum.setFocus()
            return
        existingrec = [R.pk for R in Invoices.objects.filter(InvoiceNumber=cRec.InvoiceNumber)]
        if len(existingrec) and cRec.pk not in existingrec:
            QMessageBox(QMessageBox.Icon.Critical, 'Invoice Number Exists', f'Invoice {cRec.InvoiceNumber} exists in another record!',
                QMessageBox.StandardButton.Ok, self).show()
            self.lnedtInvNum.clear()
            self.lnedtInvNum.setFocus()
            return
        
        #There must be an HBL
        if not cRec.HBL:
            QMessageBox(QMessageBox.Icon.Critical, 'Must provide HBL','You must provide a HBL!',
                QMessageBox.StandardButton.Ok, self).show()
            self.dlistHBL.setFocus()
            return
        # existence was handled when the HBL was entered
        
        # check other traps later
        
        cRec.save()
        pk = cRec.pk
        self.lblRecID.setText(str(pk))
        
        if newrec:
            # add this record to self.gotoHBL.completer().model()
            ...
            
        self.setFormDirty(self, False)
    # writeRecord


    ##########################################
    ########    Delete

    # Delete not supported yet


    ##########################################
    ########    CRUD support

    @Slot()
    def setFormDirty(self, wdgt:QWidget, dirty:bool = True):
        wdgt.setProperty('dirty', dirty)
        # if wdgt === self, set all children dirty
        if wdgt is not self:
            if dirty: self.setProperty('dirty',True)
        else:
            for W in self.children():
                if any([W.inherits(tp) for tp in ['QLineEdit', 'QTextEdit', 'QCheckBox', 'QComboBox', 'QDateEdit', ]]):
                    W.setProperty('dirty', dirty)
        
        # enable btnCommit if anything dirty
        self.btnCommit.setEnabled(self.property('dirty'))
    
    def isFormDirty(self) -> bool:
        return self.property('dirty')


    ##########################################
    ########    Widget-responding procs
    


############################################################
############################################################
############################################################

