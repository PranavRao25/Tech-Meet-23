# { input = database }, { output = identified affected flights & passengers }
import sqlite3

conn = sqlite3.connect('../database/data_models.db')
cursor = conn.cursor()

Disruptions = [
    {
        "FlightNumber": 2008,
        "Date": '12/17/2023',
        "Type": "Cancelled",
    },
    # {
    #     "FlightNumber": ,
    #     "Type": "Delayed",
    # }
]

for disruption in Disruptions:

    if disruption["Type"] == "Cancelled":

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
        INSERT INTO  affected_cities (source, destination)
        VALUES (?,?);
        '''

        # Execute the select query
        cursor.execute(update_data_query, (row[6], row[7]))

        # Commit changes to the database
        conn.commit()

        select_data_query = '''
        SELECT * FROM pnr_booking
        WHERE (FLT_NUM = ? and DEP_DT = ?)
        '''

        # Execute the select query
        cursor.execute(select_data_query, (disruption["FlightNumber"], disruption["Date"]))

        affected_pnrs = cursor.fetchall()

        for pnr in affected_pnrs:

            print(pnr)

            update_data_query = '''
            INSERT INTO  affected_pnr 
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);
            '''

            # Execute the select query
            cursor.execute(update_data_query,pnr)

            # Commit changes to the database
            conn.commit()

# Close the connection
conn.close()
