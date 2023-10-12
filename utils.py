"""
List of functions for the Poglin server web automation project
"""
from dotenv import load_dotenv
import os
from time import sleep
import csv
from pathlib import Path
import requests
import random
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

load_dotenv()

os.makedirs('output', exist_ok=True)

BASE_DIR = Path(os.getenv('poglin_dir'))
OUTPUT_DIR = BASE_DIR / 'output'

HEADERS = {
    'authorization': os.getenv('authorization'),
    'user-agent': os.getenv('user-agent'),
    'cookie': os.getenv('cookie')
}


# Selenium was the initial approach. The top 3 selenium functions below have no use for now.
# daily tasks
def work(driver, action):
    text_box = driver.find_element(By.XPATH, '//div[@role="textbox"]')
    # !work, should sleep every 6hours
    action.move_to_element(text_box).click().send_keys('!work', Keys.ENTER).perform()
    action.move_to_element(text_box).click().send_keys('!dep all', Keys.ENTER).perform()


def collect_income(driver, action):

    text_box = driver.find_element(By.XPATH, '//div[@role="textbox"]')
    # !collect_income, should sleep every 24 hours
    action.move_to_element(text_box).click().send_keys('!collect_income', Keys.ENTER).perform()
    action.move_to_element(text_box).click().send_keys('!dep all', Keys.ENTER).perform()


def login_discord(driver, action, email, password):
    # Perform a GET request to a webpage
    driver.get("https://discord.com/login")

    email_elem = driver.find_element(By.XPATH, '//input[@name="email"]')
    password_elem = driver.find_element(By.XPATH, '//input[@name="password"]')

    action.move_to_element(email_elem).click().send_keys(str(email)).perform()
    action.move_to_element(password_elem).click().send_keys(str(password), Keys.ENTER).perform()
    sleep(60)


def write_log(row_data: list, mode='a'):
    """
    writes to csv file in output directory

    :param row_data: the row content information
    :param mode: whether append 'a' or write 'w' mode of the csv file object
    :return: writes to the specified csv file
    """

    file_name = 'poglin_log.csv'

    with open(OUTPUT_DIR / file_name, mode, newline='', encoding='utf8') as f_obj:
        writer = csv.writer(f_obj)
        writer.writerow(row_data)


def send_msg(channel_id: int, msg: str):
    # generate 'nonce'
    random_number = random.randint(1160000000000000000, 1170000000000000000)

    url = f'https://discord.com/api/v9/channels/{str(channel_id)}/messages'
    payload = {'mobile_network_type': "unknown", 'content': f"{msg}", 'nonce': str(random_number),
               'tts': 'false', 'flags': 0}

    r = requests.post(url, json=payload, headers=HEADERS)

    if r.status_code == 200:
        print(f"{msg} sent!")
    else:
        print(f"ERROR sending message STATUS CODE: {r.status_code}")


def get_response(channel_id, retmax=20):
    """
    make GET request to channel URL and return reponse
    :param channel_id:
    :param retmax: max returned chats
    :return:
    """

    # retrieve channel msg
    msg_url = f'https://discord.com/api/v9/channels/{channel_id}/messages?limit={retmax}'
    r = requests.get(msg_url, headers=HEADERS)

    if r.status_code == 200:
        return r.json()
    else:
        print(f"ERROR!. status code: {r.status_code}")


def retrieve_msg(username, channel_id):

    """
    retrieves poglin bot response to your commands i.e '!work'
    :param username:
    :param channel_id:
    :return:
    """

    # send get requests to the channel id
    response = get_response(channel_id)

    # parse response to retrieve important info(list)
    important_info = get_important_info(response)

    for info in important_info:
        replied_msg = info['replied_msg']
        initiator_name = info['initiator_name']

        if initiator_name == str(username):
            return replied_msg
        break


def get_important_info(json_response):
    """
    Parses json response and get the required info
    :param json_response:
    :return: list of important info. i.e 'initiator_name', 'replied_msg' of members as a dictionary
    """
    important_info = []
    for item in json_response:
        for embed in item.get('embeds', []):
            embed_data = {
                'replied_msg': embed.get('description', ''),
                'initiator_name': embed['author']['name'],
            }
            important_info.append(embed_data)

    return important_info


def extract_time_units(text):
    text = str(text)
    hours = 0
    minutes = 0
    seconds = 0

    # Regular expressions to match hours, minutes, and seconds
    hour_pattern = r'(\d+)\s*hour'
    minute_pattern = r'(\d+)\s*minute'
    second_pattern = r'(\d+)\s*second'

    # Match and extract hours
    hour_match = re.search(hour_pattern, text)
    if hour_match:
        hours = int(hour_match.group(1))

    # Match and extract minutes
    minute_match = re.search(minute_pattern, text)
    if minute_match:
        minutes = int(minute_match.group(1))

    # Match and extract seconds
    second_match = re.search(second_pattern, text)
    if second_match:
        seconds = int(second_match.group(1))

    total_seconds = (hours * 3600) + (minutes * 60) + seconds
    return total_seconds
