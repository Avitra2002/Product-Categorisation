#!/usr/bin/env python
# coding: utf-8

# In[ ]:


###TRANSFORMING SURVERY/PROBLEM SOLUTION
from Functions.is_english import is_english
from Functions.format_date import format_date
from Functions.valid_feedback import is_valid_feedback
import pandas as pd
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from datetime import datetime
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler
from Classifications.Classifications_products import classification_defined_products
from Classifications.Classification_Others import classification_undefined_products
import logging
import re
from pubsub_helper import publish_message

# Initialize Cloud Logging
client = google.cloud.logging.Client()
handler = CloudLoggingHandler(client)
cloud_logger = logging.getLogger('cloudLogger')
cloud_logger.setLevel(logging.DEBUG)
cloud_logger.addHandler(handler)

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


def process_survey_data(product, source, file_path):

    try:
        # Load data from Excel or CSV
        if file_path.lower().endswith('.xls') or file_path.lower().endswith('.xlsx'):
            data = pd.read_excel(file_path)
            cloud_logger.info(f"Excel data loaded successfully from {file_path}.")
        elif file_path.lower().endswith('.csv'):
            data = pd.read_csv(file_path)
            cloud_logger.info(f"CSV data loaded successfully from {file_path}.")
        else:
            raise ValueError(f"Unsupported file format for {file_path}. Only Excel (.xls, .xlsx) and CSV (.csv) files are supported.")
    except Exception as e:
        publish_message("Error processing {file_path}: {e}")
        cloud_logger.error(f"Error processing {file_path}: {e}")
        raise

    date_column = None
    for col in data.columns:
        if 'date' in col.lower() or data[col].apply(lambda x: isinstance(x, str) and '/' in x).all():
            date_column = col
            cloud_logger.info(f"Date column identified: {col}")
            data[col] = data[col].apply(format_date)
            
            break

    if not date_column:
        publish_message("Error: No date column identified. Date column is needed for processing")
        cloud_logger.warning("No date column identified.")

    question_texts = data.iloc[0]

    columns_to_drop = []
    for col in data.columns:
        if not (re.match(r'Q\d+[a-zA-Z]*$', col)):
            if col != date_column:
                columns_to_drop.append(col)
        else:
            if "NPS" in col or "rating" in col.lower() or "scale" in col.lower():
                columns_to_drop.append(col)
            elif pd.to_numeric(data[col][3:], errors='coerce').notna().all():
                columns_to_drop.append(col)
            elif data[col][3:].str.strip().str.lower().isin(['yes', 'no']).all():
                columns_to_drop.append(col)

    data.drop(columns=columns_to_drop, inplace=True)
    cloud_logger.info(f"Dropped columns: {columns_to_drop}")

    if date_column:
        date_series = data[date_column].copy()

    data = data[1:]

    data = data[~data.apply(lambda row: row.astype(str).str.contains('QID').any(), axis=1)]
    # cloud_logger.info("Filtered out rows containing 'QID'.")


    for col in data.columns:
        data[col] = data[col].apply(lambda x: x if is_valid_feedback(x) and is_english(x) else None)
        # cloud_logger.info(f"Processed feedback for column: {col}")

    for col in data.columns:
        if col.startswith('Q'):
            question_text = question_texts[col]
            if product != "Others":
                data[col] = data[col].apply(lambda x: f"{product} {question_text}: {x}" if pd.notna(x) else x)
            else:
                data[col] = data[col].apply(lambda x: f"{question_text}: {x}" if pd.notna(x) else x)
            # cloud_logger.info(f"Appended question text to column: {col}")

    data.dropna(axis=1, how='all', inplace=True)
    # cloud_logger.info("Dropped columns with all NaN values.")

    if date_column:
        data['Date'] = date_series

    long_format_data = data.melt(id_vars=['Date'], var_name='Question Code', value_name='Feedback')
    long_format_data = long_format_data.dropna(subset=['Feedback'])
    # cloud_logger.info("Converted data to long format and filtered out rows with NaN feedback.")

    if product != "Others":
        long_format_data['Product'] = None
        long_format_data['Subcategory'] = product
        long_format_data['Feedback Category'] = ''
        long_format_data['Sentiment'] = None
        long_format_data['Sentiment Score'] = None
        long_format_data['Source'] = source

        #TODO: Classification
        long_format_data=classification_defined_products(long_format_data)


    
    else:
        long_format_data['Product'] = None
        long_format_data['Subcategory'] = None
        long_format_data['Feedback Category'] = ''
        long_format_data['Sentiment'] = None
        long_format_data['Sentiment Score'] = None
        long_format_data['Source'] = source

        #TODO: Classification
        long_format_data=classification_undefined_products(long_format_data)

    desired_columns = ['Date', 'Feedback', 'Product', 'Subcategory', 'Feedback Category', 'Sentiment', 'Sentiment Score', 'Source']
    long_format_data = long_format_data.reindex(columns=desired_columns)

    return long_format_data
        

