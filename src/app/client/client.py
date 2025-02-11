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
        encrypted_aes_key, aes_iv = self.crypto.encrypted_key_iv(rsa_public)
        self.send_with_size(base64.b64encode(encrypted_aes_key))
        self.send_with_size(base64.b64encode(aes_iv))
        return_message = self.recv()
        print(return_message[0])
        
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
    
    def send(self, *msg):
        msg = self.format_message(msg)
        self.send_with_size(self.crypto.encrypt(msg))
    def recv(self):
        return self.unformat_message(self.crypto.decrypt(self.recv_with_size()))
        
    def format_message(self, args):
        return "".args
    def unformat_message(self, msg):
        return [msg]


class ClientCrypto:
    def __init__(self):
        self.aes_key = os.urandom(32)
        self.aes_iv = os.urandom(16)
    def encrypted_key_iv(self, rsa_key):
        rsa_key = RSA.import_key(rsa_key)
        cipher_rsa = PKCS1_OAEP.new(rsa_key)
        encrypted_aes_key = cipher_rsa.encrypt(self.aes_key)
        aes_iv = self.aes_iv
        return encrypted_aes_key, aes_iv
    
    def encrypt(self, plaintext):

        cipher = AES.new(self.aes_key, AES.MODE_CBC, self.aes_iv)
        padded_data = pad(plaintext.encode(), AES.block_size)
        ciphertext = cipher.encrypt(padded_data)

        return ciphertext

    def decrypt(self, encrypted_text):

        cipher = AES.new(self.aes_key, AES.MODE_CBC, self.aes_iv)
        decrypted_padded = cipher.decrypt(encrypted_text)
        plaintext = unpad(decrypted_padded, AES.block_size)

        return plaintext.decode()
