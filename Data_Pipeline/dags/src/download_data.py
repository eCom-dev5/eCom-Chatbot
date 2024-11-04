import os
import requests
import zipfile
import shutil
from src.bucket_connection import *

# Function to download, extract, and upload metadata file to cloud storage
def ingest_data_meta(file_url):
    # Send an HTTP GET request to download the file from the given URL
    response = requests.get(file_url, timeout=30)
    filename = os.path.basename(file_url)  # Extract the filename from the URL
    zipfile_path = os.path.join('Data', 'temp1', filename)  # Path where the zip file will be saved
    extract_to = os.path.join('Data', 'temp1')  # Directory to extract files

    # Check if the file was downloaded successfully
    if response.status_code == 200:
        # Write the content of the response to a zip file in binary mode
        with open(zipfile_path, "wb") as file:
            file.write(response.content)
    else:
        print(f"Failed to download the file. Status code: {response.status_code}")

    extracted_files = []
    try:
        # Try to open and extract the contents of the zip file
        with zipfile.ZipFile(zipfile_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
            extracted_files = zip_ref.namelist()  # List of files in the zip archive
    except zipfile.BadZipFile:
        print(f"Failed to unzip {zipfile_path}. It may not be a zip file.")

    # Get the name of the first extracted file
    nfile_name = str(extracted_files[0])
    temp_csv_file_path = os.path.join('Data', 'temp1', nfile_name)  # Path to the extracted CSV file

    # Define the destination path in the cloud storage
    destination_blob_directory = "Data/Raw/TEST/"
    destination_blob_name = os.path.join(destination_blob_directory, nfile_name)

    # Upload the extracted file to the cloud bucket
    upload_blob(temp_csv_file_path, destination_blob_name)

    # Clean up the temporary directory by removing all files and recreating the folder
    folder_path = 'Data/temp1'
    shutil.rmtree(folder_path)
    os.makedirs(folder_path)

    message = "Done"
    return message

# Function to download, extract, and upload review data to cloud storage
def ingest_data_review(file_url):
    # Send an HTTP GET request to download the file from the given URL
    response = requests.get(file_url, timeout=30)
    filename = os.path.basename(file_url)  # Extract the filename from the URL
    zipfile_path = os.path.join('Data', 'temp2', filename)  # Path where the zip file will be saved
    extract_to = os.path.join('Data', 'temp2')  # Directory to extract files

    # Check if the file was downloaded successfully
    if response.status_code == 200:
        # Write the content of the response to a zip file in binary mode
        with open(zipfile_path, "wb") as file:
            file.write(response.content)
    else:
        print(f"Failed to download the file. Status code: {response.status_code}")

    extracted_files = []
    try:
        # Try to open and extract the contents of the zip file
        with zipfile.ZipFile(zipfile_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
            extracted_files = zip_ref.namelist()  # List of files in the zip archive
    except zipfile.BadZipFile:
        print(f"Failed to unzip {zipfile_path}. It may not be a zip file.")

    # Get the name of the first extracted file
    nfile_name = str(extracted_files[0])
    temp_csv_file_path = os.path.join('Data', 'temp2', nfile_name)  # Path to the extracted CSV file

    # Define the destination path in the cloud storage
    destination_blob_directory = "Data/Raw/TEST/"
    destination_blob_name = os.path.join(destination_blob_directory, nfile_name)

    # Upload the extracted file to the cloud bucket
    upload_blob(temp_csv_file_path, destination_blob_name)

    # Clean up the temporary directory by removing all files and recreating the folder
    folder_path = 'Data/temp2'
    shutil.rmtree(folder_path)
    os.makedirs(folder_path)

    message = "Done"
    return message
