import google.cloud.aiplatform as vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
import pandas as pd
from collections import defaultdict
import json
import re
import functions_framework
from Actionables_Cloud_Function.auth import access_secret_version, execute_postgres_query, init_vertex_ai, fetch_data

# Initialize Vertex AI
project_id = "jbaaam"
init_vertex_ai()
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
    feedback_categories = defaultdict(list)
    
    for _, row in df.iterrows():
        product_feedback[row['Subcategory']].append(row['Feedback'])
        feedback_categories[row['Subcategory']].append(row['Feedbackcategory'])

    summarized_actions = []

    for product in product_feedback:
        feedbacks = product_feedback[product]
        categories = feedback_categories[product]

        combined_feedback = " | ".join(feedbacks)
        combined_feedback_category = " | ".join(categories)

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
        2. Mobile Banking App: "Prioritise app stability and user interface improvements based on customer feedback"
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
            'feedback_data': feedbacks,  # Store as list
            'status': 'New',
            'feedback_category': categories  # Store as list
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
    source = request.args.get('source')
    to_date = request.args.get('to_date')
    from_date = request.args.get('from_date')
    product = request.args.get('product')

    project_id = '903333611831'
    
    db_user_secret_id = 'DB_USER'
    db_password_secret_id = 'DB_PASS'
    
    # Retrieve secrets
    db_user = access_secret_version(db_user_secret_id, project_id)
    db_password = access_secret_version(db_password_secret_id, project_id)
    db_host= '/cloudsql/jbaaam:asia-southeast1:feedback'
    db_name='feedback_db'

    df= fetch_data(db_user, db_password, db_name, db_host,source, from_date, to_date, product)

    action_items_json = generate_actionable_items(df)
    action_items = json.loads(action_items_json)

    # Insert the actionable items into the database
    data_to_insert = [
        (
            item['subproduct'], 
            item['actionable_category'], 
            item['action'], 
            item['feedback_count'], 
            item['feedback_data'],  # json.dumps(item['feedback_data']) if the schema is json
            item['status'], 
            item['feedback_cat']
        ) for item in action_items
    ]
    
    ##TODO: configure actionables table in the db
    """actioanbles table
        CREATE TABLE actionables (
            id SERIAL PRIMARY KEY,
            subproduct TEXT,
            actionable_category TEXT,
            action TEXT,
            feedback_count INTEGER,
            feedback_data TEXT[], -- Storing list of text / if json then JSON
            status TEXT,
            feedback_category TEXT
    );"""

    insert_query = """
    INSERT INTO actionables (subproduct, actionable_category, action, feedback_count, feedback_data, status, feedback_category)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    execute_postgres_query(db_user, db_password, db_name, db_host, insert_query, data_to_insert)

    return json.dumps({"message": "Actionable items processed and stored successfully"}, indent=4), 200

