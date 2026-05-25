from app.database import app_Session
from app.forms import std_id_def
from app.models import WhsePartTypes


from PySide6.QtWidgets import QCheckBox, QLineEdit
from calvincTools.utils import cSRFSingleRecordForm


class PartTypesForm(cSRFSingleRecordForm):
    _ORMmodel = WhsePartTypes
    _ssnmaker = app_Session
    _formname = 'Warehouse Part Types Form'

    def defineFields(self):
        fieldDefs = {
            'id': std_id_def,
            'WhsePartType': {'label': 'Warehouse Part Type', 'widget_type': QLineEdit, 'position': (1,0)},
            'PartTypePriority': {'label': 'Part Type Priority', 'widget_type': QLineEdit, 'position': (2,0)},
            'InactivePartType': {'label': 'Inactive Part Type', 'widget_type': QCheckBox, 'position': (3,0)},
        }
        retList = []
        for fieldname, fieldDef in fieldDefs.items():
            fieldDef['name'] = fieldname
            retList.append(fieldDef)
        return retList
    # defineFields
    def end_of_class(self):
        pass
    