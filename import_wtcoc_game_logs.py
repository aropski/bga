## TODO add indiciator for abandoned games


# this will be one of many scripts to import game logs
# game id list will be generated from the list of wtcoc games

# these games play to completion (only the 1st is actually a tournament which cannot be resigned)



import launch_bga_crawler
import pyodbc
import pandas as pd
import json

import sys



(driver, wait, EC, By, Keys) = launch_bga_crawler.login_to_bga()

#################
### GAME LOGS ###
#################
import game


# get unlogged game_ids
connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-BN7PJQ0\HOMESQL;DATABASE=carcassonne;Trusted_Connection=yes;')
cursor = connection.cursor()
cursor.execute('SELECT distinct game_id FROM [carcassonne].[dbo].[Game_Outcomes] where game_id not in ( SELECT distinct game_id FROM [carcassonne].[dbo].[Game_Logs])')
unlogged_game_ids = [item for t in cursor.fetchall() for item in t]
print(unlogged_game_ids)
cursor.commit()
cursor.close()
connection.close()



for game_id in unlogged_game_ids[:40]:
    #sys.stdout = open('./game.log', 'w')
    print(game_id)
    my_game = game.Game(game_id)
    my_game.get_player_ids(driver)
    my_game.get_gamelog(driver)
    my_game.transform_game_json_to_sql()
    print(my_game.moves.to_string())
    my_game.dump_to_sql()
    #sys.stdout.close()

#######################
### PLAYER GAME IDS ###
#######################

# import player
#
#
#
# my_playa = player.Player(name='Alexey_LV')
# my_playa.get_id_from_sql()
# my_playa.get_game_ids(driver)


