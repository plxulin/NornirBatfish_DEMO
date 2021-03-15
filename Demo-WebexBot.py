"""A simple bot script, built on Flask.
"""
from builtins import *
from flask import Flask, request
import requests
from webexteamssdk import WebexTeamsAPI, Webhook

from nornir import InitNornir
from nornir.core import configuration
from nornir.plugins.runners import ThreadedRunner, SerialRunner
from nornir.core.plugins.inventory import InventoryPluginRegister
import logging
from nornir_utils.plugins.functions import print_result
from nornir_utils.plugins.tasks.files import write_file
from nornir_napalm.plugins.tasks import *
from nornir_netmiko.tasks import *
from nornir_jinja2.plugins.tasks import *
from nornir.core.filter import F
from mytasks import *

import _thread
import time

InventoryPluginRegister.register("SerialRunner", SerialRunner)
InventoryPluginRegister.register("ThreadedRunner", ThreadedRunner)

nr = InitNornir(
    config_file='config.yaml',
    dry_run=False)
nr = nr.filter(F(groups__contains="IOS"))
# Module constants
CAT_FACTS_URL = 'https://catfact.ninja/fact'
# Initialize the environment
# Create the web application instance
flask_app = Flask(__name__)
# Create the Webex Teams API connection object
api = WebexTeamsAPI(access_token = "OGMzMjEyYWItNzU4NC00ODQ0LTljYzYtMGVlYzUxYzgzMTNmYWE4NzA5MDEtNzkz_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f"
)


# Helper functions
def get_catfact() -> None:
    """Get a cat fact from catfact.ninja and return it as a string.

    Functions for Soundhound, Google, IBM Watson, or other APIs can be added
    to create the desired functionality into this bot.

    """
    response = requests.get(CAT_FACTS_URL, verify=False)
    response.raise_for_status()
    json_data = response.json()
    return json_data['fact']

# Nornir functions
def get_connection_result() -> str:
    result = nr.run(
        task=connection_check
        )
    r = ''
    for key,value in result.items():
        r += f'{ key }: { not value.failed }\n'
    return r

# Thread
def get_connection_result_loop(delay: int) -> str:
    while(1):
        time.sleep(delay)
        room_id = "Y2lzY29zcGFyazovL3VzL1JPT00vNzkwNGRiYjAtN2E2MS0xMWViLWI3ZDItYzEwNzQ2MTgyMmU3"
        result = nr.run(
            task=connection_check,
            on_failed=True,
            )
        r = ''
        if result.failed:
            for host in result.failed_hosts.keys():
                r += f'{ host } lost connection'
            api.messages.create(room_id, text=r)


# Core bot functionality
@flask_app.route('/', methods=['GET', 'POST'])
def webex_teams_webhook_events():
    """Processes incoming requests to the '/events' URI."""
    if request.method == 'GET':
        return ("""<!DOCTYPE html>
                   <html lang="en">
                       <head>
                           <meta charset="UTF-8">
                           <title>Webex Teams Bot served via Flask</title>
                       </head>
                   <body>
                   <p>
                   <strong>Your Flask web server is up and running!</strong>
                   </p>
                   <p>
                   Here is a nice Cat Fact for you:
                   </p>
                   <blockquote>{}</blockquote>
                   </body>
                   </html>
                """.format(get_catfact()))
    elif request.method == 'POST':
        """Respond to inbound webhook JSON HTTP POST from Webex Teams."""

        # Get the POST data sent from Webex Teams
        json_data = request.json
        print("\n")
        print("WEBHOOK POST RECEIVED:")
        print(json_data)
        print("\n")

        # Create a Webhook object from the JSON data
        webhook_obj = Webhook(json_data)
        # Get the room details
        room = api.rooms.get(webhook_obj.data.roomId)
        # Get the message details
        message = api.messages.get(webhook_obj.data.id)
        # Get the sender's details
        person = api.people.get(message.personId)

        print("NEW MESSAGE IN ROOM '{}'".format(room.title))
        print("FROM '{}'".format(person.displayName))
        print("MESSAGE '{}'\n".format(message.text))

        # This is a VERY IMPORTANT loop prevention control step.
        # If you respond to all messages...  You will respond to the messages
        # that the bot posts and thereby create a loop condition.
        me = api.people.me()
        if message.personId == me.id:
            # Message was sent by me (bot); do not respond.
            return 'OK'

        else:
            # Message was sent by someone else; parse message and respond.
            if "/CAT" in message.text:
                print("FOUND '/CAT'")
                # Get a cat fact
                cat_fact = get_catfact()
                print("SENDING CAT FACT '{}'".format(cat_fact))
                # Post the fact to the room where the request was received
                api.messages.create(room.id, text=cat_fact)
                
            elif "hello" in message.text:
                api.messages.create(room.id, text=f'Hello {person.displayName}! ')
                
            elif "check" in message.text:
                api.messages.create(room.id, text=str(get_connection_result()))
            
            else:
                api.messages.create(room.id, text="Sorry I don't understand")
            return 'OK'



if __name__ == '__main__':
    # Start thread
    _thread.start_new_thread( get_connection_result_loop, (5,) )
    # Start the Flask web server
    flask_app.run(host='0.0.0.0', port=8080)
