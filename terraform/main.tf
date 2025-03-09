terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

variable "google_credentials" {}


provider "google" {
  # credentials = file("admin-credentials.json") # Admin credentials for project creation
  credentials = var.google_credentials
  project     = var.billing_project
  region      = "us-central1"
}

resource "google_project" "petfinder_project" {
  name       = var.project_name
  project_id = var.project_id
  billing_account = var.billing_account
}

resource "google_project_service" "enable_services" {
  for_each = toset([
    "iam.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "storage.googleapis.com",
    "bigquery.googleapis.com"
  ])
  project = google_project.petfinder_project.project_id
  service = each.key
}

resource "google_service_account" "terraform_sa" {
  account_id   = "terraform-service-account"
  display_name = "Terraform Service Account"
  project      = google_project.petfinder_project.project_id
}

resource "google_service_account_key" "terraform_sa_key" {
  service_account_id = google_service_account.terraform_sa.name
}

resource "google_storage_bucket" "petfinder_bucket" {
  name     = "${var.project_id}-petfinder-data"
  location = "US"
  project  = google_project.petfinder_project.project_id
}

resource "google_bigquery_dataset" "petfinder_dataset" {
  dataset_id = "petfinder_data"
  project    = google_project.petfinder_project.project_id
  location   = "US"
}

variable "billing_project" {}
variable "billing_account" {}
variable "project_name" {}
variable "project_id" {}
