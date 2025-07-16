import json
import requests
import sqlite3
import time

# Database setup
conn = sqlite3.connect('premier_league.db')
cursor = conn.cursor()

def insert_fixture_statistics(json_data):
    fixture_id = json_data['parameters']['fixture']
    fixture_data = json.dumps(json_data)  # Save the entire JSON data as a string

    # Iterate through the teams and their statistics
    for team_stats in json_data['response']:
        team_id = team_stats['team']['id']
        team_name = team_stats['team']['name']
        team_logo = team_stats['team']['logo']

        # Default values for the statistics
        stats = {
            "shots_on_goal": None,
            "shots_off_goal": None,
            "total_shots": None,
            "blocked_shots": None,
            "shots_inside_box": None,
            "shots_outside_box": None,
            "fouls": None,
            "corner_kicks": None,
            "offsides": None,
            "ball_possession": None,
            "yellow_cards": None,
            "red_cards": None,
            "goalkeeper_saves": None,
            "total_passes": None,
            "passes_accurate": None,
            "passes_percentage": None
        }
        
        for stat in team_stats['statistics']:
            stat_type = stat['type']
            stat_value = stat['value']
            
            # Map the statistic type to the column name
            if stat_type == "Shots on Goal":
                stats["shots_on_goal"] = stat_value
            elif stat_type == "Shots off Goal":
                stats["shots_off_goal"] = stat_value
            elif stat_type == "Total Shots":
                stats["total_shots"] = stat_value
            elif stat_type == "Blocked Shots":
                stats["blocked_shots"] = stat_value
            elif stat_type == "Shots insidebox":
                stats["shots_inside_box"] = stat_value
            elif stat_type == "Shots outsidebox":
                stats["shots_outside_box"] = stat_value
            elif stat_type == "Fouls":
                stats["fouls"] = stat_value
            elif stat_type == "Corner Kicks":
                stats["corner_kicks"] = stat_value
            elif stat_type == "Offsides":
                stats["offsides"] = stat_value
            elif stat_type == "Ball Possession":
                stats["ball_possession"] = stat_value
            elif stat_type == "Yellow Cards":
                stats["yellow_cards"] = stat_value
            elif stat_type == "Red Cards":
                stats["red_cards"] = stat_value
            elif stat_type == "Goalkeeper Saves":
                stats["goalkeeper_saves"] = stat_value
            elif stat_type == "Total passes":
                stats["total_passes"] = stat_value
            elif stat_type == "Passes accurate":
                stats["passes_accurate"] = stat_value
            elif stat_type == "Passes %":
                stats["passes_percentage"] = stat_value

        # Insert the statistics into the database
        cursor.execute('''
        INSERT INTO fixture_statistics (
            fixture_id, team_id, team_name, team_logo, shots_on_goal, shots_off_goal, total_shots,
            blocked_shots, shots_inside_box, shots_outside_box, fouls, corner_kicks,
            offsides, ball_possession, yellow_cards, red_cards, goalkeeper_saves,
            total_passes, passes_accurate, passes_percentage
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            fixture_id, team_id, team_name, team_logo,
            stats["shots_on_goal"], stats["shots_off_goal"], stats["total_shots"],
            stats["blocked_shots"], stats["shots_inside_box"], stats["shots_outside_box"],
            stats["fouls"], stats["corner_kicks"], stats["offsides"],
            stats["ball_possession"], stats["yellow_cards"], stats["red_cards"],
            stats["goalkeeper_saves"], stats["total_passes"], stats["passes_accurate"],
            stats["passes_percentage"]
        ))

    conn.commit()

def extract_fixture_ids_from_file(file_path):
    # Initialize an empty list to store fixture IDs
    fixture_ids = []
    
    # Open and read the JSON file
    with open(file_path, 'r') as file:
        # Load the JSON data into a Python dictionary
        data = json.load(file)
        
        # Check if the response key exists and is a list
        if "response" in data and isinstance(data["response"], list):
            # Iterate through each item in the response list
            for item in data["response"]:
                # Extract the fixture ID and append it to the list
                if "fixture" in item and "id" in item["fixture"]:
                    fixture_ids.append(item["fixture"]["id"])

    return fixture_ids

def fetch_api_data(url, params, headers):
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()

def fetch_and_insert_matches(fixture_id):
    try:
        url = 'https://v3.football.api-sports.io/fixtures/statistics'
        query_params = {
            'fixture': fixture_id
        }
        headers = {
            'x-apisports-key': '976171bed1265a44a340b40680b71219'
        }
        
        json_data = fetch_api_data(url, query_params, headers)
        print(json_data)
        insert_fixture_statistics(json_data)
        return "Matches fetched and inserted successfully", 200
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"An error occurred: {e}", 500

def process_first_n_ids(ids, n=93, rate_limit=10):
    # Slice the list to get only the first n IDs
    first_n_ids = ids[:n]
    
    # Calculate the delay between requests
    delay = 60 / rate_limit
    
    for index, fixture_id in enumerate(first_n_ids):
        print(f"Processing fixture ID: {fixture_id}")
        fetch_and_insert_matches(fixture_id)
        
        # Sleep to respect the rate limit, except for the last request
        if index < len(first_n_ids) - 1:
            time.sleep(delay)

# file_path = '2023.json'
# fixture_ids = extract_fixture_ids_from_file(file_path)
# process_first_n_ids(fixture_ids)
with open("game1.json", 'r') as file:
    # Load the JSON data into a Python dictionary
    data = json.load(file)
    insert_fixture_statistics(data)


with open("game2.json", 'r') as file:
    # Load the JSON data into a Python dictionary
    data = json.load(file)
    insert_fixture_statistics(data)


