#launch_bga_crawler.py
"""
import launch_bga_crawler
(driver, wait, EC, By, Keys) = launch_bga_crawler.login_to_bga()
"""

from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

chromedriver_path = r"..\chromedriver_win32\chromedriver.exe"

def login_to_bga():

    login_link = 'https://en.boardgamearena.com/account'

    # create chromedriver
    try:
        driver = webdriver.Chrome(chromedriver_path)
    except SessionNotCreatedException as error_message:
        print(f"{error_message}")
        print(f"Use the following link to update chromedriver32 located in: {chromedriver_path}")
        print(f"https://chromedriver.storage.googleapis.com/index.html")
    else:
        driver.get(login_link)
        wait = WebDriverWait(driver, 10)

        wait.until(EC.visibility_of_element_located((By.ID, "username_input")))
        username = driver.find_element_by_id("username_input")
        username.send_keys("")

        wait.until(EC.visibility_of_element_located((By.ID, "password_input")))
        password = driver.find_element_by_id("password_input")
        password.send_keys("")

        wait.until(EC.visibility_of_element_located((By.ID, "submit_login_button")))
        driver.find_element_by_id("submit_login_button").click()

        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "bga-main-player-avatar")))
        print(f"Driver creation successful")

        return(driver, wait, EC, By, Keys)


# (driver, wait, EC, By, Keys) = login_to_bga()
# elms = driver.find_elements_by_class_name('stats_by_opp')
# for elm in elms:
#    print(elm.text)





