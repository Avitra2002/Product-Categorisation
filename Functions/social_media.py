#!/usr/bin/env python
# coding: utf-8




from Functions.is_english import is_english
from Functions.format_date import format_date
from Functions.valid_feedback import is_valid_feedback
import pandas as pd
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from datetime import datetime
import logging
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler
from Classifications.Classifications_products import classification_defined_products
from Classifications.Classification_Others import classification_undefined_products
import logging

# # Initialize Cloud Logging
# client = google.cloud.logging.Client()
# handler = CloudLoggingHandler(client)
# cloud_logger = logging.getLogger('cloudLogger')
# cloud_logger.setLevel(logging.DEBUG)
# cloud_logger.addHandler(handler)

#### FOR LOCAL TEST######
cloud_logger = logging.getLogger('cloudLogger')
cloud_logger.setLevel(logging.DEBUG)  # Set the logging level to DEBUG

# Create a console handler and set its log level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # Set the console handler level to DEBUG

# Define the log format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the console handler to the logger
cloud_logger.addHandler(console_handler)

#### FOR LOCAL TEST######

# file_path= '/Users/phonavitra/Desktop/term 5/Service Studio/Test/Others__Social Media__Cloud_function_test.csv'

def process_social_media_data(file_path, product, source):
    ##TODO: Change file to csv
    try:
        data = pd.read_csv(file_path)
        cloud_logger.info("Data loaded successfully social media.")
    except Exception as e:
        cloud_logger.error(f"Error loading data: {e}")
        raise

    date_column = None
    for col in data.columns:
        if 'date' in col.lower() and data[col].apply(lambda x: isinstance(x, str) and '/' in x).all():
            date_column = col
            data[col] = data[col].apply(format_date)
            cloud_logger.info(f"Date column identified and formatted: {col}")
            break
    if date_column:
        data.rename(columns={date_column: 'Date'}, inplace=True)

    if not date_column:
        cloud_logger.warning("No date column identified.")

    feedback_column = None
    for col in data.columns:
        if 'feedback' in col.lower() or 'comments' in col.lower() or 'mentions' in col.lower():
            feedback_column = col
            cloud_logger.info(f"Feedback column identified: {col}")
            break

    if feedback_column:
        data = data[data[feedback_column].apply(lambda x: pd.notna(x) and is_english(x) and is_valid_feedback(x))]
        data.rename(columns={feedback_column: 'Feedback'}, inplace=True)
    else:
        cloud_logger.warning("No feedback column identified.")
        raise ValueError("Feedback column is required for processing.")

    if product != "Others":
        data['Product'] = product
        data['Subcategory'] = None
        data['Feedback Category'] = ''
        data['Sentiment'] = None
        data['Sentiment Score'] = None
        data['Source'] = source
        # cloud_logger.info(f"Data identified: {data}")

        #TODO: Classification
        data= classification_defined_products(data)
    
    else:
        data['Product'] = ''
        data['Subcategory'] = None
        data['Feedback Category'] = ''
        data['Sentiment'] = None
        data['Sentiment Score'] = None
        data['Source'] = source
        # cloud_logger.info(f"Data identified: {data}")

        #TODO: Classification
        data = classification_undefined_products(data)

    desired_columns = ['Date', 'Feedback', 'Product', 'Subcategory', 'Feedback Category', 'Sentiment', 'Sentiment Score', 'Source']

    # if feedback_column:
    #     data.rename(columns={feedback_column: 'Feedback'}, inplace=True)
    

    data = data.reindex(columns=desired_columns)

    return data

     #TODO: Add to SQL Analytics

    # output_file_path = f'/path/to/output/Transformed_{product}_{source}_Social_Media.csv'
    # try:
    #     data.to_csv(output_file_path, index=False)
    #     cloud_logger.info(f"Data transformation complete. File saved to: {output_file_path}")
    # except Exception as e:
    #     cloud_logger.error(f"Error saving transformed data: {e}")
    #     raise

# Example usage:
# process_social_media_data('/Users/phonavitra/Desktop/term 5/Service Studio/raw part 1/Social Media mock data.csv', 'Product Name', 'Social Media Source')

