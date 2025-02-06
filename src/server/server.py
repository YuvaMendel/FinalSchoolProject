import socket
import threading
from time import sleep
class Server:
    def __init__(self):
        
        self.online = False
        self.sock = socket.socket()
        self.sock.bind(("127.0.0.1", 6627))
        self.sock.listen(10)
        self.clients = []
    def activate_server(self):
        self.online = True
        while self.online:
            s, a = self.sock.accept()
            handler = ClientHandler(s)
            self.clients.append(handler)
            handler.start()
            
class ClientHandler(threading.Thread):
    def __init__(self, soc):
        super().__init__()
        self.soc = soc
    def start(self):
        self.business_logic()
    def business_logic(self):
        sleep(20)
        
            
        