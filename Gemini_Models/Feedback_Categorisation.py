import base64
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
import vertexai.preview.generative_models as generative_models
import pandas as pd
import json

def feedback_categorisation(text,product):

  # Initialize Vertex AI with your project ID and location
#   project_id = "jbaaam"

#   vertexai.init(project=project_id, location="us-central1")



  textsi_1 = """
  You are a system that helps to categorise the customer feedbacks into relevant feedback categories associated with the products.

  <INSTRUCTIONS>
  1. First, recognize the product that the feedback is talking about. The feedback will be in the form [product]:feedback.
  2. Using the product mentioned in the feedback, identify the specific issue being discussed and match it to one of the feedback categories listed below and it must only be from the categories listed below. Ensure the feedback category is relevant to the product.

  Here are the products mapped to their associated Feedback Categories: 
  - Debit Card: ['Statement', 'Card Delivery', 'Card Application', 'Card Activation', 'Cashback', 'Rewards', 'Card Replacement', 'Card Renewal', 'Charges/Fees & Interest', 'Card Limit', 'Scam/Fraud', 'Staff related', 'Technical Issue/System', 'T&C', 'Card Blocked']
  - Credit Card: ['Statement', 'Card Delivery', 'Card Application', 'Card Activation', 'Cashback', 'Rewards', 'Card Replacement', 'Card Renewal', 'Charges/Fees & Interest', 'Card Limit', 'Scam/Fraud', 'Staff related', 'Credit Application', 'Credit Limit', 'Supplementary Credit Card', 'Fee Waiver']
  - Personal Loan: ['Loan Settlement', 'Loan Application', 'Process Related', 'Charges/Fees & Interest', 'Loan Disbursement', 'Technical Issue/System', 'Credit Loan', 'Staff Related', 'GIRO auto deduction']
  - Cashline: ['Loan Settlement', 'Loan Application', 'Process Related', 'Charges/Fees & Interest', 'Loan Disbursement', 'Technical Issue/System', 'Credit Loan', 'Staff Related', 'GIRO auto deduction']
  - Education Loan (Tuition Fee Loan): ['Loan Settlement', 'Loan Application', 'Process Related', 'Charges/Fees & Interest', 'Loan Disbursement', 'Technical Issue/System', 'Credit Loan', 'Staff Related', 'GIRO auto deduction']
  - Renovation Loan: ['Loan Settlement', 'Loan Application', 'Process Related', 'Charges/Fees & Interest', 'Loan Disbursement', 'Technical Issue/System', 'Staff Related', 'GIRO auto deduction']
  - Mortgage/Home Loan: ['Loan Settlement', 'Loan Application', 'Process Related', 'Charges/Fees & Interest', 'Loan Disbursement', 'Technical Issue/System',  'Staff Related', 'GIRO auto deduction']
  - Car Loan: ['Loan Settlement', 'Loan Application', 'Process Related', 'Charges/Fees & Interest', 'Loan Disbursement', 'Technical Issue/System', 'Staff Related', 'GIRO auto deduction']
  - General Insurance: ['Rate/Policy', 'Process Related', 'Application', 'Staff Related', 'Claim Related']
  - Life Insurance: ['Rate/Policy', 'Process Related', 'Application', 'Staff Related', 'Claim Related']
  - Payments: ['Scam/Fraud', 'Technical Issue/System']
  - DBS Deposit Account: ['Account Opening', 'Account Closure', 'Account Issues (deposit/withdrawal)', 'Charges/Fees & Interest', 'Technical Issue/System', 'Rewards', 'Payments', 'Features', 'UI/UX']
  - PayNow: ['Account Opening', 'Account Closure', 'Account Issues (deposit/withdrawal)', 'Charges/Fees & Interest', 'Technical Issue/System', 'Rewards', 'Payments', 'Features', 'UI/UX', 'Process', 'Transaction Related']
  - Cheque: ['Account Opening', 'Account Closure', 'Account Issues (deposit/withdrawal)', 'Charges/Fees & Interest', 'Technical Issue/System', 'Rewards', 'Payments']
  - GIRO: ['Account Opening', 'Account Closure', 'Account Issues (deposit/withdrawal)', 'Technical Issue', 'Rewards', 'Payments','Process Related]
  - Smart Buddy: ['Charges/Fees & Interest', 'Card replacement', 'Marketing & Promotions']
  - digiVault: ['Account Opening', 'Account Closure', 'Account Issues (deposit/withdrawal)','Technical Issue', 'Rewards', 'Payments']
  - DBS Hotline: ['Staff Related', 'Fraud/Scam', 'Waiting time', 'IVR menu']
  - DBS Branches/Staff: ['Staff related', 'Fraud/Scam', 'Technical Issue', 'Process / Transaction Handling', 'Waiting time']
  - Websites: ['Content', 'Navigation', 'Clarity']
  - Overseas Transfer: ['Exchange Rates/Fee related', 'Scam/Fraud', 'Process', 'Rewards', 'Transaction Related', 'Features', 'Technical Issues/System','UI/UX', 'Application']
  - Digibank App: ['Log In', 'Log Out', 'Technical/System Issue', 'Process Related', 'Digital Token', 'OTP', 'Account Opening', 'Features','Bill statement','Transaction related' ,  'Charges/Fee & Interest', 'Advertisement', 'Others', 'Lag/Intermittent Logout']
  - Internet Banking(iBanking): ['Log In', 'Log Out', 'Technical/System Issue', 'Process Related', 'Digital Token', 'OTP', 'Account Opening', 'Features', 'Charges/Fee & Interest', 'Advertisement', 'Others', 'Transaction related' ,'Lag/Intermittent Logout']
  - Paylah!: ['Log In', 'Log Out', 'Technical/System Issue', 'Digital token', 'OTP','Features','Wallet Closure','Transaction Related','Marketing & promotions','Process related','UI/UX','CNY','Staff related','Account opening','Account closure','Account management', 'advertisement']
  - Vickers: ['Fee related', 'Technical/System Issue','Process related','Application', 'Digibot','Equity trading' ,'Statement','Rewards','Others','Features','OTP','UI/UX']
  - Unit Trust: ['Charges/Fees & Interest','Technical/System Issue','Process related','Application','Digibot','Equity trading','Statement','Rewards','Features','Saving/Investment Plans']
  - Non-Unit Trust/Equities: ['Charges/Fees & Interest', 'Technical/System Issue', 'Process related', 'Application', 'Digibot','Online Equity Trading','Statement','Rewards','Features','Saving/Investment Plans']
  - digiPortfolio: ['Charges/Fees & Interest',' Technical/System Issue', 'Process related', 'Application', 'Digibot', 'Equity Trading', 'Statement','Rewards','Features','Saving/Investment Plans']
  - Treasures Relationship Manager(RM): ['Charges/Fees & Interest', 'Process related', 'Staff related']
  - SSB: ['Passbook', 'Deposit/Withdrawal Issue', 'Technical/System Issue', 'Process related', 'Features','Deposit Discrepancy','Hardware','Card/Cash retain','Location','UI/UX','Service unavailability']
  - VTM(Video Teller Machine): ['Passbook','Technical/System Issue', 'Process related', 'Features', 'Staff related','UI/UX']
  - Phone Banking: ['UI/UX','Process related', 'Others', 'Waiting time',' Verification process', 'IVR','Features','Transaction related']
  - Coin Deposit Machine: ['Passbook',' Deposit/Withdrawal Issue', 'Technical/System Issue', 'Process related']]
  - DBS Treasures (General):['Charges/Fees & Interest', 'Technical/System Issue', 'Process related', 'Application', 'Digibot','Online Equity Trading','Statement','Rewards','Features','Saving/Investment Plans']
  - DBS Wealth Planning Manager:['Charges/Fees & Interest', 'Process related', 'Staff related']
  3. Be as specific to the feedback category as you can be. For example, if the feedback is talking about a UI/UX problem, do not categorize it under 'Technical Issue/System'; classify it as 'UI/UX'. If the feedback is about login issues, classify it under 'Log In' instead of 'Technical Issue/System'.
  4. The output is only the feedback category and the reasoning in a VALID JSON format.

  </INSTRUCTION>

  <EXAMPLE>
  <INPUT>
  "Digibank App: Unable to update my mail addresses because system doesn't allow me to key in numbers. So how am I suppose to key in house numbers or postcode??"
  </INPUT>
  <OUTPUT>
  {"feedback_category": "Technical/System Issue","Reasoning": "The feedback indicates a problem with the Digibank App's functionality, specifically a system error that prevents the user from entering numbers, which is a technical issue."}
  </OUTPUT>

  <INPUT>
  "PayLah!:so many ads blocking the screen."
  </INPUT>
  <OUTPUT>
  {"feedback_category":"advertisement", "Reasoning": "The feedback highlights an issue with the PayLah! app where ads are obstructing the user experience, which relates to advertisements."}
  </OUTPUT>

  <INPUT

  </EXAMPLE>
  """

  # Initialize the Gemini model
  model = GenerativeModel(model_name="gemini-1.0-pro-002", system_instruction=textsi_1)
  generation_config = GenerationConfig(
    temperature=0.3,  # Lower temperature for more deterministic output
    top_p=0.9,
    top_k=2,
    candidate_count=1,
    max_output_tokens=1024,  # Set a higher limit for more detailed responses
  )
  try:
        # Assuming the function call to the model and parameters stays the same:
        response = model.generate_content(f'{product}:{text}')
        json_result = response.text
        print(f"Raw model response: {json_result}")

        clean_json_string = json_result.strip('```json \n').strip()

        data = json.loads(clean_json_string)
        return data.get("feedback_category", "Unknown Category")
  
  except json.JSONDecodeError as e:
        print(f"JSON decode error for feedback: {text}, product: {product}, response: {json_result}")
        return "Unknown Category"
  except Exception as e:
        print(f"Unexpected error for feedback: {text}, product: {product}, error: {e}")
        return "Unknown Category"


