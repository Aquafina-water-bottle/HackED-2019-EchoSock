import os
import time
import logging
import argparse
import datetime
from typing import NamedTuple

from google.cloud import pubsub_v1

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/austin/pgc/prog/Events/HackED-Jan-2019/temp/auth.json"

project_id = "steady-mason-229223"
subscription_name = "iot-sample-sub"



# set of Device
devices = set()

# esp_id: number
boards = {
    "C": "?",
    "H": "?",
    "A": "?",
    }

class Board(NamedTuple):
    # esp board ID: uppercase A-Z
    esp_id: str
    number: int
    recorded_time: int


def reset_messages():
    for key in boards:
        if time.time() - boards[key].recorded_time > 10:
            logging.info("reset " + key)
            boards[key] = "?"

def decode_message2(message: str):
    """
    {esp_id}{#}
    """
    #try:
    esp_id = message[0]
    number = int(message[1:])
    boards[esp_id] = Board(esp_id, number, time.time())

    try:
        formatted_strs = []
        for key in boards:
            if boards[key] == "?":
                formatted_strs.append(" ? ")
            else:
                formatted_strs.append("%3s" % boards[key].number)

        print(datetime.datetime.now(), ":",  " ".join(formatted_strs))
        #print(datetime.datetime.now(), " ".join(("%3s" % boards[c].number) for c in 'CHA'))

        logging.info("success: " + message)

        # checks if any has to be reset to "?"
        reset_messages()

    except Exception:
        logging.info("error: " + message)



def parse_args():
    # Usage: main.py fileName [output_path] [-d, --debug]
    parser = argparse.ArgumentParser()

    # debug
    parser.add_argument("-d", "--debug", action="store_true")

    args = parser.parse_args()
    if args.debug:
        logger = logging.getLogger()
        logger.setLevel("INFO")



def main2():
    parse_args()

    subscriber = pubsub_v1.SubscriberClient()
    # The `subscription_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/subscriptions/{subscription_name}`
    subscription_path = subscriber.subscription_path( # pylint: disable=no-member
        project_id, subscription_name)

    def callback(message):
        data = message.data.decode("utf-8")
        decode_message2(data)
        #print(datetime.datetime.now(), message.data.decode("utf-8"))
        message.ack()

    subscriber.subscribe(subscription_path, callback=callback)

    # The subscriber is non-blocking. We must keep the main thread from
    # exiting to allow it to process messages asynchronously in the background.
    print('Listening for messages on {}'.format(subscription_path))

    while True:
        time.sleep(5)
        reset_messages()


def test2():
    decode_message2("A24")
    decode_message2("C23")
    decode_message2("H22")
    decode_message2("A21")
    decode_message2("H20")


if __name__ == "__main__":
    main2()


