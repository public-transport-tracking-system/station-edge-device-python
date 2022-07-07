import itertools
import logging
import sys
import json
from os import system
from sensorData import SensorData
from utils.RepeatTimer import RepeatTimer
from utils.SocketService import SocketService
from queue import Queue
from threading import Thread
import time

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

logging.info("Connecting to server…")
sockService = SocketService()

pendingDataToSent = {}
dataGenerationQueue = Queue()
dataDisplayQueue = Queue()

sensorData = SensorData()
#start data generation and display pending data
sensorData.startDataGeneration(dataGenerationQueue, dataDisplayQueue)

def display_information_on_screen(information):
    print('Sending information to the server...')
    print('...')
    print('Arriving at Station: ', information.id, ' Bus: ', information.dataFromSensor.bus_id)
    print('Avg bus speed: ', information.dataFromSensor.avSpeed)
    print("Arriving at: ", information.sentAt)

def displayData(queue, pendingDataToSent):
    if not queue.empty():
        data = queue.get()
        if data.dataFromSensor.bus_id in pendingDataToSent:
            pending = pendingDataToSent.get(data.dataFromSensor.bus_id)
            pending.append(data)
            pendingDataToSent[data.dataFromSensor.bus_id] = pending
        else:
            pendingDataToSent[data.dataFromSensor.bus_id] = [data]
    for k, v in pendingDataToSent.items():
        number = len(v)
        print ("{:<8} {:<15}".format(k, number))

timer = RepeatTimer(1,displayData, (dataDisplayQueue,pendingDataToSent))  
timer.start()

def read_data(queue, pendingDataToSent):
    for sequence in itertools.count():
        time.sleep(1)
        if not queue.empty():
            currentRoute = queue.get()
            request = str(currentRoute.dataFromSensor.bus_id).encode()
            sockService.sendNewRequest(request)
            #display_information_on_screen(currentRoute)
            while True:
                if (sockService.shouldReadValue()) != 0:
                    reply = sockService.retrieveValue()
                    if int(reply) == int(currentRoute.dataFromSensor.bus_id):
                        allInfoForRoute = pendingDataToSent[currentRoute.dataFromSensor.bus_id]
                        pendingDataToSent[currentRoute.dataFromSensor.bus_id] = []
                        json_data = json.dumps(allInfoForRoute, default=vars)
                        #TODO: don't access the publisher directly
                        sockService.publisher.send_string(f"{currentRoute.dataFromSensor.bus_id} {json_data}")
                        logging.info("Server replied OK (%s)", reply)
                        break
                    else:
                        logging.error("Malformed reply from server: %s", reply)
                        continue
                sockService.configureRequestAfterTimeout(request)
                client = sockService.client

#wait for some data to be generated
time.sleep(6)
t2 = Thread(target=read_data, args=(dataGenerationQueue, pendingDataToSent))
t2.start()

time.sleep(10)
sensorData.event.set()