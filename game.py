import pandas as pd
import json
import pyodbc

class Game:
    """A game consists of 71 tile plays (moves).
    Score represents pointed earned respective of the move; i.e. not cumulative
    A move may be a discarded tile. (x&y = NULL)"""

    def __init__(self, bga_id):
        self.bga_id = bga_id
        self.plyr1 = None # player 1 is the first player to place a tile
        self.plyr2 = None
        self.score1 = 0
        self.score2 = 0
        self.curr_move = 1
        self.inc_move = False
        # index represents the order in which tiles are played from 1-71
        # tile_id is a unique value, pre-assigned to identify each individual tile
        self.moves = pd.DataFrame(columns=['tile_id', 'tile_type',
                                           'player_id','x','y','ori','pos',
                                           'p1_pts','p2_pts'],
                                  index=range(1, 72))

    def __str__(self):
        if self.plyr1 is not None and self.plyr2 is not None:
            return(f"Game #{self.bga_id} final score:\n\t{self.plyr1}: {self.score1}\n\t{self.plyr2}: {self.score2}" )
        else:
            return (f"Game #{self.bga_id} has not been detailed." )

    def get_player_ids(self, driver):

        game_url =  'https://boardgamearena.com/gamereview?table=' + str(self.bga_id)
        #game_url =  'https://boardgamearena.com/gamereview?table=267661051'
        driver.get(game_url)
        out_html = driver.page_source

        #find player ids from class="playerselection "id="choosePlayerLink_<player bga id>"
        match_text = "choosePlayerLink_"
        match_len = len(match_text)

        # extract both player ids
        res = [i for i in range(len(out_html)) if out_html.startswith(match_text, i)]

        ## TODO player ids may be 7,8,9 digits
        # set player IDs
        try:
            self.plyr1 = int(out_html[res[0]+match_len:res[0]+match_len+8])
            self.plyr2 = int(out_html[res[1]+match_len:res[1]+match_len+8])
        except(Exception,):
            print("player IDs did not convert to integers")
        else:
            print(f"player IDs assigned as {self.plyr1} and {self.plyr2}")

    def get_gamelog(self, driver):
        """ retrieve html
        parse game log from single row of text
        output as json for archive
        json will be further parsed in moves dataframe
        """
        # 220513-1000 base arena games
        # 220420-1001 tournament games
        # 220602-1001 includes expansions

        ## TODO ensure correct game type argument; correctly crashes in dump_to_sql
        ## TODO add layer for tournament prefix in url; tag expansions
        driver.get('https://boardgamearena.com/archive/replay/220513-1000/?table=' + str(self.bga_id) + \
                       '&player=' + str(self.plyr1) + '&comments=' + str(self.plyr1))

        if len(driver.find_elements_by_class_name("fatalerror")) == 1:
            driver.get('https://boardgamearena.com/archive/replay/220420-1001/?table=' + str(self.bga_id) + \
                       '&player=' + str(self.plyr1) + '&comments=' + str(self.plyr1))

        out_html = driver.page_source
        index = out_html.find('g_gamelogs')
        end_half = out_html[index:]
        index2 = end_half.find('\n')
        g_gamelogs = end_half[:index2]
        g_gamelog = g_gamelogs.replace('{"channel":', r'\n{"channel":').split(r'\n')

        g_dict = {}
        i = 1
        for line in g_gamelog[1:]:
            if i == len(g_gamelog) - 1:
                line = line[:-4]
            else:
                line = line[:-1]
            g_dict[i] = json.loads(line)
            i += 1

        with open('../archive_game_json/game_' + str(self.bga_id) + '.json', 'w') as json_file:
        #with open('game_' + str(self.bga_id) + '.json', 'w') as json_file:
            json.dump(g_dict, json_file, indent=4)

    def transform_game_json_to_sql(self):
        # using archive json file, convert to row data and insert to sql
        with open('../archive_game_json/game_' + str(self.bga_id) + '.json') as json_file:
            g_gamelog = json.load(json_file)

        # inspect each packet component's (UID) type
        ## TODO reorder the types in each data dictionary

        for packet_id in g_gamelog:
            data_packet = g_gamelog[packet_id]["data"]
            print('\n\n')
            print(packet_id)

            for uid in data_packet:
                uid_type = uid["type"]
                print(uid_type)

                if uid_type in ("simpleNote", "deck_size","gameStateChange","updateReflexionTime","realizationAchieved","pickTile","simpleNode","realizationAchieved"):
                    pass
                elif uid_type == "playTile":
                    self.process_playTile(uid)
                    self.inc_move = True
                elif uid_type == "cantPlay":
                    self.process_cantPlay(uid)
                    self.inc_move = True
                elif uid_type == "playPartisan":
                    self.process_playPartisan(uid)
                elif uid_type == "winPoints":
                    self.process_winPoints(uid)

            # prevent early incrementing when cantPlay occurs before winPoints in a data_packet
            # else score gets assigned to discarded move
            if self.inc_move is True:
                if self.curr_move < 71:
                    self.curr_move += 1
                self.inc_move = False

    def process_playTile(self, uid):
        print("process_playTile")
        # print(json.dumps(uid["args"], indent=4))
        # print(self.curr_move)
        # print(self.plyr1)
        # print(self.plyr2)

        if self.curr_move == 1 and self.plyr1 is None:
            plyr1_id = int(uid["args"]["player_id"])
            print(f'Updating self.plyr1 to {plyr1_id}')
            self.plyr1 = plyr1_id
        if self.curr_move == 2 and self.plyr2 is None:
            plyr2_id = int(uid["args"]["player_id"])
            print(f'Updating self.plyr2 to {plyr2_id}')
            self.plyr2 = plyr2_id

        self.moves["player_id"].loc[self.curr_move] = int(uid["args"]["player_id"])
        self.moves["tile_type"].loc[self.curr_move] = int(uid["args"]["type"]) # defines tile class
        self.moves["tile_id"].loc[self.curr_move]   = int(uid["args"]["id"]) # ID specific tile
        self.moves["x"].loc[self.curr_move]         = int(uid["args"]["x"])
        self.moves["y"].loc[self.curr_move]         = int(uid["args"]["y"])
        self.moves["ori"].loc[self.curr_move]       = int(uid["args"]["ori"])

        # if self.curr_move < 71:
        #     self.curr_move += 1

    def process_cantPlay(self, uid):

        ## TODO when this occurs, tile_type is not readily available; udpate in SQL
        ## TODO this may get logged after winPoints

        print("process_cantPlay")
        #print(json.dumps(uid["args"], indent=4))

        move_index = self.moves[self.moves['tile_id'] == int(uid["args"]["tile_id"])].index

        print(f'adding: int(uid["args"]["player_id"])')
        print(self.curr_move)

        self.moves["player_id"].loc[self.curr_move] = int(uid["args"]["player_id"])
        self.moves["tile_id"].loc[self.curr_move] = int(uid["args"]["tile_id"])  # ID specific tile

        print(self.moves.iloc[move_index])
        # if self.curr_move < 71:
        #     self.curr_move += 1

    def process_playPartisan(self, uid):
        print("process_playPartisan")
        #print(json.dumps(uid["args"], indent=4))
        #print(int(uid["args"]["id"]))

        # #which row in self.moves matches tile ID
        move_index = self.moves[self.moves['tile_id'] == int(uid["args"]["id"])].index
        #
        # # Audit player_id and x/y/ori
        #print(f"move_index {move_index}")
        #print(self.moves.loc[move_index])
        self.moves["pos"].iloc[move_index] = int(uid["args"]["pos"])
        #print(self.moves.loc[move_index])

    def process_winPoints(self, uid):

        ## TODO make additive, multiple scores may be added within the turn

        print("process_winPoints")
        # print(json.dumps(uid["args"], indent=4))
        player_id = int(uid["args"]["player_id"])
        # print(player_id)
        # print(int(uid["args"]["score"]))
        # print(self.curr_move)
        # print(self.moves.loc[self.curr_move])
        # print(self.plyr1)
        # print(self.plyr2)

        if int(player_id) == int(self.plyr1):
            # print('updating plyr 1 score')
            self.moves["p1_pts"].iloc[self.curr_move] = int(uid["args"]["score"])
            # if self.moves["p1_pts"].iloc[self.curr_move] is None:
            #     self.moves["p1_pts"].iloc[self.curr_move] = int(uid["args"]["points"])
            # else:
            #     self.moves["p1_pts"].iloc[self.curr_move] = int(uid["args"]["points"]) + self.moves["p1_pts"].iloc[self.curr_move]
        if int(player_id) == int(self.plyr2):
            # print('updating plyr 2 score')
            self.moves["p2_pts"].iloc[self.curr_move] = int(uid["args"]["score"])
            # if self.moves["p2_pts"].iloc[self.curr_move] is None:
            #     self.moves["p2_pts"].iloc[self.curr_move] = int(uid["args"]["points"])
            # else:
            #     self.moves["p2_pts"].iloc[self.curr_move] = int(uid["args"]["points"]) + self.moves["p2_pts"].iloc[
            #         self.curr_move]
            # self.moves["p2_pts"].iloc[self.curr_move] = int(uid["args"]["points"])

        # print(self.moves.loc[self.curr_move])

        pass

    def dump_to_sql(self):
        ## TODO build sql table with complete list of unique id:type assignments
        self.moves.reset_index(inplace=True)
        self.moves = self.moves.rename(columns={'index': 'move_n'})

        tmp = self.moves
        tmp = tmp.where(tmp.notna(), None)

        connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-BN7PJQ0\HOMESQL;DATABASE=carcassonne;Trusted_Connection=yes;')
        cursor = connection.cursor()

        cursor.execute("DELETE FROM Game_Logs WHERE game_id = ?", self.bga_id)

        for index, row in tmp.iterrows():
            cursor.execute("INSERT INTO Game_Logs ([game_id],[move_n],[tile_id],[tile_type],[player_id],[x],[y],[ori],[pos],[p1_pts],[p2_pts]) values(?,?,?,?,?,?,?,?,?,?,?)",
                           self.bga_id,row["move_n"],row["tile_id"],row["tile_type"],row["player_id"],row["x"],row["y"],row["ori"],row["pos"],row["p1_pts"],row["p2_pts"])
        cursor.commit()
        cursor.close()
        connection.close()
