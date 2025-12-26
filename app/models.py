from typing import Any
from datetime import datetime, date

from sqlalchemy.orm import (DeclarativeBase, Mapped, mapped_column, relationship, Session, )
from sqlalchemy import (
    Column, MetaData, 
    Integer, String, Boolean, SmallInteger, Float, LargeBinary, Date,
    ForeignKey, UniqueConstraint, Index,
    inspect, 
    )
from sqlalchemy.exc import IntegrityError

# from random import randint

from PySide6.QtCore import (QObject, )
from PySide6.QtWidgets import (QApplication, )
# from cMenu.utils import (pleaseWriteMe, )

from .database import app_Session       # pylint: disable=relative-beyond-top-level      # this is correct

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

    # The list of all materials linked to this organization
    materials: Mapped[list["MaterialList"]] = relationship(
        "MaterialList", 
        back_populates="organization",
        cascade="all, delete-orphan" # Optional: deletes materials if the org is deleted
    )
    
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
    _rltblOrgName = Organizations.__tablename__
    _rltblPtTypFld = 'PartType_id'
    _rltblPtTypName = WhsePartTypes.__tablename__

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{_rltblOrgName}.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=True)
    Material : Mapped[str] = mapped_column(String(100), nullable=False)
    Description : Mapped[str] = mapped_column(String(250), nullable=False, default='')
    PartType_id : Mapped[int] = mapped_column(Integer, ForeignKey(f"{_rltblPtTypName}.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=True, default=None)
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

    # This allows self.organization to pull the actual Organizations object
    organization: Mapped["Organizations"] = relationship("Organizations", back_populates="materials", lazy="joined")
    
    __table_args__ = (
        UniqueConstraint('org_id', 'Material'),
        Index('ix_materiallist_material', Material),
        )

    @property
    def tupleOrgMaterial(self) -> tuple[str | None, str]:
        """Returns (Organization Name, Material Name)"""
        # Since org_id is nullable, we check if organization exists first
        org_name = self.organization.orgname if self.organization else None
        return (org_name, self.Material)
    
    def __repr__(self) -> str:
        return f'<MaterialList(id={self.id}, Material="{self.Material}", org_id={self.org_id})>'
    
    def __str__(self) -> str:
        # if MaterialList.objects.filter(Material=self.Material).exclude(org=self.org).exists():
        #     # there is a Material with this number in another org; specify this org
        #     # return str(self.Material) + ' (' + str(self.org) + ')'
        #     return f'{self.Material} ({self.org})'
        # else:
        return f'{self.tupleOrgMaterial[0]}={self.Material}'
class tmpMaterialListUpdate(cAppModelBase):

    __tablename__ = 'tmpmateriallistupdate'
    _rltblOrgFld = 'org_id'
    _rltblOrgName = Organizations.__tablename__
    _rltblMatlFld = 'MaterialLink'
    _rltblMatlName = MaterialList.__tablename__
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recStatus: Mapped[str] = mapped_column(String(32), nullable=True)      # Error, Add, Del
    errmsg: Mapped[str] = mapped_column(String(256), nullable=True)
    org_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{_rltblOrgName}.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=True)
    Material : Mapped[str] = mapped_column(String(100), nullable=False)
    MaterialLink: Mapped[int] = mapped_column(Integer, ForeignKey(f"{_rltblMatlName}.id", onupdate="CASCADE", ondelete="SET NULL"), nullable=True)
    Description : Mapped[str] = mapped_column(String(250), nullable=True)
    Plant : Mapped[str] = mapped_column(String(20), nullable=True, default='')
    SAPMaterialType : Mapped[str] = mapped_column(String(100), nullable=True)
    SAPMaterialGroup : Mapped[str] = mapped_column(String(100), nullable=True)
    SAPManuf : Mapped[str] = mapped_column(String(100), nullable=True, default='')
    SAPMPN : Mapped[str] = mapped_column(String(100), nullable=True, default='')
    SAPABC : Mapped[str] = mapped_column(String(5), nullable=True, default='')
    Price : Mapped[float] = mapped_column(Float, nullable=True)
    PriceUnit : Mapped[int] = mapped_column(Integer, nullable=True)
    Currency : Mapped[str] = mapped_column(String(20), nullable=True)
    delMaterialLink : Mapped[int] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint('org_id', 'Material', name='tmpmateriallistupdate_org_material_unq'),
        Index('ix_tmpmateriallistupdate_recstatus', recStatus),
        Index('ix_tmpmateriallistupdate_delmateriallink', delMaterialLink),
        )
    
    def __repr__(self) -> str:
        return f'<tmpMaterialListUpdate(id={self.id}, Material="{self.Material}", org={self.org_id})>'

    def __str__(self) -> str:
        return f'{self.Material}'
        
###########################################################
###########################################################

class CountSchedule(cAppModelBase):

    __tablename__ = 'countschedule'
    _rltblMatlFld = 'Material_id'
    _rltblMatlName = MaterialList.__tablename__
    
    # _rltblUserFld = 'Requestor_userid'
    # _rltblUserName = WICSuser.__tablename__
    #  why does Pylint get confused when it sees these commented-out lines? before Mapped[...] lines?

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    CountDate: Mapped[date] = mapped_column(Date, nullable=False)
    Material_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{_rltblMatlName}.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    Requestor: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    # do this when users implemented - Requestor_userid: Mapped[int] = mapped_column(Integer, ForeignKey(f"{WICSuser.__tablename__}.id"), onupdate="CASCADE", ondelete="SET NULL", nullable=True)
    Requestor_userid: Mapped[int] = mapped_column(Integer, nullable=True)
    RequestFilled: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    Counter: Mapped[str] = mapped_column(String(250), nullable=True, default=None)
    Priority: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    ReasonScheduled: Mapped[str] = mapped_column(String(250), nullable=True, default=None)
    Notes: Mapped[str] = mapped_column(String(250), nullable=True, default=None)

    Material: Mapped[MaterialList] = relationship(MaterialList, backref="count_schedules")
    
    __table_args__ = (
        UniqueConstraint('CountDate', 'Material_id', name='wics_countschedule_realpk'),
        Index('ix_countschedule_material', Material_id),
        Index('ix_countschedule_countdate', CountDate),
        )

    def __repr__(self) -> str:
        return f'<CountSchedule(id={self.id}, CountDate="{self.CountDate}", Material_id={self.Material_id})>'

    def __str__(self) -> str:
        # return str(self.pk) + ": " + str(self.CountDate) + " / " + str(self.Material) + " / " + str(self.Counter)

###########################################################
        return f'{self.id}: {self.CountDate:%Y-%m-%d}  / {self.Material} / {self.Counter}'
###########################################################

class ActualCounts(cAppModelBase):

    __tablename__ = 'actualcounts'
    _rltblMatlFld = 'Material_id'
    _rltblMatlName = MaterialList.__tablename__

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    CountDate: Mapped[date] = mapped_column(Date, nullable=False)
    CycCtID: Mapped[str] = mapped_column(String(100), nullable=True)
    Material_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{_rltblMatlName}.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    Counter: Mapped[str] = mapped_column(String(250), nullable=False)
    LocationOnly: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    CTD_QTY_Expr: Mapped[str] = mapped_column(String(500), nullable=True)
    LOCATION: Mapped[str] = mapped_column(String(250), nullable=False)
    PKGID_Desc: Mapped[str] = mapped_column(String(250), nullable=True)
    TAGQTY: Mapped[str] = mapped_column(String(250), nullable=True)
    FLAG_PossiblyNotRecieved: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    FLAG_MovementDuringCount: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    Notes: Mapped[str] = mapped_column(String(250), nullable=True)
    
    Material: Mapped[MaterialList] = relationship(MaterialList, backref="actual_counts", lazy="selectin")

    __table_args__ = (
        Index('ix_actualcounts_countdate_material', 'CountDate', 'Material_id'),
        Index('ix_actualcounts_material', Material_id),
        Index('ix_actualcounts_location', LOCATION),
        )    

    def __repr__(self) -> str:
        return f'<ActualCounts(id={self.id}, CountDate="{self.CountDate}", Material_id={self.Material_id}, LOCATION="{self.LOCATION}")>'
    
    def __str__(self) -> str:
        # return str(self.pk) + ": " + str(self.CountDate) + " / " + str(self.Material) + " / " + str(self.Counter) + " / " + str(self.LOCATION)
        return f'{self.id}: {self.CountDate:%Y-%m-%d}  / {self.Material} / {self.Counter} / {self.LOCATION}'


# def FoundAt(db_to_use:HttpRequest|User|str, matl = None):
#     # Django's generated SQL takes longer than I'd like.  I can do better, so...

#     # dbUsing = user_db(db_to_use)  # VIEW_actualcounts will do this

#     if matl is None:
#         Totalqs = VIEW_actualcounts(db_to_use).all()
#     else:
#         Totalqs = VIEW_actualcounts(db_to_use).filter(Material=matl)

#     FA_qs = Totalqs.order_by('Material_org', '-CountDate').values('Material', 'Material_org', 'CountDate').annotate(FoundAt=GroupConcat('LOCATION',distinct=True, ordering='LOCATION'))
#     return FA_qs

# def VIEW_LastFoundAtList(db_to_use:HttpRequest|User|str, matl=None):

#     dbUsing = user_db(db_to_use)
#     FA_qs = None

#     if (matl is not None) and (not matl):
#         matl = None

#     MaxDates = ActualCounts.objects.using(dbUsing).all().values('Material').annotate(MaxCtDt=Max('CountDate'))
#     FA_qs = VIEW_actualcounts(dbUsing).filter(
#                         CountDate = Subquery(MaxDates.filter(Material=OuterRef('Material')).values('MaxCtDt')[:1])
#                 )

#     if matl is not None:
#         try:
#             iter(matl)
#             FA_qs = FA_qs.filter(Material__in=matl)
#         except TypeError:
#             FA_qs = None

#     if FA_qs is None:
#         FA_qs = VIEW_actualcounts(dbUsing).filter(Material=matl)

#     LFAqs = FA_qs.annotate(FoundAt=F('LOCATION')).values('Material','Material_org','CountDate','FoundAt').distinct().order_by('Material__Material', 'Material__org', 'FoundAt') if FA_qs is not None else None

#     return LFAqs

###########################################################
###########################################################

class SAP_SOHRecs(cAppModelBase):

    __tablename__ = 'sap_sohrecs'
    _rltblMatlFld = 'Material_id'
    _rltblMatlName = MaterialList.__tablename__
    _rltblOrgFld = 'org_id'
    _rltblOrgName = Organizations.__tablename__

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uploaded_at: Mapped[date] = mapped_column(Date, nullable=False)
    org_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{_rltblOrgName}.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    MaterialPartNum: Mapped[str] = mapped_column(String(100), nullable=False)
    Material_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{_rltblMatlName}.id", onupdate="CASCADE", ondelete="SET NULL"), nullable=True)
    Description: Mapped[str] = mapped_column(String(250), nullable=True)
    Plant: Mapped[str] = mapped_column(String(20), nullable=True)
    MaterialType: Mapped[str] = mapped_column(String(50), nullable=True)
    StorageLocation: Mapped[str] = mapped_column(String(20), nullable=True)
    BaseUnitofMeasure: Mapped[str] = mapped_column(String(20), nullable=True)
    Amount: Mapped[float] = mapped_column(Float, nullable=True)
    Currency: Mapped[str] = mapped_column(String(20), nullable=True)
    ValueUnrestricted: Mapped[float] = mapped_column(Float, nullable=True)
    SpecialStock: Mapped[str] = mapped_column(String(20), nullable=True)
    Blocked: Mapped[float] = mapped_column(Float, nullable=True)
    ValueBlocked: Mapped[float] = mapped_column(Float, nullable=True)
    Batch: Mapped[str] = mapped_column(String(20), nullable=True)
    Vendor: Mapped[str] = mapped_column(String(20), nullable=True)
    
    Material: Mapped[MaterialList] = relationship(MaterialList, backref="sap_soh_recs", lazy="selectin")

    __table_args__ = (
        Index('ix_sap_sohrecs_uploadedat_org_materialpartnum', 'uploaded_at', 'org_id', 'MaterialPartNum'),
        Index('ix_sap_sohrecs_plant', 'Plant'),
        )
    
    def __repr__(self) -> str:
        return f'<SAP_SOHRecs(id={self.id}, uploaded_at="{self.uploaded_at}", org_id={self.org_id}, MaterialPartNum="{self.MaterialPartNum}")>' 
    def __str__(self) -> str:
        return f'{self.uploaded_at:%Y-%m-%d} / {self.org_id} / {self.MaterialPartNum}'
    
class UploadSAPResults(cAppModelBase):

    __tablename__ = 'uploadsapresults'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    errState: Mapped[str] = mapped_column(String(100), nullable=True)
    errmsg: Mapped[str] = mapped_column(String(512), nullable=True)
    rowNum: Mapped[int] = mapped_column(Integer, nullable=True)

    def __repr__(self):
        return f'<UploadSAPResults(id={self.id}, errState="{self.errState}", rowNum={self.rowNum})>'
    def __str__(self):
        return f'{self.errState}: {self.errmsg} at row {self.rowNum}'

class SAPPlants_org(cAppModelBase):

    __tablename__ = 'sapplants_org'
    _rltblOrgFld = 'org_id'
    _rltblOrgName = Organizations.__tablename__

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    SAPPlant: Mapped[str] = mapped_column(String(20), nullable=False)
    org_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{_rltblOrgName}.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)

    def __repr__(self) -> str:
        return f'<SAPPlants_org(id={self.id}, SAPPlant="{self.SAPPlant}", org_id={self.org_id})>'
    def __str__(self) -> str:
        return f'{self.SAPPlant} ({self.org_id})'

# TODO later    
# class UnitsOfMeasure(cAppModelBase):

#     __tablename__ = PUT_THE_TABLE_NAME_HERE

#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     UOM = models.CharField(max_length=50, unique=True)
#     UOMText = models.CharField(max_length=100, blank=True, default='')
#     DimensionText = models.CharField(max_length=100, blank=True, default='')
#     Multiplier1 = models.FloatField(default=1.0)

###########################################################
###########################################################

# TODO later
# class WorksheetZones(cAppModelBase):

#     __tablename__ = PUT_THE_TABLE_NAME_HERE

#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     zone = models.IntegerField(primary_key=True)
#     zoneName = models.CharField(max_length=10,blank=True)


# class Location_WorksheetZone(cAppModelBase):

#     __tablename__ = PUT_THE_TABLE_NAME_HERE

#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     location = models.CharField(max_length=50,blank=False)
#     zone = models.ForeignKey(WorksheetZones, on_delete=models.RESTRICT)

###########################################################
###########################################################

# class MaterialPhotos(cAppModelBase):

#     __tablename__ = 'materialphotos'
#     _rltblMatlFld = 'Material_id'
#     _rltblMatlName = MaterialList.__tablename__

#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     Material_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{_rltblMatlName}.id"), onupdate="CASCADE", ondelete="RESTRICT", nullable=False)
#     Photo: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
#     # use this object instead? Photo = models.ImageField(upload_to='MatlImg/',height_field='height',width_field='width')
#     height: Mapped[int] = mapped_column(Integer, nullable=False)
#     width: Mapped[int] = mapped_column(Integer, nullable=False)
#     Notes : Mapped[str] = mapped_column(String(250), nullable=False, default='')
    
# class MfrPNtoMaterial(cAppModelBase):

#     __tablename__ = PUT_THE_TABLE_NAME_HERE

#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     MfrPN = models.CharField(max_length=250, null=False)
#     Manufacturer = models.CharField(max_length=250, null=True, blank=True)
#     Material = models.ForeignKey(MaterialList, on_delete=models.CASCADE)
#     Notes = models.CharField(max_length=250, null=True, blank=True)

#     class Meta:
#         constraints = [
#                 models.UniqueConstraint(fields=['MfrPN'],name="wics_mfrpntomaterial_mfrpn_unq"),
#             ]
#         indexes = [
#             models.Index(fields=['Manufacturer']),
#         ]


#TODO later
# class WICSPermissions(cAppModelBase):
#     class Meta:
#         managed = False  # No database table creation or deletion  \
#                          # operations will be performed for this model.
#         default_permissions = () # disable "add", "change", "delete"
#                                  # and "view" default permissions
#         permissions = [
#             ('Material_onlyview', 'For restricting Material Form to view only'),
#         ]

###########################################################
###########################################################


####################################################################################
####################################################################################
####################################################################################

cAppModelBase.metadata.create_all(app_Session().get_bind())
# Ensure that the tables are created when the module is imported
