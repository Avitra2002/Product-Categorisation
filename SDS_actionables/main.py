import google.cloud.aiplatform as vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
import pandas as pd
from collections import defaultdict
import json
import re
import functions_framework

# Initialize Vertex AI
project_id = "jbaaam"
vertexai.init(project=project_id, location="us-central1")
model = GenerativeModel(model_name="gemini-1.5-flash-001")
generation_config = GenerationConfig(
    temperature=0.3,
    top_p=0.9,
    top_k=2,
    candidate_count=1,
    max_output_tokens=900,
)

def generate_actionable_items(df):
    product_feedback = defaultdict(list)
    for _, row in df.iterrows():
        product_feedback[row['Subcategory']].append(row['Feedback'])

    summarized_actions = []

    for product, feedbacks in product_feedback.items():
        combined_feedback = " | ".join(feedbacks)

        prompt = f"""
        Product: {product}
        Combined Feedback: {combined_feedback}

        Based on the combined feedback for the product "{product}", please generate one general actionable item that addresses the main themes or issues across all the feedback for this product.

        Format the response as follows:
        Category: [To Fix/To Promote/Keep in mind/To Amplify]
        Action: [Summarized general action]

        Ensure that the category is classified according to this:
        1. To Fix: regarding issues that require maintenance or repair, where services are not working
        2. To Promote: regarding feedback that talks about certain promotions that could be done or undermarketed stuff.
        3. Keep in mind: regarding feedback that compliments the service, and any form of suggestions
        4. To Amplify: regarding feedback that is neutral, but could have room for improvements.
        
        Ensure that the action is:
        1. Always provided
        2. As general as possible while still being relevant to the specific product. It should be very general.
        3. Addresses the most common or significant issues/themes in the feedback
        4. Focused on improving the overall product or customer experience

        Examples of generalized actions for various products:
        1. Savings Account: "Enhance interest rates and account features to improve customer satisfaction"
        2. Mobile Banking App: "Prioritize app stability and user interface improvements based on customer feedback"
        3. Credit Cards: "Revamp reward program and address common billing concerns"
        4. Customer Service: "Implement comprehensive training program to address recurring customer issues"
        5. Loans: "Streamline application process and improve communication throughout the loan lifecycle"

        
        Ensure response is:
        1. Always includes all specified fields
        2. Is formatted clearly and consistently according to the provided format, DO NOT GIVE ANY HEADERS
        Remember to tailor the action to the specific product and the themes present in the combined feedback.
        REMEMBER TO COMPLETE ALL GENERATED RESPONSES FOR ALL PRODUCTS 
        """

        response = model.generate_content(prompt, generation_config=generation_config)
        response_text = response.text.strip()
        response_text_cleaned = re.sub(r'^##.*?\n', '', response_text, flags=re.DOTALL).strip()

        actionable_category = 'Not specified'
        action = 'Not specified'

        lines = response_text_cleaned.split('\n')
        current_item = {
            'subproduct': product,
            'actionable_category': actionable_category,
            'action': action,
            'feedback_count': len(feedbacks),
            'feedback_data': feedbacks
        }
        for line in lines:
            line = line.strip()
            if line.startswith('Category:'):
                current_item['actionable_category'] = line.split(':')[1].strip()
            elif line.startswith('Action:'):
                current_item['action'] = line.split(':')[1].strip()

        if 'actionable_category' in current_item and 'action' in current_item:
            summarized_actions.append(current_item)
        else:
            print(f"Warning: Incomplete response for product '{product}'. Response text: {response_text}")

    return json.dumps(summarized_actions, indent=4)

@functions_framework.http
def generate_actions(request):
    request_json = request.get_json()
    feedback_data = request_json['feedback_data']
    
    
    df = pd.DataFrame(feedback_data)
    output = generate_actionable_items(df)
    
    return output