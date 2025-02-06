import socket
import threading
import queue
class Client(threading.Thread):
    def __init__(self, dest_ip, dest_port):
        super().__init__()
        self.dest = (dest_ip, dest_port)
        self.sock = socket.socket()
        self.request_queue = queue.Queue()
        self.connected = False
    
    def connect(self):
        try:
            self.sock.connect(self.dest)
            self.connected = True
        except socket.error as e:
            self.connected = False
            
    def run(self):
        self.connect()
        self.handshake()
        self.activate()
    def handshake(self):
        pass
    def activate(self):
        while self.connected:
            task = self.request_queue.get()
            if task is None:
                break
                
            
    def send_file(self, file_path):
        pass
    def is_connected(self):
        return self.connected
    def close(self):
        
        self.connected = False
        self.request_queue.put(None)
        self.sock.close()