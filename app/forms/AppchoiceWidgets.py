from calvincTools.utils import cDataList

from app.models import (
    MaterialList,
)
from app.database import ( Repository, get_app_sessionmaker )

# many, many choices for these tables - construct the choice list only once or spend forever waiting
Nochoice = {'---': None}    # only needed for combo boxes, not datalists
choices_Materials = {rec.id: str(rec) for rec in Repository(get_app_sessionmaker(), MaterialList).get_all()}

class chooseMaterials(cDataList):
    def __init__(self, choices = choices_Materials, initval = '', parent = None):
        choices = choices_Materials # ensure we use the prebuilt choice list
        super().__init__(choices, initval, parent)

# List of nested classes - used to check types (see cQFmFldWidg)
nested_classes = [
    chooseMaterials,
]
