import os
import pg8000
import sqlalchemy
from dotenv import load_dotenv
from google.cloud.sql.connector import Connector, IPTypes

# Load environment variables from a .env file
load_dotenv()

def connect_with_db() -> sqlalchemy.engine.base.Engine:
    # Retrieve database connection parameters from environment variables
    instance_connection_name = os.getenv("INSTANCE_CONNECTION_NAME")  # Google Cloud SQL instance connection name
    db_user = os.getenv("DB_USER")  # Database username
    db_pass = os.getenv("DB_PASS")  # Database password
    db_name = os.getenv("DB_NAME")  # Database name
    # Determine whether to use private or public IP based on environment variable
    ip_type = IPTypes.PRIVATE if os.getenv("PRIVATE_IP") else IPTypes.PUBLIC
    
    # Create a connector for Google Cloud SQL
    connector = Connector()
    
    # Function to create a new database connection
    def getconn() -> pg8000.dbapi.Connection:
        # Establish a connection to the database using the pg8000 driver
        conn: pg8000.dbapi.Connection = connector.connect(
            instance_connection_name,  # Connection name for the instance
            "pg8000",                  # Database driver
            user=db_user,              # Database user
            password=db_pass,          # Database password
            db=db_name,                # Database name
            ip_type=ip_type,           # IP type (private/public)
        )
        return conn  # Return the established connection
    
    # Create a connection pool for SQLAlchemy using the defined connection function
    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",  # SQLAlchemy connection string
        creator=getconn,         # Function to create new connections
    )
    
    return pool  # Return the connection pool
