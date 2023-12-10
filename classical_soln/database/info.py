import sqlite3

# Connect to the database
conn = sqlite3.connect('data_models.db')
cursor = conn.cursor()

# Get the list of tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Iterate through tables and print columns for each
for table in tables:
    table_name = table[0]
    print(f"Table: {table_name}")

    # Get the columns for each table
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns_info = cursor.fetchall()

    # Extract column names from the result and print
    column_names = [info[1] for info in columns_info]
    print("Columns:", column_names)
    print()  # Add a newline between tables

# Close the connection
conn.close()
