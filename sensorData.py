from random import *
import random
import time
from Sensor import Sensor
from Station import Station

class SensorData:
    def mockData():
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
        