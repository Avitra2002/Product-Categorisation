#!/usr/bin/env python
# coding: utf-8

# In[ ]:


##Classification Pipleline for defined products
from Gemini_Models.Subcategory_Classification_Gemini_model import classify_subcategory
from Gemini_Models.Sentiment_Score_Category_model import classify_sentiment
import time

def classify_subcategory_batch(texts, batch_size=20, delay_per_batch=12):
    subcategories = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_subcategories = [classify_subcategory(text) for text in batch]
        subcategories.extend(batch_subcategories)
        if i + batch_size < len(texts):  # To avoid sleeping after the last batch
            time.sleep(delay_per_batch)  # Wait before processing the next batch
    return subcategories

def classify_sentiment_batch(texts, batch_size=20, delay_per_batch=12):
    sentiments = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_sentiments = [classify_sentiment(text) for text in batch]
        sentiments.extend(batch_sentiments)
        if i + batch_size < len(texts):  
            time.sleep(delay_per_batch)

def classification_defined_products(df):

    ##categorise into subproducts
    df['Subcategory'] = classify_subcategory_batch(df['Feedback'].tolist())

    ##categorise into feedback sentiment


    ## categorise sentiment and score
    sentiment_results = classify_sentiment_batch(df['Feedback'].tolist())
    df['Sentiment Score'], df['Sentiment'] = zip(*sentiment_results)

    return df

