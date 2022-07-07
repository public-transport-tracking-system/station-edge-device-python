import zmq

class SocketService:
    def __init__(self):
        REQUEST_TIMEOUT = 10000
        SERVER_ENDPOINT = "tcp://localhost:5555"
        context = zmq.Context()
        logging.info("Connecting to server…")
        client = context.socket(zmq.REQ)
        client.connect(SERVER_ENDPOINT)
        publisher = context.socket(zmq.PUB)
        publisher.connect("tcp://localhost:5556")
        publisher.bind("tcp://*:5556")