import os
from airflow import DAG
from datetime import datetime
from google.cloud import storage
from dotenv import load_dotenv
from sqlalchemy import text

from src.db_connection import *

# Load environment variables from a .env file
load_dotenv()

# Function to create database schema and migrate data from the 'metadata' and 'user_reviews' tables
def db_to_schema():
    # Fetch the PostgreSQL connection string from environment variables
    postgres_conn_string = os.getenv("postgres_conn_string")
    # Establish connection to the PostgreSQL database
    engine = connect_with_db()
    
    with engine.begin() as connection:
        try:
            # Create the 'productimages' table if it doesn't exist
            query = text("""CREATE TABLE IF NOT EXISTS productimages (
                            parent_asin TEXT, 
                            thumb TEXT, 
                            hi_res TEXT, 
                            large_res TEXT
                            );""")
            result = connection.execute(query)

            # Create the 'productmetadata' table if it doesn't exist
            query = text("""CREATE TABLE IF NOT EXISTS productmetadata (
                            parent_asin TEXT, 
                            title TEXT, 
                            average_rating TEXT, 
                            rating_number TEXT, 
                            features TEXT, 
                            description TEXT, 
                            price TEXT, 
                            store TEXT, 
                            details TEXT, 
                            main_category TEXT
                            );""")
            result = connection.execute(query)

            # Create the 'productcategories' table if it doesn't exist
            query = text("""CREATE TABLE IF NOT EXISTS productcategories (
                            parent_asin TEXT, 
                            categories TEXT
                            );""")
            result = connection.execute(query)

            # Create the 'userreviews' table if it doesn't exist
            query = text("""CREATE TABLE IF NOT EXISTS userreviews (
                            rating TEXT, 
                            title TEXT, 
                            text TEXT, 
                            asin TEXT, 
                            parent_asin TEXT, 
                            user_id TEXT, 
                            timestamp TEXT, 
                            helpful_vote TEXT, 
                            verified_purchase TEXT
                            );""")
            result = connection.execute(query)

            # Clean up the 'metadata' table by deleting records with images not in a valid URL format
            query = text("""DELETE FROM public.metadata m WHERE images NOT LIKE '%https://%';""")
            result = connection.execute(query)

            # Update the 'images' field in 'metadata' to replace single quotes with double quotes for JSON compatibility
            query = text("""UPDATE public.metadata SET images = REPLACE(images, '''', '"') WHERE images IS NOT NULL;""")
            result = connection.execute(query)

            # Replace occurrences of 'None' with 'null' in the 'images' field of the 'metadata' table
            query = text("""UPDATE public.metadata SET images = REPLACE(images, 'None', 'null') WHERE images IS NOT NULL;""")
            result = connection.execute(query)

            # Insert data into 'productimages' by extracting relevant fields from the 'metadata' table
            query = text("""INSERT INTO productimages (parent_asin, thumb, hi_res, large_res) 
                            SELECT parent_asin, 
                                   COALESCE(images::jsonb -> 0 ->> 'thumb', '') AS thumb, 
                                   COALESCE(images::jsonb -> 0 ->> 'hi_res', '') AS hi_res, 
                                   COALESCE(images::jsonb -> 0 ->> 'large', '') AS large_res 
                            FROM public.metadata;""")
            result = connection.execute(query)

            # Insert data into 'productmetadata' by selecting all relevant fields from the 'metadata' table
            query = text("""INSERT INTO productmetadata (parent_asin, title, average_rating, rating_number, features, description, price, store, details, main_category) 
                            SELECT parent_asin, title, average_rating, rating_number, features, description, price, store, details, main_category 
                            FROM public.metadata;""")
            result = connection.execute(query)

            # Insert data into 'productcategories' by selecting relevant fields from the 'metadata' table
            query = text("""INSERT INTO productcategories (parent_asin, categories) 
                            SELECT parent_asin, categories 
                            FROM public.metadata;""")
            result = connection.execute(query)

            # Insert data into 'userreviews' by selecting relevant fields from the 'user_reviews' table
            query = text("""INSERT INTO userreviews (rating, title, text, asin, parent_asin, user_id, timestamp, helpful_vote, verified_purchase) 
                            SELECT rating, title, text, asin, parent_asin, user_id, timestamp, helpful_vote, verified_purchase 
                            FROM public.user_reviews;""")
            result = connection.execute(query)

        except Exception as e:
            # Print error message if any part of the data insertion fails
            message = f"Error during insert: {e}"
