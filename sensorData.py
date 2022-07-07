from random import *
import random
from Sensor import Sensor
from Station import Station
from threading import Thread, Event
from queue import Queue
import time


class SensorData:
    def __init__(self):
        self = self
        self.event = Event()
        self.dataToSend = {}
        self.waitTime = 1

    def mock_data(self):
        bus100 = Sensor("100", randint(10, 60))
        bus101 = Sensor("101", randint(10, 60))
        bus102 = Sensor("102", randint(10, 60))
        bus103 = Sensor("103", randint(10, 60))

        route1 = Station("Alexander Platz", randint(10, 15), time.time(), bus100)
        route2 = Station("Friedrichstrasse", randint(10, 15), time.time(), bus101)
        route3 = Station("Hackescher Markt", randint(10, 15), time.time(), bus102)
        route4 = Station("Hauptbahnhof", randint(10, 15), time.time(), bus103)
        items = [route1, route2, route3, route4]
        return random.choice(items)

    def modify_variable(self, queue_out, queue_out2):
        while not self.event.wait(self.waitTime):
            currentRoute = self.mock_data()
            queue_out.put(currentRoute)
            queue_out2.put(currentRoute)
            
    def startDataGeneration(self, queue, queue2):
        t = Thread(target=self.modify_variable, args=(queue, queue2))
        t.start()