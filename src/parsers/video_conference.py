from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

"""
This function uses selenium library for parsing data
It generates link for video web conference in SberJazz web app
SberJazz doesn't require registration and payment
"""


def generate_link() -> str:
    # use a virtual display (headless mode)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1420,1080')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    # web driver installation
    driver = webdriver.Chrome(
        service=ChromeService(executable_path=ChromeDriverManager().install()),
        options=chrome_options
    )
    # go to the SberJazz web page
    driver.get('https://jazz.sber.ru/')
    # take time to load the web page
    driver.implicitly_wait(5)
    # search and click the button "arrange meeting"
    arrange_meeting = driver.find_element(
        by=By.XPATH,
        value="//*[@id='root']/div[1]/div[1]/div/div[1]/div[2]/button[1]"
    )
    arrange_meeting.click()
    # search and click the button "confirm meeting", leaving the conference name as default
    confirm_meeting = driver.find_element(
        by=By.XPATH,
        value="//*[@id='plasma-modals-root']/div/div[2]/div[2]/div/div/form/button"
    )
    confirm_meeting.click()
    # search and get the url of created conference room
    input_field = driver.find_element(
        by=By.XPATH,
        value="//*[@id='plasma-modals-root']/div/div[2]/div[2]/div/div/div[3]/div/input"
    )
    link = input_field.get_attribute('value')

    return link
