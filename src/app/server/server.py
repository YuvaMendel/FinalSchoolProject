import socket


import threading

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import app.protocol as protocol

__auther__ = 'Yuval Mendel'

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
                s, _ = self.sock.accept()
                handler = ClientHandler(s, self.rsa_key)
                self.clients.append(handler)
                handler.start()
            except socket.error as e:
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
        self.crypto.decrypt_aes_key(self.recv_with_size(), self.recv_with_size()) # Get aes key and aes iv (for cbc) and give them to crypto object)
        self.send(protocol.ACK_START)
    def send(self, *msg):
        msg = self.format_message(msg)
        self.send_with_size(self.crypto.encrypt(msg))
    def recv(self):
        return self.unformat_message(self.recv_with_size())
        
    def format_message(self, args):
        return b"".join(args)
    def unformat_message(self, msg):
        return [msg]
        
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
        self.aes_iv = aes_iv
    def encrypt(self, plaintext):
        
        if not self.aes_key or not self.aes_iv:
            raise ValueError("AES key and IV must be set before encryption.")

        cipher = AES.new(self.aes_key, AES.MODE_CBC, self.aes_iv)
        padded_data = pad(plaintext, AES.block_size)
        ciphertext = cipher.encrypt(padded_data)

        return ciphertext

    def decrypt(self, encrypted_text):
        if not self.aes_key or not self.aes_iv:
            raise ValueError("AES key and IV must be set before decryption.")

        cipher = AES.new(self.aes_key, AES.MODE_CBC, self.aes_iv)
        decrypted_padded = cipher.decrypt(encrypted_text)
        plaintext = unpad(decrypted_padded, AES.block_size)

        return plaintext.decode()
