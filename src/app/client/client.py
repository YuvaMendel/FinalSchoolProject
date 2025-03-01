import socket
import threading
import queue
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import app.protocol as protocol
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


class Client(threading.Thread):
    def __init__(self, dest_ip, dest_port, gui_callback=None):
        super().__init__()
        self.dest = (dest_ip, dest_port)
        self.sock = socket.socket()
        self.request_queue = queue.Queue()
        self.connected = False
        self.crypto = ClientCrypto()
        self.gui_callback = gui_callback
    
    def connect(self):
        try:
            self.sock.connect(self.dest)
            self.connected = True
        except socket.error as e:
            print(e)
            self.connected = False
            
    def run(self):
        self.connect()
        self.handshake()
        self.activate()


        

        
    def handshake(self):
        rsa_public = protocol.recv_by_size(self.sock)
        encrypted_aes_key, aes_iv = self.crypto.encrypted_key_iv(rsa_public)
        protocol.send_by_size(self.sock, encrypted_aes_key)
        protocol.send_by_size(self.sock, aes_iv)
        return_message = self.recv()
        print(return_message[0])

    def queue_task(self, task_code ,*args):
        self.request_queue.put((task_code, args))
        
    def activate(self):
        while self.connected:
            task = self.request_queue.get()
            if task is None:
                break
            task_code, args = task
            self.handle_task(task_code, args)
            response = self.recv()
            self.business_logic(response)

    def business_logic(self, response):
        if response[0] == protocol.IMAGE_IDENTIFIED:
            self.gui_callback.display_result(response[1])

    def send_file(self, file_path):
        self.queue_task(protocol.REQUEST_IMAGE, file_path)

    def handle_task(self, task_code, args):
        if task_code == protocol.REQUEST_IMAGE:
            file_name = args[0].split('/')[-1]
            with self.open_file(args[0], 'rb') as file:
                file_content = file.read()
                self.send(protocol.REQUEST_IMAGE, file_name, file_content)
        
    def is_connected(self):
        return self.connected
        
    def close(self):
        
        self.connected = False
        self.request_queue.put(None)
        self.sock.close()

    def send(self, *msg):
        msg = protocol.format_message(msg)
        protocol.send_by_size(self.sock, self.crypto.encrypt(msg))

    def recv(self):
        return protocol.unformat_message(self.crypto.decrypt(protocol.recv_by_size(self.sock)))
        

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
