"""
code that's being auditioned
"""
from typing import (Any, )
from datetime import (date, )

from PySide6.QtCore import (
    Slot, Signal,
    QDate, 
    )
from PySide6.QtGui import (
    QDragEnterEvent, QDropEvent,
    )
from PySide6.QtWidgets import (
    QWidget,
    QPushButton, QLabel, QCheckBox, QCalendarWidget,
    QGroupBox, QScrollArea,
    QHBoxLayout, QVBoxLayout, QFileDialog,
    )

from sqlalchemy import select, and_, or_, literal_column
from sqlalchemy.orm import aliased

from calvincTools.utils import (
    Excelfile_fromqs, 
)

from mathematical_expressions_parser.eval import evaluate

from app.database import (Repository, get_app_sessionmaker, get_app_session, )
from app.models import (
    ActualCounts, CountSchedule, SAP_SOHRecs, MaterialList, Organizations,
    # UnitsOfMeasure,
    )


# these probably should be part of rptCountSummary, but for now, leaving them here
def CreateOutputRows(raw_qs, SAP_SOH, Excel_qdict, Eval_CTDQTY=True):
    """
    Create output rows for Count Summary report
    raw_qs: queryset of ActualCounts records
    SAP_SOH: dict as returned by fnSAPList
    Eval_CTDQTY: if True, evaluate the CTD_QTY_Expr field; if False, just put in '----'
    """
    outputrows = []
    lastrow = {}
    
    def SummaryLine(lastrow):
        # summarize last Matl
        # total SAP Numbers
        SAPTot = 0
        outputline = dict()
        outputline['type'] = 'Summary'
        outputline['SAPNum'] = []
        for SAProw in SAP_SOH['SAPTable'].filter(Material_id=lastrow['Material_id']):
            outputline['SAPNum'].append((SAProw.StorageLocation, SAProw.Amount, SAProw.BaseUnitofMeasure))
            SAPTot += SAProw.Amount*SAProw.mult
        outputline['TypicalContainerQty'] = lastrow['TypicalContainerQty']
        outputline['TypicalPalletQty'] = lastrow['TypicalPalletQty']
        outputline['OrgName'] = lastrow['OrgName']
        outputline['Material'] = lastrow['Material']
        outputline['Material_id'] = lastrow['Material_id']
        outputline['Description'] = lastrow['Description']
        outputline['SchedCounter'] = lastrow['SchedCounter']
        outputline['Counters'] = lastrow['Counters']
        outputline['Requestor'] = lastrow['Requestor']
        outputline['RequestFilled'] = lastrow['RequestFilled']
        outputline['PartType'] = lastrow['PartType']
        outputline['CountTotal'] = lastrow['TotalCounted']
        outputline['SAPTotal'] = int(SAPTot)
        outputline['Diff'] = int(lastrow['TotalCounted'] - SAPTot)
        divsr = 1
        if lastrow['TotalCounted']!=0 or SAPTot!=0: divsr = max(lastrow['TotalCounted'], SAPTot)
        outputline['Accuracy'] = min(lastrow['TotalCounted'], SAPTot) / divsr * 100
        outputline['ReasonScheduled'] = lastrow['ReasonScheduled']
        outputline['SchedNotes'] = lastrow['SchedNotes']
        outputline['MatlNotes'] = lastrow['MatlNotes']
        #outputrows.append(outputline)

        return outputline
    # end def SummaryLine

    def CreateLastrow(rawrow):
        lastrow = dict()
        lastrow['OrgName'] = rawrow.OrgName
        lastrow['Material'] = rawrow.Matl_PartNum
        lastrow['Material_id'] = rawrow.matl_id
        lastrow['Description'] = rawrow.Description
        lastrow['SchedCounter'] = rawrow.cs_Counter
        lastrow['Counters'] = rawrow.ac_Counter if rawrow.ac_Counter is not None else ''
        lastrow['Requestor'] = rawrow.Requestor
        lastrow['RequestFilled'] = rawrow.RequestFilled
        lastrow['PartType'] = rawrow.PartType
        lastrow['TotalCounted'] = 0
        lastrow['SchedNotes'] = rawrow.cs_Notes
        lastrow['TypicalContainerQty'] = rawrow.TypicalContainerQty
        lastrow['TypicalPalletQty'] = rawrow.TypicalPalletQty
        lastrow['MatlNotes'] = rawrow.mtl_Notes
        lastrow['ReasonScheduled'] = rawrow.cs_ReasonScheduled

        return lastrow
    # end def CreateLastRow

    def DetailLine(rawrow, Eval_CTDQTY=True):
        outputline = dict()
        outputline['type'] = 'Detail'
        outputline['CycCtID'] = rawrow.ac_CycCtID
        outputline['Material'] = rawrow.Matl_PartNum
        outputline['Material_id'] = rawrow.matl_id
        outputline['org_id'] = rawrow.org_id
        outputline['orgName'] = rawrow.OrgName
        outputline['ActCounter'] = rawrow.ac_Counter
        if rawrow.ac_Counter is not None and rawrow.ac_Counter not in lastrow['Counters']:
            lastrow['Counters'] += ', ' + rawrow.ac_Counter
        outputline['LOCATION'] = rawrow.ac_LOCATION
        outputline['PKGID'] = rawrow.ac_PKGID_Desc
        outputline['TAGQTY'] = rawrow.ac_TAGQTY
        outputline['PossNotRec'] = rawrow.FLAG_PossiblyNotRecieved
        outputline['MovDurCt'] = rawrow.FLAG_MovementDuringCount
        outputline['CTD_QTY_Expr'] = rawrow.ac_CTD_QTY_Expr
        if Eval_CTDQTY:
            try:
                outputline['CTD_QTY_Eval'] = evaluate(rawrow.ac_CTD_QTY_Expr)
                # do next line at caller
                # lastrow['TotalCounted'] += outputline['CTD_QTY_Eval']
            except Exception:   # pylint: disable=broad-exception-caught   # catch any exceptions from evaluate
                # Exception('bad expression:'+rawrow.ac_CTD_QTY_Expr)
                outputline['CTD_QTY_Eval'] = "????"
        else:
            outputline['CTD_QTY_Eval'] = "----"
        outputline['ActCountNotes'] = rawrow.ac_Notes
        # outputrows.append(outputline)

        return outputline
    #end def DetailLine
    
    outputrows = []
    lastrow = {'Material_id': None}
    for rawrow in raw_qs:
        if rawrow.matl_id != lastrow['Material_id']:     # new Matl
            if outputrows:
                SmLine = SummaryLine(lastrow)
                outputrows.append(SmLine)
                Excel_qdict.append(
                    {key:SmLine[key] 
                        for key in ['OrgName','Material','PartType','Description','CountTotal','SAPTotal','Diff','Accuracy','Counters']
                    })
            # no else -  if outputrows is empty, this is the first row, so keep going

            # this new material is now the "old" one; save values for when it switches, and we do the above block
            # this whole block becomes
            lastrow = CreateLastrow(rawrow)
        #endif

        # process this row
        outputline = DetailLine(rawrow, Eval_CTDQTY)
        outputrows.append(outputline)
        assert isinstance(lastrow['TotalCounted'], (int,float)), "lastrow['TotalCounted'] is not numeric"
        if isinstance(outputline['CTD_QTY_Eval'],(int,float)): 
            lastrow['TotalCounted'] += outputline['CTD_QTY_Eval']     # type: ignore
    # endfor
    # need to do the summary on the last row
    if outputrows:
        # summarize last Matl
        SmLine = SummaryLine(lastrow)
        outputrows.append(SmLine)
        Excel_qdict.append(
            {key:SmLine[key] 
                for key in ['OrgName','Material','PartType','Description','CountTotal','SAPTotal','Diff','Accuracy','Counters']
            })
    
    return outputrows
# end def CreateOutputRows
class  rptCountSummary(QWidget):
    """
    Count Summary Report
    
    A lot of the original WICS code is preserved. That's why, for instance, outputlines dictionary is built 
    and then later parsed to create the report, instead of just building the report directly.
    
    """
    _formname = "Count Summary"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(self._formname)
        myLayout = QVBoxLayout(self)
        lblResultsTitle = QLabel(self._formname)
        myLayout.addWidget(lblResultsTitle)
        
        wdgtCountDate = QWidget()
        layoutCountDate = QHBoxLayout(wdgtCountDate)
        lblCountDate = QLabel("Count Date: N/A")
        self.clndrCountDate = QCalendarWidget()
        self.clndrCountDate.setGridVisible(True)
        self.clndrCountDate.setMinimumDate(QDate(2000,1,1))
        self.clndrCountDate.setMaximumDate(QDate(2199,12,31))
        layoutCountDate.addWidget(lblCountDate)
        layoutCountDate.addWidget(self.clndrCountDate)


        wdgtMainArea = QWidget()
        self.layoutMainArea = QVBoxLayout(wdgtMainArea)
        wdgtScrollArea = QScrollArea()
        wdgtScrollArea.setWidgetResizable(True)
        wdgtScrollArea.setWidget(wdgtMainArea)
        myLayout.addWidget(wdgtScrollArea)

        self.Excel_qdict = []

        # statusVal = Repository(get_app_sessionmaker(), UploadSAPResults).get_all(
        #     UploadSAPResults.errState == 'nRowsTotal'
        # )
        # nRowsRead = statusVal[0].rowNum - 1 if statusVal else 0     # -1 because header doesn't count
        # statusVal = Repository(get_app_sessionmaker(), UploadSAPResults).get_all(
        #     UploadSAPResults.errState == 'nRowsAdded'
        # )
        # nRowsAdded = statusVal[0].rowNum if statusVal else 0
        # statusVal = Repository(get_app_sessionmaker(), UploadSAPResults).get_all(
        #     UploadSAPResults.errState == 'nRowsErrors'
        # )
        # nRowsErrors = statusVal[0].rowNum if statusVal else 0
        # statusVal = Repository(get_app_sessionmaker(), UploadSAPResults).get_all(
        #     UploadSAPResults.errState == 'nRowsIgnored'
        # )
        # nRowsNoMaterial = statusVal[0].rowNum if statusVal else 0
        
        # UplResults = Repository(get_app_sessionmaker(), UploadSAPResults).get_all(
        #     UploadSAPResults.errState.notin_(['nRowsAdded','nRowsTotal','nRowsErrors','nRowsIgnored'])
        # )
        # lblSummary = QLabel(f"Upload Summary: {nRowsRead} rows read, {nRowsAdded} rows added, {nRowsErrors} rows with errors, {nRowsNoMaterial} rows ignored (no material).")
        # layoutMainArea.addWidget(lblSummary)
        
        # for res in UplResults:
        #     rstr = f"{res.errState}: {res.errmsg}" if 'error' in res.errState else f"Count Record {res.errmsg} added"
        #     lblrslt = QLabel(rstr)
        #     layoutMainArea.addWidget(lblrslt)
    # __init__
    
    def buildReport(self, Rptvariation = None):
        """
        Build the report for the selected date
        """
        def buildFieldList(ac, cs, mtl) -> list[Any]:
            fld_list = [
                literal_column("0").label("id"),
                cs.id.label("cs_id"),
                cs.CountDate.label("cs_CountDate"),
                cs.Counter.label("cs_Counter"),
                cs.Priority.label("cs_Priority"),
                cs.ReasonScheduled.label("cs_ReasonScheduled"),
                cs.Requestor,
                cs.RequestFilled,
                cs.Notes.label("cs_Notes"),
                ac.c.id.label("ac_id"),
                ac.c.CountDate.label("ac_CountDate"),
                ac.c.CycCtID.label("ac_CycCtID"),
                ac.c.Counter.label("ac_Counter"),
                ac.c.LocationOnly.label("ac_LocationOnly"),
                ac.c.CTD_QTY_Expr.label("ac_CTD_QTY_Expr"),
                ac.c.LOCATION.label("ac_LOCATION"),
                ac.c.PKGID_Desc.label("ac_PKGID_Desc"),
                ac.c.TAGQTY.label("ac_TAGQTY"),
                ac.c.FLAG_PossiblyNotRecieved,
                ac.c.FLAG_MovementDuringCount,
                ac.c.Notes.label("ac_Notes"),
                mtl.id.label("matl_id"),
                mtl.org_id,
                mtl.OrgName,
                mtl.Material_org.label("Matl_PartNum"),
                mtl.PartType.label("PartType"),
                mtl.Description,
                mtl.TypicalContainerQty,
                mtl.TypicalPalletQty,
                mtl.Notes.label("mtl_Notes"),
            ]
            return fld_list
        # buildFieldList
            
        countDate = self.clndrCountDate.selectedDate().toPython()
        assert isinstance(countDate, date), "countDate is not a date"
        SAP_SOH = fnSAPList(countDate)
        SummaryReport = []

        for org in [rec.id for rec in Repository(get_app_sessionmaker(), Organizations).get_all()]:
            ###### PART A: Records Scheduled and Counted ######        
            # 1. Define Aliases
            cs = aliased(CountSchedule, name='cs')
            mtl = aliased(MaterialList, name='mtl')

            # 2. Handle the ActualCounts subquery: (SELECT * FROM WICS_actualcounts WHERE not LocationOnly)
            ac = (
                select(ActualCounts)
                .where(ActualCounts.LocationOnly == False)
                .subquery(name='ac')
            )

            # 3. Define the Field List with exact Labels
            fld_list = buildFieldList(ac, cs, mtl)

            # 4. Build the Query
            stmt = (
                select(*fld_list)
                .select_from(cs)
                .join(mtl, ac.c.Material_id == mtl.id) # Matches: ac.Material_id=mtl.id
                .join(ac, and_(
                    cs.CountDate == ac.c.CountDate,
                    cs.Material_id == ac.c.Material_id
                ))
                .where(
                    # date_condition: (ac.CountDate = ? OR cs.CountDate = ?)
                    or_(
                        ac.c.CountDate == countDate,
                        cs.CountDate == countDate
                    ),
                    # org_condition
                    mtl.org_id == org
                )
            )

            # Add dynamic Rptvariation filter
            if Rptvariation == 'REQ':
                stmt = stmt.where(cs.Requestor.is_not(None))

            # Order by the label we created
            stmt = stmt.order_by(literal_column("Matl_PartNum"))

            with get_app_session() as session:
                rslt = session.execute(stmt)
                # Note: rslt.detach() is rarely used in SQLAlchemy 2.0 unless 
                # using specific legacy drivers; usually rslt.all() is safer.
                partA_qs = rslt.all()
            # end with get_app_session
            
            # 5. Process the Query Results
            ttl = 'Scheduled and Counted'
            if Rptvariation == 'REQ':
                ttl = 'Requested and Counted'            
            SummaryReport.append({
                        'org':org,
                        'Title':ttl,
                        'outputrows': CreateOutputRows(partA_qs, SAP_SOH, self.Excel_qdict),
                        })


            ###### PART B: Records UnScheduled but Counted ######        
            # 1. Define Aliases
            cs = aliased(CountSchedule, name='cs')
            mtl = aliased(MaterialList, name='mtl')
            ac = aliased(ActualCounts, name='ac')

            # no step 2 since we are using ac directly
            
            # 3. Define the Field List with exact Labels
            fld_list = buildFieldList(ac, cs, mtl)

            # 4. Build the Query
            stmt = (
                select(*fld_list)
                .select_from(ac)
                .join(mtl, ac.Material_id == mtl.id) # Matches
                .outerjoin(cs, and_(
                    cs.CountDate == ac.CountDate,
                    cs.Material_id == ac.Material_id
                ))
                .where(
                    ac.LocationOnly == False,
                    # date_condition: (ac.CountDate = ? OR cs.CountDate = ?)
                    or_(
                        ac.CountDate == countDate,
                        cs.CountDate == countDate
                    ),
                    # org_condition
                    mtl.org_id == org,
                    cs.id.is_(None) # unscheduled only
                )
            )

            # Order by the label we created
            stmt = stmt.order_by(literal_column("Matl_PartNum"))

            with get_app_session() as session:
                rslt = session.execute(stmt)
                # Note: rslt.detach() is rarely used in SQLAlchemy 2.0 unless 
                # using specific legacy drivers; usually rslt.all() is safer.
                partB_qs = rslt.all()
            # end with get_app_session
            
            # 5. Process the Query Results
            ttl = 'UnScheduled'
            SummaryReport.append({
                        'org':org,
                        'Title':ttl,
                        'outputrows': CreateOutputRows(partB_qs, SAP_SOH, self.Excel_qdict),
                        })
            
            ###### PART C: Records Scheduled but not Counted ######
            # 1. Define Aliases
            cs = aliased(CountSchedule, name='cs')
            mtl = aliased(MaterialList, name='mtl')

            # 2. Handle the ActualCounts subquery: (SELECT * FROM WICS_actualcounts WHERE not LocationOnly)
            ac = (
                select(ActualCounts)
                .where(ActualCounts.LocationOnly == False)
                .subquery(name='ac')
            )
            
            # 3. Define the Field List with exact Labels
            fld_list = buildFieldList(ac, cs, mtl)

            # 4. Build the Query
            stmt = (
                select(*fld_list)
                .select_from(cs)
                .join(mtl, cs.Material_id == mtl.id) # Matches
                .outerjoin(ac, and_(
                    cs.CountDate == ac.c.CountDate,
                    cs.Material_id == ac.c.Material_id
                ))
                .where(
                    # date_condition: (ac.CountDate = ? OR cs.CountDate = ?)
                    or_(
                        ac.c.CountDate == countDate,
                        cs.CountDate == countDate
                    ),
                    # org_condition
                    mtl.org_id == org,
                    ac.c.id.is_(None),  # not counted
                )
            )

            # Add dynamic Rptvariation filter
            if Rptvariation == 'REQ':
                stmt = stmt.where(cs.Requestor.is_not(None))

            # Order by the label we created
            stmt = stmt.order_by(literal_column("Matl_PartNum"))

            with get_app_session() as session:
                rslt = session.execute(stmt)
                # Note: rslt.detach() is rarely used in SQLAlchemy 2.0 unless 
                # using specific legacy drivers; usually rslt.all() is safer.
                partC_qs = rslt.all()
            # end with get_app_session
            
            # 5. Process the Query Results
            ttl = 'Scheduled but Not Counted'
            if Rptvariation == 'REQ':
                ttl = 'Requested but Not Counted'            
            SummaryReport.append({
                        'org':org,
                        'Title':ttl,
                        'outputrows': CreateOutputRows(partC_qs, SAP_SOH, self.Excel_qdict),
                        })
        # end for org
        
        AccuracyCutoff = {          # TODO: make a parameter later
            'DANGER': 70.0,
            'WARNING': 90.0,
            'OK': 99.0,
            }
        
        ExcelFileNamePrefix = f"Count_Summary_{countDate.isoformat()}"
        ExcelFileName = Excelfile_fromqs(
            self.Excel_qdict,
            ExcelFileNamePrefix,
            )    
        
        self.displayReport(SummaryReport, AccuracyCutoff, ExcelFileName)
    # buildReport
    
# ShowUpdateMatlListfromSAPForm

# read the last SAP list before for_date into a list of SAP_SOHRecs
def fnSAPList(for_date = date.today(), matl = None) -> dict:
    """
    finally done!: allow matl to be a MaterialList object or an id
    matl is a Material (string, NOT object!), or list, tuple or queryset of Materials to list, or None if all records are to be listed
    the SAPDate returned is the last one prior or equal to for_date
    """
    _myDtFmt = '%Y-%m-%d %H:%M'

    dateObj = for_date

    tmp0 = Repository(get_app_sessionmaker(), SAP_SOHRecs).get_all(
        SAP_SOHRecs.uploaded_at <= dateObj
    )
    if not tmp0:
        tmp0 = Repository(get_app_sessionmaker(), SAP_SOHRecs).get_all()
        if tmp0:
            LatestSAPDate = min(rec.uploaded_at for rec in tmp0)
        else:
            LatestSAPDate = None
    else:
        LatestSAPDate = max(rec.uploaded_at for rec in tmp0)
    # endif not tmp0
    
    SAPLatest = Repository(get_app_sessionmaker(), SAP_SOHRecs).get_all(
        SAP_SOHRecs.uploaded_at == LatestSAPDate, 
        order_by=[SAP_SOHRecs.Material.org, SAP_SOHRecs.Material.Material, SAP_SOHRecs.StorageLocation],
        )
    
    SList = {'reqDate': for_date, 'SAPDate': LatestSAPDate, 'SAPTable':[]}

    if not matl:
        STable = SAPLatest
    else:
        if isinstance(matl,str):
            raise TypeError('fnSAPList by Matl string is deprecated')
        elif isinstance(matl,MaterialList):  # handle case matl is a MaterialList instance here
            STable = [rec for rec in SAPLatest if rec.Material == matl]
        elif isinstance(matl,int):  # handle case matl is a MaterialList id here
            STable = [rec for rec in SAPLatest if rec.Material.id == matl]
        else:   # it better be an iterable!
            STable = [rec for rec in SAPLatest if rec.Material in matl]
    # endif not matl

    # yea, building SList is sorta wasteful, but a lot of existing code depends on it
    # won't be changing it until a total revamp of WICS
    if not STable:
        SList['SAPDate'] = None
    SList['SAPTable'] = STable

    return SList
