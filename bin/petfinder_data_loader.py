# Standard imports
import time
import json
from datetime import datetime
import logging
import traceback
import os

# External imports
from google.cloud import storage
from google.oauth2.service_account import Credentials
import requests
import pandas as pd


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
            'limit': 10,  # Limit to 10 pets for testing, adjust as needed
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
    def __init__(self, credentials_json: str, bucket_name: str):
        """Initialize Google Cloud Storage client using secrets."""
        credentials_dict = json.loads(credentials_json)
        credentials = Credentials.from_service_account_info(credentials_dict)
        self.storage_client = storage.Client(credentials=credentials)
        self.bucket = self.storage_client.bucket(bucket_name)

    def transform_to_dataframe(self, pet_data):
        """Convert pet data JSON to a Pandas DataFrame."""
        records = []
        for pet in pet_data:
            record = {
                "id": pet.get("id"),
                "name": pet.get("name"),
                "species": pet.get("species"),
                "age": pet.get("age"),
                "gender": pet.get("gender"),
                "size": pet.get("size"),
                "coat": pet.get("coat"),
                "status": pet.get("status"),
                "primary_breed": pet["breeds"].get("primary") if pet.get("breeds") else None,
                "secondary_breed": pet["breeds"].get("secondary") if pet.get("breeds") else None,
                "mixed_breed": pet["breeds"].get("mixed") if pet.get("breeds") else None,
                "location": f"{pet['contact']['address']['city']}, {pet['contact']['address']['state']}" if pet.get("contact") else None,
                "published_at": pet.get("published_at"),
            }
            records.append(record)

        return pd.DataFrame(records)

    def save_csv_to_gcs(self, df, blob_name):
        """Upload CSV to Google Cloud Storage."""
        csv_data = df.to_csv(index=False)
        blob = self.bucket.blob(blob_name)
        blob.upload_from_string(csv_data, "text/csv")
        print(f"CSV uploaded to {blob_name}")

    def fetch_transform_upload(self, pet_data):
        """Fetch, transform, and upload data."""
        try:
            df = self.transform_to_dataframe(pet_data)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            blob_name = f"processed/petfinder_{timestamp}.csv"
            self.save_csv_to_gcs(df, blob_name)
        except Exception as e:
            print(f"Error processing data: {e}")
            logging.error(traceback.format_exc())


# Example usage:
def main():
    # Load secrets from environment variables
    client_id = os.getenv("PETFINDER_CLIENT_ID")
    client_secret = os.getenv("PETFINDER_CLIENT_SECRET")
    bucket_name = os.getenv("PETFINDER_BUCKET_NAME")
    credentials_json = os.getenv("GCS_CREDENTIALS")

    if not client_id or not client_secret or not bucket_name or not credentials_json:
        raise ValueError("Missing required environment variables!")

    # Initialize the Petfinder API client
    petfinder_client = PetfinderAPIClient(client_id, client_secret)

    # Fetch the initial access token
    petfinder_client.get_access_token()

    # Fetch pet data from Petfinder
    pet_data = petfinder_client.get_petfinder_data()

    # If data is fetched, upload it to Google Cloud Storage
    if pet_data:
        loader = PetFinderDataLoader(credentials_json, bucket_name)
        loader.fetch_transform_upload(pet_data)


if __name__ == "__main__":
    main()
