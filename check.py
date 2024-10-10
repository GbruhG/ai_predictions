# Assuming the table name is 'fixture_statistics'
import json
import requests
import sqlite3
import time

# Database setup
conn = sqlite3.connect('premier_league.db')
cursor = conn.cursor()
def print_fixture_statistics():
    cursor.execute('SELECT * FROM fixture_statistics')
    rows = cursor.fetchall()
    
    # Print the column names
    column_names = [description[0] for description in cursor.description]
    print("\t".join(column_names))
    
    # Print each row in the table
    for row in rows:
        print("\t".join(str(item) for item in row))

# Call the function to print the data
print_fixture_statistics()
