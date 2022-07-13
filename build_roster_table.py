# PROD: utd for wtcoc 2022

# this program initializes the WTCOC_Rosters database, seeding it with WTCOC 2022 players
# Player Name will be used as the linking variables across tables
# Player ID will be the PK; necessary for scrapping BGA player pages

## TODO after running, audit Player table for each name and BGA

import datetime
import pandas as pd

currentDateTime = datetime.datetime.now()
current_year = datetime.date.today().year

roster_file = "../wtcoc/" + str(current_year) + ".xlsx"
roster = pd.read_excel(roster_file, sheet_name = "rosters")

freq_country = roster["country"].value_counts()

# insert each team roster into database; drops existing current year roster
if all(freq_country.between(8, 10)):
    # Insert Dataframe into SQL Server:
    connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-BN7PJQ0\HOMESQL;DATABASE=carcassonne;Trusted_Connection=yes;')
    cursor = connection.cursor()
    cursor.execute("DELETE FROM WTCOC_Rosters WHERE YEAR = ?", year)

    for index, row in roster.iterrows():
        cursor.execute("INSERT INTO WTCOC_Rosters (country,name,year,captain) values(?,?,?,?)", row["country"],  row["name"], year, row["captain"])
    cursor.commit()
    cursor.close()
    connection.close()
else:
    print("The following rosters have invalid number of players")
    for index,value in freq_country.iteritems():
        if value < 8 or value > 10:
            print(index, value)
        else:
            print(f"{index} has {value} team members.")

#select count(*), Country from WTCOC_Rosters group by Country















