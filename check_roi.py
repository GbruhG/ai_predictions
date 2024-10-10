import os
import time
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def roi_checker():
    # Fetch prediction data from the Supabase table
    fixtures = supabase.table('prediction').select('*').execute()
    
    if not fixtures.data:
        print("No fixtures found in the database.")
        return

    # Initialize counters
    correct_preds = 0
    incorrect_preds = 0
    total_profit = 0.0

    # Iterate over each fixture
    for fixture in fixtures.data:
        if fixture.get('finished') == 'true':
            if fixture.get('correct') == 'true':
                # If the prediction is correct, calculate the profit
                correct_preds += 1
                match_odds = float(fixture.get('odds', 1.0))
                total_profit += (match_odds - 1)  # profit is odds - 1
            else:
                # If incorrect, subtract the bet (loss of 1 unit)
                incorrect_preds += 1
                total_profit -= 1  # lose the unit bet

    # Total number of predictions
    total_predictions = correct_preds + incorrect_preds

    if total_predictions == 0:
        print("No finished predictions found.")
        return

    # Calculate ROI
    roi = (total_profit / total_predictions) * 100

    # Output results
    print(f"Total predictions: {total_predictions}")
    print(f"Correct predictions: {correct_preds}")
    print(f"Incorrect predictions: {incorrect_preds}")
    print(f"Total profit: {total_profit:.2f}")
    print(f"Current ROI: {roi:.2f}%")

if __name__ == "__main__":
    try:
        print("Checking if predictions were correct and calculating ROI...")
        roi_checker()  
        print("Finished checking...")
        print("Script execution completed.")
    except Exception as e:
        print(f"An error occurred during script execution: {str(e)}")
