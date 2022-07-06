from random import *
import random
import time
from Sensor import Sensor
from Station import Station
from threading import Thread, Event
from queue import Queue
import itertools
import json
import threading
from os import system
import sys


class SensorData:
    def __init__(self):
        self = self
        self.event = Event()
        self.dataToSend = {}

    def mockData(self):
        bus100 = Sensor("100", randint(10, 60))
        bus101 = Sensor("101", randint(10, 60))
        bus102 = Sensor("102", randint(10, 60))
        bus103 = Sensor("103", randint(10, 60))

        route1 = Station("100", randint(10, 15), int(time.time()), bus100)
        route2 = Station("101", randint(10, 15), int(time.time()), bus101)
        route3 = Station("102", randint(10, 15), int(time.time()), bus102)
        route4 = Station("103", randint(10, 15), int(time.time()), bus103)
        items = [route1, route2, route3, route4]
        return random.choice(items)

    def modify_variable(self, queue_out):
        while not self.event.wait(2):
            currentRoute = self.mockData()
            queue_out.put(currentRoute)
        
    def displayData(self, queue):
        for sequence in itertools.count():
            data = queue.queue[0]
            if data.dataFromSensor.routeId in self.dataToSend:
                count = self.dataToSend.get(data.dataFromSensor.routeId)
                count += 1
                self.dataToSend[data.dataFromSensor.routeId] = count
            else:
                self.dataToSend[data.dataFromSensor.routeId] = 1
            for k, v in self.dataToSend.items():
                number = v
                print ("{:<8} {:<15}".format(k, number))
            

    def startDataGeneration(self, queue):
        t = threading.Timer(1, self.modify_variable, args=(queue,))
        t.start()
        t2 = threading.Timer(1, self.displayData, args=(queue,))
        t2.start()