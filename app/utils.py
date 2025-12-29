from app.database import Repository, get_app_sessionmaker
from app.models import MaterialList, SAP_SOHRecs


from datetime import date


def fnSAPList(for_date = date.today(), matl = None) -> dict:
    """
    read the last SAP list before for_date into a list of SAP_SOHRecs

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
        order_by=[SAP_SOHRecs.org_id, SAP_SOHRecs.MaterialPartNum, SAP_SOHRecs.StorageLocation],
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
# fnSAPList
