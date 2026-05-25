from app.database import app_Session
from app.forms import std_id_def
from app.models import MaterialList


from PySide6.QtWidgets import QLineEdit, QPlainTextEdit
from calvincTools.utils import cSRFSingleRecordForm


class MaterialForm(cSRFSingleRecordForm):
    _ORMmodel = MaterialList
    _ssnmaker = app_Session
    _formname = 'Material Form'

    def defineFields(self):
        fieldDefs = {
            'id': std_id_def,
            'org': {'label': 'Organization', 'widget_type': QLineEdit, 'position': (1,0)},
            'Material': {'label': 'Material', 'widget_type': QLineEdit, 'position': (2,0)},
            'Description': {'label': 'Description', 'widget_type': QLineEdit, 'position': (3,0)},
            'PartType': {'label': 'Part Type', 'widget_type': QLineEdit, 'position': (4,0)},
            'SAPMaterialType': {'label': 'SAP Material Type', 'widget_type': QLineEdit, 'position': (5,0)},
            'SAPMaterialGroup': {'label': 'SAP Material Group', 'widget_type': QLineEdit, 'position': (6,0)},
            'SAPManuf': {'label': 'SAP Manufacturer', 'widget_type': QLineEdit, 'position': (7,0)},
            'SAPMPN': {'label': 'SAP MPN', 'widget_type': QLineEdit, 'position': (8,0)},
            'SAPABC': {'label': 'SAP ABC', 'widget_type': QLineEdit, 'position': (9,0)},
            'Price': {'label': 'Price', 'widget_type': QLineEdit, 'position': (10,0)},
            'TypicalContainerQty': {'label': 'Typical Container Qty', 'widget_type': QLineEdit, 'position': (11,0)},
            'TypicalPalletQty': {'label': 'Typical Pallet Qty', 'widget_type': QLineEdit, 'position': (12,0)},
            'PriceUnit': {'label': 'Price Unit', 'widget_type': QLineEdit, 'position': (13,0)},
            'Notes': {'label': 'Notes', 'widget_type': QPlainTextEdit, 'position': (14,0)},
        }
        retList = []
        for fieldname, fieldDef in fieldDefs.items():
            fieldDef['name'] = fieldname
            retList.append(fieldDef)
        return retList
    