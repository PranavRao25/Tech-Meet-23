# Searching through the created database
import sqlite3

# Connect to the database
conn = sqlite3.connect('data_models.db')
cursor = conn.cursor()

# select_data_query = '''
# SELECT * FROM flight WHERE (FlightNumber = 3417 and DepartureDate = '05/25/2024');
# '''
select_data_query = '''
SELECT * FROM flight
WHERE 
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

