#!/usr/bin/env python
# coding: utf-8

# In[ ]:
# gcloud auth application-default login

##Classification for undefined products
# from Gemini_Models.Subcategory_Classification_Gemini_model import classify_subcategory
# import time

# ##dictionary to map from subproducts to products

# def classification_undefined_products(df):
#     product_dict = {
#         "Cards": ["Debit Card", "Credit Card"],
#         "Unsecured Loans": ["Cashline", "Personal Loan", "Renovation Loan", "Education Loan"],
#         "Secured Loans": ["Car Loan", "Mortgage/Home Loan"],
#         "Digital Channels": ["DigiBank App", "Internet Banking(iBanking)", "Paylah!"],
#         "Investments": ["digiPortfolio", "Non-Unit Trust/Equities", "Unit Trust", "Vickers"],
#         "DBS Treasures": ["Treasures Relationship Manager(RM)", "DBS Wealth Planning Manager", "DBS Treasures (General)"],
#         "Self-Service Banking": ["SSB", "VTM(Video Teller Machine)", "Phone Banking", "Coin Deposit Machine"],
#         "Insurance": ["General Insurance", "Life Insurance"],
#         "Deposits": ["DBS Deposit Account", "Payments", "PayNow", "Cheque", "GIRO", "digiVault"],
#         "Contact Center": ["DBS Hotline", "DBS Branches/Staff"],
#         "Webpages": ["Websites"],
#         "Remittance": ["Overseas Transfer"],
#         "Others": ["Others"]
#     }

#     ##########classify into subproducts############
#     def classify_subcategory_batch(texts):
    
#         batch_size = 20  # Define the batch size
#         batch_delay = 60 / 300  # Delay between each batch (60 seconds / 300 requests per minute)
        
#         subcategories = []
#         for i in range(0, len(texts), batch_size):
#             batch = texts[i:i+batch_size]
#             for text in batch:
#                 subcategory = classify_subcategory(text)
#                 subcategories.append(subcategory)
#             time.sleep(batch_delay)  # Wait before processing the next batch
        
#         return subcategories

    
#     # Classify feedback into subproducts
#     df['Subcategory'] = classify_subcategory_batch(df['Feedback'].tolist())

#     # Link subproducts to products
#     def match_product(subcategory):
#         for product, subproducts in product_dict.items():
#             if subcategory in subproducts:
#                 return product
#         return 'Others'  # Return 'Others' if subcategory doesn't match any product
    
#     df['Product'] = df['Subcategory'].apply(match_product)

    
    # df['Subcategory'] = df['Feedback'].apply(classify_subcategory)

    # ## link subproducts to products
    # def match_product(subcategory):
    #     for product, subproducts in product_dict.items():
    #         if subcategory in subproducts:
    #             return product
    #     return 'Others'  # Return None if subcategory doesn't match any product
    
    # df['Product'] = df['Subcategory'].apply(match_product)




    ####categorise into feedback sentiment#############


    ## categorise sentiment and score

    # return df


import time
from Gemini_Models.Subcategory_Classification_Gemini_model import classify_subcategory
from Gemini_Models.Sentiment_Score_Category_model import classify_sentiment
from Gemini_Models.Feedback_Categorisation import feedback_categorisation
import logging

# Dictionary to map from subproducts to products
product_dict = {
    "Cards": ["Debit Card", "Credit Card"],
    "Unsecured Loans": ["Cashline", "Personal Loan", "Renovation Loan", "Education Loan"],
    "Secured Loans": ["Car Loan", "Mortgage/Home Loan"],
    "Digital Channels": ["DigiBank App", "Internet Banking(iBanking)", "Paylah!"],
    "Investments": ["digiPortfolio", "Non-Unit Trust/Equities", "Unit Trust", "Vickers"],
    "DBS Treasures": ["Treasures Relationship Manager(RM)", "DBS Wealth Planning Manager", "DBS Treasures (General)"],
    "Self-Service Banking": ["SSB", "VTM(Video Teller Machine)", "Phone Banking", "Coin Deposit Machine","SSB (Self-Service Banking)"],
    "Insurance": ["General Insurance", "Life Insurance"],
    "Deposits": ["DBS Deposit Account", "Payments", "PayNow", "Cheque", "GIRO", "digiVault"],
    "Contact Center": ["DBS Hotline", "DBS Branches/Staff","Contact Center"],
    "Webpages": ["Websites"],
    "Remittance": ["Overseas Transfer"],
    "Others": ["Others"]
}

def classify_subcategory_batch(texts, batch_size=30, delay_per_batch=15):
    subcategories = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_subcategories = [classify_subcategory(text) for text in batch]
        subcategories.extend(batch_subcategories)
        if i + batch_size < len(texts):  # To avoid sleeping after the last batch
            time.sleep(delay_per_batch)  # Wait before processing the next batch
    return subcategories

logging.basicConfig(level=logging.INFO)

def classify_sentiment_batch(texts, batch_size=30, delay_per_batch=12):
    sentiments = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_sentiments = [classify_sentiment(text) for text in batch]
        sentiments.extend(batch_sentiments)
        if i + batch_size < len(texts):  
            logging.info(f"Processed batch {i // batch_size + 1}, sleeping for {delay_per_batch} seconds.")
            time.sleep(delay_per_batch)
    return sentiments

def classify_feedback_batch(feedbacks, products, batch_size=30, delay_per_batch=15):
    categories = []
    for i in range(0, len(feedbacks), batch_size):
        batch_feedbacks = feedbacks[i:i+batch_size]
        batch_products = products[i:i+batch_size]
        batch_categories = [feedback_categorisation(feedback, product) for feedback, product in zip(batch_feedbacks, batch_products)]
        categories.extend(batch_categories)
        if i + batch_size < len(feedbacks):  # To avoid sleeping after the last batch
            time.sleep(delay_per_batch)  # Wait before processing the next batch
    return categories

def classification_undefined_products(df):
    ###### Classify feedback into subproducts#########
    df['Subcategory'] = classify_subcategory_batch(df['Feedback'].tolist())

    # Link subproducts to products
    def match_product(subcategory):
        for product, subproducts in product_dict.items():
            if subcategory in subproducts:
                return product
        return 'Others'  # Return 'Others' if subcategory doesn't match any product
    
    df['Product'] = df['Subcategory'].apply(match_product)

    ####categorise into feedback category#############
    df['Feedback Category'] = classify_feedback_batch(df['Feedback'].tolist(), df['Subcategory'].tolist())

     ## categorise sentiment and score
    sentiment_results = classify_sentiment_batch(df['Feedback'].tolist())
    df['Sentiment Score'], df['Sentiment'] = zip(*sentiment_results)
    return df








