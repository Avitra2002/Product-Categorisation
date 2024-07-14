#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# pip install --upgrade google-cloud-aiplatform
# gcloud auth application-default login


# In[12]:


import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models
import pandas as pd

# Function to classify feedback text
# def classify_feedback(text):
#     model = GenerativeModel(
#         "projects/903333611831/locations/asia-southeast1/endpoints/6000136107843387392",
#         system_instruction=textsi_1
#     )
#     chat = model.start_chat(response_validation=False)
#     response = chat.send_message(
#         text,
#         generation_config=generation_config,
#         safety_settings=safety_settings
#     )
#     return response.text

# # Initialize Vertex AI
# vertexai.init(project="903333611831", location="asia-southeast1")

# # Configuration settings
# generation_config = {
#     "max_output_tokens": 2048,
#     "temperature": 1,
#     "top_p": 1,
# }

# # generation_config = {
# #     "max_output_tokens": 2048,
# #     "temperature": 0.6,
# #     "top_p": 1,
# # }

# safety_settings = {
#     generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
#     generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
#     generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
#     generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
# }

# textsi_1 = """You are a system that helps to categorize customer feedback as input into product categories for a banking company. 

# Classify the given text into one of the following categories: Debit Cards, Credit Cards, Personal Loan, Cashline, Education Loan (Tuition Fee Loan), Renovation Loan, Mortgage Loan, Car/Auto Loan, DigiBank App, Internet Banking, Paylah!, Vickers, Unit-Trust, Non-Unit Trust / Equities, digiPortfolio, Treasures Relationship Manager (RM), SSB, VTM, Phone Banking, Coin Deposit Machine, General Insurance, Life Insurance, Payments, DBS Deposit Account, Paynow, Cheque, GIRO, digiVault", DBS Hotline, DBS Branches/Staff, Overseas Transfer, Contact Center, Others, DBS Wealth Planning Manager. 

# <INSTRUCTIONS> 
# 1. If the text consists of a single word or is a general comment without detailed information about products (e.g., 'Well Done', 'good', 'nil', 'great', 'No Comment', 'Na', '-', '..'), classify it as "Others". 
# 2. If the text mentions talking to someone for help or waiting for a response, classify it as "Contact Center". 
# 3. If the text mentions 'account','interest rates', 'account opening', 'withdrawal', or 'deposit', classify it as "DBS Deposit Account". Provide only the category name as your answer. 
# 4. If the text mentions 'automated machines' or 'ATM', classify it as 'SSB' which is the full form for 'Self-Service Banking'
# 5. If the text mentions 'digital banking' or 'app', classify it as 'DigiBank App'
# 6. If the text mentions 'trading', classify it as "Vickers"

# Provide only the category name as your answer with no quotations.
# </INSTRUCTIONS> 

# <EXAMPLES> 
# <Input>Personally banking interest rates are not as attractive as other banks in Singapore.</Input> 
# <Output>"DBS Deposit Account"</Output> 
# <Reason>It talks about banking and its interest rates which are associated with account-related services.</Reason> 

# <Input>nil</Input> 
# <Output>"Others"</Output> 
# <Reason>It is a general comment without detailed information about products.</Reason> 

# <Input>Need help with my account</Input> 
# <Output>"Contact Center"</Output> 
# <Reason>It mentions needing help, indicating interaction with customer support.</Reason> 

# <Input>The app is very poor and dated, even the pin entry keyboard is non standard and buggy. You should really be 100% native like the main banking app. I want a super simple view on how my stocks are performing % and $ based on the original purchase price. I find it really amazing that the only way to make such a fundamental view is with a custom made custom portfolio.</Input> 
# <Output>"Non-Unit Trust / Equities"</Output> 
# <Reason>It discusses the performance and management of stocks, which falls under non-unit trust investments.</Reason> 
# </EXAMPLES>"""

# # Read the CSV file
# df = pd.read_csv('/Users/phonavitra/Desktop/term 5/Service Studio/Test/Model Test set.csv')

# # Classify each feedback and store the result in 'Subcategory' column
# df['Subcategory'] = df['Feedback'].apply(classify_feedback)

# # Write the updated DataFrame back to the CSV file
# df.to_csv('feedback_with_subcategories.csv', index=False)

# print("Classification complete. Results saved to 'feedback_with_subcategories.csv'.")


# # In[13]:


# df.to_csv('/Users/phonavitra/Desktop/term 5/Service Studio/Test/Model Test Subcat.csv', index=False)


# # In[ ]:


#line by line
def classify_subcategory(text):
    textsi_1 = """You are a system that helps to categorize customer feedback as input into product categories for a banking company. 

Classify the given text into one of the following categories: Debit Cards, Credit Cards, Personal Loan, Cashline, Education Loan (Tuition Fee Loan), Renovation Loan, Mortgage Loan, Car/Auto Loan, DigiBank App, Internet Banking, Paylah!, Vickers, Unit-Trust, Non-Unit Trust / Equities, digiPortfolio, Treasures Relationship Manager (RM), SSB, VTM, Phone Banking, Coin Deposit Machine, General Insurance, Life Insurance, Payments, DBS Deposit Account, Paynow, Cheque, GIRO, digiVault", DBS Hotline, DBS Branches/Staff, Overseas Transfer, Contact Center, Others, DBS Wealth Planning Manager. 

<INSTRUCTIONS> 
1. If the text consists of a single word or is a general comment without detailed information about products (e.g., 'Well Done', 'good', 'nil', 'great', 'No Comment', 'Na', '-', '..'), classify it as "Others". 
2. If the text mentions talking to someone for help or waiting for a response, classify it as "Contact Center". 
3. If the text mentions 'account','interest rates', 'account opening', 'withdrawal', or 'deposit', classify it as "DBS Deposit Account". Provide only the category name as your answer. 
4. If the text mentions 'automated machines' or 'ATM', classify it as 'SSB' which is the full form for 'Self-Service Banking'
5. If the text mentions 'digital banking' or 'app', classify it as 'DigiBank App'
6. If the text mentions 'trading', classify it as "Vickers"

Provide only the category name as your answer with no quotations.
</INSTRUCTIONS> 

<EXAMPLES> 
<Input>Personally banking interest rates are not as attractive as other banks in Singapore.</Input> 
<Output>"DBS Deposit Account"</Output> 
<Reason>It talks about banking and its interest rates which are associated with account-related services.</Reason> 

<Input>nil</Input> 
<Output>"Others"</Output> 
<Reason>It is a general comment without detailed information about products.</Reason> 

<Input>Need help with my account</Input> 
<Output>"Contact Center"</Output> 
<Reason>It mentions needing help, indicating interaction with customer support.</Reason> 

<Input>The app is very poor and dated, even the pin entry keyboard is non standard and buggy. You should really be 100% native like the main banking app. I want a super simple view on how my stocks are performing % and $ based on the original purchase price. I find it really amazing that the only way to make such a fundamental view is with a custom made custom portfolio.</Input> 
<Output>"Non-Unit Trust / Equities"</Output> 
<Reason>It discusses the performance and management of stocks, which falls under non-unit trust investments.</Reason> 
</EXAMPLES>""" 

    generation_config = {
        "max_output_tokens": 2048,
        "temperature": 1,
        "top_p": 1,
    }
    safety_settings = {
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    }

    model = GenerativeModel(
        "projects/903333611831/locations/asia-southeast1/endpoints/6000136107843387392",
        system_instruction=textsi_1
    )
    chat = model.start_chat(response_validation=False)
    response = chat.send_message(
        text,
        generation_config=generation_config,
        safety_settings=safety_settings
    )
    return response.text

