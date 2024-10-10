import sqlite3
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam

# Connect to the SQLite database
conn = sqlite3.connect('premier_league.db')

# Load data
query = """
SELECT 
    f.fixture_id, f.date, f.home_team_id, f.away_team_id, 
    f.goals_home, f.goals_away,
    home_stats.ball_possession as home_possession,
    away_stats.ball_possession as away_possession,
    home_stats.shots_on_goal as home_shots_on_goal,
    away_stats.shots_on_goal as away_shots_on_goal,
    home_stats.total_passes as home_total_passes,
    away_stats.total_passes as away_total_passes
FROM fixtures f
JOIN fixture_statistics home_stats ON f.fixture_id = home_stats.fixture_id AND f.home_team_id = home_stats.team_id
JOIN fixture_statistics away_stats ON f.fixture_id = away_stats.fixture_id AND f.away_team_id = away_stats.team_id
WHERE f.league_id = 39  -- Assuming 39 is the Premier League ID
"""

df = pd.read_sql_query(query, conn)

# Preprocess data
df['date'] = pd.to_datetime(df['date'])
df['home_possession'] = df['home_possession'].str.rstrip('%').astype(float) / 100
df['away_possession'] = df['away_possession'].str.rstrip('%').astype(float) / 100

# Create target variable (2 for home win, 1 for draw, 0 for away win)
df['target'] = np.select(
    [df['goals_home'] > df['goals_away'], df['goals_home'] == df['goals_away'], df['goals_home'] < df['goals_away']],
    [2, 1, 0]
)

# Select features
features = ['home_possession', 'away_possession', 'home_shots_on_goal', 'away_shots_on_goal', 
            'home_total_passes', 'away_total_passes']

X = df[features]
y = df['target']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Build the model
model = Sequential([
    Dense(64, activation='relu', input_shape=(len(features),)),
    Dropout(0.2),
    Dense(32, activation='relu'),
    Dropout(0.2),
    Dense(16, activation='relu'),
    Dense(3, activation='softmax')  # 3 output neurons for away win, draw, home win
])

model.compile(optimizer=Adam(learning_rate=0.001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Train the model
history = model.fit(X_train_scaled, y_train, epochs=100, batch_size=32, validation_split=0.2, verbose=1)

# Evaluate the model
test_loss, test_accuracy = model.evaluate(X_test_scaled, y_test, verbose=0)
print(f'Test accuracy: {test_accuracy:.4f}')

# Make predictions
predictions = model.predict(X_test_scaled)

# Convert predictions to class labels
predicted_classes = np.argmax(predictions, axis=1)

# Create a mapping to interpret the results
result_mapping = {0: "Away Win", 1: "Draw", 2: "Home Win"}

# Print some example predictions
for true_label, predicted_label in zip(y_test[:10], predicted_classes[:10]):
    print(f"True: {result_mapping[true_label]}, Predicted: {result_mapping[predicted_label]}")

# Optional: Plot training history
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

plt.tight_layout()
plt.savefig('training_history.png')
plt.show()

def get_team_stats(team_id, conn):
    query = """
    SELECT AVG(ball_possession) as avg_possession,
           AVG(shots_on_goal) as avg_shots_on_goal,
           AVG(total_passes) as avg_total_passes
    FROM fixture_statistics
    WHERE team_id = ?
    GROUP BY team_id
    """
    return pd.read_sql_query(query, conn, params=(team_id,)).iloc[0]

def predict_match(home_team_id, away_team_id, model, scaler, conn):
    home_stats = get_team_stats(home_team_id, conn)
    away_stats = get_team_stats(away_team_id, conn)
    
    match_features = [
        home_stats['avg_possession'],
        away_stats['avg_possession'],
        home_stats['avg_shots_on_goal'],
        away_stats['avg_shots_on_goal'],
        home_stats['avg_total_passes'],
        away_stats['avg_total_passes']
    ]
    
    # Reshape and scale the features
    match_features = np.array(match_features).reshape(1, -1)
    match_features_scaled = scaler.transform(match_features)
    
    # Make prediction
    prediction = model.predict(match_features_scaled)
    predicted_class = np.argmax(prediction)
    
    return result_mapping[predicted_class], prediction[0]

# Add this at the end of your script
while True:
    home_team_id = int(input("Enter home team ID (or -1 to quit): "))
    if home_team_id == -1:
        break
    away_team_id = int(input("Enter away team ID: "))
    
    result, probabilities = predict_match(home_team_id, away_team_id, model, scaler, conn)
    print(f"Predicted result: {result}")
    print(f"Probabilities: Away Win: {probabilities[0]:.2f}, Draw: {probabilities[1]:.2f}, Home Win: {probabilities[2]:.2f}")

