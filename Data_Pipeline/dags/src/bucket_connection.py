import os
from google.cloud import storage
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Function to connect to a Google Cloud Storage bucket
def connect_to_bucket():
    bucket_name = os.getenv("GCS_BUCKET_NAME")  # Retrieve the bucket name from environment variables
    client = storage.Client()  # Initialize the GCP storage client
    bucket = client.bucket(bucket_name)  # Access the specified bucket
    return bucket  # Return the bucket object for further operations

# Function to upload a file to a specified location in the bucket
def upload_blob(source_file_name: str, destination_blob_name: str):
    bucket = connect_to_bucket()  # Connect to the bucket
    blob = bucket.blob(destination_blob_name)  # Create a blob (file placeholder) in the bucket
    blob.upload_from_filename(source_file_name)  # Upload the local file to the blob

# Function to download a file from the bucket to a local path
def download_blob(source_blob_name: str, destination_file_name: str):
    bucket = connect_to_bucket()  # Connect to the bucket
    blob = bucket.blob(source_blob_name)  # Access the specified blob (file) in the bucket
    blob.download_to_filename(destination_file_name)  # Download the blob to a local file

# Function to list all blobs (files) in the connected bucket
def list_blobs():
    bucket = connect_to_bucket()  # Connect to the bucket
    blobs = bucket.list_blobs()  # Retrieve an iterator for all blobs in the bucket
    print("Blobs in the bucket:")
    for blob in blobs:
        print(blob.name)  # Print the name of each blob
