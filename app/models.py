
from typing import Any
from sqlalchemy.orm import (DeclarativeBase, Mapped, mapped_column, relationship, Session, )
from sqlalchemy import (Column, Integer, MetaData, String, Boolean, ForeignKey, SmallInteger, UniqueConstraint, inspect, )
from sqlalchemy.exc import IntegrityError

from random import randint

from PySide6.QtCore import (QObject, )
from PySide6.QtWidgets import (QApplication, )
from .utils import (pleaseWriteMe, )

from .database import cMenu_Session
from .menucommand_constants import MENUCOMMANDS, COMMANDNUMBER
from .dbmenulist import (newgroupnewmenu_menulist, )


tblName_menuGroups = 'cMenu_menuGroups'
tblName_menuItems = 'cMenu_menuItems'
tblName_cParameters = 'cMenu_cParameters'
tblName_cGreetings = 'cMenu_cGreetings'


ix_naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
ix_metadata_obj = MetaData(naming_convention=ix_naming_convention)

class cMenuBase(DeclarativeBase):
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
    
    def getValue(self, field: str) -> Any:
        """
        Get the value of a field in the model instance.
        :param field: The name of the field to get.
        :return: The value of the field.
        """
        return getattr(self, field, None)

    # these look good on paper, but I need the caller to have control over the Session. Best to let caller do all the heavy lifting
    # def save(self, session: Session = cMenu_Session()):
    #     """
    #     Save the current instance to the database.
    #     :param session: Optional SQLAlchemy session to use for saving.
    #     If not provided, a new session will be created.
    #     """
    #     if session is None:
    #         session = cMenu_Session()
    #     try:
    #         session.add(self)
    #         session.commit()
    #     except IntegrityError:
    #         session.rollback()
    #         raise
    #     finally:
    #         session.close()
    
    # def delete(self, session: Session = cMenu_Session()) -> Any:
    #     """
    #     Delete the current instance from the database.
    #     :param session: Optional SQLAlchemy session to use for deletion.
    #     If not provided, a new session will be created.
    #     """
    #     if session is None:
    #         session = cMenu_Session()
    #     try:
    #         session.delete(self)
    #         session.commit()
    #         retval = True
    #     except IntegrityError as e:
    #         session.rollback()
    #         retval = e
    #     except Exception as e:
    #         session.rollback()
    #         retval = e
    #     finally:
    #         session.close()

    #     return retval

class menuGroups(cMenuBase):
    """
    id = models.AutoField(primary_key=True)
    GroupName = models.CharField(max_length=100, unique=True)
    GroupInfo = models.CharField(max_length=250, default="")
    """
    
    __tablename__ = tblName_menuGroups

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    GroupName: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    GroupInfo: Mapped[str] = mapped_column(String(250), default="", nullable=False)

    def __repr__(self) -> str:
        return f"<menuGroups(id={self.id}, GroupName='{self.GroupName}')>"

    def __str__(self) -> str:
        return f"{self.GroupName} ({self.GroupInfo})"

    @classmethod
    def _createtable(cls, engine):
        # Create tables if they don't exist
        cMenuBase.metadata.create_all(engine)

        session = Session(engine)
        try:
            # Check if any group exists
            if not session.query(cls).first():
                # Add starter group
                starter = cls(GroupName="Group Name", GroupInfo="Group Info")
                session.add(starter)
                session.commit()
                # Add default menu items for the starter group
                starter_id = starter.id
                menu_items = [
                    menuItems(
                        MenuGroup_id=starter_id, MenuID=0, OptionNumber=0, 
                        OptionText='New Menu', 
                        Command=None, Argument='Default', 
                        PWord='', TopLine=True, BottomLine=True
                        ),
                    menuItems(
                        MenuGroup_id=starter_id, MenuID=0, OptionNumber=11, 
                        OptionText='Edit Menu', 
                        Command=COMMANDNUMBER.EditMenu, Argument='', 
                        PWord='', TopLine=None, BottomLine=None
                        ),
                    menuItems(
                        MenuGroup_id=starter_id, MenuID=0, OptionNumber=19, 
                        OptionText='Change Password', 
                        Command=COMMANDNUMBER.ChangePW, Argument='', 
                        PWord='', TopLine=None, BottomLine=None
                        ),
                    menuItems(
                        MenuGroup_id=starter_id, MenuID=0, OptionNumber=20, 
                        OptionText='Go Away!', 
                        Command=COMMANDNUMBER.ExitApplication, Argument='', 
                        PWord='', TopLine=None, BottomLine=None
                        ),
                    ]
                session.add_all(menu_items)
                session.commit()
        except IntegrityError:
            session.rollback()
        finally:
            session.close()

        
class menuItems(cMenuBase):
    __tablename__ = tblName_menuItems
    _rltblFld = 'MenuGroup_id'
    _rltblName = tblName_menuGroups

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    MenuGroup_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{_rltblName}.id"))
    MenuID: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    OptionNumber: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    OptionText: Mapped[str] = mapped_column(String(250), nullable=False, default="")
    Command: Mapped[int] = mapped_column(Integer, nullable=True)
    Argument: Mapped[str] = mapped_column(String(250), nullable=False, default="")
    PWord: Mapped[str] = mapped_column(String(250), nullable=False, default="")
    TopLine: Mapped[bool] = mapped_column(nullable=True)
    BottomLine: Mapped[bool] = mapped_column(nullable=True)

    __table_args__ = (
        UniqueConstraint('MenuGroup_id', 'MenuID', 'OptionNumber'),     # Unique constraint for MenuGroup_id, MenuID, and OptionNumber
        {'sqlite_autoincrement': True, # Enable autoincrement for the primary key
         'extend_existing': True},
    )
    
    def __repr__(self) -> str:
        return f"<menuItems(id={self.id}, MenuID={self.MenuID}, OptionNumber={self.OptionNumber}, OptionText='{self.OptionText}')>"

    def __str__(self) -> str:
        return f"{self.OptionText} (ID: {self.MenuID}, Option: {self.OptionNumber})"

    def __init__(self, **kw: Any):
        """
        Initialize a new menuItems instance. If the menu table doesn't exist, it will be created.
        If the menuGroups table doesn't exist, it will also be created, and a starter group and menu will be added.
        :param kw: Keyword arguments for the menuItems instance.
        """
        inspector = inspect(cMenu_Session().get_bind())
        if not inspector.has_table(self.__tablename__):
            # If the table does not exist, create it
            cMenuBase.metadata.create_all(cMenu_Session().get_bind())
            # Optionally, you can also create a starter group and menu here
            menuGroups._createtable(cMenu_Session().get_bind())
        #endif not inspector.has_table():
        super().__init__(**kw)

    # @classmethod
    # def _createtable(cls, engine):
    #     cMenuBase.metadata.create_all(engine)


class cParameters(cMenuBase):
    __tablename__ = tblName_cParameters

    ParmName: Mapped[str] = mapped_column(String(100), primary_key=True)
    ParmValue: Mapped[str] = mapped_column(String(512), nullable=False)
    UserModifiable: Mapped[bool] = mapped_column(Boolean, nullable=False)
    Comments: Mapped[str] = mapped_column(String(512), nullable=False)

    def __repr__(self) -> str:
        return f"<cParameters(ParmName='{self.ParmName}')>"

    def __str__(self) -> str:
        return f"{self.ParmName} ({self.ParmValue})"

    # @classmethod
    # def _createtable(cls, engine):
    #     # Create tables if they don't exist
    #     cMenuBase.metadata.create_all(engine, cls.)

# def getcParm(req, parmname):
# use code like below instead
    # """
    # Get the value of a parameter from the cParameters table.
    # :param req: The request object (not used in this function).
    # :param parmname: The name of the parameter to retrieve.
    # :return: The value of the parameter or an empty string if not found.
    # """
    # session = cMenu_Session()
    # try:
    #     param = session.query(cParameters).filter_by(ParmName=parmname).first()
    #     return param.ParmValue if param else ''
    # finally:
    #     session.close()

# def setcParm(req, parmname, parmvalue):
    # """Set the value of a parameter in the cParameters table.
    # :param req: The request object (not used in this function).
    # :param parmname: The name of the parameter to set.
    # :param parmvalue: The value of the parameter to set.
    # """


class cGreetings(cMenuBase):
    """
    id = models.AutoField(primary_key=True)
    Greeting = models.CharField(max_length=2000)
    """
    __tablename__ = tblName_cGreetings

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Greeting: Mapped[str] = mapped_column(String(2000), nullable=False)
    __table_args__ = (
        {'sqlite_autoincrement': True,
         'extend_existing': True},
    )
    
    def __repr__(self) -> str:
        return f"<cGreetings(id='{self.id}', Greeting='{self.Greeting}')>"

    def __str__(self) -> str:
        return f"{self.Greeting} (ID: {self.id})"


cMenuBase.metadata.create_all(cMenu_Session().get_bind())
# Ensure that the tables are created when the module is imported
menuGroups._createtable(cMenu_Session().get_bind())
menuItems() #._createtable(cMenu_Session().get_bind())
cParameters() #._createtable(cMenu_Session().get_bind())
cGreetings() #._createtable(cMenu_Session().get_bind())

####################################################################################
####################################################################################
####################################################################################

from typing import Any
from django.contrib.auth.models import User
from django.db import connection, models
from django.db.models import F, Exists, OuterRef, Value, Case, When, Subquery, Max, Min, QuerySet
from django.db.models.functions import Concat
from django.http import HttpRequest
from userprofiles.models import WICSuser
from cMenu.utils import GroupConcat, dictfetchall, user_db

from .models_async_comm import *


# I'm quite happy with automaintained pk fields, so I don't specify any

class Organizations(models.Model):
    orgname = models.CharField(max_length=250)

    class Meta:
        ordering = ['orgname']

    def __str__(self) -> str:
        return f'{self.orgname}'
        # return super().__str__()

###########################################################
###########################################################

class WhsePartTypes(models.Model):
    WhsePartType = models.CharField(max_length=50)
    PartTypePriority = models.SmallIntegerField(null=True)
    InactivePartType = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ['WhsePartType']
        constraints = [
                models.UniqueConstraint(fields=['WhsePartType'], name='PTypeUNQ_PType'),
            ]

    def __str__(self) -> str:
        return f'{self.WhsePartType}'
        # return super().__str__()

###########################################################
###########################################################

##### Material_org prototype construction code cannot be
##### fn.  It involves an OuterRef, which anchors to its
##### Subquery.  Do not actually call this fn.  Use it as
##### a prototype for each instance.

def fnMaterial_org_constr(fld_matlName, fld_org, fld_orgname):
    return Case(
        When(Exists(MaterialList.objects.filter(Material=OuterRef(fld_matlName)).exclude(org=OuterRef(fld_org))),
            then=Concat(F(fld_matlName), Value(' ('), F(fld_orgname), Value(')'), output_field=models.CharField())
            ),
        default=F(fld_matlName)
        )

###########################################################
###########################################################

class MaterialList(models.Model):
    org = models.ForeignKey(Organizations, on_delete=models.RESTRICT, blank=True)
    Material = models.CharField(max_length=100)
    Description = models.CharField(max_length=250, blank=True, default='')
    PartType = models.ForeignKey(WhsePartTypes, null=True, on_delete=models.RESTRICT, default=None)
    Plant = models.CharField(max_length=20, null=True, blank=True, default='')
    SAPMaterialType = models.CharField(max_length=100, null=True, blank=True, default='')
    SAPMaterialGroup = models.CharField(max_length=100, null=True, blank=True, default='')
    SAPManuf = models.CharField(max_length=100, null=True, blank=True, default='')
    SAPMPN = models.CharField(max_length=100, null=True, blank=True, default='')
    SAPABC = models.CharField(max_length=5, null=True, blank=True, default='')
    Price = models.FloatField(null=True, blank=True, default=0.0)
    PriceUnit = models.PositiveIntegerField(null=True, blank=True, default=1)
    Currency = models.CharField(max_length=20, null=True, blank=True, default='')
    TypicalContainerQty = models.CharField(max_length=100, null=True, blank=True, default=None)
    TypicalPalletQty = models.CharField(max_length=100, null=True, blank=True, default=None)
    Notes = models.CharField(max_length=250, null=True, blank=True, default='')

    class Meta:
        ordering = ['org','Material']
        constraints = [
                models.UniqueConstraint(fields=['org', 'Material'],name="wics_materiallist_realpk"),
            ]
        indexes = [
            models.Index(fields=['Material']),
        ]

    def __str__(self) -> str:
        if MaterialList.objects.filter(Material=self.Material).exclude(org=self.org).exists():
            # there is a Material with this number in another org; specify this org
            # return str(self.Material) + ' (' + str(self.org) + ')'
            return f'{self.Material} ({self.org})'
        else:
            return f'{self.Material}'
class tmpMaterialListUpdate(models.Model):
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

class MaterialPhotos(models.Model):
    Material = models.ForeignKey(MaterialList, on_delete=models.RESTRICT)
    Photo = models.ImageField(upload_to='MatlImg/',height_field='height',width_field='width')
    height = models.IntegerField()
    width = models.IntegerField()
    Notes = models.CharField(max_length=250, null=True, blank=True, default='')
    
class VIEW_materials(models.Model):
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

class MfrPNtoMaterial(models.Model):
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

class CountSchedule(models.Model):
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

class ActualCounts(models.Model):
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

class SAP_SOHRecs(models.Model):
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

class UploadSAPResults(models.Model):
    errState = models.CharField(max_length=100, null=True)
    errmsg = models.CharField(max_length=512, null=True)
    rowNum = models.IntegerField(null=True)

    def __str__(self):
        return f'{self.errState}: {self.errmsg} at row {self.rowNum}'

class SAPPlants_org(models.Model):
    SAPPlant = models.CharField(max_length=20, primary_key=True)
    org = models.ForeignKey(Organizations, on_delete=models.RESTRICT, blank=False)

class UnitsOfMeasure(models.Model):
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

class WorksheetZones(models.Model):
    zone = models.IntegerField(primary_key=True)
    zoneName = models.CharField(max_length=10,blank=True)


class Location_WorksheetZone(models.Model):
    location = models.CharField(max_length=50,blank=False)
    zone = models.ForeignKey(WorksheetZones, on_delete=models.RESTRICT)

###########################################################
###########################################################

class WICSPermissions(models.Model):
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

