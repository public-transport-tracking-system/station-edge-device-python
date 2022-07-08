import zmq
import logging

class SocketService:
    def __init__(self):
        self.REQUEST_TIMEOUT = 10000
        self.SERVER_ENDPOINT = "tcp://localhost:5555"
        self.context = zmq.Context()
        logging.info("Connecting to server…")
        self.client = self.context.socket(zmq.REQ)
        self.client.connect(self.SERVER_ENDPOINT)
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.connect("tcp://localhost:5556")
        self.publisher.bind("tcp://*:5556")
    
    def configureRequestAfterTimeout(self, request):
        logging.warning("No response from server")
        self.client.setsockopt(zmq.LINGER, 0)
        self.client.close()
        
        logging.info("Reconnecting to server…")
        self.client = self.context.socket(zmq.REQ)
        self.client.connect(self.SERVER_ENDPOINT)
        logging.info("Resending (%s)", request)
        self.sendNewRequest(request)

    def sendNewRequest(self, request):
        self.client.send(request)
    
    def shouldReadValue(self):
        return (self.client.poll(self.REQUEST_TIMEOUT) & zmq.POLLIN) != 0
    
    def retrieveValue(self):
        return self.client.recv()
