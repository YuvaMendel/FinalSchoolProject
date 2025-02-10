import socket

import base64

import threading

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import app.protocol as protocol


class Server:
    def __init__(self):
        self.rsa_key = RSA.generate(2048)
        self.online = False
        self.sock = socket.socket()
        self.sock.bind(('127.0.0.1', protocol.PORT))
        self.sock.listen(10)
        self.clients = []
        
    def activate_server(self):
        self.online = True
        while self.online:
            try:
                s, a = self.sock.accept()
                handler = ClientHandler(s, self.rsa_key)
                self.clients.append(handler)
                handler.start()
            except socket.error() as e:
                print(f"Socket error: {e}")
                
                
class ClientHandler(threading.Thread):
    def __init__(self, soc, rsa_key):
        super().__init__()
        self.crypto = ServerCrypto(rsa_key)
        self.soc = soc
    
    def run(self):
        self.handshake()
        self.business_logic()
    def recv_with_size(self):
        return protocol.recv_by_size(self.soc)
        
    def send_with_size(self, msg):
        protocol.send_by_size(self.soc, msg)
    
    def handshake(self):
        self.send_with_size(self.crypto.get_public())
        self.crypto.decrypt_aes_key(base64.b64decode(self.recv_with_size()), base64.b64decode(self.recv_with_size())) # Get aes key and aes iv (for cbc) and give them to crypto object)
        self.send_with_size(protocol.ACK_START)
    def send(self):
        pass
    def recv(self):
        pass
        
    def business_logic(self):
        pass
        
        
class ServerCrypto:
    def __init__(self, rsa_key):
        self.rsa_key = rsa_key
        self.aes_key = None
        self.aes_iv = None
        
    def get_public(self):
        return self.rsa_key.publickey().export_key()
        
    def decrypt_aes_key(self, aes_key, aes_iv):
        decipher_rsa = PKCS1_OAEP.new(self.rsa_key)
        self.aes_key = decipher_rsa.decrypt(aes_key)
        self.aes_iv = decipher_rsa.decrypt(aes_iv)
