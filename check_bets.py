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
            winner = "home"
        else:
            winner = "away"
        
        check_fixture(fixture_id, winner, double_chance, under_over)
        

def check_fixture(fixture_id, pred_winner, double_chance, under_over):
    print(f"Fetching odds for fixture (ID: {fixture_id})")
    url = 'https://v3.football.api-sports.io/fixtures'
    query_params = {
        'id': fixture_id
    }
    headers = {
        'x-apisports-key': '976171bed1265a44a340b40680b71219'
    }

    json_data = fetch_api_data(url, query_params, headers)

    game_status = json_data["response"][0]["fixture"]["status"]["short"]

    print(game_status)

    if "FT" in game_status:
        correct = False 

        home_goals = json_data["response"][0]["goals"]["home"]
        away_goals = json_data["response"][0]["goals"]["away"]
        draw = False

        if home_goals > away_goals:
            actual_winner = "home"
        elif away_goals > home_goals:
            actual_winner = "away"
        else: 
            actual_winner = "draw"

        if double_chance:
            if "draw" in actual_winner or pred_winner == actual_winner:
                correct = True 

        if under_over is not None:
            under_over = str(under_over)
            if "-" in under_over:
                under_over = under_over.replace('-', '')
                if float(under_over) < float(home_goals) + float(away_goals):
                    correct = False
            else:
                if float(under_over) > float(home_goals) + float(away_goals):
                    correct = False

        if correct:
            response = (
            supabase.table("prediction")
            .update({"finished": "true", "correct": "true"})
            .eq("fixture_id", fixture_id)
            .execute()
        )
        else:
            response = (
                supabase.table("prediction")
                .update({"finished": "true", "correct": "false"})
                .eq("fixture_id", fixture_id)
                .execute()
            )


if __name__ == "__main__":
    try:
        print("Checking if predictions were correct and calculating ROI...")
        fixture_data = fetch_predictions()  
        print("Finished checking...")
        print("Script execution completed.")
    except Exception as e:
        print(f"An error occurred during script execution: {str(e)}")