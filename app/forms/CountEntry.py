from app.database import app_Session
from app.forms import std_id_def
from app.models import ActualCounts


from PySide6.QtWidgets import QCheckBox, QDateEdit, QLineEdit, QPlainTextEdit
from calvincTools.utils import cSimpleRecordForm


class CountEntryForm(cSimpleRecordForm):
    _ORMmodel = ActualCounts
    _ssnmaker = app_Session
    _formname = 'Count Entry Form'

    fieldDefs = {
        'id': std_id_def,
        'CountDate': {'label': 'Count Date', 'widgetType': QDateEdit, 'position': (1,0)},
        'Material': {'label': 'Material', 'widgetType': QLineEdit, 'position': (2,0)},
        'Counter': {'label': 'Counter', 'widgetType': QLineEdit, 'position': (3,0)},
        'LocationOnly': {'label': 'Location Only', 'widgetType': QCheckBox, 'position': (4,0)},
        'LOCATION': {'label': 'Location', 'widgetType': QLineEdit, 'position': (5,0)},
        'CTD_QTY_Expr': {'label': 'Count Quantity Expression', 'widgetType': QLineEdit, 'position': (6,0)},
        'FLAG_PossiblyNotRecieved': {'label': 'Possibly Not Received', 'widgetType': QCheckBox, 'position': (7,0)},
        'FLAG_MovementDuringCount': {'label': 'Movement During Count', 'widgetType': QCheckBox, 'position': (8,0)},
        'PKGID_Desc': {'label': 'Package ID/Description', 'widgetType': QLineEdit, 'position': (9,0)},
        'TAGQTY': {'label': 'Tag Quantity', 'widgetType': QLineEdit, 'position': (10,0)},
        'Notes': {'label': 'Notes', 'widgetType': QPlainTextEdit, 'position': (11,0)},
    }