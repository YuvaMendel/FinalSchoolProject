import socket
import threading
from Crypto.PublicKey import RSA
class Server:
    def __init__(self):
        self.rsa_key = RSA.generate(2048)
        self.online = False
        self.sock = socket.socket()
        self.sock.bind(("127.0.0.1", 6627))
        self.sock.listen(10)
        self.clients = []
    def activate_server(self):
        self.online = True
        while self.online:
            s, a = self.sock.accept()
            handler = ClientHandler(s, self.rsa_key)
            self.clients.append(handler)
            handler.start()
            
class ClientHandler(threading.Thread):
    def __init__(self, soc, rsa_key):
        super().__init__()
        self.crypto = ServerCrypto(rsa_key)
        self.soc = soc
    
    def start(self):
        self.business_logic()
        self.handshake()
    def handshake(self):
        pass
    def business_logic(self):
        pass
        
            
class ServerCrypto:
    def __init__(self, rsa_key):
        self.private_key = rsa_key.export_key()
        self.public_key = rsa_key.publickey.export_key()