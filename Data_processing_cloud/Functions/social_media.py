#!/usr/bin/env python
# coding: utf-8




from Data_processing_cloud.Functions.is_english import is_english
from Data_processing_cloud.Functions.format_date import format_date
from Data_processing_cloud.Functions.valid_feedback import is_valid_feedback
import pandas as pd
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from datetime import datetime
import logging
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler
from Data_processing_cloud.Classifications.Classifications_products import classification_defined_products
from Data_processing_cloud.Classifications.Classification_Others import classification_undefined_products
import logging
from Data_processing_cloud.pubsub_helper import publish_message
from Data_processing_cloud.matching_subproduct import find_best_match

# Initialize Cloud Logging
# client = google.cloud.logging.Client()
# handler = CloudLoggingHandler(client)
# cloud_logger = logging.getLogger('cloudLogger')
# cloud_logger.setLevel(logging.DEBUG)
# cloud_logger.addHandler(handler)

#### FOR LOCAL TEST######
# cloud_logger = logging.getLogger('cloudLogger')
# cloud_logger.setLevel(logging.DEBUG)  # Set the logging level to DEBUG

# # Create a console handler and set its log level
# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.DEBUG)  # Set the console handler level to DEBUG

# # Define the log format
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# console_handler.setFormatter(formatter)

# # Add the console handler to the logger
# cloud_logger.addHandler(console_handler)

#### FOR LOCAL TEST######

# file_path= '/Users/phonavitra/Desktop/term 5/Service Studio/Test/Others__Social Media__Cloud_function_test.csv'

def process_social_media_data(file_path, product, source):
    
    try:
        # Load data from Excel or CSV
        if file_path.lower().endswith('.xls') or file_path.lower().endswith('.xlsx'):
            data = pd.read_excel(file_path)
            print(f"Excel data loaded successfully from {file_path}.")
        elif file_path.lower().endswith('.csv'):
            data = pd.read_csv(file_path)
            print(f"CSV data loaded successfully from {file_path}.")
        else:
            raise ValueError(f"Unsupported file format for {file_path}. Only Excel (.xls, .xlsx) and CSV (.csv) files are supported.")
    except Exception as e:
        publish_message(f"Error processing {file_path}: {e}","ERROR")
        print(f"Error processing {file_path}: {e}")
        raise

    date_column = None
    for col in data.columns:
        if 'date' in col.lower() and data[col].apply(lambda x: isinstance(x, str) and '/' in x).all():
            date_column = col
            data[col] = data[col].apply(format_date)
            print(f"Date column identified and formatted: {col}")
            break
        elif 'date' in col.lower() and data[col].apply(lambda x: isinstance(x, str) and '-' in x).all():
            date_column = col
            data[col] = data[col].apply(format_date)
            print(f"Date column identified and formatted: {col}")
            break
    if date_column:
        data.rename(columns={date_column: 'Date'}, inplace=True)

    if not date_column:
        publish_message("Error: No date column identified. Date column is required for processing",'ERROR')
        print("No date column identified.")
        raise ValueError("Date column is needed for processing")

    feedback_column = None
    for col in data.columns:
        if 'date' in col.lower() and data[col].apply(lambda x: isinstance(x, str) and '/' in x).all():
            date_column = col
            data[col] = data[col].apply(format_date)
            print(f"Date column identified and formatted: {col}")
            break
        elif 'date' in col.lower() and data[col].apply(lambda x: isinstance(x, str) and '-' in x).all():
            date_column = col
            data[col] = data[col].apply(format_date)
            print(f"Date column identified and formatted: {col}")
            break

    if feedback_column:
        data = data[data[feedback_column].apply(lambda x: pd.notna(x) and is_english(x) and is_valid_feedback(x))]
        data.rename(columns={feedback_column: 'Feedback'}, inplace=True)
    else:
        publish_message("Error: No feedback column identified. Feedback column is required for processing",'ERROR')
        print("No feedback column identified.")
        raise ValueError("Feedback column is required for processing.")
    
    if len(data) > 95:
        error_message = f"Data exceeds the manageable row limit: {len(data)} rows. Keep upload dataset size to about 80-95 rows after transformation."
        print(error_message)
        publish_message(error_message, 'ERROR')
        raise ValueError("Exceeded maximum row limit for processing.")

    if product != "Others":
        subproduct= find_best_match(product)
        
        data['Product'] = ''
        data['Subcategory'] = subproduct
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
    print(f"Data received from social media processing: Type = {type(data)}, Shape = {data.shape if isinstance(data, pd.DataFrame) else 'N/A'}")


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

