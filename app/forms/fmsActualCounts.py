from datetime import date
from typing import Any

from PySide6.QtCore import QDate, Qt, Slot
from PySide6.QtWidgets import QCalendarWidget, QCheckBox, QDateEdit, QFrame, QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget
from sqlalchemy import and_, literal, literal_column, or_, select
from sqlalchemy.orm import aliased

from mathematical_expressions_parser.eval import evaluate
from app.database import Repository, app_Session, get_app_session, get_app_sessionmaker
from app.forms import std_id_def
from app.models import ActualCounts, CountSchedule, MaterialList, Organizations
from app.utils import fnSAPList

from calvincTools.utils import (
    ExcelWorkbook_fileext, Excelfile_fromqs, 
    cSimpleRecordForm, clearLayout,
    cPrintManager,
    )


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

    def changeInternalVarField(self, wdgt, intVarField: str, wdgt_value: Any) -> None:
        """
        Handle changes to internal variable fields.
        """
        return


class rptCountSummary(QWidget):
    """
    Count Summary Report

    A lot of the original WICS code is preserved. That's why, for instance, outputlines dictionary is built 
    and then later parsed to create the report, instead of just building the report directly.

    """
    _formname = "Count Summary"

    def CreateOutputRows(self, raw_qs, SAP_SOH, Excel_qdict, Eval_CTDQTY=True):
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
            for SAProw in SAP_SOH['SAPTable']:
                if SAProw.Material_id == lastrow['Material_id']:
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
            outputline['Description'] = rawrow.Description
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


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO: be consistent - move this to _buildFormLayout, _buildPages, _placeFields, etc.
        self.setWindowTitle(self._formname)
        myLayout = QVBoxLayout(self)
        lblResultsTitle = QLabel(self._formname)
        myLayout.addWidget(lblResultsTitle)

        wdgtCountDate = QWidget()
        layoutCountDate = QHBoxLayout(wdgtCountDate)
        self.clndrCountDate = QCalendarWidget()
        lblCountDate = QLabel("Count Date: "+self.clndrCountDate.selectedDate().toString("yyyy-MM-dd"+"  "))
        self.clndrCountDate.setGridVisible(True)
        self.clndrCountDate.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.clndrCountDate.setMinimumDate(QDate(2000,1,1))
        self.clndrCountDate.setMaximumDate(QDate(2199,12,31))
        self.clndrCountDate.selectionChanged.connect(
            lambda: lblCountDate.setText("Count Date: "+self.clndrCountDate.selectedDate().toString("yyyy-MM-dd"))
            )
        self.clndrCountDate.selectionChanged.connect(self.buildReport)
        layoutCountDate.addWidget(lblCountDate)
        layoutCountDate.addWidget(self.clndrCountDate)
        myLayout.addWidget(wdgtCountDate)

        btnPrintPreview = QPushButton("Print Preview")
        btnPrintPreview.clicked.connect(self.handlePrintPreview)
        myLayout.addWidget(btnPrintPreview)

        self.lblSAPDate = QLabel("SAP Data Date: N/A")
        myLayout.addWidget(self.lblSAPDate)

        wdgtMainArea = QWidget()
        self.layoutMainArea = QVBoxLayout(wdgtMainArea)
        self.layoutMainArea.setSpacing(1)
        wdgtScrollArea = QScrollArea()
        wdgtScrollArea.setWidgetResizable(True)
        wdgtScrollArea.setWidget(wdgtMainArea)
        myLayout.addWidget(wdgtScrollArea)

        self.Excel_qdict = []

        Rptvariation = None  # or 'REQ' for requested only - implement later
        self.buildReport(Rptvariation=Rptvariation)
    # __init__

    @Slot()
    def buildReport(self, Rptvariation = None):
        """
        Build the report for the selected date
        """
        def buildFieldList(ac, cs, mtl, orgname) -> list[Any]:
            acCols = ac.c if hasattr(ac,"c") else ac
            csCols = cs.c if hasattr(cs,"c") else cs
            mtlCols = mtl.c if hasattr(mtl,"c") else mtl
            fld_list = [
                literal_column("0").label("id"),
                csCols.id.label("cs_id"),
                csCols.CountDate.label("cs_CountDate"),
                csCols.Counter.label("cs_Counter"),
                csCols.Priority.label("cs_Priority"),
                csCols.ReasonScheduled.label("cs_ReasonScheduled"),
                csCols.Requestor,
                csCols.RequestFilled,
                csCols.Notes.label("cs_Notes"),
                acCols.id.label("ac_id"),
                acCols.CountDate.label("ac_CountDate"),
                acCols.CycCtID.label("ac_CycCtID"),
                acCols.Counter.label("ac_Counter"),
                acCols.LocationOnly.label("ac_LocationOnly"),
                acCols.CTD_QTY_Expr.label("ac_CTD_QTY_Expr"),
                acCols.LOCATION.label("ac_LOCATION"),
                acCols.PKGID_Desc.label("ac_PKGID_Desc"),
                acCols.TAGQTY.label("ac_TAGQTY"),
                acCols.FLAG_PossiblyNotRecieved,
                acCols.FLAG_MovementDuringCount,
                acCols.Notes.label("ac_Notes"),
                mtlCols.id.label("matl_id"),
                mtlCols.org_id,
                # literal("(SELECT name FROM organizations WHERE organizations.id = "+str(mtl.org_id)+")").label("OrgName"),
                literal(orgname).label("OrgName"),
                # mtl.Material_org.label("Matl_PartNum"),
                (literal(orgname)+literal("-")+mtlCols.Material).label("Matl_PartNum"),
                mtlCols.PartType_id.label("PartType"),  #TODO: join to PartTypes to get the name
                mtlCols.Description,
                mtlCols.TypicalContainerQty,
                mtlCols.TypicalPalletQty,
                mtlCols.Notes.label("mtl_Notes"),
            ]
            return fld_list
        # buildFieldList

        countDate = self.clndrCountDate.selectedDate().toPython()
        assert isinstance(countDate, date), "countDate is not a date"
        SAP_SOH = fnSAPList(countDate)
        SummaryReport = []

        for org in [rec.id for rec in Repository(get_app_sessionmaker(), Organizations).get_all()]:
            orgname = Repository(get_app_sessionmaker(), Organizations).get_by_id(org).orgname      # type: ignore

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
            fld_list = buildFieldList(ac, cs, mtl, orgname)

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
                        'OrgName':orgname,
                        'Title':ttl,
                        'outputrows': self.CreateOutputRows(partA_qs, SAP_SOH, self.Excel_qdict),
                        })


            ###### PART B: Records UnScheduled but Counted ######        
            # 1. Define Aliases
            cs = aliased(CountSchedule, name='cs')
            mtl = aliased(MaterialList, name='mtl')
            ac = aliased(ActualCounts, name='ac')

            # no step 2 since we are using ac directly

            # 3. Define the Field List with exact Labels
            fld_list = buildFieldList(ac, cs, mtl, orgname)

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
                        'OrgName':orgname,
                        'Title':ttl,
                        'outputrows': self.CreateOutputRows(partB_qs, SAP_SOH, self.Excel_qdict),
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
            fld_list = buildFieldList(ac, cs, mtl, orgname)

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
                        'OrgName':orgname,
                        'Title':ttl,
                        'outputrows': self.CreateOutputRows(partC_qs, SAP_SOH, self.Excel_qdict),
                        })
        # end for org

        AccuracyCutoff = {          # TODO: make a parameter later
            'DANGER': 70.0,
            'WARNING': 90.0,
            'OK': 99.0,
            }

        ExcelFileName = None
        DEBUGskipExcel = True   # TODO: make a parameter later
        if not DEBUGskipExcel:
            import os
            ExcelFileDir = "D:/tmp0/"   # TODO: make a parameter later
            k = 0
            while True:
                _ExcelFileNameSuffix = f"{k:02x}"
                _ExcelFileName = f"{ExcelFileDir}Count_Summary_{countDate.isoformat()}_{_ExcelFileNameSuffix}"
                if not os.path.exists(_ExcelFileName + ExcelWorkbook_fileext):
                    break
                k += 1
                if k>0xffff:
                    raise FileExistsError("Cannot find unique Excel file name for Count Summary report")
            # end while
            ExcelFileName = Excelfile_fromqs(
                self.Excel_qdict,
                _ExcelFileName,
                returnFileName=True
                )

        self.displayReport(
            Rptvariation,
            CountDate=countDate,
            SAPDate=SAP_SOH['SAPDate'],
            AccuracyCutoff=AccuracyCutoff,
            SummaryReport=SummaryReport,
            ExcelFileName=ExcelFileName
        )
    # buildReport

    def displayReport(
        self,
        variation,      # pylint: disable=unused-argument
        CountDate,
        SAPDate,
        AccuracyCutoff,
        SummaryReport,
        ExcelFileName
        ):
        """
        display the report using the information passed in
        In the Django world, this was done by templt = 'rpt_CountSummary.html'\
        using 
        cntext = {
            'variation': variation,
            'CountDate': CountDate,
            'SAPDate': SAPDate,
            'AccuracyCutoff': AccuracyCutoff,
            'SummaryReport': SummaryReport,
            'ExcelFileName': ExcelFileName,
        }
        """
        def horizontalLine()->QFrame:
            horizontalLine = QFrame()
            horizontalLine.setFrameShape(QFrame.Shape.HLine)
            horizontalLine.setFrameShadow(QFrame.Shadow.Sunken)
            horizontalLine.setStyleSheet("QFrame { border: 3px solid black; }")
            return horizontalLine
        # horizontalLine

        # for now, just print to console
        outputMedium = self.layoutMainArea

        clearLayout(outputMedium)        # clear any existing widgets
        self.lblSAPDate.setText("SAP Data Date: "+ (SAPDate.isoformat() if SAPDate else "N/A"))

        #temporary until better formatting is done
        outputMedium.addWidget(QLabel(f"Accuracy Cutoff: {AccuracyCutoff}"))
        outputMedium.addWidget(QLabel(f"Excel File: {ExcelFileName}"))
        outputMedium.addWidget(horizontalLine())    # horizontal line
        outputMedium.addWidget(QLabel(f"Count Summary Report for Count Date: {CountDate:%Y-%m-%d}"))
        outputMedium.addWidget(QLabel(self.lblSAPDate.text()))
        outputMedium.addWidget(QLabel(" "))   # blank line

        prevValues = {}
        forloop_first_rptSection = True
        org_has_data = False
        for rptSection in SummaryReport:
            # has the organization changed?
            if rptSection['org'] != prevValues.get('rptSection-org'):
                if not forloop_first_rptSection:
                    # did previous section have data?
                    if not org_has_data:
                        outputMedium.addWidget(QLabel("    NO COUNTS"))
                    # add a spacer between organizations
                    outputMedium.addWidget(horizontalLine())
                # end if not forloop_first
                lineToAdd = ""
                lineToAdd += f" <h2><u>Organization: {rptSection['OrgName']}</u></h2>"
                outputMedium.addWidget(QLabel(lineToAdd))
                org_has_data = False

                prevValues['rptSection-org'] = rptSection['org']
            # end if org changed

            if not rptSection['outputrows']:
                # no data for this section
                # lineToAdd = f"No data for section: {rptSection['Title']}"
                # outputMedium.addWidget(QLabel(lineToAdd))
                forloop_first_rptSection = False
                continue
            #end if no outputrows
            org_has_data = True

            # Header for this section
            outputMedium.addWidget(QLabel(""))   # blank line

            lineToAdd = "<h3>"
            lineToAdd += "Counts"
            lineToAdd += f" {rptSection['Title']}"
            lineToAdd += "</h3>"
            outputMedium.addWidget(QLabel(lineToAdd))

            for outputline in rptSection['outputrows']:
                if outputline['Material_id'] != prevValues.get('Material-id'):
                    diviLine = QLabel("  ")
                    outputMedium.addWidget(diviLine)
                    wdgtToAdd = QLabel(f"<h4><u>Material: {outputline['Material']} - {outputline['Description']}</u></h4>")
                    outputMedium.addWidget(wdgtToAdd)

                    wdgtToAdd = QWidget()
                    layoutL = QHBoxLayout(wdgtToAdd)
                    #TODO: better formatting here
                    layoutL.addWidget(QLabel("<b>Count Date</b>"))
                    layoutL.addWidget(QLabel("<b>Material</b>"))
                    layoutL.addWidget(QLabel("<b>Counter</b>"))
                    layoutL.addWidget(QLabel("<b>LOCATION</b>"))
                    layoutL.addWidget(QLabel("<b>PKG ID/Desc</b>"))
                    layoutL.addWidget(QLabel("<b>TAG QTY</b>"))
                    outputMedium.addWidget(wdgtToAdd)
                # endif material changed

                if outputline['type'] == 'Detail':
                    wdgtToAdd = QWidget()
                    layoutL = QHBoxLayout(wdgtToAdd)
                    #TODO: better formatting here
                    layoutL.addWidget(QLabel(f"{CountDate:%m/%d}"))
                    layoutL.addWidget(QLabel(f"{outputline['Material']}"))
                    layoutL.addWidget(QLabel(f"{outputline['ActCounter']}"))
                    layoutL.addWidget(QLabel(f"{outputline['LOCATION']}"))
                    layoutL.addWidget(QLabel(f"{outputline['PKGID']}"))
                    layoutL.addWidget(QLabel(f"{outputline['TAGQTY']}"))
                    outputMedium.addWidget(wdgtToAdd)

                    if outputline['ActCountNotes']:
                        wdgtToAdd = QLabel(f"   Count Notes: {outputline['ActCountNotes']}")
                        outputMedium.addWidget(wdgtToAdd)
                    wdgtToAdd = QLabel(f"Actual Count: {outputline['CTD_QTY_Expr']} = <b>{outputline['CTD_QTY_Eval']}</b>")
                    wdgtToAdd.setAlignment(Qt.AlignmentFlag.AlignRight)
                    outputMedium.addWidget(wdgtToAdd)

                    wdgtToAdd = QLabel("")
                    if outputline['PossNotRec']:
                        wdgtToAdd.setText(wdgtToAdd.text() + " | Possibly Not Received |")
                    if outputline['MovDurCt']:
                        wdgtToAdd.setText(wdgtToAdd.text() + " | Movement During Count |")
                    wdgtToAdd.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                    if wdgtToAdd.text():
                        outputMedium.addWidget(wdgtToAdd)

                elif outputline['type'] == 'Summary':
                    lblSummary = QLabel(
                        f"Material: {outputline['Material']} | "
                        f"Counted Total: {outputline['CountTotal']} | "
                        f"SAP Total: {outputline['SAPTotal']} | "
                        f"Diff: {outputline['Diff']} | "
                        f"Accuracy: {outputline['Accuracy']:.2f}%"
                    )
                    outputMedium.addWidget(lblSummary)
                    #TODO: better formatting here, print Scheduled Counter and Requestor info too
                # end if outputline type

                prevValues['Material-id'] = outputline['Material_id']
            # end for outputline in rptSection['outputrows']

            outputMedium.addWidget(horizontalLine())
            forloop_first_rptSection = False
        # end for rptSection

        # footer for last section
        # did previous section have data?
        if not org_has_data:
            outputMedium.addWidget(QLabel("    NO COUNTS"))
        # add a spacer between organizations
        outputMedium.addWidget(horizontalLine())
    # displayReport

    @Slot()
    def handlePrintPreview(self):
        """
        Handle print preview button click
        """
        widgParent = self.layoutMainArea.parent()
        assert isinstance(widgParent, QWidget), "layoutMainArea parent is not a QWidget"
        manager = cPrintManager(widgParent)
        manager.open_preview()
    # handlePrintPreview
# rptCountSummary
