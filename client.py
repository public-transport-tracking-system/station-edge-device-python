#
#  Lazy Pirate client
#  Use zmq_poll to do a safe request-reply
#  To run, start lpserver and then randomly kill/restart it
#
#   Author: Daniel Lundin <dln(at)eintr(dot)org>
#
import itertools
import logging
import sys
import zmq
import json
from os import system
from sensorData import SensorData
from queue import Queue
from threading import Thread, Event
import time

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

REQUEST_TIMEOUT = 10000
SERVER_ENDPOINT = "tcp://localhost:5555"

context = zmq.Context()
retries_left = 3

logging.info("Connecting to server…")
client = context.socket(zmq.REQ)
client.connect(SERVER_ENDPOINT)

publisher = context.socket(zmq.PUB)
publisher.connect("tcp://localhost:5556")
publisher.bind("tcp://*:5556")

dataToDisplay = {}
pendingDataToSent = {}
queue1 = Queue()

sensorData = SensorData()
#start data generation and display pending data
sensorData.startDataGeneration(queue1)

def display_information_on_screen(information):
    print('Sending information to the server...')
    print('...')
    print('Arriving at Station: ', information.id, ' Bus: ', information.dataFromSensor.bus_id)
    print('Avg bus speed: ', information.dataFromSensor.avSpeed)
    print("Arriving at: ", information.sentAt)

def displayData():
    _ = system('clear')
    for k, v in pendingDataToSent.items():
        number = v
        print ("{:<8} {:<15}".format(k, number))

def read_data(queue, client, context, pendingDataToSent):
    for sequence in itertools.count():
        time.sleep(1)
        if not queue.empty():
            print('Queue size (%s)', queue.qsize())
            currentRoute = queue.get()
            request = str(currentRoute.dataFromSensor.bus_id).encode()
            pendingDataToSent[currentRoute.dataFromSensor.bus_id] = sequence
            client.send(request)
            display_information_on_screen(currentRoute)

            while True:
                print("wait")
                if (client.poll(REQUEST_TIMEOUT) & zmq.POLLIN) != 0:
                    reply = client.recv()
                    if int(reply) == int(currentRoute.dataFromSensor.bus_id):
                        json_data = json.dumps(currentRoute, default=vars)
                        pendingDataToSent[currentRoute.dataFromSensor.bus_id] = 0
                        publisher.send_string(f"{currentRoute.dataFromSensor.bus_id} {json_data}")
                        logging.info("Server replied OK (%s)", reply)
                        break
                    else:
                        logging.error("Malformed reply from server: %s", reply)
                        continue
                logging.warning("No response from server")
                client.setsockopt(zmq.LINGER, 0)
                client.close()
                
                logging.info("Reconnecting to server…")
                # Create new connection
                client = context.socket(zmq.REQ)
                client.connect(SERVER_ENDPOINT)
                logging.info("Resending (%s)", request)
                client.send(request)

#wait for some data to be generated
time.sleep(6)
t2 = Thread(target=read_data, args=(queue1, client, context, pendingDataToSent))
t2.start()
# for sequence in itertools.count():
#     currentRoute = SensorData.mockData()
#     request = str(currentRoute.dataFromSensor.bus_id).encode()
#     # logging.info("Sending (%s)", request)
#     pendingDataToSent[currentRoute.dataFromSensor.bus_id] = sequence
#     client.send(request)
#     # logging.info(request)
#     # logging.info(sequence)

#     while True:
#         displayData()
#         if (client.poll(REQUEST_TIMEOUT) & zmq.POLLIN) != 0:
#             reply = client.recv()
#             if int(reply) == int(currentRoute.dataFromSensor.bus_id):
#                 # logging.info("Publish")
#                 json_data = json.dumps(currentRoute, default=vars)
#                 # print(json_data)
#                 # obj = json.loads(json_data)
#                 # print(json_data)
#                 pendingDataToSent[currentRoute.dataFromSensor.bus_id] = 0
#                 publisher.send_string(f"{currentRoute.dataFromSensor.bus_id} {json_data}")
#                 # logging.info("Server replied OK (%s)", reply)
#                 break
#             else:
#                 logging.error("Malformed reply from server: %s", reply)
#                 continue

#         retries_left -= 1
#         logging.warning("No response from server")

#         # Socket is confused. Close and remove it.
#         client.setsockopt(zmq.LINGER, 0)
#         client.close()
#         if retries_left == 0:
#             context = zmq.Context()
#             logging.error("Server seems to be offline, abandoning")
#             #sys.exit()

#         logging.info("Reconnecting to server…")
#         # Create new connection
#         client = context.socket(zmq.REQ)
#         client.connect(SERVER_ENDPOINT)
#         logging.info("Resending (%s)", request)
#         client.send(request)
