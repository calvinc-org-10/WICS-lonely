# from PySide6.QtSql import (QSqlDatabase, QSqlQuery )

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

rootdir = "."
app_dbName = f"{rootdir}\\WICSdb.sqlite"

# an Engine, which the Session will use for connection
# resources, typically in module scope
app_engine = create_engine(
    f"sqlite:///{app_dbName}",
    )
# a sessionmaker(), also in the same scope as the engine
app_Session = sessionmaker(app_engine)

def get_app_session():
    return app_Session()

def get_app_sessionmaker():
    return app_Session

##########################################################
###################    REPOSITORIES    ###################
##########################################################

from calvincTools.database import Repository
