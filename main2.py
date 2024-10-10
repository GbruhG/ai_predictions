import sqlite3
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.optimizers import Adam

conn = sqlite3.connect('premier_league.db')

def get_team_form(team_id, num_games):
    query = f"""
    SELECT 
        CASE 
            WHEN home_team_id = {team_id} AND goals_home > goals_away THEN 3
            WHEN away_team_id = {team_id} AND goals_away > goals_home THEN 3
            WHEN goals_home = goals_away THEN 1
            ELSE 0
        END as points,
        date
    FROM fixtures
    WHERE home_team_id = {team_id} OR away_team_id = {team_id}
    ORDER BY date DESC
    LIMIT {num_games}
    """
    df = pd.read_sql_query(query, conn)
    df['weight'] = np.linspace(1, 0.5, num=len(df))  # Linear weight decay
    return (df['points'] * df['weight']).sum() / df['weight'].sum()

def get_head_to_head(team1_id, team2_id):
    query = f"""
    SELECT 
        CASE 
            WHEN home_team_id = {team1_id} AND goals_home > goals_away THEN 1
            WHEN away_team_id = {team1_id} AND goals_away > goals_home THEN 1
            WHEN home_team_id = {team2_id} AND goals_home > goals_away THEN -1
            WHEN away_team_id = {team2_id} AND goals_away > goals_home THEN -1
            ELSE 0
        END as result
    FROM fixtures
    WHERE (home_team_id = {team1_id} AND away_team_id = {team2_id})
       OR (home_team_id = {team2_id} AND away_team_id = {team1_id})
    ORDER BY date DESC
    LIMIT 5
    """
    df = pd.read_sql_query(query, conn)
    return df['result'].mean()

def get_team_stats(team_id):
    query = f"""
    SELECT 
        AVG(shots_on_goal) as avg_shots_on_goal,
        AVG(shots_off_goal) as avg_shots_off_goal,
        AVG(total_shots) as avg_total_shots,
        AVG(blocked_shots) as avg_blocked_shots,
        AVG(shots_inside_box) as avg_shots_inside_box,
        AVG(shots_outside_box) as avg_shots_outside_box,
        AVG(fouls) as avg_fouls,
        AVG(corner_kicks) as avg_corner_kicks,
        AVG(offsides) as avg_offsides,
        AVG(CAST(REPLACE(ball_possession, '%', '') AS FLOAT)) as avg_ball_possession,
        AVG(yellow_cards) as avg_yellow_cards,
        AVG(red_cards) as avg_red_cards,
        AVG(goalkeeper_saves) as avg_goalkeeper_saves,
        AVG(total_passes) as avg_total_passes,
        AVG(passes_accurate) as avg_passes_accurate,
        AVG(CAST(REPLACE(passes_percentage, '%', '') AS FLOAT)) as avg_passes_percentage
    FROM fixture_statistics
    WHERE team_id = {team_id}
    """
    return pd.read_sql_query(query, conn).iloc[0]

def get_team_player_stats(team_id):
    query = f"""
    SELECT 
        AVG(games_rating) as avg_rating,
        AVG(games_minutes) as avg_minutes,
        SUM(goals_total) as total_goals,
        SUM(goals_assists) as total_assists,
        AVG(shots_total) as avg_shots,
        AVG(shots_on) as avg_shots_on_target,
        AVG(passes_total) as avg_passes,
        AVG(passes_accuracy) as avg_pass_accuracy,
        AVG(tackles_total) as avg_tackles,
        AVG(duels_total) as avg_duels,
        AVG(duels_won) as avg_duels_won,
        AVG(dribbles_attempts) as avg_dribbles,
        AVG(dribbles_success) as avg_successful_dribbles
    FROM player_stats
    WHERE team_id = {team_id} AND season = (SELECT MAX(season) FROM player_stats)
    """
    return pd.read_sql_query(query, conn).iloc[0]


def get_player_shot_stats(player_id):
    query = f"""
    SELECT 
        AVG(shots_total) as avg_shots_total,
        AVG(shots_on) as avg_shots_on_target
    FROM player_match_statistics
    WHERE player_id = 152982
    """
    return pd.read_sql_query(query, conn).iloc[0]

def prepare_match_data(home_team_id, away_team_id, home_player_id, away_player_id):
    features = []
    
    # Team form (last 5, 10, and 20 games)
    for team_id in [home_team_id, away_team_id]:
        features.extend([
            get_team_form(team_id, 5),
            get_team_form(team_id, 10),
            get_team_form(team_id, 20)
        ])
    
    # Head-to-head
    features.append(get_head_to_head(home_team_id, away_team_id))
    
    # Team stats
    for team_id in [home_team_id, away_team_id]:
        stats = get_team_stats(team_id)
        features.extend(stats.values)
    
    # Team player stats
    for team_id in [home_team_id, away_team_id]:
        player_stats = get_team_player_stats(team_id)
        features.extend(player_stats.values)
    
    # Add player shot stats
    for player_id in [home_player_id, away_player_id]:
        shot_stats = get_player_shot_stats(player_id)
        features.extend(shot_stats.values)
    
    return np.array(features).reshape(1, -1)

def create_model(input_shape, output_shapes):
    inputs = Input(shape=(input_shape,))
    x = Dense(128, activation='relu')(inputs)
    x = Dense(64, activation='relu')(x)
    x = Dense(32, activation='relu')(x)
    
    outputs = []
    for key, shape in output_shapes.items():
        outputs.append(Dense(shape[1], activation='softmax', name=key)(x))
    
    model = Model(inputs=inputs, outputs=outputs)
    
    losses = {key: 'categorical_crossentropy' for key in output_shapes.keys()}
    
    model.compile(optimizer=Adam(learning_rate=0.001),
                  loss=losses,
                  loss_weights={key: 1.0 for key in output_shapes.keys()},
                  metrics={key: 'accuracy' for key in output_shapes.keys()})
    
    return model

def prepare_training_data():
    query = """
    SELECT 
        f.home_team_id, 
        f.away_team_id,
        CASE 
            WHEN f.goals_home > f.goals_away THEN 0
            WHEN f.goals_home = f.goals_away THEN 1
            ELSE 2
        END as match_outcome,
        f.goals_home + f.goals_away as total_goals,
        f.halftime_home + f.halftime_away as first_half_goals,
        (f.goals_home + f.goals_away) - (f.halftime_home + f.halftime_away) as second_half_goals,
        CAST(CASE WHEN f.goals_home > 0 AND f.goals_away > 0 THEN 1 ELSE 0 END AS INT) as both_teams_scored
    FROM fixtures f
    ORDER BY f.date DESC
    LIMIT 1000
    """
    matches = pd.read_sql_query(query, conn)
    print(f"Number of matches retrieved: {len(matches)}")
    
    X = []
    y = {
        'match_outcome': [],
        'goals_full': [],
        'goals_first_half': [],
        'goals_second_half': [],
        'both_teams_to_score': []
    }
    
    for _, match in matches.iterrows():
        try:
            X.append(prepare_match_data(match['home_team_id'], match['away_team_id'], 
                                        None, None).flatten())
            
            y['match_outcome'].append(match['match_outcome'])
            y['goals_full'].append(min(match['total_goals'], 4))  # 0, 1, 2, 3, 4+ goals
            y['goals_first_half'].append(min(match['first_half_goals'], 4))
            y['goals_second_half'].append(min(match['second_half_goals'], 4))
            y['both_teams_to_score'].append(match['both_teams_scored'])
        except Exception as e:
            print(f"Error processing match: {e}")
    
    print(f"Number of samples prepared: {len(X)}")
    
    for key in y.keys():
        print(f"Key: {key}, Data type: {type(y[key])}, Shape: {np.array(y[key]).shape}")
        print(f"Sample values: {y[key][:5]}")
        
        # Convert to integer and find the maximum value
        y[key] = np.array(y[key], dtype=int)
        num_classes = max(2, np.max(y[key]) + 1)  # Ensure at least 2 classes for binary outcomes
        y[key] = np.eye(num_classes)[y[key]]  # One-hot encoding for all outputs
        
        print(f"After processing - Shape: {y[key].shape}")
        print(f"Sample processed values: {y[key][:2]}\n")
    
    return np.array(X), y

def train_model():
    X, y = prepare_training_data()
    
    X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)
    y_train = {}
    y_test = {}
    
    for key in y.keys():
        y_train[key], y_test[key] = train_test_split(y[key], test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    output_shapes = {key: value.shape for key, value in y_train.items()}
    model = create_model(X_train.shape[1], output_shapes)
    
    model.fit(X_train_scaled, y_train, epochs=100, batch_size=32, validation_split=0.2, verbose=1)
    
    return model, scaler

def predict_match(model, scaler, home_team_id, away_team_id, home_player_id, away_player_id, num_simulations=10000):
    match_data = prepare_match_data(home_team_id, away_team_id, home_player_id, away_player_id)
    match_data_scaled = scaler.transform(match_data)
    
    predictions = model.predict(match_data_scaled, verbose=0)
    
    results = {
        'match_outcome': np.zeros(3),
        'goals_full': np.zeros(5),
        'goals_first_half': np.zeros(5),
        'goals_second_half': np.zeros(5),
        'both_teams_to_score': np.zeros(2),
        'home_player_shots_on_target': np.zeros(4),
        'away_player_shots_on_target': np.zeros(4),
        'home_player_shots_total': np.zeros(4),
        'away_player_shots_total': np.zeros(4)
    }
    
    for _ in range(num_simulations):
        for i, key in enumerate(results.keys()):
            results[key] += np.random.choice(len(predictions[i]), p=predictions[i])
    
    for key in results.keys():
        results[key] /= num_simulations
    
    return results

# Main execution
model, scaler = train_model()

# Example prediction
home_team_id = 49  # Replace with actual team ID
away_team_id = 50  # Replace with actual team ID
home_player_id = 152982  # Replace with actual player ID
away_player_id = 152982  # Replace with actual player ID

results = predict_match(model, scaler, home_team_id, away_team_id, home_player_id, away_player_id)

print("Match Outcome Probabilities:")
print(f"Home Win: {results['match_outcome'][0]:.2f}")
print(f"Draw: {results['match_outcome'][1]:.2f}")
print(f"Away Win: {results['match_outcome'][2]:.2f}")

print("\nGoals Probabilities:")
for i, prob in enumerate(results['goals_full']):
    print(f"Over {i-0.5} Goals: {sum(results['goals_full'][i:]):.2f}")

print("\nBoth Teams to Score Probability:")
print(f"{results['both_teams_to_score'][1]:.2f}")

print("\nHome Player Shots On Target Probabilities:")
for i, prob in enumerate(results['home_player_shots_on_target']):
    if i < 3:
        print(f"Over {i+0.5}: {sum(results['home_player_shots_on_target'][i+1:]):.2f}")

print("\nAway Player Shots On Target Probabilities:")
for i, prob in enumerate(results['away_player_shots_on_target']):
    if i < 3:
        print(f"Over {i+0.5}: {sum(results['away_player_shots_on_target'][i+1:]):.2f}")

conn.close()