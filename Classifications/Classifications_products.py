#!/usr/bin/env python
# coding: utf-8

# In[ ]:


##Classification Pipleline for defined products
from Gemini_Models.Subcategory_Classification_Gemini_model import classify_subcategory
from Gemini_Models.Sentiment_Score_Category_model import classify_sentiment
import time
from Gemini_Models.Feedback_Categorisation import feedback_categorisation

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
    return sentiments

def classify_feedback_batch(feedbacks, products, batch_size=10, delay_per_batch=15):
    categories = []
    for i in range(0, len(feedbacks), batch_size):
        batch_feedbacks = feedbacks[i:i+batch_size]
        batch_products = products[i:i+batch_size]
        batch_categories = [feedback_categorisation(feedback, product) for feedback, product in zip(batch_feedbacks, batch_products)]
        categories.extend(batch_categories)
        if i + batch_size < len(feedbacks):  # To avoid sleeping after the last batch
            time.sleep(delay_per_batch)  # Wait before processing the next batch
    return categories

def classification_defined_products(df):

    ##categorise into subproducts
    df['Subcategory'] = classify_subcategory_batch(df['Feedback'].tolist())

    ##categorise into feedback sentiment
    df['Feedback Category'] = classify_feedback_batch(df['Feedback'].tolist(), df['Subcategory'].tolist())

    ## categorise sentiment and score
    sentiment_results = classify_sentiment_batch(df['Feedback'].tolist())
    df['Sentiment Score'], df['Sentiment'] = zip(*sentiment_results)

    return df

