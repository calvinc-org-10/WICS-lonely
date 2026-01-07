from app.database import app_Session
from app.forms import std_id_def
from app.models import CountSchedule


from PySide6.QtWidgets import QCheckBox, QDateEdit, QLineEdit, QPlainTextEdit
from calvincTools.utils import cSimpleRecordForm


class CountScheduleRecordForm(cSimpleRecordForm):
    _ORMmodel = CountSchedule
    _ssnmaker = app_Session
    _formname = 'Count Schedule Record Form'

    fieldDefs = {
        'id': std_id_def,
        'CountDate': {'label': 'Count Date', 'widgetType': QDateEdit, 'position': (1,0)},
        'Material': {'label': 'Material', 'widgetType': QLineEdit, 'position': (2,0)},
        'Counter': {'label': 'Counter', 'widgetType': QLineEdit, 'position': (3,0)},
        'Priority': {'label': 'Priority', 'widgetType': QLineEdit, 'position': (4,0)},
        'ReasonScheduled': {'label': 'Reason Scheduled', 'widgetType': QLineEdit, 'position': (5,0)},
        'Requestor': {'label': 'Requestor', 'widgetType': QLineEdit, 'position': (6,0)},
        'RequestFilled': {'label': 'Request Filled', 'widgetType': QCheckBox, 'position': (7,0)},
        'Notes': {'label': 'Notes', 'widgetType': QPlainTextEdit, 'position': (8,0)},
    }