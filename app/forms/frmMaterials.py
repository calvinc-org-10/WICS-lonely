from app.database import app_Session
from app.forms import std_id_def
from app.models import MaterialList


from PySide6.QtWidgets import QLineEdit, QPlainTextEdit
from calvincTools.utils import cSimpleRecordForm


class MaterialForm(cSimpleRecordForm):
    _ORMmodel = MaterialList
    _ssnmaker = app_Session
    _formname = 'Material Form'

    fieldDefs = {
        'id': std_id_def,
        'org': {'label': 'Organization', 'widgetType': QLineEdit, 'position': (1,0)},
        'Material': {'label': 'Material', 'widgetType': QLineEdit, 'position': (2,0)},
        'Description': {'label': 'Description', 'widgetType': QLineEdit, 'position': (3,0)},
        'PartType': {'label': 'Part Type', 'widgetType': QLineEdit, 'position': (4,0)},
        'SAPMaterialType': {'label': 'SAP Material Type', 'widgetType': QLineEdit, 'position': (5,0)},
        'SAPMaterialGroup': {'label': 'SAP Material Group', 'widgetType': QLineEdit, 'position': (6,0)},
        'SAPManuf': {'label': 'SAP Manufacturer', 'widgetType': QLineEdit, 'position': (7,0)},
        'SAPMPN': {'label': 'SAP MPN', 'widgetType': QLineEdit, 'position': (8,0)},
        'SAPABC': {'label': 'SAP ABC', 'widgetType': QLineEdit, 'position': (9,0)},
        'Price': {'label': 'Price', 'widgetType': QLineEdit, 'position': (10,0)},
        'TypicalContainerQty': {'label': 'Typical Container Qty', 'widgetType': QLineEdit, 'position': (11,0)},
        'TypicalPalletQty': {'label': 'Typical Pallet Qty', 'widgetType': QLineEdit, 'position': (12,0)},
        'PriceUnit': {'label': 'Price Unit', 'widgetType': QLineEdit, 'position': (13,0)},
        'Notes': {'label': 'Notes', 'widgetType': QPlainTextEdit, 'position': (14,0)},
    }