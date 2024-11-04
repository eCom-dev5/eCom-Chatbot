import os
import pg8000
import sqlalchemy
from google.cloud.sql.connector import Connector, IPTypes


def connect_with_db(credentials) -> sqlalchemy.engine.base.Engine:
    ip_type = IPTypes.PRIVATE if os.getenv("PRIVATE_IP") else IPTypes.PUBLIC
    connector = Connector()
    def getconn() -> pg8000.dbapi.Connection:
        conn: pg8000.dbapi.Connection = connector.connect(
            credentials['INSTANCE_CONNECTION_NAME'],
            "pg8000",
            user=credentials['DB_USER'],
            password=credentials['DB_PASS'],
            db=credentials['DB_NAME'],
            ip_type=ip_type,
        )
        return conn
    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )
    return pool