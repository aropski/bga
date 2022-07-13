# PROD: utd for wtcoc 2022

# BGAs ID is used to jump to BGA player page for pulling game/opponent details

import pyodbc
import launch_bga_crawler

BGA_SEARCH_PAGE = "https://boardgamearena.com/community"

(driver, wait, EC, By, Keys) = launch_bga_crawler.login_to_bga()

# get list of names from Players Table that do not have an ID
connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-BN7PJQ0\HOMESQL;DATABASE=carcassonne;Trusted_Connection=yes;')
cursor = connection.cursor()
#cursor.execute("select distinct aaa.name from WTCOC_Rosters as aaa left join Players as bbb on aaa.name = bbb.name where bbb.id is NULL")
cursor.execute("SELECT name FROM Players WHERE id IS NULL")
rows = cursor.fetchall()
print(len(rows))
cursor.close()
connection.close()


# scrap if from BGA player page, insert into SQL
connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-BN7PJQ0\HOMESQL;DATABASE=carcassonne;Trusted_Connection=yes;')

for name in rows:

    ## TODO understand why SQL query returns empty element
    plyr_name = name[0]

    # navigate to search page
    driver.get(BGA_SEARCH_PAGE)
    wait.until(EC.visibility_of_element_located((By.ID, "findplayer")))

    # enter Player name to search for
    username = driver.find_element_by_id("findplayer")
    username.send_keys(plyr_name)
    username.send_keys(Keys.RETURN)

    # pull ID from URL
    wait.until(EC.visibility_of_element_located((By.ID, "startchat")))
    cur_url = driver.current_url
    bga_id = int(''.join(filter(str.isdigit, cur_url)))

    # insert into Player table
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Players (name,id) values(?,?)", plyr_name, bga_id)
    cursor.commit()
    cursor.close()

connection.close()


