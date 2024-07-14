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

# Initialize Cloud Logging
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


def process_survey_data(product, source, file_path):

    try:
        data = pd.read_csv(file_path)
        cloud_logger.info("Data loaded successfully.")
    except Exception as e:
        cloud_logger.error(f"Error loading data: {e}")
        raise

    date_column = None
    for col in data.columns:
        if 'date' in col.lower() or data[col].apply(lambda x: isinstance(x, str) and '/' in x).all():
            date_column = col
            data[col] = data[col].apply(format_date)
            cloud_logger.info(f"Date column identified: {col}")
            break

    if not date_column:
        cloud_logger.warning("No date column identified.")

    question_texts = data.iloc[0]

    columns_to_drop = []
    for col in data.columns:
        if not (col.startswith('Q') and col[1:].isdigit()):
            if col != date_column:
                columns_to_drop.append(col)
        else:
            if "NPS" in col or "rating" in col.lower() or "scale" in col.lower():
                columns_to_drop.append(col)
            elif pd.to_numeric(data[col][1:], errors='coerce').notna().all():
                columns_to_drop.append(col)
            elif data[col][1:].str.strip().str.lower().isin(['yes', 'no']).all():
                columns_to_drop.append(col)

    data.drop(columns=columns_to_drop, inplace=True)
    # cloud_logger.info(f"Dropped columns: {columns_to_drop}")

    data = data[1:]

    data = data[~data.apply(lambda row: row.astype(str).str.contains('QID').any(), axis=1)]
    # cloud_logger.info("Filtered out rows containing 'QID'.")


    for col in data.columns:
        data[col] = data[col].apply(lambda x: x if is_valid_feedback(x) and is_english(x) else None)
        # cloud_logger.info(f"Processed feedback for column: {col}")

    for col in data.columns:
        if col.startswith('Q'):
            question_text = question_texts[col]
            data[col] = data[col].apply(lambda x: f"{source}: {question_text}: {x}" if pd.notna(x) else x)
            # cloud_logger.info(f"Appended question text to column: {col}")

    data.dropna(axis=1, how='all', inplace=True)
    # cloud_logger.info("Dropped columns with all NaN values.")

    long_format_data = data.melt(var_name='Question Code', value_name='Feedback')
    long_format_data = long_format_data.dropna(subset=['Feedback'])
    # cloud_logger.info("Converted data to long format and filtered out rows with NaN feedback.")

    if product != "Others":
        long_format_data['Product'] = product
        long_format_data['Subcategory'] = None
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

    if date_column:
        long_format_data['Date'] = data[date_column].values

    desired_columns = ['Date', 'Feedback', 'Product', 'Subcategory', 'Feedback Category', 'Sentiment', 'Sentiment Score', 'Source']
    long_format_data = long_format_data.reindex(columns=desired_columns)

    return data

    #TODO: Add to SQL Analytics

    # output_file_path = f'/path/to/output/Transformed_{product}_{source}.csv'
    # try:
    #     long_format_data.to_csv(output_file_path, index=False)
    #     cloud_logger.info(f"Data transformation complete. File saved to: {output_file_path}")
    # except Exception as e:
    #     cloud_logger.error(f"Error saving transformed data: {e}")
    #     raise
        

