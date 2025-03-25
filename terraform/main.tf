terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.6.0"
    }
  }
}

provider "google" {
  credentials = var.gcs_credentials
  project     = jsondecode(var.gcs_credentials)["project_id"] # Extract project_id
  region      = var.region
}

# Create GCS Bucket
resource "google_storage_bucket" "petfinder_bucket" {
  #name          = "petfinderapi-petfinder-data"
  name          = var.bucket
  location      = var.region
  force_destroy = true
}

# Create BigQuery Dataset
resource "google_bigquery_dataset" "petfinder_dataset" {
  dataset_id = "petfinder_data"
  project    = jsondecode(var.gcs_credentials)["project_id"]
  location   = var.region
}

# Variables
variable "gcs_credentials" {}
variable "region" {
  default = "us-central1"
}
variable "bucket" {}
