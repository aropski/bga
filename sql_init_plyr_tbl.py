# PROD: DO NOT RUN AGAIN, CONTAINS DESTRUCTIVE SQL CODE (commented out)
# create first record in the Plyaer table

import pyodbc

delete_records = input("This code deletes all records in the Players table, do you wish to proceed with this destructive action?")

if delete_records:
    connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-BN7PJQ0\HOMESQL;DATABASE=carcassonne;Trusted_Connection=yes;')
    cursor = connection.cursor()
    # cursor.execute("TRUNCATE TABLE Players;")
    cursor.execute("INSERT INTO Players (ID, Name) VALUES (87741956, 'arop');")
    cursor.execute("SELECT * FROM Players")

    for row in cursor.fetchall():
        print(row)

    delete_records = input("Do you wish to proceed and commit the destructive changes to the Players table?")

    if delete_records:
        cursor.commit()

    cursor.close()
    connection.close()



# USE [carcassonne]
# GO
# CREATE TABLE [dbo].[WTCOC_Rosters](
# 	[country] [varchar](63) NOT NULL,
# 	[name] [varchar](63) NOT NULL,
# 	[year] [int] NOT NULL,
# 	[captain] [bit] NOT NULL
# ) ON [PRIMARY]
# GO




