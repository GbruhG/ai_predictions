import os
import requests
import time
from typing import Dict, Any, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def fetch_api_data(url, params, headers):
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    print(f"API request successful: {url}")
    time.sleep(6)
    return response.json()

def fetch_predictions():
    fixtures = supabase.table('prediction').select('*').execute()
    #print(fixtures.data)
    for x in fixtures.data:
        #print(x['fixture_id'])
        fixture_id = x['fixture_id']
        winner_name = x['winner_name']
        advice = x['advice']
        double_chance = False
        under_over = x['under_over']

        if "Double chance" in advice:
            #print("AAAAAAAAAAAAAAAAAA")
            double_chance = True

        if winner_name == x['home_team_name']:
            winner = "Home"
        else:
            winner = "Away"
        
        check_fixture(fixture_id, winner, double_chance, under_over)
        

def check_fixture(fixture_id, winner, double_chance, under_over):
    print(f"Fetching odds for fixture (ID: {fixture_id})")
    url = 'https://v3.football.api-sports.io/odds'
    query_params = {
        'fixture': fixture_id
    }
    headers = {
        'x-apisports-key': '976171bed1265a44a340b40680b71219'
    }

    json_data = fetch_api_data(url, query_params, headers)
    odds = 1.0

    if double_chance:
        for x in json_data['response'][0]['bookmakers'][0]['bets']:
            if x['id'] == 12:
                for y in x['values']:
                    if winner == "Home":
                        if "Home/Draw" in y['value']:
                            odds = float(odds) * float(y['odd'])
                    elif "Draw/Away" in y['value']:
                        odds = float(odds) * float(y['odd'])
    else:
        for x in json_data['response'][0]['bookmakers'][0]['bets']:
            if x['id'] == 1:
                for y in x['values']:
                    if winner in y['value']:
                        odds = float(odds) * float(y['odd'])

    if under_over is not None:
        under_over = str(under_over)
        if "-" in under_over:
            bet = "Under "
            under_over = under_over.replace('-', '')
        else:
            bet = "Over "
        bet = bet + str(under_over)

        for x in json_data['response'][0]['bookmakers'][0]['bets']:
            if x['id'] == 5:
                for y in x['values']:
                    if bet in y['value']:
                        odds = float(odds) * float(y['odd'])
                        
    print(f"Odds for the prediction {fixture_id} have been calculateD: {odds}")
    
    response = (
        supabase.table("prediction")
        .update({"odds": odds})
        .eq("fixture_id", fixture_id)
        .execute()
    )
    return odds

if __name__ == "__main__":
    try:
        print("Checking if predictions were correct and calculating ROI...")
        fixture_data = fetch_predictions()  
        print("Finished checking...")
        print("Script execution completed.")
    except Exception as e:
        print(f"An error occurred during script execution: {str(e)}")