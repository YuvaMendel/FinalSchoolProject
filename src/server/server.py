import socket
import threading
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
            
class ClientHandler(threading):
# need to finish this class
    def __init__(self, soc):
        self.soc = soc
            
        