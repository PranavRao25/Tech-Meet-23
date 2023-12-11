# { input = database }, { output = identified affected flights & passengers }
import sqlite3
import pandas as pd

conn = sqlite3.connect('../database/data_models.db')
cursor = conn.cursor()

Disruptions = [
    {
        "FlightNumber": 3417,
        "Date": '05/25/2024',
        "Type": "Cancelled",
    },
    # {
    #     "FlightNumber": ,
    #     "Type": "Delayed",
    # }
]

# Assumes unique entry for each cancelled flight
for disruption in Disruptions:

    if disruption["Type"] == "Cancelled":

        # TODO 1 : Update the affectd cities table

        select_data_query = '''
        SELECT * FROM flight
        WHERE (FlightNumber = ? and DepartureDate = ?)
        '''

        # Execute the select query
        cursor.execute(select_data_query, (disruption["FlightNumber"], disruption["Date"]))

        flight = cursor.fetchall()[0]

        print(flight)
        print(flight[6], flight[7])

        update_data_query = '''
        INSERT INTO  affected_cities 
        VALUES (?,?);
        '''

        cursor.execute(update_data_query, (flight[6], flight[7]))
        conn.commit()

        # TODO 2 : get the affected passengers

        select_data_query = '''
        SELECT * FROM booking
        WHERE (FLT_NUM = ? and DEP_DT = ?)
        '''

        # Execute the select query
        cursor.execute(select_data_query, (disruption["FlightNumber"], disruption["Date"]))

        affected_pnrs = cursor.fetchall()

        # TODO 3 : Create a table for the affected passengers

        table_name = flight[6]+'_'+flight[7]

        # Check if the table already exists
        existing_tables_query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
        cursor.execute(existing_tables_query)
        existing_tables = cursor.fetchall()

        if not existing_tables:
            # If the table does not exist, create it
            df = pd.read_csv('../database/booking_template.csv')
            df.to_sql(table_name, conn, index=False, if_exists='fail')
            conn.commit()
            print(f"Table '{table_name}' created.")
        else:
            print(f"Table '{table_name}' already exists. Skipping table creation.")

        for pnr in affected_pnrs:

            print(pnr)

            update_data_query = f'''
            INSERT INTO  {table_name}
            VALUES {pnr};
            '''

            # Execute the select query
            cursor.execute(update_data_query)

            # Commit changes to the database
            conn.commit()

# Close the connection
conn.close()
