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

# def classify_subcategory_batch(texts, batch_size=60, delay_per_batch=8):
#     subcategories = []
#     for i in range(0, len(texts), batch_size):
#         batch = texts[i:i+batch_size]
#         batch_subcategories = [classify_subcategory(text) for text in batch]
#         subcategories.extend(batch_subcategories)
#         if i + batch_size < len(texts):  # To avoid sleeping after the last batch
#             time.sleep(delay_per_batch)  # Wait before processing the next batch
#     return subcategories


def classification_defined_products(df):

    ##categorise into subproducts - ALREADY CLASSIFIED FROM FILTER
    # df['Subcategory'] = classify_subcategory_batch(df['Feedback'].tolist())

    # Link subproducts to products
    def match_product(subcategory):
        for product, subproducts in product_dict.items():
            if subcategory in subproducts:
                return product
        return 'Others'  # Return 'Others' if subcategory doesn't match any product
    
    
    try: 
        df['Product'] = df['Subcategory'].apply(match_product)
        publish_message('Completed Subcategory Categorisation', 'IN PROGRESS')

        print('Completed: Subcategory Categorisation')

        publish_message('Feedback Categorisation in progress','IN PROGRESS')
        ##categorise into feedback sentiment
        df['Feedback Category'] = df.apply(lambda row: feedback_categorisation(row['Feedback'], row['Subcategory']), axis=1)
        publish_message('Completed Feedback Categorisation', "IN PROGRESS")
        print("Completed: Feedback")
        
        print('Completed: Feedback Categorisation')

        ## categorise sentiment and score
        publish_message('Sentiment Analysis in progress', 'IN PROGRESS')
        sentiment_results = df['Feedback'].apply(classify_sentiment)
        df['Sentiment Score'], df['Sentiment'] = zip(*sentiment_results)
        publish_message('Completed Sentiment Analysis', "IN PROGRESS")
        print("Completed: Sentiment")

        return df
    
    except Exception as e:
        print(f"An error occurred: {e}")
        publish_message(f"Error - Operation could not be completed: {e}", 'ERROR')

