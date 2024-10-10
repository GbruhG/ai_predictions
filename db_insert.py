import sqlite3
import json

# Connect to SQLite database (or change to your specific database)
conn = sqlite3.connect('premier_league.db')
cursor = conn.cursor()



# # Query to retrieve the schema
# cursor.execute("SELECT * FROM fixtures;")
# tables = cursor.fetchall()

# # Print out the schema of each table
# for table in tables:
#     print(table[1])


def insert_fixtures(data):
    # Create table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fixtures (
        fixture_id INTEGER PRIMARY KEY,
        referee TEXT,
        timezone TEXT,
        date TEXT,
        timestamp INTEGER,
        first_period INTEGER,
        second_period INTEGER,
        venue_id INTEGER,
        venue_name TEXT,
        venue_city TEXT,
        status_long TEXT,
        status_short TEXT,
        status_elapsed INTEGER,
        league_id INTEGER,
        league_name TEXT,
        league_country TEXT,
        league_logo TEXT,
        league_flag TEXT,
        league_season INTEGER,
        league_round TEXT,
        home_team_id INTEGER,
        home_team_name TEXT,
        home_team_logo TEXT,
        away_team_id INTEGER,
        away_team_name TEXT,
        away_team_logo TEXT,
        home_team_winner BOOLEAN,
        away_team_winner BOOLEAN,
        goals_home INTEGER,
        goals_away INTEGER,
        halftime_home INTEGER,
        halftime_away INTEGER,
        fulltime_home INTEGER,
        fulltime_away INTEGER,
        extratime_home INTEGER,
        extratime_away INTEGER,
        penalty_home INTEGER,
        penalty_away INTEGER
    )
    ''')

    # Insert data into the table
    for fixture in data['response']:
        fixture_data = (
            fixture['fixture']['id'],
            fixture['fixture']['referee'],
            fixture['fixture']['timezone'],
            fixture['fixture']['date'],
            fixture['fixture']['timestamp'],
            fixture['fixture']['periods']['first'],
            fixture['fixture']['periods']['second'],
            fixture['fixture']['venue']['id'],
            fixture['fixture']['venue']['name'],
            fixture['fixture']['venue']['city'],
            fixture['fixture']['status']['long'],
            fixture['fixture']['status']['short'],
            fixture['fixture']['status']['elapsed'],
            fixture['league']['id'],
            fixture['league']['name'],
            fixture['league']['country'],
            fixture['league']['logo'],
            fixture['league']['flag'],
            fixture['league']['season'],
            fixture['league']['round'],
            fixture['teams']['home']['id'],
            fixture['teams']['home']['name'],
            fixture['teams']['home']['logo'],
            fixture['teams']['away']['id'],
            fixture['teams']['away']['name'],
            fixture['teams']['away']['logo'],
            fixture['teams']['home']['winner'],
            fixture['teams']['away']['winner'],
            fixture['goals']['home'],
            fixture['goals']['away'],
            fixture['score']['halftime']['home'],
            fixture['score']['halftime']['away'],
            fixture['score']['fulltime']['home'],
            fixture['score']['fulltime']['away'],
            fixture['score']['extratime']['home'],
            fixture['score']['extratime']['away'],
            fixture['score']['penalty']['home'],
            fixture['score']['penalty']['away']
        )
        print(fixture_data)

        cursor.execute('''
        INSERT INTO fixtures (
            fixture_id, referee, timezone, date, timestamp, first_period, second_period, 
            venue_id, venue_name, venue_city, status_long, status_short, status_elapsed,
            league_id, league_name, league_country, league_logo, league_flag, league_season, 
            league_round, home_team_id, home_team_name, home_team_logo, away_team_id, 
            away_team_name, away_team_logo, home_team_winner, away_team_winner, goals_home, 
            goals_away, halftime_home, halftime_away, fulltime_home, fulltime_away, 
            extratime_home, extratime_away, penalty_home, penalty_away
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', fixture_data)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
# Function to insert player statistics into the database
def insert_player_stats(data):

    
    response = data["response"][0]
    player = response["player"]
    statistics = response["statistics"][0]  # Only the first entry under statistics

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS player_stats (
        id INTEGER PRIMARY KEY,
        name TEXT,
        firstname TEXT,
        lastname TEXT,
        age INTEGER,
        birth_date TEXT,
        birth_place TEXT,
        birth_country TEXT,
        nationality TEXT,
        height TEXT,
        weight TEXT,
        injured BOOLEAN,
        photo TEXT,
        team_id INTEGER,
        team_name TEXT,
        team_logo TEXT,
        league_id INTEGER,
        league_name TEXT,
        league_country TEXT,
        league_logo TEXT,
        league_flag TEXT,
        season INTEGER,
        games_appearences INTEGER,
        games_lineups INTEGER,
        games_minutes INTEGER,
        games_number INTEGER,
        games_position TEXT,
        games_rating REAL,
        games_captain BOOLEAN,
        substitutes_in INTEGER,
        substitutes_out INTEGER,
        substitutes_bench INTEGER,
        shots_total INTEGER,
        shots_on INTEGER,
        goals_total INTEGER,
        goals_conceded INTEGER,
        goals_assists INTEGER,
        goals_saves INTEGER,
        passes_total INTEGER,
        passes_key INTEGER,
        passes_accuracy INTEGER,
        tackles_total INTEGER,
        tackles_blocks INTEGER,
        tackles_interceptions INTEGER,
        duels_total INTEGER,
        duels_won INTEGER,
        dribbles_attempts INTEGER,
        dribbles_success INTEGER,
        dribbles_past INTEGER,
        fouls_drawn INTEGER,
        fouls_committed INTEGER,
        cards_yellow INTEGER,
        cards_yellowred INTEGER,
        cards_red INTEGER,
        penalty_won INTEGER,
        penalty_commited INTEGER,
        penalty_scored INTEGER,
        penalty_missed INTEGER,
        penalty_saved INTEGER
    )
    ''')
    
    player_stats = {
        "id": player["id"],
        "name": player["name"],
        "firstname": player["firstname"],
        "lastname": player["lastname"],
        "age": player["age"],
        "birth_date": player["birth"]["date"],
        "birth_place": player["birth"]["place"],
        "birth_country": player["birth"]["country"],
        "nationality": player["nationality"],
        "height": player["height"],
        "weight": player["weight"],
        "injured": player["injured"],
        "photo": player["photo"],
        "team_id": statistics["team"]["id"],
        "team_name": statistics["team"]["name"],
        "team_logo": statistics["team"]["logo"],
        "league_id": statistics["league"]["id"],
        "league_name": statistics["league"]["name"],
        "league_country": statistics["league"]["country"],
        "league_logo": statistics["league"]["logo"],
        "league_flag": statistics["league"]["flag"],
        "season": statistics["league"]["season"],
        "games_appearences": statistics["games"]["appearences"],
        "games_lineups": statistics["games"]["lineups"],
        "games_minutes": statistics["games"]["minutes"],
        "games_number": statistics["games"]["number"],
        "games_position": statistics["games"]["position"],
        "games_rating": statistics["games"]["rating"],
        "games_captain": statistics["games"]["captain"],
        "substitutes_in": statistics["substitutes"]["in"],
        "substitutes_out": statistics["substitutes"]["out"],
        "substitutes_bench": statistics["substitutes"]["bench"],
        "shots_total": statistics["shots"]["total"],
        "shots_on": statistics["shots"]["on"],
        "goals_total": statistics["goals"]["total"],
        "goals_conceded": statistics["goals"]["conceded"],
        "goals_assists": statistics["goals"]["assists"],
        "goals_saves": statistics["goals"]["saves"],
        "passes_total": statistics["passes"]["total"],
        "passes_key": statistics["passes"]["key"],
        "passes_accuracy": statistics["passes"]["accuracy"],
        "tackles_total": statistics["tackles"]["total"],
        "tackles_blocks": statistics["tackles"]["blocks"],
        "tackles_interceptions": statistics["tackles"]["interceptions"],
        "duels_total": statistics["duels"]["total"],
        "duels_won": statistics["duels"]["won"],
        "dribbles_attempts": statistics["dribbles"]["attempts"],
        "dribbles_success": statistics["dribbles"]["success"],
        "dribbles_past": statistics["dribbles"]["past"],
        "fouls_drawn": statistics["fouls"]["drawn"],
        "fouls_committed": statistics["fouls"]["committed"],
        "cards_yellow": statistics["cards"]["yellow"],
        "cards_yellowred": statistics["cards"]["yellowred"],
        "cards_red": statistics["cards"]["red"],
        "penalty_won": statistics["penalty"]["won"],
        "penalty_commited": statistics["penalty"]["commited"],
        "penalty_scored": statistics["penalty"]["scored"],
        "penalty_missed": statistics["penalty"]["missed"],
        "penalty_saved": statistics["penalty"]["saved"]
    }

    # Insert player stats into the database
    cursor.execute('''
        INSERT OR REPLACE INTO player_stats (
            id, name, firstname, lastname, age, birth_date, birth_place, birth_country, nationality, height, weight, injured, photo, 
            team_id, team_name, team_logo, league_id, league_name, league_country, league_logo, league_flag, season, 
            games_appearences, games_lineups, games_minutes, games_number, games_position, games_rating, games_captain, 
            substitutes_in, substitutes_out, substitutes_bench, shots_total, shots_on, goals_total, goals_conceded, 
            goals_assists, goals_saves, passes_total, passes_key, passes_accuracy, tackles_total, tackles_blocks, 
            tackles_interceptions, duels_total, duels_won, dribbles_attempts, dribbles_success, dribbles_past, fouls_drawn, 
            fouls_committed, cards_yellow, cards_yellowred, cards_red, penalty_won, penalty_commited, penalty_scored, 
            penalty_missed, penalty_saved
        ) VALUES (
            :id, :name, :firstname, :lastname, :age, :birth_date, :birth_place, :birth_country, :nationality, :height, :weight, 
            :injured, :photo, :team_id, :team_name, :team_logo, :league_id, :league_name, :league_country, :league_logo, 
            :league_flag, :season, :games_appearences, :games_lineups, :games_minutes, :games_number, :games_position, 
            :games_rating, :games_captain, :substitutes_in, :substitutes_out, :substitutes_bench, :shots_total, :shots_on, 
            :goals_total, :goals_conceded, :goals_assists, :goals_saves, :passes_total, :passes_key, :passes_accuracy, 
            :tackles_total, :tackles_blocks, :tackles_interceptions, :duels_total, :duels_won, :dribbles_attempts, 
            :dribbles_success, :dribbles_past, :fouls_drawn, :fouls_committed, :cards_yellow, :cards_yellowred, :cards_red, 
            :penalty_won, :penalty_commited, :penalty_scored, :penalty_missed, :penalty_saved
        )
    ''', player_stats)

    # Commit the transaction
    conn.commit()

def insert_player_fixture_stats(data):
    # Database connection
    fixture_id = data["parameters"]["fixture"]
    # Create table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_match_statistics (
            fixture_id INTEGER,
            team_id INTEGER,
            player_id INTEGER,
            player_name TEXT,
            minutes INTEGER,
            number INTEGER,
            position TEXT,
            rating REAL,
            captain BOOLEAN,
            substitute BOOLEAN,
            shots_total INTEGER,
            shots_on INTEGER,
            goals_total INTEGER,
            goals_conceded INTEGER,
            assists INTEGER,
            saves INTEGER,
            passes_total INTEGER,
            passes_key INTEGER,
            passes_accuracy TEXT,
            tackles_total INTEGER,
            tackles_blocks INTEGER,
            tackles_interceptions INTEGER,
            duels_total INTEGER,
            duels_won INTEGER,
            dribbles_attempts INTEGER,
            dribbles_success INTEGER,
            fouls_drawn INTEGER,
            fouls_committed INTEGER,
            cards_yellow INTEGER,
            cards_red INTEGER,
            penalty_won INTEGER,
            penalty_committed INTEGER,
            penalty_scored INTEGER,
            penalty_missed INTEGER,
            penalty_saved INTEGER,
            FOREIGN KEY(fixture_id) REFERENCES fixtures(fixture_id)
        )
    ''')

    # Iterate through the response to extract and insert player statistics
    for team_data in data["response"]:
        team_id = team_data["team"]["id"]
        for player_data in team_data["players"]:
            player = player_data["player"]
            player_id = player["id"]
            player_name = player["name"]

            statistics = player_data["statistics"][0]

            # Extract statistics data
            games = statistics["games"]
            shots = statistics["shots"]
            goals = statistics["goals"]
            passes = statistics["passes"]
            tackles = statistics["tackles"]
            duels = statistics["duels"]
            dribbles = statistics["dribbles"]
            fouls = statistics["fouls"]
            cards = statistics["cards"]
            penalty = statistics["penalty"]

            # Insert data into the table
            cursor.execute('''
                INSERT INTO player_match_statistics (
                    fixture_id, team_id, player_id, player_name, minutes, number, position, rating, captain, substitute,
                    shots_total, shots_on, goals_total, goals_conceded, assists, saves, passes_total, passes_key, passes_accuracy,
                    tackles_total, tackles_blocks, tackles_interceptions, duels_total, duels_won, dribbles_attempts, dribbles_success,
                    fouls_drawn, fouls_committed, cards_yellow, cards_red, penalty_won, penalty_committed, penalty_scored, penalty_missed, penalty_saved
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                fixture_id, team_id, player_id, player_name,
                games["minutes"], games["number"], games["position"], games.get("rating", None), games["captain"], games["substitute"],
                shots["total"], shots["on"], goals["total"], goals["conceded"], goals["assists"], goals["saves"],
                passes["total"], passes["key"], passes["accuracy"], tackles["total"], tackles["blocks"], tackles["interceptions"],
                duels["total"], duels["won"], dribbles["attempts"], dribbles["success"], fouls["drawn"], fouls["committed"],
                cards["yellow"], cards["red"], penalty["won"], penalty["commited"], penalty["scored"], penalty["missed"], penalty["saved"]
            ))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

def insert_fixture_statistics(json_data):
    conn = sqlite3.connect('fixture_statistics.db')
    cursor = conn.cursor()

    fixture_id = json_data['parameters']['fixture']
    fixture_data = json.dumps(json_data)  # Save the entire JSON data as a string

    # Insert the fixture data into the fixtures table
    cursor.execute('''
    INSERT OR IGNORE INTO fixtures (fixture_id, fixture_data)
    VALUES (?, ?)
    ''', (fixture_id, fixture_data))

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
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    conn.close()



# with open("2023.json", "r") as file:
#     data = json.load(file)
#     insert_fixtures(data)


# with open("palmer.json", "r") as file:
#     data = json.load(file)
#     insert_player_stats(data)

with open("player_fixture_stats.json", "r", encoding="utf-8") as file:
    data = json.load(file)
    insert_player_fixture_stats(data)