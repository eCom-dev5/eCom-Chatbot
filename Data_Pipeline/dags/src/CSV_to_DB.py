import os
from airflow import DAG
from datetime import datetime
from google.cloud import storage
from dotenv import load_dotenv
from sqlalchemy import text
import subprocess

from src.db_connection import *

# Load environment variables from a .env file
load_dotenv()

# Function to create a table for storing user review data if it doesn’t exist
def create_table_user_review():
    # Fetch the connection string for PostgreSQL from environment variables
    postgres_conn_string = os.getenv("postgres_conn_string")
    # Establish connection to the PostgreSQL database
    engine = connect_with_db()
    with engine.begin() as connection:
        try:
            # Define SQL query to create the 'user_reviews' table with necessary columns
            query = text("""CREATE TABLE IF NOT EXISTS user_reviews (
                            rating TEXT, 
                            title TEXT, 
                            text TEXT, 
                            images TEXT, 
                            asin TEXT, 
                            parent_asin TEXT, 
                            user_id TEXT, 
                            timestamp TEXT, 
                            helpful_vote TEXT, 
                            verified_purchase TEXT
                            ); """)
            # Execute the query to create the table
            result = connection.execute(query)
        except Exception as e:
            # Print error message if table creation fails
            message = f"Error during insert: {e}"

# Function to create a table for storing metadata if it doesn’t exist
def create_table_meta_data():
    # Fetch the connection string for PostgreSQL from environment variables
    postgres_conn_string = os.getenv("postgres_conn_string")
    # Establish connection to the PostgreSQL database
    engine = connect_with_db()
    with engine.begin() as connection:
        try:
            # Define SQL query to create the 'metadata' table with necessary columns
            query = text("""CREATE TABLE IF NOT EXISTS metadata (
                            main_category TEXT, 
                            title TEXT, 
                            average_rating TEXT, 
                            rating_number TEXT, 
                            features TEXT, 
                            description TEXT, 
                            price TEXT, 
                            images TEXT, 
                            videos TEXT, 
                            store TEXT, 
                            categories TEXT, 
                            details TEXT, 
                            parent_asin TEXT, 
                            bought_together TEXT, 
                            subtitle TEXT, 
                            author TEXT
                            ); """)
            # Execute the query to create the table
            result = connection.execute(query)
        except Exception as e:
            # Print error message if table creation fails
            message = f"Error during insert: {e}"

# Function to upload metadata from a CSV file in GCS to the PostgreSQL 'metadata' table
def add_meta_data():
    # Define the GCS bucket and file paths
    bucket_name = "mlops_data_pipeline/Data/Raw_CSV/TEST"
    file_name = 'test_metadata.csv'
    # Fetch the PostgreSQL connection string from environment variables
    postgres_conn_string = os.getenv("postgres_conn_string")
    table_name = 'metadata'
    # Define the gcloud command to import CSV data from GCS to PostgreSQL
    transfer_command = f"""
    yes | gcloud sql import csv data-wharehousing \
    gs://{bucket_name}/{file_name} \
    --project=dockdecoder \
    --database=postgres \
    --table={table_name}
    """

    try:
        # Run the command and capture the output
        result = subprocess.run(transfer_command, shell=True, check=True, capture_output=True, text=True)
        print("Import successful:", result.stdout)
    except subprocess.CalledProcessError as e:
        # Print error message if import fails
        print("Error during import:", e.stderr)

# Function to upload user review data from a CSV file in GCS to the PostgreSQL 'user_reviews' table
def add_review_data():
    # Define the GCS bucket and file paths
    bucket_name = "mlops_data_pipeline/Data/Raw_CSV/TEST"
    file_name = 'test_user_reviews.csv'
    # Fetch the PostgreSQL connection string from environment variables
    postgres_conn_string = os.getenv("postgres_conn_string")
    table_name = 'user_reviews'
    # Define the gcloud command to import CSV data from GCS to PostgreSQL
    transfer_command = f"""
    yes | gcloud sql import csv data-wharehousing \
    gs://{bucket_name}/{file_name} \
    --project=dockdecoder \
    --database=postgres \
    --table={table_name}
    """

    try:
        # Run the command and capture the output
        result = subprocess.run(transfer_command, shell=True, check=True, capture_output=True, text=True)
        print("Import successful:", result.stdout)
    except subprocess.CalledProcessError as e:
        # Print error message if import fails
        print("Error during import:", e.stderr)
