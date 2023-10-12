"""Main script. Asynchronously sends the required commands automatically."""

import re
from datetime import datetime
import asyncio
from utils import extract_time_units, retrieve_msg, get_response, get_important_info, send_msg
import os
from dotenv import load_dotenv

# load .env file
load_dotenv()

USERNAME = os.getenv('discord_username')


async def rob_user(username: str, cash_lb_rank=5):  # per day
    # send msg to thief-den '1154367784059412500' to get the 'cash leaderboard and rob the any of the top 10'
    # send get requests to the channel id
    channel_id = 1154367784059412500
    send_msg(channel_id, msg='!lb -cash')
    response = get_response(channel_id)

    # parse response to retrieve important infos(list of author info; 'replier name' and 'bot response' as dictionary)
    important_info = get_important_info(response)
    for info in important_info:
        replied_msg = info['replied_msg']
        initiator_name = info['initiator_name']

        if initiator_name == 'Poglin Cash Leaderboard':  # bot response found?
            # Define the text
            text = replied_msg
            # Use regular expression to find names within square brackets
            names = re.findall(r'\[`(.*?)`\]', text)

            # rob task
            rob_command = f'!rob {names[cash_lb_rank]}'
            await task(username=username, channel_id=channel_id, task_command=rob_command)
            timestamp = datetime.now().strftime("%H:%M")
            print(f'Done with {rob_command} Task. TIME: {timestamp}')

        else:
            print("Author: 'Poglin Cash Leaderboard' not found")
        break


async def task(username: str, channel_id: int, task_command: str):
    """
    Perform the task command(!) and sleep if need be
    :param username: your discord id
    :param channel_id:
    :param task_command:
    :return:
    """
    # send !work to labor-camp channel '1154367183745470464'
    send_msg(channel_id, msg=task_command)

    # retrieve poglin bot response
    msg = retrieve_msg(username, channel_id=channel_id)
    print(f"MESSAGE_CONTENT: {msg}")

    # get sleep time from msg and convert to seconds
    sleep_time = extract_time_units(msg)

    if sleep_time == 0:  # meaning no timestamp in msg. Task went through i.e !work hence the 'deposit all'
        send_msg(channel_id=channel_id, msg='!dep all')

        # to get the  time to sleep, resend task i.e '!work'
        send_msg(channel_id=channel_id, msg=task_command)
        # retrieve poglin bot response for user
        msg = retrieve_msg(username, channel_id=channel_id)
        # get sleep time and convert to seconds
        sleep_time2 = extract_time_units(msg)
        print(f"{task_command} is sleeping for {sleep_time2} seconds")
        await asyncio.sleep(sleep_time2)
        timestamp = datetime.now().strftime("%H:%M")
        print(f'Done with {task_command} Task. TIME: {timestamp}')

    else:
        print(f"{task_command} is sleeping for {sleep_time} seconds!")
        await asyncio.sleep(sleep_time)
        timestamp = datetime.now().strftime("%H:%M")
        print(f'Done with {task_command} Task. TIME: {timestamp}')


# create event loop
loop = asyncio.get_event_loop()


async def main():
    while True:
        # task 1 and 2 are for the labor-camp channel '1154367183745470464'
        task1 = task(username=USERNAME, channel_id=1154367183745470464, task_command='!work')
        task2 = task(username=USERNAME, channel_id=1154367183745470464, task_command='!collect')
        task3 = rob_user(username=USERNAME)
        await asyncio.gather(task1, task2, task3)

if __name__=="__main__":
    loop.run_until_complete(main())
