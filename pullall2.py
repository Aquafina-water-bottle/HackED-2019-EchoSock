import os
import time
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
    "A": "?",
    "C": "?",
    "H": "?"
    }

# (esp_id, cycle_id) : last time they were used
cycle_ids = {}

class Device(NamedTuple):
    # esp board ID: uppercase A-Z
    esp_id: str

    # cycle id: uppercase A-Z
    cycle_id: str

    # 4 chars
    mac_address: str

class Board(NamedTuple):
    # esp board ID: uppercase A-Z
    esp_id: str
    number: int

def decode_message(message: str):
    esp_id = message[0]
    cycle_id = message[1]
    addresses_str = message[2:]
    for i in range(0, len(addresses_str), 4):
        address = addresses_str[i:i+4]
        if address == "0000":
            break

        #pylint: disable=too-many-function-args
        device = Device(esp_id, cycle_id, address)
        devices.add(device)
        #print("esp id:", esp_id, "cycle id:", cycle_id, "addr:", addresses_str[i:i+4])

        cycle_ids[(esp_id, cycle_id)] = time.time()


def decode_message2(message: str):
    """
    {esp_id}{#}
    """
    try:
        esp_id = message[0]
        number = int(message[1:])
        boards[esp_id] = number
        print(datetime.datetime.now(), "%3s %3s %3s" % tuple(boards[c] for c in 'CHA'))
    except Exception:
        print("idk", repr(message))

def check_ids():
    for key in cycle_ids:
        if time.time() - cycle_ids[key] > 10:
            print(key)
            for device in devices:
                if (device.esp_id, device.cycle_id) == key:
                    print(device)
                devices.remove(device)
            cycle_ids.pop(key)



def main():
    subscriber = pubsub_v1.SubscriberClient()
    # The `subscription_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/subscriptions/{subscription_name}`
    subscription_path = subscriber.subscription_path( # pylint: disable=no-member
        project_id, subscription_name)

    def callback(message):
        message = message.data.decode("utf-8")
        decode_message(message)
        #print(datetime.datetime.now(), message.data.decode("utf-8"))
        message.ack()
        check_ids()

    subscriber.subscribe(subscription_path, callback=callback)

    # The subscriber is non-blocking. We must keep the main thread from
    # exiting to allow it to process messages asynchronously in the background.
    print('Listening for messages on {}'.format(subscription_path))

    while True:
        time.sleep(10)

def main2():
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
        time.sleep(10)


def test():
    decode_message("AB12343456abcd0000lolo")
    print(devices)
    print(cycle_ids)

def test2():
    decode_message2("A24")
    decode_message2("C23")
    decode_message2("H22")
    decode_message2("A21")
    decode_message2("H20")


if __name__ == "__main__":
    #test2()
    #main()
    main2()


