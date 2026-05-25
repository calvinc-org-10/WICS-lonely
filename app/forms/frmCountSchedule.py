from app.database import app_Session
from app.forms import std_id_def
from app.models import CountSchedule


from PySide6.QtWidgets import QCheckBox, QDateEdit, QLineEdit, QPlainTextEdit
from calvincTools.utils.forms import cSRFSingleRecordForm


class CountScheduleRecordForm(cSRFSingleRecordForm):
    _ORMmodel = CountSchedule
    _ssnmaker = app_Session
    _formname = 'Count Schedule Record Form'

    def defineFields(self):
        fieldDefs = {
            'id': std_id_def,
            'CountDate': {'label': 'Count Date', 'widget_type': QDateEdit, 'position': (1,0)},
            'Material': {'label': 'Material', 'widget_type': QLineEdit, 'position': (2,0)},
            'Counter': {'label': 'Counter', 'widget_type': QLineEdit, 'position': (3,0)},
            'Priority': {'label': 'Priority', 'widget_type': QLineEdit, 'position': (4,0)},
            'ReasonScheduled': {'label': 'Reason Scheduled', 'widget_type': QLineEdit, 'position': (5,0)},
            'Requestor': {'label': 'Requestor', 'widget_type': QLineEdit, 'position': (6,0)},
            'RequestFilled': {'label': 'Request Filled', 'widget_type': QCheckBox, 'position': (7,0)},
            'Notes': {'label': 'Notes', 'widget_type': QPlainTextEdit, 'position': (8,0)},
        }
        retList = []
        for fieldname, fieldDef in fieldDefs.items():
            fieldDef['name'] = fieldname
            retList.append(fieldDef)
        
        return retList
    