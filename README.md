# PetFinder API Data Pipeline

# TODO - Google Cloud Storage Bucket using TERRAFORM 

[![Python](https://img.shields.io/badge/Python-3.9-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![API](https://img.shields.io/badge/API-PetFinder-green.svg)](https://www.petfinder.com/developers/)
[![Status](https://img.shields.io/badge/Status-Active-green.svg)](https://github.com/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://www.docker.com/)


## Problem Description

This project demonstrates the creation of an end-to-end data pipeline using the **PetFinder API** [docs](https://www.petfinder.com/developers/v2/docs/). 
The pipeline ingests data, processes it, performs transformations, stores it in a data warehouse (BigQuery), 
and visualizes it in a dashboard. The pipeline uses a combination of **Python**, **CI/CD**, **DBT**, 
**Google BigQuery**, and **Google Cloud Storage** to automate and scale the data workflow.

I developed a dashboard with two tiles by:

* Using the PetFinder dataset of cats and dogs
* Creating a pipeline for processing this dataset and putting it into the Google Cloud Bucket datalake using python and IaC terraform
* Creating a pipeline for moving the data from the lake to a data warehouse using python
* Transforming the data in the data warehouse: prepare it for the dashboard using dbt and spark
* Building a dashboard to visualize the data using looker
* Batch processing is automated to run daily using Github Actions

## Table of Contents
- [Project Goal](#goal)
- [Data Source](#data-source)
- [Pipeline Architecture](#pipeline-architecture)
- [Technologies Used](#technologies-used)
- [Setup Instructions](#setup-instructions)
  - [Docker](#docker)
  - [Data Ingestion](#data-ingestion)
  - [Data Processing](#data-processing)
  - [DBT Transformations](#dbt-transformations)
- [Data Flow](#data-flow)
- [Running the Pipeline](#running-the-pipeline)
- [Visualization](#visualization)
- [Lessons Learned](#lessons-learned)

---

## Goal

The goal of this project is to create a scalable and automated data pipeline that:
1. Ingests data daily from the **PetFinder API**.
2. Processes the data using **Spark**.
3. Transforms and loads it into **BigQuery** using **DBT**.
4. Visualizes the data in a dashboard.

This pipeline is designed to handle large-scale data, allowing users to analyze pet adoption data for insights.

---

## Data Source

The data is sourced from the **PetFinder API**, which provides information about adoptable pets from various organizations. 
The dataset includes details such as pet names, types, ages, breeds, and adoption statuses.

- PetFinder API documentation: [PetFinder API Documentation](https://www.petfinder.com/developers/)

---

## Pipeline Architecture

The architecture of the data pipeline involves several components:
1. **Data Ingestion**: A Python script fetches data from the PetFinder API and stores it in **Google Cloud Storage**.
2. **Data Processing**: The ingested data is processed using **Apache Spark** to clean, transform, and aggregate it.
3. **Transformations**: **DBT** is used for further transformations of the processed data in **BigQuery**.
4. **Visualization**: Data is visualized using a dashboard tool (e.g., Google Data Studio or Metabase).

---

## Technologies Used

- **Docker**: For containerizing the components of the pipeline, ensuring a consistent environment for data ingestion, processing, and transformations.
- **Terraform**: Infrastructure as code (IaC)
- **Apache Spark**: For batch processing of large datasets.
- **DBT**: For performing SQL-based transformations on the data in BigQuery.
- **Google Cloud Storage (GCS)**: For storing raw data before and after processing.
- **BigQuery Data Warehouse**: For storing processed and transformed data in a data warehouse.
- **Visualization Tools**: Google Data Studio Looker
- **Python**: For writing scripts to handle data ingestion.


* **Workflow orchestration**: Airflow, Prefect, Luigi, ...
* **Batch processing**: Spark, Flink, AWS Batch, ...
* **Stream processing**: Kafka, Pulsar, Kinesis, ...

---

## Setup Instructions

### **Clone/Fork My Repo in Gihub**

1. **Fork/Clone the repository**:
   - Clone the repository to your local machine or fork it to your GitHub account.

2. **Set up secrets**:
   - Go to the repository's **Settings** > **Secrets and variables** > **Actions**.
   - Add the following secrets:
     - `GCP_CREDENTIALS`: Google Cloud credentials file (as a JSON string).
     - `PETFINDER_API_KEY`: PetFinder API key.
     - `PETFINDER_API_ID`: PetFinder API ID.

3. **Ensure dependencies are listed** in the `requirements.txt` file:
   - Make sure the `requirements.txt` file includes all the required dependencies for the project.
   - Install dependencies via the following command:
     ```bash
     pip install -r requirements.txt
     ```

4. **Review the README**:
   - Go through the README for any specific environment setup or instructions related to the cloud environment and the pipeline.

5. **Wait for the Action to Run**:
   - The scheduled GitHub Action will automatically trigger according to the defined schedule (e.g., daily at midnight UTC).
   - Alternatively, the action can be manually triggered via the **GitHub Actions tab** in the repository.


### **API Key and Access Token Setup**

To use the PetFinder API, you need to obtain your **API key** and **API secret** from PetFinder. Here's how to get them:

1. **Sign up for an account** on PetFinder:
   - Visit [PetFinder API](https://www.petfinder.com/developers/) to sign up and create a developer account.
   - Once logged in, go to the [API Key Management](https://www.petfinder.com/developers/) page to generate your API key and secret.

2. **Get Access Token**:
   After you have your **API key** and **API secret**, you'll need to generate an **access token** to authenticate your API requests.

   Use the following `curl` command (or a Python script) to get the access token:
   ```bash
   curl -d "grant_type=client_credentials&client_id={YOUR-CLIENT-ID}&client_secret={YOUR-CLIENT-SECRET}" https://api.petfinder.com/v2/oauth2/token
   ```
   
   Replace `{YOUR-CLIENT-ID}` and `{YOUR-CLIENT-SECRET}` with your own **API Key** and **API Secret**.

   The response will look something like this:
   ```json
   {
     "token_type": "bearer",
     "expires_in": 3600,
     "access_token": "your_access_token_here"
   }
   ```

3. **Set up environment variables**:
   - Store your **API key**, **API secret**, and **access token** in your environment variables for security and convenience.

   For example, in your terminal (Linux/macOS):
   ```bash
   export PETFINDER_API_KEY="your-client-id"
   export PETFINDER_API_SECRET="your-client-secret"
   export PETFINDER_ACCESS_TOKEN="your-access-token"
   ```

   Or, for Windows (using PowerShell):
   ```bash
   $env:PETFINDER_API_KEY="your-client-id"
   $env:PETFINDER_API_SECRET="your-client-secret"
   $env:PETFINDER_ACCESS_TOKEN="your-access-token"
   ```

4. **Use the Access Token**:
   After setting up the environment variables, the program will use the access token to authenticate requests to the PetFinder API.


### **Important Notes**:
- Each user needs to create their own API key and access token as **they are unique to each user**.
- The access token typically expires after an hour, so you'll need to refresh it periodically.
- Make sure not to share your **API key** and **secret** publicly to avoid unauthorized access.


### Steps to Create a Google Cloud Storage Bucket

1. **Sign in to Google Cloud Console**:
   - Visit the [Google Cloud Console](https://console.cloud.google.com/).
   - Sign in with your Google account. If you don't have one, you will need to create an account.

2. **Create a Google Cloud Project**:
   - If you don't have a project yet, you'll need to create one.
     1. In the Cloud Console, click on the **project drop-down** at the top of the page.
     2. Click **New Project**.
     3. Name your project, select your billing account (if prompted), and choose a location.
     4. Click **Create**.

3. **Enable Google Cloud Storage API**:
   - In the Cloud Console, navigate to the **APIs & Services** > **Library**.
   - Search for **Google Cloud Storage** in the search bar and select **Google Cloud Storage JSON API**.
   - Click **Enable** to enable the API for your project.

4. **Create a Service Account**:
   - Navigate to **IAM & Admin** > **Service Accounts** in the Google Cloud Console.
   - Click **Create Service Account**.
     1. **Service Account Name**: Enter a name (e.g., `petfinder-api-access`).
     2. **Role**: Choose **Project > Owner** (or a more restrictive role if needed).
     3. In the **Role** dropdown, select **Storage Object Admin**.
     4. **Key**: Under **Key**, select **JSON**. This will generate a key file that you'll download, which will be used in your Python script to authenticate.
   - Click **Create** and save the downloaded JSON key to a secure location on your machine.

5. **Create a Google Cloud Storage Bucket**:
   - In the Google Cloud Console, go to the **Cloud Storage** section: **Storage** > **Browser**.
   - Click **Create Bucket**.
     1. **Bucket Name**: Choose a globally unique name for your bucket (e.g., `my-petfinder-bucket-12345`).
     2. **Location Type**: Choose the location (e.g., **Multi-region** or **Region**). For simplicity, you can choose a **Multi-region** location such as `US`.
     3. **Storage Class**: Select the default storage class (e.g., **Standard**).
     4. Click **Create**.

6. **[IF NEEDED] To Adjust Permissions for Your Service Account**:
   - In the **IAM & Admin** section, click **IAM**.
   - Re-download key: Click the three vertical dots next to your service account and select **Manage Keys**

7. **Use the Bucket and Service Account in Your Script**:
   - In your Python script, set the `credentials_file` path to the downloaded JSON file for the service account.
   - Set the `bucket_name` to the name of the bucket you created in step 5.

### Example Setup in Python Script:
In your `main()` function in petfinder_data_loader.py `PetFinderDataLoader`, use the following values:

```python
credentials_file = '/path/to/your/service-account-file.json'  # Path to your Service Account JSON key
bucket_name = 'your-gcs-bucket-name'  # Replace with the name of your bucket
```

---

### Additional Notes:
- **Bucket Naming Convention**: The bucket name must be globally unique across Google Cloud. Try appending random numbers or using unique prefixes.
- **Service Account Key**: Keep the service account JSON file secure. It's used for authenticating your application to Google Cloud services.
  
By following these steps, you should be able to create a Google Cloud Storage bucket and configure your script to upload data to it securely.


--

### Docker

1. Install [Docker](https://www.docker.com/get-started) on your local machine.
2. Clone this repository and navigate to the project folder.
3. Build the Docker images for the different components using the following commands:

   ```bash
   docker build -t petfinder-data-ingestion ./data-ingestion
   docker build -t petfinder-spark-job ./spark-job
   docker build -t petfinder-dbt ./dbt
   ```

### Data Ingestion

1. The data ingestion component fetches pet data from the PetFinder API and stores it in Google Cloud Storage.
2. You need to create a **Google Cloud Storage bucket** for storing raw data.

**Dockerfile for Data Ingestion**:
```Dockerfile
# Use a base image with Python installed
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy the script to the container
COPY petfinder_data_loader.py /app

# Install dependencies
RUN pip install requests google-cloud-storage

# Command to run the data ingestion script
CMD ["python", "petfinder_data_loader.py"]
```

### Data Processing

1. The **Spark** job processes the raw data stored in Google Cloud Storage. The job cleans and transforms the data, such as handling missing values, formatting dates, and aggregating pet adoption data.

**Dockerfile for Spark Processing**:
```Dockerfile
# Use the official Spark image
FROM bitnami/spark:latest

# Set working directory
WORKDIR /app

# Copy your Spark job to the container
COPY spark_job.py /app

# Install dependencies
RUN pip install google-cloud-bigquery

# Command to run the Spark job
CMD ["spark-submit", "spark_job.py"]
```

### DBT Transformations

1. The **DBT** transformations take place in **BigQuery**, where raw data is cleaned and prepared for analysis.

Tables are partitioned and clustered in a way that makes sense for the upstream queries (with explanation)

**Dockerfile for DBT**:
```Dockerfile
# Use the official DBT image for BigQuery
FROM fishtownanalytics/dbt-bigquery:latest

# Set working directory
WORKDIR /app

# Copy DBT project files to the container
COPY dbt_project.yml /app
COPY models /app/models

# Command to run DBT transformations
CMD ["dbt", "run"]
```

DBT Example of partitioning and clustering:

```SQL

-- models/pet_adoption_model.sql
{{ 
  config(
    materialized='table',
    partition_by={"field": "adopted_at", "type": "DATE"},
    cluster_by=["adoption_center", "breed"]
  )
}}

WITH pet_adoptions AS (
  SELECT
    pet_id,
    pet_name,
    breed,
    adoption_center,
    adopted_at
  FROM
    raw.pet_adoptions
  WHERE
    adopted_at >= '2023-01-01'
)

SELECT
  pet_id,
  pet_name,
  breed,
  adoption_center,
  adopted_at
FROM
  pet_adoptions


```

---

## Data Flow

1. **Data Ingestion**: The Python script (`petfinder_data_loader.py`) pulls data from the PetFinder API and stores it in **Google Cloud Storage**.
2. **Spark Processing**: The Spark job (`spark_job.py`) fetches the raw data from GCS, processes it, and stores the cleaned data in BigQuery.
3. **DBT Transformations**: The DBT project applies transformations on the data in BigQuery for further analysis.
4. **Visualization**: A dashboard in Google Data Studio or Metabase uses the transformed data from BigQuery to visualize adoption trends, pet categories, and more.

---

## Running the Pipeline

1. **Build Docker Images**: Run the `docker build` commands for each component as mentioned in the Setup Instructions.
2. **Start Data Ingestion**: Run the data ingestion container to fetch data from the PetFinder API.
   ```bash
   docker run petfinder-data-ingestion
   ```
3. **Run Spark Job**: After ingestion, run the Spark job to process the data.
   ```bash
   docker run petfinder-spark-job
   ```
4. **Run DBT Transformations**: Apply transformations to the data in BigQuery using DBT.
   ```bash
   docker run petfinder-dbt
   ```

---

## Visualization

After loading the transformed data into BigQuery, you can create a dashboard to visualize key metrics and trends in pet adoption. For example:
- **Tile 1**: A bar chart showing the distribution of pets by type.
- **Tile 2**: A time series chart showing the number of adoptions over time.

You can use **Google Data Studio** or **Metabase** to create and share the dashboard.

Your dashboard should contain at least two tiles, we suggest you include:

- 1 graph that shows the distribution of some categorical data 
- 1 graph that shows the distribution of the data across a temporal line

Ensure that your graph is easy to understand by adding references and titles.

---

## Lessons Learned

- **Batch Processing**: Learning how to process large datasets efficiently with Spark was key to handling the PetFinder data at scale.
- **Containerization**: Docker helped me create isolated environments for each part of the pipeline, making development and deployment much easier.
- **Transformation Best Practices**: Using DBT for transformations made it easier to maintain and version control SQL-based transformations, ensuring the integrity of the data.
- **Cloud Integration**: Integrating with **Google Cloud Storage** and **BigQuery** enabled me to scale the pipeline and store data securely for analysis.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

