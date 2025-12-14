from app.database import app_Session
from app.forms import std_id_def
from app.models import WhsePartTypes


from PySide6.QtWidgets import QCheckBox, QLineEdit
from calvincTools.utils import cSimpleRecordForm


class PartTypesForm(cSimpleRecordForm):
    _ORMmodel = WhsePartTypes
    _ssnmaker = app_Session
    _formname = 'Warehouse Part Types Form'

    fieldDefs = {
        'id': std_id_def,
        'WhsePartType': {'label': 'Warehouse Part Type', 'widgetType': QLineEdit, 'position': (1,0)},
        'PartTypePriority': {'label': 'Part Type Priority', 'widgetType': QLineEdit, 'position': (2,0)},
        'InactivePartType': {'label': 'Inactive Part Type', 'widgetType': QCheckBox, 'position': (3,0)},
    }