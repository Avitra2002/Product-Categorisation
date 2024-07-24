#!/usr/bin/env python
# coding: utf-8

# In[6]:


import os
from pubsub_helper import publish_message
# from zoneinfo import ZoneInfo
def parse_filename(file_path):

    filename = os.path.basename(file_path)
    # Split the filename using the double underscore separator
    parts = filename.split('__')
    
    # Check if the filename is in the correct format
    if len(parts) < 3:
        publish_message("Error: Filename format is incorrect. Expected format: 'product__source__fname'")
        raise ValueError("Filename format is incorrect. Expected format: 'product__source__fname'")
    
    # Extract the product and source values
    product = parts[0]
    source = parts[1]
    
    return product, source


# In[11]:


# Cloud Function entry point
import os
import pandas as pd
from authentification import access_secret_version, download_file_from_bucket, execute_postgres_query, init_vertex_ai
from  Functions.survey_problem_solution import process_survey_data
from Functions.five_Star_Review import process_five_star_reviews
from Functions.social_media import process_social_media_data
from Functions.voice_call import process_voice_call_data
import logging
from clear_logs import clear_logs

##event and context is passed by google bucket
def process_data(event,context):
    print("Script started")
    # cloud_logger.info(f"Context: {context}")
    init_vertex_ai()

    project_id = '903333611831'
    
    db_user_secret_id = 'DB_USER'
    db_password_secret_id = 'DB_PASS'
    storage_bucket_name = 'jbaaam_upload'
    
    # Retrieve secrets
    db_user = access_secret_version(db_user_secret_id, project_id)
    db_password = access_secret_version(db_password_secret_id, project_id)
    print("Secrets retrieved successfully")
    print (f'DB_USER: {db_user}, DB_PASSWORD:{db_password}')

    clear_logs(db_user, db_password, '/cloudsql/jbaaam:asia-southeast1:feedback', 'feedback_db')

    ##Get info from trigger in bucket
    file = event
    file_name= file["name"]
    bucket_name=file['bucket']

    # content_type = event['data']['contentType']
    # time_created = event['data']['timeCreated']
    print(f"File: {file_name}, Bucket: {bucket_name}")

    
    # Download the file from Google Cloud Storage
    local_file_path = download_file_from_bucket(bucket_name, file_name)

    # local_file_path='/Users/phonavitra/Desktop/term 5/Service Studio/Test/Others__Social Media__smalltest.csv'
    product, source=parse_filename(file_name)

    # df = pd.read_csv(local_file_path)

    if source == "Product Survey" or source == "Problem Solution Survey":
        data= process_survey_data(product, source, local_file_path)
    elif source == "Call Center":
        data=process_voice_call_data(local_file_path, product,source)
    elif source == "Social Media":
        data= process_social_media_data(local_file_path,product,source)
    elif source == "5 Star Review":
        data= process_five_star_reviews(local_file_path,product,source)
    else:
        # Raise a ValueError for unsupported source values
        publish_message("Error: Source not supported: {}".format(source))
        raise ValueError("Source not supported: {}".format(source))

    publish_message(f"Upload Successful. Filename: {file_name}. Data classification started")


    # Insert processed data into PostgreSQL
    # Prepare the data for insertion
    if isinstance(data, pd.DataFrame) and not data.empty:
        data_to_insert = [
            (
                row['Date'], 
                row['Feedback'], 
                row['Product'], 
                row['Subcategory'], 
                row['Feedback Category'], 
                row['Sentiment'], 
                row['Sentiment Score'], 
                row['Source']
            )
            for index, row in data.iterrows()
        ]
    else:
        publish_message("Error:No data to process or data is not in expected format.")
        # cloud_logger.error("No data to process or data is not in expected format.")
        return

    query = """INSERT INTO test_dataprocessing (date, feedback, product, subcategory, feedback_category, sentiment, sentiment_score, source) VALUES %s"""
    execute_postgres_query(db_user, db_password, 'feedback_db', '/cloudsql/jbaaam:asia-southeast1:feedback', query,data_to_insert)

    
    # Delete the temporary file
    os.remove(local_file_path)
    publish_message("Success: Data classification completed and added to database.")

    print("Script ended")




# In[ ]:




