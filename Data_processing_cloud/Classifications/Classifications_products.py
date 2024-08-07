#!/usr/bin/env python
# coding: utf-8

# In[ ]:


##Classification Pipleline for defined products
from Data_processing_cloud.Gemini_Models.Subcategory_Classification_Gemini_model import classify_subcategory
from Data_processing_cloud.Gemini_Models.Sentiment_Score_Category_model import classify_sentiment
import time
from Data_processing_cloud.Gemini_Models.Feedback_Categorisation import feedback_categorisation
from Data_processing_cloud.pubsub_helper import publish_message

product_dict = {
    "Cards": ["Debit Card", "Credit Card"],
    "Unsecured Loans": ["Cashline", "Personal Loan", "Renovation Loan", "Education Loan"],
    "Secured Loans": ["Car Loan", "Mortgage/Home Loan"],
    "Digital Channels": ["DigiBank App", "Internet Banking(iBanking)", "Paylah!"],
    "Investments": ["digiPortfolio", "Non-Unit Trust/Equities", "Unit Trust", "Vickers"],
    "DBS Treasures": ["Treasures Relationship Manager(RM)", "DBS Wealth Planning Manager", "DBS Treasures (General)"],
    "Self-Service Banking": ["SSB", "VTM(Video Teller Machine)", "Phone Banking", "Coin Deposit Machine","SSB (Self-Service Banking)"],
    "Insurance": ["General Insurance", "Life Insurance"],
    "Deposits": ["DBS Deposit Account", "Payments", "PayNow", "Cheque", "GIRO", "digiVault","Paynow"],
    "Contact Center": ["DBS Hotline", "DBS Branches/Staff","Contact Center"],
    "Webpages": ["Websites"],
    "Remittance": ["Overseas Transfer"],
    "Others": ["Others"]
}

def match_product(subcategory):
    if not isinstance(subcategory, str):
        # Log an error or handle it accordingly
        return 'Others'
    for product, subproducts in product_dict.items():
        if subcategory in subproducts:
            return product
    return 'Others'
    

import logging

def classification_defined_products(df):
    import os
    os.environ["GOOGLE_CLOUD_PROJECT"] = "903333611831"
    logging.basicConfig(level=logging.INFO)

    if df['Subcategory'].isnull().any() or df['Feedback'].isnull().any() or df['Subcategory'].eq('').any() or df['Feedback'].eq('').any():
        error_message = "Subcategory or Feedback contains None or empty values."
        logging.error(error_message)
        publish_message(f"Error - Operation could not be completed: {error_message}", 'ERROR')
        return None  # Early exit with None to indicate processing failure due to invalid input

    try: 
        logging.info("Starting Subcategory Categorisation")
        df['Product'] = df['Subcategory'].apply(match_product)
        publish_message('Completed Subcategory Categorisation', 'IN PROGRESS')
        logging.info("Completed: Subcategory Categorisation")

        logging.info("Starting Feedback Categorisation")
        df['Feedback Category'] = df.apply(lambda row: feedback_categorisation(row['Feedback'], row['Subcategory']), axis=1)
        publish_message('Completed Feedback Categorisation', "IN PROGRESS")
        logging.info("Completed: Feedback Categorisation")

        logging.info("Starting Sentiment Analysis")
        sentiment_results = df['Feedback'].apply(classify_sentiment)
        df['Sentiment Score'], df['Sentiment'] = zip(*sentiment_results)
        publish_message('Completed Sentiment Analysis', "IN PROGRESS")
        logging.info("Completed: Sentiment Analysis")

        

        return df
    
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        publish_message(f"Error - Operation could not be completed: {e}", 'ERROR')
        return None

