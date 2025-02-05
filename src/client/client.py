import socket
import threading
import queue
class Client(threading.Thread):
    def __init__(self, dest_ip, dest_port):
        super().__init__()
        self.dest = (dest_ip, dest_port)
        self.sock = None
        self.request_queue = queue.Queue()
    
    def connect(self):
        self.sock = socket.socket()
        self.sock.connect(self.dest)
        print("connected")
    def run(self):
        self.connect()
        self.handshake()
        self.activate()
    def handshake(self):
        pass
    def activate(self):
        pass
    def send_file(self, file_path):
        pass