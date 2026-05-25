# from PySide6.QtSql import (QSqlDatabase, QSqlQuery )

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# dialect+driver://username:password@host:port/database
dialect = "sqlite://"   # for in-memory, no username, pw, host, port or database name needed, just the dialect and three slashes. For file-based, add the path to the file after the three slashes, e.g. sqlite:///path/to/dbfile.sqlite
    # postgresql+psycopg2:/
    # mysql+pymysql:/
    # mssql+pyodbc:/
rootdir = "."
app_dbName = f"{rootdir}/WICSdb.sqlite"

# an Engine, which the Session will use for connection
# resources, typically in module scope
app_engine = create_engine(
    f"{dialect}/{app_dbName}",
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
