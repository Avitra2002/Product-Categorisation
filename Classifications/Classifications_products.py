#!/usr/bin/env python
# coding: utf-8

# In[ ]:


##Classification Pipleline for defined products
from Gemini_Models.Subcategory_Classification_Gemini_model import classify_subcategory

def classification_defined_products(df):

    ##categorise into subproducts
    df['Subcategory'] = df['Feedback'].apply(classify_subcategory)

    ##categorise into feedback sentiment


    ## categorise sentiment and score

    return df

