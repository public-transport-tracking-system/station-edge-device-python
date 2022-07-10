import itertools
import logging
import sys
import json
import os
from sensorData import SensorData
from utils.RepeatTimer import RepeatTimer
from utils.SocketService import SocketService
from queue import Queue
from threading import Thread
import time

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
sockService = SocketService()

pendingDataToSent = {}
lastUpdatedRoute = {}
dataGenerationQueue = Queue()
dataDisplayQueue = Queue()

sensorData = SensorData()
#start data generation and display pending data
sensorData.startDataGeneration(dataGenerationQueue, dataDisplayQueue)

def displayData(queue, pendingDataToSent):
    os.system('clear')
    if not queue.empty():
        data = queue.get()
        if data.dataFromSensor.bus_id in pendingDataToSent:
            pending = pendingDataToSent.get(data.dataFromSensor.bus_id)
            pending.append(data)
            pendingDataToSent[data.dataFromSensor.bus_id] = pending
        else:
            pendingDataToSent[data.dataFromSensor.bus_id] = [data]
    for key, value in pendingDataToSent.items():
        number = len(value)
        if key in lastUpdatedRoute:
            lastestKnowUpdate = lastUpdatedRoute[key]
            diff_seconds = int(time.time() - lastestKnowUpdate)
        else:
            lastestKnowUpdate = 0
            diff_seconds = -1
        
        if diff_seconds == -1:
            print ("{:<8} {:<15} {:<15}".format(key, number, "pendingToSend"))
        else:
            print ("{:<8} {:<15} {:<15}".format(key, number, f"{diff_seconds} seconds ago"))

timer = RepeatTimer(1,displayData, (dataDisplayQueue,pendingDataToSent))  
timer.start()

def read_data(queue, pendingDataToSent):
    for sequence in itertools.count():
        time.sleep(1)
        if not queue.empty():
            currentRoute = queue.get()
            request = str(f"{currentRoute.id}/{currentRoute.dataFromSensor.bus_id}")
            sockService.sendNewRequest(request)
            lastUpdatedRoute[currentRoute.dataFromSensor.bus_id] = int(time.time())
            while True:
                if (sockService.shouldReadValue()) != 0:
                    reply = sockService.retrieveValue()
                    if int(reply) == int(currentRoute.dataFromSensor.bus_id):
                        allInfoForRoute = pendingDataToSent[currentRoute.dataFromSensor.bus_id]
                        pendingDataToSent[currentRoute.dataFromSensor.bus_id] = []
                        json_data = json.dumps(allInfoForRoute, default=vars)
                        #TODO: don't access the publisher directly
                        sockService.publisher.send_string(f"{currentRoute.id}/{json_data}")
                        logging.info("Server replied OK (%s)", reply)
                        break
                    else:
                        logging.error("Malformed reply from server: %s", reply)
                        continue
                sockService.configureRequestAfterTimeout(request)

#wait for some data to be generated
t2 = Thread(target=read_data, args=(dataGenerationQueue, pendingDataToSent))
t2.start()

def subscriber_data(pendingDataToSent):
    for sequence in itertools.count():
        station_id, bus_id, updatedTime = sockService.subscriber.recv_string().split("/")
        lastUpdatedRoute[bus_id] = int(updatedTime)

t3 = Thread(target=subscriber_data, args=(pendingDataToSent,))
t3.start()

#time.sleep(15)
## stop generating data after 15 seconds
#sensorData.event.set()