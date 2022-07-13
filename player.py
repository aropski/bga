import requests
import launch_bga_crawler as login_to_bga
import pyodbc

from bs4 import BeautifulSoup
import time
import re
import pyodbc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BGA_ENDPOINT = "https://boardgamearena.com/"


# my_playa = player.Player(name='arop')
# my_playa = player.Player(name='arop', id=87741956)

class Player:

    def __init__(self, **kwargs):
        self.id = None
        self.name = None
        self.__dict__.update(kwargs)

    def __str__(self):
       return (f"Name: {self.name}\nBGA id: {self.id}")

    def get_id_from_sql(self):
        connection = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-BN7PJQ0\HOMESQL;DATABASE=carcassonne;Trusted_Connection=yes;')
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM Players WHERE NAME = (?)", str(self.name))
        self.id = int(cursor.fetchall()[0][0])
        cursor.close()
        connection.close()


    def get_game_ids(self, driver):
        ## TODO minimize clicks of 'See more' by checking most recent game dt stamp in sql
        """ retrieves the list of a players game ids
        metadata will be retrieved using the Game.get_game_meta method
        moves will be retrieved using the Game.get_gamelog method """

        player_page = "https://boardgamearena.com/gamestats?player=" + str(self.id) + "&opponent_id=0&game_id=1&finished=0"
        driver.get(player_page)

        # click id "see_more_table"
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_element_located((By.ID, "see_more_tables")))

        # until class="head_infomsg_1" appears
        test_done = False
        my_int = 1
        while test_done is False:
            driver.find_element_by_id("see_more_tables").click()
            time.sleep(0.1)
            test_msg = driver.find_element_by_id("head_infomsg")
            test_done = test_msg.is_displayed()
            my_int += 1
            if my_int % 100 == 0:
                print("max clicks, breaking loop and extracting available game IDs")
                break

        out_html = driver.page_source
        page_html = BeautifulSoup(out_html, 'html.parser')
        game_html = page_html.find(id="gamelist")

        # get just the game IDs
        #tmp_strings = re.findall('Carcassonne#\d*/\d\d/\d\d\d\d', game_html.text)
        #game_ids = [int(re.findall(r'\d+',string[:-10])[0]) for string in tmp_strings]
        tmp_strings = re.findall('Carcassonne#\d{9}', game_html.text)
        game_ids = [int(re.findall(r'\d+',string)[0]) for string in tmp_strings]

        # add to sql table
        connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-BN7PJQ0\HOMESQL;DATABASE=carcassonne;Trusted_Connection=yes;')
        cursor = connection.cursor()

        for game_id in game_ids:
            cursor.execute("INSERT INTO Game_Outcomes(game_id) values(?)", str(game_id))
        cursor.commit()
        cursor.close()
        connection.close()

        # run dedupper


    def get_rank(self):
        pass

    # check which games exist and update all new
    def populate_games(self):
        pass

