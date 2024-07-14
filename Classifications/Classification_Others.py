#!/usr/bin/env python
# coding: utf-8

# In[ ]:


##Classification for undefined products
from Gemini_Models.Subcategory_Classification_Gemini_model import classify_subcategory

##dictionary to map from subproducts to products

def classification_undefined_products(df):
    product_dict = {
        "Cards": ["Debit Card", "Credit Card"],
        "Unsecured Loans": ["Cashline", "Personal Loan", "Renovation Loan", "Education Loan"],
        "Secured Loans": ["Car Loan", "Mortgage/Home Loan"],
        "Digital Channels": ["DigiBank App", "Internet Banking(iBanking)", "Paylah!"],
        "Investments": ["digiPortfolio", "Non-Unit Trust/Equities", "Unit Trust", "Vickers"],
        "DBS Treasures": ["Treasures Relationship Manager(RM)", "DBS Wealth Planning Manager", "DBS Treasures (General)"],
        "Self-Service Banking": ["SSB", "VTM(Video Teller Machine)", "Phone Banking", "Coin Deposit Machine"],
        "Insurance": ["General Insurance", "Life Insurance"],
        "Deposits": ["DBS Deposit Account", "Payments", "PayNow", "Cheque", "GIRO", "digiVault"],
        "Contact Center": ["DBS Hotline", "DBS Branches/Staff"],
        "Webpages": ["Websites"],
        "Remittance": ["Overseas Transfer"],
        "Others": ["Others"]
    }

    ##classify into subproducts
    df['Subcategory'] = df['Feedback'].apply(classify_subcategory)

    ## link subproducts to products
    def match_product(subcategory):
        for product, subproducts in product_dict.items():
            if subcategory in subproducts:
                return product
        return 'Others'  # Return None if subcategory doesn't match any product
    
    df['Product'] = df['Subcategory'].apply(match_product)

    ####categorise into feedback sentiment


    ## categorise sentiment and score

    return df







