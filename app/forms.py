# import datetime

from PySide6.QtWidgets import (
    QLabel, QLineEdit, QCheckBox, QPlainTextEdit, QDateEdit, 
    )
from cMenu.utils import (cSimpleRecordForm, )

from app.database import app_Session
from app.models import (MaterialList, ActualCounts, CountSchedule, WhsePartTypes, )
# from WICS.models import MaterialList, MfrPNtoMaterial, ActualCounts, CountSchedule, WhsePartTypes

from WICS.procs_misc import HolidayList


std_id_def = {'label': 'ID', 'widgetType': QLabel, 'noedit': True, 'readonly': True, 'position': (0,0)}


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
    

# class RequestCountScheduleRecordForm(cSimpleRecordForm):
#     id = forms.IntegerField(required=False, widget=forms.HiddenInput)
#     CountDate = forms.DateField(required=True, 
#         initial=calvindate().nextWorkdayAfter(extraNonWorkdayList=HolidayList(None)).as_datetime()    #TODO: find a workaround for this - HolidayList needs to know which db to query
#         )
#     Requestor = forms.CharField(max_length=100, required=True)
#       # the requestor can type whatever they want here, but WICS will record the userid behind-the-scenes
#     RequestFilled = forms.BooleanField(required=False, initial=False)
#     Material = forms.CharField(required=False)     # requestors cannot change Material; it's shown, but r/o
#     Counter = forms.CharField(required=False)
#     Priority = forms.CharField(max_length=50, required=False)
#     ReasonScheduled = forms.CharField(max_length=250, required=False)
#     Notes  = forms.CharField(required=False)

#     class Meta:
#         model = CountSchedule
#         fields = ['id', 'CountDate', 'Requestor', 'Counter', 'Priority', 'ReasonScheduled', 'Notes']
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#     def save(self, req:str|HttpRequest|User, savingUser = None) -> CountSchedule:
#         dbUsing = user_db(req)
#         dbmodel = self.Meta.model
#         required_fields = ['CountDate', 'Material', 'Requestor'] #id handled separately
#         PriK = self['id'].value()
#         M = MaterialList.objects.using(dbUsing).get(pk=self.data['Material']) 
#         if not str(PriK).isnumeric(): PriK = -1
#         existingrec = dbmodel.objects.using(dbUsing).filter(pk=PriK).exists()
#         if existingrec: rec = dbmodel.objects.using(dbUsing).get(pk=PriK)
#         else: rec = dbmodel()
#         for fldnm in self.changed_data + required_fields:
#             if fldnm=='id': continue
#             elif fldnm=='Material':
#                 setattr(rec,fldnm, M)
#             else:
#                 setattr(rec, fldnm, self.cleaned_data[fldnm])
#         rec.Requestor_userid = savingUser
        
#         rec.save(using=dbUsing)
#         return rec


################################
################################

# class RelatedMaterialInfo(cSimpleRecordForm):
#     Description = forms.CharField(max_length=250, disabled=True, required=False)
#     PartType = forms.ModelChoiceField(queryset=WhsePartTypes.objects.none(), empty_label=None, required=False)
#     TypicalContainerQty = forms.CharField(max_length=100,required=False)
#     TypicalPalletQty = forms.CharField(max_length=100,required=False)
#     Notes = forms.CharField(required=False)
#     class Meta:
#         model = MaterialList
#         fields = ['id', 'Description', 'PartType', 
#                 'TypicalContainerQty', 'TypicalPalletQty', 'Notes']

# class RelatedScheduleInfo(cSimpleRecordForm):
#     CountDate = forms.DateField(disabled=True, required=False)
#     Counter = forms.CharField(max_length=250, disabled=True, required=False)
#     Priority = forms.CharField(max_length=50, disabled=True, required=False)
#     ReasonScheduled = forms.CharField(max_length=250, disabled=True, required=False)
#     Notes = forms.CharField(max_length=250, disabled=True, required=False)
#     class Meta:
#         model = CountSchedule
#         fields = ['id', 'CountDate', 'Counter', 'Priority', 'ReasonScheduled', 
#                 'Notes']

############################################################
############################################################
############################################################

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
 
# class MaterialCountSummary(forms.Form):
#     Material = forms.CharField(max_length=100, disabled=True)
#     CountDate = forms.DateField(required=False, disabled=True)
#     CountQTY_Eval = forms.IntegerField(required=False, disabled=True)
#     SAPDate = forms.DateField(required=False, disabled=True)
#     SAPQty = forms.CharField(max_length=20, required=False, disabled=True)
#     Diff = forms.CharField(max_length=20, required=False, disabled=True)
#     Accuracy = forms.CharField(max_length=20, required=False, disabled=True)

# class MfrPNtoMaterialForm(forms.Form):
#     class Meta:
#         model = MfrPNtoMaterial
#         fields = ['id', 'MfrPN', 'Manufacturer', 'Material', 'Notes',]
#         # fields = '__all__'

############################################################
############################################################
############################################################

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
