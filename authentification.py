from google.cloud import secretmanager_v1beta1
from google.cloud import storage
import psycopg2
import os
import vertexai

# Function to retrieve secret from Secret Manager
def access_secret_version(secret_id, project_id):
    client = secretmanager_v1beta1.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")

# Function to download a file from Google Cloud Storage bucket
def download_file_from_bucket(bucket_name, file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    temp_local_file = f"/tmp/{file_name}"  # Use /tmp directory for temporary storage in Cloud Function

    blob.download_to_filename(temp_local_file)
    return temp_local_file

# Function to connect to PostgreSQL and execute queries
def execute_postgres_query(db_user, db_password, db_name, db_host, query):
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host='/cloudsql/jbaaam:asia-southeast1:feedback'
    )
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()

def execute_postgres_query(db_user, db_password, db_name, db_host, query):
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host
    )
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()

def init_vertex_ai():
    # Initialize Vertex AI
    vertexai.init(project="903333611831", location="asia-southeast1") ##for Subcategory Classification Model
    vertexai.init(project="jbaaam", location="us-central1") ##for sentiment analysis model

