######################################## Searching through the created database
import sqlite3

# Connect to the database
conn = sqlite3.connect('data_models.db')
cursor = conn.cursor()

# select_data_query = '''
# SELECT * FROM flight WHERE (FlightNumber = 3417 and DepartureDate = '05/25/2024');
# '''
select_data_query = '''
SELECT * FROM affected_pnr
'''

# Execute the select query
cursor.execute(select_data_query)

# Fetch all the results
results = cursor.fetchall()

# Print the results
for row in results:
    print(row)

# Close the connection
conn.close()

######################### Creating the database
# import sqlite3
# import pandas as pd
#
# # Path to your CSV file
# csv_file_path = 'INV.csv'
#
# # Read the CSV file into a Pandas DataFrame
# df = pd.read_csv(csv_file_path)
#
# # Connect to a SQLite database
# conn = sqlite3.connect('data_models.db')
#
# # Write the DataFrame to a SQLite table
# df.to_sql('flight', conn, index=False, if_exists='replace')
#
# # Commit the changes to the database
# conn.commit()
#
# # Close the connection
# conn.close()

######################### Copying SCH fields to flight table inside data_models.db
# import pandas as pd
# import sqlite3
#
# # Read CSV into a Pandas DataFrame
# df = pd.read_csv('SCH.csv')
#
# # Connect to the database
# conn = sqlite3.connect('data_models.db')
# cursor = conn.cursor()
#
# # Iterate through rows and update the 'flight' table
# for i in range(len(df)):
#     row = df.iloc[i]
#
#     SID = row["ScheduleID"]
#     DepartureTime = row["DepartureTime"]
#     ArrivalTime = row["ArrivalTime"]
#     Status = row["Status"]
#
#     # Use parameterized query to avoid SQL injection
#     sql_query = '''
#     UPDATE flight
#     SET Status = ?
#     WHERE ScheduleId = ?;
#     '''
#
#     # Execute the query with parameters
#     cursor.execute(sql_query, (Status, SID))
#
# # Commit changes to the database
# conn.commit()
#
# # Close the connection
# conn.close()

######################### Creating passenger table
# import sqlite3
# import pandas as pd
#
# # Path to your CSV file
# csv_file_path = 'pnr.csv'
#
# # Read the CSV file into a Pandas DataFrame
# df = pd.read_csv(csv_file_path)
#
# # Connect to a SQLite database
# conn = sqlite3.connect('data_models.db')
#
# # Write the DataFrame to a SQLite table
# df.to_sql('pnr_booking', conn, index=False, if_exists='replace')
#
# # Commit the changes to the database
# conn.commit()
#
# # Close the connection
# conn.close()

######################### Creating affected_cities table
# import sqlite3
#
# # Connect to a database
# conn = sqlite3.connect('data_models.db')
#
# # Create a cursor object
# cursor = conn.cursor()
#
# # Define a table creation SQL statement
# create_table_query = '''
# CREATE TABLE IF NOT EXISTS affected_cities (
#     source TEXT,
#     destination TEXT
# );
# '''
#
# # Execute the table creation SQL statement
# cursor.execute(create_table_query)
#
# # Commit the changes to the database
# conn.commit()
#
# # Close the connection
# conn.close()

######################### Creating affected_cities table
# import sqlite3
#
# # Connect to a database
# conn = sqlite3.connect('data_models.db')
#
# # Create a cursor object
# cursor = conn.cursor()
#
# # Define a table creation SQL statement
# create_table_query = '''
# CREATE TABLE IF NOT EXISTS affected_pnr (
#     RELOC TEXT,
#     CREATION_DTZ TEXT,
#     DEP_KEY TEXT,
#     CNF_STATUS TEXT,
#     COS_CD TEXT,
#     SEQ INT,
#     PAS_CNT INT,
#     AIRLINE TEXT,
#     FLT_NUM INT,
#     DEP TEXT,
#     ARR TEXT,
#     DEP_DT TEXT,
#     DEP_TIME TEXT,
#     ARR_DATE TEXT,
#     ARR_TIME TEXT
# );
# '''
#
# # Execute the table creation SQL statement
# cursor.execute(create_table_query)
#
# # Commit the changes to the database
# conn.commit()
#
# # Close the connection
# conn.close()
