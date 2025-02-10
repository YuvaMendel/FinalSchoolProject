import socket

import base64

import threading
import queue

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import app.protocol as protocol

class Client(threading.Thread):
    def __init__(self, dest_ip, dest_port):
        super().__init__()
        self.dest = (dest_ip, dest_port)
        self.sock = socket.socket()
        self.request_queue = queue.Queue()
        self.connected = False
        self.crypto = ClientCrypto()
    
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
    def recv_with_size(self):
        return protocol.recv_by_size(self.sock)
        
    def send_with_size(self, msg):
        protocol.send_by_size(self.sock, msg)
        
    def handshake(self):
        rsa_public = self.recv_with_size()
        encrypted_aes_key, encrypted_aes_iv = self.crypto.encrypted_key(rsa_public)
        self.send_with_size(base64.b64encode(encrypted_aes_key))
        self.send_with_size(base64.b64encode(encrypted_aes_iv))
        return_message = self.recv_with_size()
        print(return_message)
        
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


class ClientCrypto:
    BLOCK_SIZE = 32
    def __init__(self):
        AES.block_size = self.BLOCK_SIZE
        self.aes_key = os.urandom(AES.block_size)
        self.aes_iv = os.urandom(AES.block_size)
    def encrypted_key(self, rsa_key):
        rsa_key = RSA.import_key(rsa_key)
        cipher_rsa = PKCS1_OAEP.new(rsa_key)
        encrypted_aes_key = cipher_rsa.encrypt(self.aes_key)
        encrypted_aes_iv = cipher_rsa.encrypt(self.aes_iv)
        return encrypted_aes_key, encrypted_aes_iv
