import requests
import json
import time
from supabase import create_client, Client

# Initialize Supabase client
url = 'https://nyflkmktapyxlfehsfvq.supabase.co'  # Replace with your Supabase URL
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im55ZmxrbWt0YXB5eGxmZWhzZnZxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjQyNDk1NDAsImV4cCI6MjAzOTgyNTU0MH0.7zPmk_3Eg_0Z2QB358mCNBLhAOnSLgub5XtxebSP5WM'  # Replace with your Supabase API key
supabase: Client = create_client(url, key)

def insert_fixture_statistics(json_data, fixture_data):
    fixture_id = json_data['parameters']['fixture']
    #print(json_data)
    
    for predictions in json_data['response']:
        # Check if the fixture already exists
        existing_fixture = supabase.table('prediction').select('*').eq('fixture_id', fixture_id).execute()
        
        if existing_fixture.data:
            print(f"Fixture with ID {fixture_id} already exists. Skipping insertion.")
            continue  # Skip to the next prediction if it already exists

        # Default values for the statistics
        stats = {
            "fixture_id": None,
            "winner_id": None,
            "winner_name": None,
            "advice": None,
            "under_over": None,
            "home_goals": None,
            "away_goals": None,
            "percent_home": None,
            "percent_draw": None,
            "percent_away": None,
            "league_name": None,
            "league_id": None,
            "league_logo": None,
            "home_team_logo": None,
            "away_team_logo": None,
            "home_team_name": None,
            "away_team_name": None,
            "home_team_id": None,
            "away_team_id": None,
            "h2h_home_percent": None,
            "h2h_away_percent": None,
            "goals_home_percent": None,
            "goals_away_percent": None,
            "total_home_percent": None,
            "total_away_percent": None,
            #"date": None,
        }
        
        # Extract prediction data
        prediction = predictions['predictions']
        league = predictions['league']
        teams = predictions['teams']
        if prediction['advice'] == 'No predictions available':
            continue

        stats["fixture_id"] = fixture_id
        stats["winner_id"] = prediction['winner']['id']
        stats["winner_name"] = prediction['winner']['name']
        stats["advice"] = prediction['advice']
        stats["under_over"] = prediction['under_over']
        stats["home_goals"] = prediction['goals']['home']
        stats["away_goals"] = prediction['goals']['away']
        stats["percent_home"] = prediction['percent']['home']
        stats["percent_draw"] = prediction['percent']['draw']
        stats["percent_away"] = prediction['percent']['away']
        stats["league_name"] = league['name']
        stats["league_id"] = league['id']
        stats["league_logo"] = league['logo']
        stats["home_team_logo"] = teams['home']['logo']
        stats["away_team_logo"] = teams['away']['logo']
        stats["home_team_name"] = teams['home']['name']
        stats["away_team_name"] = teams['away']['name']
        stats["home_team_id"] = teams['home']['id']
        stats["away_team_id"] = teams['away']['id']
        #stats["date"] = fixture_data[fixture_id]

        # Extract comparison data
        comparison = predictions['comparison']
        stats["h2h_home_percent"] = comparison['h2h']['home']
        stats["h2h_away_percent"] = comparison['h2h']['away']
        stats["goals_home_percent"] = comparison['goals']['home']
        stats["goals_away_percent"] = comparison['goals']['away']
        stats["total_home_percent"] = comparison['total']['home']
        stats["total_away_percent"] = comparison['total']['away']

        # Insert statistics into the prediction table
        response = supabase.table('prediction').insert(stats).execute()


        # Insert h2h data
        for h2h_match in predictions['h2h']:
            h2h_fixture = h2h_match['fixture']
            h2h_teams = h2h_match['teams']
            h2h_goals = h2h_match['goals']

            h2h_stats = {
                "fixture_id": fixture_id,
                "h2h_fixture_id": h2h_fixture['id'],
                "h2h_date": h2h_fixture['date'],
                "h2h_home_team_id": h2h_teams['home']['id'],
                "h2h_home_team_name": h2h_teams['home']['name'],
                "h2h_away_team_id": h2h_teams['away']['id'],
                "h2h_away_team_name": h2h_teams['away']['name'],
                "h2h_home_goals": h2h_goals['home'],
                "h2h_away_goals": h2h_goals['away'],
                "h2h_winner": h2h_teams['home']['winner'] if h2h_teams['home']['winner'] else 
                (h2h_teams['away']['winner'] if h2h_teams['away']['winner'] else 'draw')
            }

            h2h_response = supabase.table('h2h').insert(h2h_stats).execute()

def fetch_api_data(url, params, headers):
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    print(f"API request successful: {url}")
    time.sleep(6)
    return response.json()

def process_fixtures(json_data):
    fixture_data = {}  # Changed to store ID as key and date as value
    for fixture in json_data['response']:
        fixture_data[fixture['fixture']['id']] = fixture['fixture']['date']  # ID as key, date as value
    return fixture_data  # Return the dictionary

def fetch_predictions(fixture_data):
    total_fixtures = len(fixture_data)
    for i, (fixture_id, fixture_date) in enumerate(fixture_data.items(), 1):  # Loop through keys and values
        try:
            print(f"Fetching prediction for fixture {i}/{total_fixtures} (ID: {fixture_id})")
            url = 'https://v3.football.api-sports.io/predictions'
            query_params = {
                'fixture': fixture_id
            }
            headers = {
                'x-apisports-key': '976171bed1265a44a340b40680b71219'
            }

            json_data = fetch_api_data(url, query_params, headers)
            insert_fixture_statistics(json_data, fixture_data)
            print(f"Prediction data inserted for fixture {fixture_id}")
        
        except Exception as e:
            print(f"Error processing fixture {fixture_id}: {str(e)}")
            continue  # Move to the next fixture
        
        if i % 10 == 0:
            print(f"Reached {i} requests, pausing for 60 seconds...")
            time.sleep(60)

def fetch_fixture_ids():
    #league_ids = [3, 848] #conference + europa
    league_ids = [39, 135, 78, 140, 61] #MAIN TOP 5 LEAGUES
    #league_ids = [5] #NATIONS LEAGUE
    #league_ids = [2] #CL
    #league_ids = [78, 135]
    #league_ids = [46, 37, 140] #EFL CUP + COPPA ITALIA + LA LIGA

    fixture_data = {}  
    for i, league_id in enumerate(league_ids, 1):
        try:
            print(f"Fetching fixtures for league {i}/{len(league_ids)} (ID: {league_id})")
            url = 'https://v3.football.api-sports.io/fixtures'
            query_params = {
                'league': league_id,
                'season': 2024,
                #'status': '1H'
                'next': 10
            }
            headers = {
                'x-apisports-key': '976171bed1265a44a340b40680b71219'
            }
        
            json_data = fetch_api_data(url, query_params, headers)
            for fixture in json_data['response']:
                fixture_data[fixture['fixture']['id']] = fixture['fixture']['date']  
            print(f"Added {len(json_data['response'])} fixtures from league {league_id}")
        
        except Exception as e:
            print(f"Error processing league {league_id}: {str(e)}")
            continue  
        
        if i % 10 == 0:
            print(f"Reached {i} league requests, pausing for 60 seconds...")
            time.sleep(60)

    print(f"Total fixtures fetched: {len(fixture_data)}")
    return fixture_data  # Return the dictionary

if __name__ == "__main__":
    try:
        print("Starting to fetch fixture IDs...")
        fixture_data = fetch_fixture_ids()  
        print("Finished fetching fixture IDs. Starting to fetch predictions...")
        fetch_predictions(fixture_data)  
        print("Script execution completed.")
    except Exception as e:
        print(f"An error occurred during script execution: {str(e)}")