#!/usr/bin/env python
# coding: utf-8

# In[6]:


import os
def parse_filename(file_path):

    filename = os.path.basename(file_path)
    # Split the filename using the double underscore separator
    parts = filename.split('__')
    
    # Check if the filename is in the correct format
    if len(parts) < 3:
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

##event and context is passed by google bucket
def process_data(event,context):
    print("Script started")
    init_vertex_ai()

    project_id = '903333611831'
    
    db_user_secret_id = 'DB_USER'
    db_password_secret_id = 'DB_PASS'
    storage_bucket_name = 'jbaaam_upload'
    
    # Retrieve secrets
    db_user = access_secret_version(db_user_secret_id, project_id)
    db_password = access_secret_version(db_password_secret_id, project_id)

    ##Get info from trigger in bucket
    bucket_name = event['bucket']
    file_name = event['name']
    
    # Download the file from Google Cloud Storage
    local_file_path = download_file_from_bucket(storage_bucket_name, file_name)
    # local_file_path='/Users/phonavitra/Desktop/term 5/Service Studio/Test/Others__Social Media__smalltest.csv'
    product, source=parse_filename(local_file_path)

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
        raise ValueError("Source not supported: {}".format(source))


    # Insert processed data into PostgreSQL
    # Prepare the data for insertion
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
    for row in data
    ]

    query = """INSERT INTO test_dataprocessing (date, feedback, product, subcategory, feedback_category, sentiment, sentiment_score, sourc) VALUES %s"""
    execute_postgres_query(db_user, db_password, 'feedback_db', '/cloudsql/jbaaam:asia-southeast1:feedback', query)
    
    # Delete the temporary file
    os.remove(local_file_path)

    # return "Data processing and storage complete"
    # output_file_path = f'/Users/phonavitra/Desktop/term 5/Service Studio/Test/Model Results (All sources)/Social Media_Results.csv'
    # try:
    #     data.to_csv(output_file_path, index=False)
    #     print(f"Data transformation complete. File saved to: {output_file_path}")
    # except Exception as e:
    #     print(f"Error saving transformed data: {e}")
    #     raise

    print("Script ended")

# process_data(None,None)


# In[ ]:




