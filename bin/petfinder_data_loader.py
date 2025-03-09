
# Standard imports
import time
import json
from datetime import datetime
import logging
import traceback
import os

# External imports
from google.cloud import storage
import requests


# Petfinder API Client
class PetfinderAPIClient:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expiration = None

    def get_access_token(self):
        """Request and retrieve the access token from Petfinder API."""
        url = 'https://api.petfinder.com/v2/oauth2/token'
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        response = requests.post(url, data=data)

        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            expires_in = token_data['expires_in']
            self.token_expiration = time.time() + expires_in
            print("Successfully fetched access token.")
        else:
            print(f"Failed to retrieve access token: {response.status_code}, {response.text}")

    def is_token_expired(self):
        """Check if the current access token has expired."""
        return time.time() > self.token_expiration

    def refresh_access_token(self):
        """Refresh the access token if expired."""
        if self.is_token_expired():
            print("Access token expired, refreshing token...")
            self.get_access_token()

    def get_petfinder_data(self):
        """Make an API request to Petfinder to fetch data."""
        if self.is_token_expired():
            self.refresh_access_token()

        if not self.access_token:
            print("Error: No access token available.")
            return None

        url = 'https://api.petfinder.com/v2/animals'
        headers = {
            'Authorization': f'Bearer {self.access_token}',
        }
        params = {
            'limit': 2,  # Limit to 100 pets for testing, adjust as needed
            'page': 1,
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            pet_data = response.json()
            print(f"Fetched {len(pet_data['animals'])} animals.")
            return pet_data['animals']
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None


# PetFinder Data Loader
class PetFinderDataLoader:
    storage_client: storage.Client = None
    bucket_name: str = None
    bucket: storage.Bucket = None
    credentials_file: str = None

    def create_storage_client(self):
        """Create and return a Google Cloud Storage client."""
        return storage.Client.from_service_account_json(self.credentials_file)

    def get_bucket(self):
        """Get the Google Cloud Storage bucket."""
        return self.storage_client.bucket(self.bucket_name)

    def upload_to_bucket(self, content: str, blob_name: str):
        """Upload the content to a Google Cloud Storage bucket."""
        blob = self.bucket.blob(blob_name)
        blob.upload_from_string(content)

    def generate_blob_name(self, animal_id: str, timestamp_string: str):
        """Generate a blob name for Google Cloud Storage."""
        timestamp = datetime.strptime(timestamp_string, '%Y-%m-%dT%H:%M:%S.%f')
        blob_name = f'raw/{timestamp.year}/{timestamp.month}/{timestamp.day}/{timestamp.hour}_{timestamp.minute}_{animal_id}.json'
        return blob_name

    def init(self):
        """Initialize the PetFinderDataLoader."""
        self.storage_client = self.create_storage_client()
        self.bucket = self.get_bucket()

    def set_api_credentials(self, credentials_file: str, bucket_name: str):
        """Set the credentials file for Google Cloud and bucket name."""
        self.credentials_file = credentials_file
        self.bucket_name = bucket_name

    def fetch_and_upload_petfinder_data(self, pet_data):
        """Process and upload each pet data to GCS."""
        try:
            for animal in pet_data:
                animal_data = json.dumps(animal)
                timestamp_string = datetime.now().isoformat()
                blob_name = self.generate_blob_name(animal['id'], timestamp_string)
                self.upload_to_bucket(animal_data, blob_name)
                print(f"Uploaded data for animal {animal['id']} to {blob_name}")
        except Exception as e:
            print(f"Error uploading data: {e}")
            logging.error(traceback.format_exc())


# Example usage:
def main():
    # Set Petfinder API credentials
    client_id = os.getenv("PETFINDER_CLIENT_ID")
    client_secret = os.getenv("PETFINDER_CLIENT_SECRET")
    bucket_name = os.getenv("PETFINDER_BUCKET_NAME")
    credentials_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    # Initialize the Petfinder API client
    petfinder_client = PetfinderAPIClient(client_id, client_secret)

    # Fetch the initial access token
    petfinder_client.get_access_token()

    # Fetch pet data from Petfinder
    pet_data = petfinder_client.get_petfinder_data()

    # If data is fetched, upload it to Google Cloud Storage
    if pet_data:
        loader = PetFinderDataLoader()
        loader.set_api_credentials(credentials_file, bucket_name)
        loader.init()
        loader.fetch_and_upload_petfinder_data(pet_data)


if __name__ == "__main__":
    main()
