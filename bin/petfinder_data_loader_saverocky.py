# Standard imports
import time
import json
from datetime import datetime, timedelta, timezone
import logging
import traceback
import os
from concurrent.futures import ThreadPoolExecutor, as_completed


# External imports
from google.cloud import storage, bigquery
# pip install google-cloud-bigquery
from google.oauth2.service_account import Credentials
import requests
import pandas as pd


# NEW
# Constants
MAX_REQUESTS_PER_DAY = 10  # Limit to 950 requests to stay safe
PAGE_LIMIT = 100            # Max allowed records per request
SLEEP_TIME = 2              # Wait 2 seconds between requests to prevent hitting limits


# Petfinder API Client
class PetfinderAPIClient:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expiration = None
        self.base_url = "https://api.petfinder.com/v2/animals"
        self.request_count = 0  # Track API requests

    def get_access_token(self):
        """Request and retrieve the access token from Petfinder API."""
        url = 'https://api.petfinder.com/v2/oauth2/token'
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        response = requests.post(url, data=data)
        self.request_count += 1

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

    # NEW Method: To handle fetching in 10-day chunks using 'before' and 'after'
    def fetch_data_for_next_period(self, start_date, days_to_fetch=10):
        """
        Fetch data for the next 'days_to_fetch' days, starting from 'start_date'.
        This fetches data progressively, 10 days at a time, using 'before' and 'after' query parameters.
        """
        # Calculate the end date of this period
        end_date = (datetime.fromisoformat(start_date) + timedelta(days=days_to_fetch)).isoformat()

        print(f"Fetching data from {start_date} to {end_date}...")

        # Fetch the data for this 10-day period using 'before' and 'after'
        return self.fetch_all_data(start_date=start_date, end_date=end_date)

    # Adjust the fetch_all_data method to use the new 'before' and 'after' logic
    def fetch_all_data(self, start_date=None, end_date=None, days_to_fetch=10):
        """
        Fetch all available data between the 'start_date' and 'end_date',
        using 'before' and 'after' query parameters.
        """
        all_pets = []
        current_date = start_date if start_date else datetime.now(timezone.utc).isoformat()
        end_date = end_date if end_date else (datetime.now(timezone.utc) - timedelta(days=days_to_fetch)).isoformat()

        while current_date > end_date:
            print(f"Fetching data before {current_date}...")

            # Fetch a page of data, passing 'before' (published before) and 'after' (published after) dates
            page_pets = self.fetch_page(1, before_date=current_date,
                                        after_date=end_date)  # Always start with page 1 for oldest data

            if not page_pets:
                print("No more older records available.")
                break  # Stop if no more data

            # Filter only for rescues from "rescueme@srgdrr.org"
            filtered_pets = [pet for pet in page_pets if pet.get("contact", {}).get("email") == "rescueme@srgdrr.org"]
            all_pets.extend(filtered_pets)

            # Update `current_date` to the oldest record in this batch
            oldest_record_date = min((pet["published_at"] for pet in page_pets if "published_at" in pet),
                                     default=current_date)
            current_date = oldest_record_date

            # Stop if we reached the desired historical date
            if current_date <= end_date:
                print(f"Reached the desired historical date: {end_date}")
                break

        print(f"Total records fetched after filtering: {len(all_pets)}")
        return all_pets

    # Adjust the fetch_page method to handle 'before_date' and 'after_date' parameters
    def fetch_page(self, page, before_date=None, after_date=None):
        """Fetch a single page of data, optionally filtering by 'before' and 'after' dates."""
        self.refresh_access_token()
        if self.request_count >= MAX_REQUESTS_PER_DAY:
            return []

        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {"limit": PAGE_LIMIT, "page": page}

        # Add 'before' and 'after' parameters if provided
        if before_date:
            params["before"] = before_date  # Fetch only records published before this date
        if after_date:
            params["after"] = after_date  # Fetch only records published after this date

        response = requests.get(self.base_url, headers=headers, params=params)
        self.request_count += 1
        time.sleep(SLEEP_TIME)

        if response.status_code == 200:
            return response.json().get("animals", [])
        else:
            print(f"Failed to fetch page {page}: {response.text}")
            return []


# PetFinder Data Loader
# TESTING added last 3 variables
class PetFinderDataLoader:
    def __init__(self, credentials_json: str, bucket_name: str, project_id: str, dataset_id: str, table_id: str):
        """Initialize Google Cloud Storage client using secrets."""
        credentials_dict = json.loads(credentials_json)
        credentials = Credentials.from_service_account_info(credentials_dict)
        self.storage_client = storage.Client(credentials=credentials)
        self.bucket = self.storage_client.bucket(bucket_name)
        self.bigquery_client = bigquery.Client(credentials=credentials, project=project_id)

        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id


    def transform_to_dataframe(self, pet_data):
        """Convert pet data JSON to a Pandas DataFrame."""
        records = []
        for pet in pet_data:
            # Ensure only processing pets from rescueme@srgdrr.org
            if pet.get("contact", {}).get("email") != "rescueme@srgdrr.org":
                continue
            record = {
                "id": pet.get("id"),
                "organization_id": pet.get("organization_id"),
                "species": pet.get("species"),
                "primary_breed": pet["breeds"].get("primary") if pet.get("breeds") else None,
                "primary_color": pet["colors"].get("primary") if pet.get("colors") else None,
                "age": pet.get("age"),
                "gender": pet.get("gender"),
                "size": pet.get("size"),
                "name": pet.get("name"),
                "status": pet.get("status"),
                "spayed_neutered": pet["attributes"].get("spayed_neutered") if pet.get("attributes") else None,
                "house_trained": pet["attributes"].get("house_trained") if pet.get("attributes") else None,
                "declawed": pet["attributes"].get("declawed") if pet.get("attributes") else None,
                "special_needs": pet["attributes"].get("special_needs") if pet.get("attributes") else None,
                "shots_current": pet["attributes"].get("shots_current") if pet.get("attributes") else None,
                "good_with_children": pet["environment"].get("children") if pet.get("environment") else None,
                "good_with_dogs": pet["environment"].get("dogs") if pet.get("environment") else None,
                "good_with_cats": pet["environment"].get("cats") if pet.get("environment") else None,
                "tags": pet.get("tags", []),  # List of tags
                "email": pet["contact"].get("email") if pet.get("contact") else None,
                "location": f"{pet['contact']['address'].get('city', '')}, {pet['contact']['address'].get('state', '')}".strip(
                    ", ")
                if pet.get("contact") and pet["contact"].get("address") else None,
                "postcode": pet["contact"]["address"].get("postcode")
                if pet.get("contact") and pet["contact"].get("address") else None,
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

    def load_csv_to_bigquery(self, blob_name):
        """Load CSV file from GCS to BigQuery."""
        table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
        uri = f"gs://{self.bucket.name}/{blob_name}"

        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            autodetect=True,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND  # Append data instead of overwriting
            # write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
        )

        load_job = self.bigquery_client.load_table_from_uri(uri, table_ref, job_config=job_config)
        load_job.result()  # Wait for the job to complete
        print(f"Loaded data from {blob_name} into BigQuery table {table_ref}")

    def fetch_transform_upload(self, pet_data):
        """Fetch, transform, and upload data."""
        try:
            df = self.transform_to_dataframe(pet_data)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            blob_name = f"processed/petfinder_saverocky_{timestamp}.csv"
            self.save_csv_to_gcs(df, blob_name)

            # TESTING
            # Load into BigQuery
            self.load_csv_to_bigquery(blob_name)

        except Exception as e:
            print(f"Error processing data: {e}")
            logging.error(traceback.format_exc())


# Example usage:
def main():
    # Load secrets from environment variables
    client_id = os.getenv("PETFINDER_CLIENT_ID")
    client_secret = os.getenv("PETFINDER_CLIENT_SECRET")
    bucket_name = "petfinderapi-petfinder-data"
    credentials_json = os.getenv("GCS_CREDENTIALS")

    if not client_id or not client_secret or not bucket_name or not credentials_json:
        raise ValueError("Missing required environment variables!")

    # Extract project_id from credentials JSON
    dataset_id = "petfinder_data"
    table_id = "raw_petfinder_saverocky"
    credentials_dict = json.loads(credentials_json)
    project_id = credentials_dict.get("project_id")

    # Initialize the Petfinder API client
    petfinder_client = PetfinderAPIClient(client_id, client_secret)

    # Fetch the initial access token
    petfinder_client.get_access_token()

    # Start from 6 months ago
    timeline = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()

    # Use a lower number of workers for deep backfill
    while True:
        # Fetch data for the current 10-day window
        pet_data, new_start_date = petfinder_client.fetch_data_for_next_period(start_date=timeline, days_to_fetch=5)

        # If data is fetched, upload it to Google Cloud Storage and BigQuery
        if pet_data:
            loader = PetFinderDataLoader(credentials_json, bucket_name, project_id, dataset_id, table_id)
            loader.fetch_transform_upload(pet_data)

        # Update the start date for the next iteration (10 days back)
        start_date = new_start_date

        # Optionally add a sleep or a break condition based on your desired frequency.
        # time.sleep(3600)  # Sleep for an hour between fetches
        # If you want to stop after a certain number of iterations, you can add a condition here.
        # Example: if a certain number of days has been processed.

    # If data is fetched, upload it to Google Cloud Storage
    # if pet_data:
    #     # TESTING
    #     loader = PetFinderDataLoader(credentials_json, bucket_name, project_id, dataset_id, table_id)
    #     # loader = PetFinderDataLoader(credentials_json, bucket_name)
    #     loader.fetch_transform_upload(pet_data)


if __name__ == "__main__":
    main()
