# PROD: utd for wtcoc 2022


import datetime
import pandas as pd
import pyodbc

currentDateTime = datetime.datetime.now()
year = datetime.date.today().year

division_file = "../wtcoc/" + str(year) + ".xlsx"
divisions = pd.read_excel(division_file, sheet_name = "divisions")

# Insert Dataframe into SQL Server:
connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-BN7PJQ0\HOMESQL;DATABASE=carcassonne;Trusted_Connection=yes;')
cursor = connection.cursor()
cursor.execute("DELETE FROM WTCOC_Divisions WHERE YEAR = ?", year)

for index, row in divisions.iterrows():
    cursor.execute("INSERT INTO WTCOC_Divisions (division,country,year,position) values(?,?,?,?)", row["division"],  row["country"], year, row["position"])
cursor.commit()
cursor.close()
connection.close()

#select * from WTCOC_Divisions where year = order by division, country















