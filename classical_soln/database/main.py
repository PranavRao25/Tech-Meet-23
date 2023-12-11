######################################## Searching through the created database
import sqlite3

# Connect to the database
conn = sqlite3.connect('data_models.db')
cursor = conn.cursor()

# select_data_query = '''
# SELECT * FROM flight WHERE (FlightNumber = 3417 and DepartureDate = '05/25/2024');
# '''

select_data_query = '''
SELECT * FROM passenger
'''

# Drop the table
drop_table_query = f'DROP TABLE IF EXISTS CNN_MAA;'

# Execute the query
cursor.execute(select_data_query)

# Fetch all the results
results = cursor.fetchall()

# Print the results
for row in results:
    print(row)

# Close the connection
conn.close()

######################### Creating affected_cities table
# import sqlite3
#
# # Connect to a SQLite database
# conn = sqlite3.connect('data_models.db')
# cursor = conn.cursor()
#
# create_table_query = '''
# CREATE TABLE IF NOT EXISTS affected_cities (
#     Source TEXT,
#     Destination TEXT
# );
# '''
# # Write the DataFrame to a SQLite table
# cursor.execute(create_table_query)
#
# # Commit the changes to the database
# conn.commit()
#
# # Close the connection
# conn.close()

######################### Creating passenger table
# import sqlite3
# import pandas as pd
#
# # Path to your CSV file
# csv_file_path = 'pnr_passanger.csv'
#
# # Read the CSV file into a Pandas DataFrame
# df = pd.read_csv(csv_file_path)
#
# # Connect to a SQLite database
# conn = sqlite3.connect('data_models.db')
#
# # Write the DataFrame to a SQLite table
# df.to_sql('passenger', conn, index=False, if_exists='replace')
#
# # Commit the changes to the database
# conn.commit()
#
# # Close the connection
# conn.close()

######################### Creating booking table
# import sqlite3
# import pandas as pd
#
# # Path to your CSV file
# csv_file_path = 'pnr_booking.csv'
#
# # Read the CSV file into a Pandas DataFrame
# df = pd.read_csv(csv_file_path)
#
# # Connect to a SQLite database
# conn = sqlite3.connect('data_models.db')
#
# # Write the DataFrame to a SQLite table
# df.to_sql('booking', conn, index=False, if_exists='replace')
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
# df = pd.read_csv('sch.csv')
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

######################### Creating the flight table
# import sqlite3
# import pandas as pd
#
# # Path to your CSV file
# csv_file_path = 'inv.csv'
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
