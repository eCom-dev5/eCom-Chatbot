import os
import pandas as pd
from dotenv import load_dotenv
# from bucket_connection import upload_blob

from src.bucket_connection import *

# Load environment variables from a .env file
load_dotenv()

# Function to convert JSON file from Google Cloud Storage to CSV, then upload it back to GCS
def json_to_csv_meta(source_blob_name, destination_blob_directory):
    # Extract the base filename (without extension) for naming temporary files
    file_name = os.path.splitext(os.path.basename(source_blob_name))[0]
    temp_json_file_path = f'Data/temp/{file_name}.json'  # Path to temporarily save the downloaded JSON file
    temp_csv_file_path = f'Data/temp/{file_name}.csv'    # Path to temporarily save the converted CSV file

    # Download the JSON file from Google Cloud Storage
    download_blob(source_blob_name, temp_json_file_path)

    # Read the JSON data into a pandas DataFrame and convert it to CSV format
    data = pd.read_json(temp_json_file_path)
    data.to_csv(temp_csv_file_path, index=False)  # Save DataFrame to CSV file without index column

    # Define the destination path for the CSV file in Google Cloud Storage
    destination_blob_name = os.path.join(destination_blob_directory, f'{file_name}.csv')

    # Upload the CSV file back to Google Cloud Storage
    upload_blob(temp_csv_file_path, destination_blob_name)

    # Clean up temporary files by removing the downloaded JSON and generated CSV files
    os.remove(temp_json_file_path)
    os.remove(temp_csv_file_path)

    # Return a success message
    message = f'Successfully converted {source_blob_name} to CSV and uploaded to {destination_blob_name}'
    return message

# Function to convert JSON review file from Google Cloud Storage to CSV, then upload it back to GCS
def json_to_csv_review(source_blob_name, destination_blob_directory):
    # Extract the base filename (without extension) for naming temporary files
    file_name = os.path.splitext(os.path.basename(source_blob_name))[0]
    temp_json_file_path = f'Data/temp/{file_name}.json'  # Path to temporarily save the downloaded JSON file
    temp_csv_file_path = f'Data/temp/{file_name}.csv'    # Path to temporarily save the converted CSV file

    # Download the JSON file from Google Cloud Storage
    download_blob(source_blob_name, temp_json_file_path)

    # Read the JSON data into a pandas DataFrame and convert it to CSV format
    data = pd.read_json(temp_json_file_path)
    data.to_csv(temp_csv_file_path, index=False)  # Save DataFrame to CSV file without index column

    # Define the destination path for the CSV file in Google Cloud Storage
    destination_blob_name = os.path.join(destination_blob_directory, f'{file_name}.csv')

    # Upload the CSV file back to Google Cloud Storage
    upload_blob(temp_csv_file_path, destination_blob_name)

    # Clean up temporary files by removing the downloaded JSON and generated CSV files
    os.remove(temp_json_file_path)
    os.remove(temp_csv_file_path)

    # Return a success message
    message = f'Successfully converted {source_blob_name} to CSV and uploaded to {destination_blob_name}'
    return message
