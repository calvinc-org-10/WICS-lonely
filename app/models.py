
from typing import Any
from sqlalchemy.orm import (DeclarativeBase, Mapped, mapped_column, relationship, Session, )
from sqlalchemy import (
    Column, MetaData, 
    Integer, String, Boolean, SmallInteger, Float,
    ForeignKey, UniqueConstraint, Index,
    inspect, 
    )
from sqlalchemy.exc import IntegrityError

# from random import randint

from PySide6.QtCore import (QObject, )
from PySide6.QtWidgets import (QApplication, )
# from cMenu.utils import (pleaseWriteMe, )

from .database import app_Session

ix_naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
ix_metadata_obj = MetaData(naming_convention=ix_naming_convention)

class cAppModelBase(DeclarativeBase):
    __abstract__ = True
    metadata = ix_metadata_obj
    # This class is used to define the base for SQLAlchemy models, if needed.
    # It can be extended with common methods or properties for all models.
    
    def setValue(self, field: str, value: Any):
        """
        Set a value for a field in the model instance.
        :param field: The name of the field to set.
        :param value: The value to set for the field.
        """
        setattr(self, field, value)
    # setValue()
    
    def getValue(self, field: str) -> Any:
        """
        Get the value of a field in the model instance.
        :param field: The name of the field to get.
        :return: The value of the field.
        """
        return getattr(self, field, None)
    # getValue()
# cAppModelBase

####################################################################################
####################################################################################
####################################################################################

class Organizations(cAppModelBase):

    __tablename__ = 'organizations'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    orgname: Mapped[str] = mapped_column(String(250), unique=True, nullable=False, default='')

    def __repr__(self) -> str:
        return f'<Organizations(id={self.id}, orgname="{self.orgname}")>'

    def __str__(self) -> str:
        return f'{self.orgname}'

###########################################################
###########################################################

class WhsePartTypes(cAppModelBase):

    __tablename__ = 'whseparttypes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    WhsePartType: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    PartTypePriority: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    InactivePartType: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)

    def __repr__(self) -> str:
        return f'<WhsePartTypes(id={self.id}, WhsePartType="{self.WhsePartType}")>'
    
    def __str__(self) -> str:
        return f'{self.WhsePartType}'
        # return super().__str__()

###########################################################
###########################################################

# ##### Material_org prototype construction code cannot be
# ##### fn.  It involves an OuterRef, which anchors to its
# ##### Subquery.  Do not actually call this fn.  Use it as
# ##### a prototype for each instance.

# def fnMaterial_org_constr(fld_matlName, fld_org, fld_orgname):
#     return Case(
#         When(Exists(MaterialList.objects.filter(Material=OuterRef(fld_matlName)).exclude(org=OuterRef(fld_org))),
#             then=Concat(F(fld_matlName), Value(' ('), F(fld_orgname), Value(')'), output_field=models.CharField())
#             ),
#         default=F(fld_matlName)
#         )

###########################################################
###########################################################

class MaterialList(cAppModelBase):

    __tablename__ = 'materiallist'
    _rltblOrgFld = 'org_id'
    _rltblOrgName = 'organizations'
    _rltblPtTypFld = 'PartType_id'
    _rltblPtTypName = 'whseparttypes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{_rltblOrgName}.id"), onupdate="CASCADE", ondelete="RESTRICT", nullable=True)
    Material : Mapped[str] = mapped_column(String(100), nullable=False)
    Description : Mapped[str] = mapped_column(String(250), nullable=False, default='')
    PartType_id : Mapped[int] = mapped_column(Integer, ForeignKey(f"{_rltblPtTypName}.id"), onupdate="CASCADE", ondelete="RESTRICT", nullable=True, default=None)
    Plant : Mapped[str] = mapped_column(String(20), nullable=True, default='')
    SAPMaterialType : Mapped[str] = mapped_column(String(100), nullable=True, default='')
    SAPMaterialGroup : Mapped[str] = mapped_column(String(100), nullable=True, default='')
    SAPManuf : Mapped[str] = mapped_column(String(100), nullable=True, default='')
    SAPMPN : Mapped[str] = mapped_column(String(100), nullable=True, default='')
    SAPABC : Mapped[str] = mapped_column(String(5), nullable=True, default='')
    Price : Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    PriceUnit : Mapped[int] = mapped_column(Integer, nullable=True, default=1)
    Currency : Mapped[str] = mapped_column(String(20), nullable=True, default='')
    TypicalContainerQty : Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    TypicalPalletQty : Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    Notes : Mapped[str] = mapped_column(String(250), nullable=False, default='')

    __table_args__ = (
        UniqueConstraint('org_id', 'Material'),
        Index('ix_materiallist_material', Material),
        )
    
    def __repr__(self) -> str:
        return f'<MaterialList(id={self.id}, Material="{self.Material}", org_id={self.org_id})>'
    
    def __str__(self) -> str:
        # if MaterialList.objects.filter(Material=self.Material).exclude(org=self.org).exists():
        #     # there is a Material with this number in another org; specify this org
        #     # return str(self.Material) + ' (' + str(self.org) + ')'
        #     return f'{self.Material} ({self.org})'
        # else:
        return f'{self.Material}'
class tmpMaterialListUpdate(cAppModelBase):

    __tablename__ = PUT_THE_TABLE_NAME_HERE

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recStatus = models.CharField(max_length=32, null=True, blank=True)      # Error, Add, Del
    errmsg = models.CharField(max_length=256, null=True, blank=True)
    org = models.ForeignKey(Organizations, on_delete=models.RESTRICT, blank=True, null=True)
    Material = models.CharField(max_length=100, blank=False)
    MaterialLink = models.ForeignKey(MaterialList, on_delete=models.SET_NULL, blank=True, null=True)
    Description = models.CharField(max_length=250, blank=True, null=True)
    Plant = models.CharField(max_length=20, null=True, blank=True, default='')
    SAPMaterialType = models.CharField(max_length=100, null=True, blank=True)
    SAPMaterialGroup = models.CharField(max_length=100, null=True, blank=True)
    SAPManuf = models.CharField(max_length=100, null=True, blank=True, default='')
    SAPMPN = models.CharField(max_length=100, null=True, blank=True, default='')
    SAPABC = models.CharField(max_length=5, null=True, blank=True, default='')
    Price = models.FloatField(null=True, blank=True)
    PriceUnit = models.PositiveIntegerField(null=True, blank=True)
    Currency = models.CharField(max_length=20, null=True, blank=True)
    delMaterialLink = models.IntegerField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=['org','Material']),
            models.Index(fields=['recStatus']),
            models.Index(fields=['delMaterialLink']),
            ]

class MaterialPhotos(cAppModelBase):

    __tablename__ = PUT_THE_TABLE_NAME_HERE

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Material = models.ForeignKey(MaterialList, on_delete=models.RESTRICT)
    Photo = models.ImageField(upload_to='MatlImg/',height_field='height',width_field='width')
    height = models.IntegerField()
    width = models.IntegerField()
    Notes = models.CharField(max_length=250, null=True, blank=True, default='')
    
class VIEW_materials(cAppModelBase):

    __tablename__ = PUT_THE_TABLE_NAME_HERE

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id = models.PositiveIntegerField(primary_key=True)
    org = models.ForeignKey(Organizations, on_delete=models.RESTRICT, blank=True, null=True)
    Material = models.CharField(max_length=100)
    Description = models.CharField(max_length=250, blank=True, default='')
    PartType = models.ForeignKey(WhsePartTypes, null=True, on_delete=models.RESTRICT, default=None)
    Plant = models.CharField(max_length=20, blank=True, default='')
    SAPMaterialType = models.CharField(max_length=100, blank=True, default='')
    SAPMaterialGroup = models.CharField(max_length=100, blank=True, default='')
    SAPManuf = models.CharField(max_length=100, null=True, blank=True, default='')
    SAPMPN = models.CharField(max_length=100, null=True, blank=True, default='')
    SAPABC = models.CharField(max_length=5, null=True, blank=True, default='')
    Price = models.FloatField(null=True, blank=True, default=0.0)
    PriceUnit = models.PositiveIntegerField(null=True, blank=True, default=1)
    Currency = models.CharField(max_length=20, blank=True, default='')
    TypicalContainerQty = models.CharField(max_length=100, null=True, blank=True, default=None)
    TypicalPalletQty = models.CharField(max_length=100, null=True, blank=True, default=None)
    Notes = models.CharField(max_length=250, blank=True, default='')
    PartTypeName = models.CharField(max_length=50,db_column='PartType')
    OrgName = models.CharField(max_length=250)
    LastCountDate = models.DateField()
    LastFoundAt = models.CharField(max_length=4096)
    Material_org =  models.CharField(max_length=100)
    NextScheduledCount = models.DateField()
    ScheduledForToday = models.BooleanField()

    class Meta:
       db_table = 'VIEW_materials'
       managed = False

class MfrPNtoMaterial(cAppModelBase):

    __tablename__ = PUT_THE_TABLE_NAME_HERE

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    MfrPN = models.CharField(max_length=250, null=False)
    Manufacturer = models.CharField(max_length=250, null=True, blank=True)
    Material = models.ForeignKey(MaterialList, on_delete=models.CASCADE)
    Notes = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        constraints = [
                models.UniqueConstraint(fields=['MfrPN'],name="wics_mfrpntomaterial_mfrpn_unq"),
            ]
        indexes = [
            models.Index(fields=['Manufacturer']),
        ]

###########################################################
###########################################################

class CountSchedule(cAppModelBase):

    __tablename__ = PUT_THE_TABLE_NAME_HERE

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    CountDate = models.DateField(null=False)
    Material = models.ForeignKey(MaterialList, on_delete=models.RESTRICT)
    Requestor = models.CharField(max_length=100, null=True, blank=True)
      # the requestor can type whatever they want here, but WICS will record the userid behind-the-scenes
    Requestor_userid = models.ForeignKey(WICSuser, on_delete=models.SET_NULL, null=True)
    RequestFilled = models.BooleanField(null=True, default=0)
    Counter = models.CharField(max_length=250, null=True, blank=True)
    Priority = models.CharField(max_length=50, null=True, blank=True)
    ReasonScheduled = models.CharField(max_length=250, null=True, blank=True)
    Notes = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        ordering = ['CountDate', 'Material']
        constraints = [
                models.UniqueConstraint(fields=['CountDate', 'Material'], name="wics_countschedule_realpk"),
            ]
        indexes = [
            models.Index(fields=['Material']),
            models.Index(fields=['CountDate']),
        ]

    def __str__(self) -> str:
        # return str(self.pk) + ": " + str(self.CountDate) + " / " + str(self.Material) + " / " + str(self.Counter)
        return f'{self.pk}: {self.CountDate:%Y-%m-%d}  / {self.Material} / {self.Counter}'
        # return super().__str__()

def VIEW_countschedule(db_to_use:HttpRequest|User|str) -> QuerySet:

    dbUsing = user_db(db_to_use)

    qs = CountSchedule.objects.using(dbUsing).all()
    qs = qs.annotate(
            Material_org = Case(
                When(Exists(MaterialList.objects.using(dbUsing).filter(Material=OuterRef('Material__Material')).exclude(org=OuterRef('Material__org'))),
                    then=Concat(F('Material__Material'), Value(' ('), F('Material__org__orgname'), Value(')'), output_field=models.CharField())
                    ),
                default=F('Material__Material')
                )
            )
    qs = qs.annotate(Description = F('Material__Description'),
                    MaterialNotes = F('Material__Notes'),
                    ScheduleNotes = F('Notes')
            )

    return qs

###########################################################
###########################################################

class ActualCounts(cAppModelBase):

    __tablename__ = PUT_THE_TABLE_NAME_HERE

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    CountDate = models.DateField(null=False, blank=False)
    CycCtID = models.CharField(max_length=100, null=True, blank=True)
    Material = models.ForeignKey(MaterialList, on_delete=models.RESTRICT)
    Counter = models.CharField(max_length=250, blank=False, null=False)
    LocationOnly = models.BooleanField(blank=True, default=False)
    CTD_QTY_Expr = models.CharField(max_length=500, null=True, blank=True)
    LOCATION = models.CharField(max_length=250, blank=False)
    PKGID_Desc = models.CharField(max_length=250, null=True, blank=True)
    TAGQTY = models.CharField(max_length=250, null=True, blank=True)
    FLAG_PossiblyNotRecieved = models.BooleanField(blank=True, default=False)
    FLAG_MovementDuringCount = models.BooleanField(blank=True, default=False)
    Notes = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        ordering = ['CountDate', 'Material']
        indexes = [
            models.Index(fields=['CountDate','Material']),
            models.Index(fields=['Material']),
            models.Index(fields=['LOCATION']),
        ]

    def __str__(self) -> str:
        # return str(self.pk) + ": " + str(self.CountDate) + " / " + str(self.Material) + " / " + str(self.Counter) + " / " + str(self.LOCATION)
        return f'{self.pk}: {self.CountDate:%Y-%m-%d}  / {self.Material} / {self.Counter} / {self.LOCATION}'
        # return super().__str__()


def VIEW_actualcounts(db_to_use:HttpRequest|User|str) -> QuerySet:

    dbUsing = user_db(db_to_use)

    qs = ActualCounts.objects.using(dbUsing).all()
    qs = qs.annotate(
            Material_org=Case(
                When(Exists(MaterialList.objects.using(dbUsing).filter(Material=OuterRef('Material__Material')).exclude(org=OuterRef('Material__org'))),
                    then=Concat(F('Material__Material'), Value(' ('), F('Material__org__orgname'), Value(')'), output_field=models.CharField())
                    ),
                default=F('Material__Material')
                )
            )
    qs = qs.annotate(Description = F('Material__Description'))
    qs = qs.annotate(MaterialNotes = F('Material__Notes'))
    qs = qs.annotate(CountNotes = F('Notes'))

    return qs

def FoundAt(db_to_use:HttpRequest|User|str, matl = None):
    # Django's generated SQL takes longer than I'd like.  I can do better, so...

    # dbUsing = user_db(db_to_use)  # VIEW_actualcounts will do this

    if matl is None:
        Totalqs = VIEW_actualcounts(db_to_use).all()
    else:
        Totalqs = VIEW_actualcounts(db_to_use).filter(Material=matl)

    FA_qs = Totalqs.order_by('Material_org', '-CountDate').values('Material', 'Material_org', 'CountDate').annotate(FoundAt=GroupConcat('LOCATION',distinct=True, ordering='LOCATION'))
    return FA_qs

def VIEW_LastFoundAtList(db_to_use:HttpRequest|User|str, matl=None):

    dbUsing = user_db(db_to_use)
    FA_qs = None

    if (matl is not None) and (not matl):
        matl = None

    MaxDates = ActualCounts.objects.using(dbUsing).all().values('Material').annotate(MaxCtDt=Max('CountDate'))
    FA_qs = VIEW_actualcounts(dbUsing).filter(
                        CountDate = Subquery(MaxDates.filter(Material=OuterRef('Material')).values('MaxCtDt')[:1])
                )

    if matl is not None:
        try:
            iter(matl)
            FA_qs = FA_qs.filter(Material__in=matl)
        except TypeError:
            FA_qs = None

    if FA_qs is None:
        FA_qs = VIEW_actualcounts(dbUsing).filter(Material=matl)

    LFAqs = FA_qs.annotate(FoundAt=F('LOCATION')).values('Material','Material_org','CountDate','FoundAt').distinct().order_by('Material__Material', 'Material__org', 'FoundAt') if FA_qs is not None else None

    return LFAqs

###########################################################
###########################################################

class SAP_SOHRecs(cAppModelBase):

    __tablename__ = PUT_THE_TABLE_NAME_HERE

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uploaded_at = models.DateField()
    org = models.ForeignKey(Organizations, on_delete=models.RESTRICT, blank=True)
    MaterialPartNum = models.CharField(max_length=100)
    Material = models.ForeignKey(MaterialList,on_delete=models.SET_NULL,null=True)
    Description = models.CharField(max_length=250, null=True, blank=True)
    Plant = models.CharField(max_length=20, null=True, blank=True)
    MaterialType = models.CharField(max_length=50, null=True, blank=True)
    StorageLocation = models.CharField(max_length=20, null=True, blank=True)
    BaseUnitofMeasure = models.CharField(max_length=20, null=True, blank=True)
    Amount = models.FloatField(null=True, blank=True)
    Currency = models.CharField(max_length=20, null=True, blank=True)
    ValueUnrestricted = models.FloatField(null=True, blank=True)
    SpecialStock = models.CharField(max_length=20, null=True, blank=True)
    Blocked = models.FloatField(blank=True, null=True)
    ValueBlocked = models.FloatField(blank=True, null=True)
    Batch = models.CharField(max_length=20, blank=True, null=True)
    Vendor = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        get_latest_by = 'uploaded_at'
        ordering = ['uploaded_at', 'org', 'MaterialPartNum']
        indexes = [
            models.Index(fields=['uploaded_at', 'org', 'MaterialPartNum']),
            models.Index(fields=['Plant']),
        ]

class UploadSAPResults(cAppModelBase):

    __tablename__ = PUT_THE_TABLE_NAME_HERE

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    errState = models.CharField(max_length=100, null=True)
    errmsg = models.CharField(max_length=512, null=True)
    rowNum = models.IntegerField(null=True)

    def __str__(self):
        return f'{self.errState}: {self.errmsg} at row {self.rowNum}'

class SAPPlants_org(cAppModelBase):

    __tablename__ = PUT_THE_TABLE_NAME_HERE

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    SAPPlant = models.CharField(max_length=20, primary_key=True)
    org = models.ForeignKey(Organizations, on_delete=models.RESTRICT, blank=False)

class UnitsOfMeasure(cAppModelBase):

    __tablename__ = PUT_THE_TABLE_NAME_HERE

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    UOM = models.CharField(max_length=50, unique=True)
    UOMText = models.CharField(max_length=100, blank=True, default='')
    DimensionText = models.CharField(max_length=100, blank=True, default='')
    Multiplier1 = models.FloatField(default=1.0)

def VIEW_SAP(db_to_use:HttpRequest|User|str):
    dbUsing = user_db(db_to_use)

    return SAP_SOHRecs.objects.using(dbUsing).all()\
        .annotate(
            Material_org=Case(
                When(Exists(MaterialList.objects.using(dbUsing).filter(Material=OuterRef('MaterialPartNum')).exclude(org=OuterRef('org'))),
                    then=Concat(F('MaterialPartNum'), Value(' ('), F('org__orgname'), Value(')'), output_field=models.CharField())
                    ),
                default=F('MaterialPartNum')
                ),
            Description = F('Material__Description'),
            Notes = F('Material__Notes'),
            mult = Subquery(UnitsOfMeasure.objects.using(dbUsing).filter(UOM=OuterRef('BaseUnitofMeasure')).values('Multiplier1')[:1])
            )
            # do I need to annotate OrgName?

###########################################################
###########################################################

class WorksheetZones(cAppModelBase):

    __tablename__ = PUT_THE_TABLE_NAME_HERE

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    zone = models.IntegerField(primary_key=True)
    zoneName = models.CharField(max_length=10,blank=True)


class Location_WorksheetZone(cAppModelBase):

    __tablename__ = PUT_THE_TABLE_NAME_HERE

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    location = models.CharField(max_length=50,blank=False)
    zone = models.ForeignKey(WorksheetZones, on_delete=models.RESTRICT)

###########################################################
###########################################################

class WICSPermissions(cAppModelBase):
    class Meta:
        managed = False  # No database table creation or deletion  \
                         # operations will be performed for this model.
        default_permissions = () # disable "add", "change", "delete"
                                 # and "view" default permissions
        permissions = [
            ('Material_onlyview', 'For restricting Material Form to view only'),
        ]

###########################################################
###########################################################


####################################################################################
####################################################################################
####################################################################################

cAppModelBase.metadata.create_all(cMenu_Session().get_bind())
# Ensure that the tables are created when the module is imported
menuGroups._createtable(cMenu_Session().get_bind())
menuItems() #._createtable(cMenu_Session().get_bind())
cParameters() #._createtable(cMenu_Session().get_bind())
cGreetings() #._createtable(cMenu_Session().get_bind())

