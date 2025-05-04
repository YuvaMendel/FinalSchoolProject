import socket


import threading

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

import sys
import os
import io
import pickle
from PIL import Image
import numpy as np
import img_db_orm

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'CNNall')))
from CNNall.CNN import models

import app.protocol as protocol

import cv2

from keyboard import on_press_key


__auther__ = 'Yuval Mendel'

db_lock = threading.Lock()


class Server:
    def __init__(self):
        self.rsa_key = RSA.generate(2048)
        self.online = False
        self.sock = socket.socket()
        self.sock.bind(('127.0.0.1', protocol.PORT))
        self.sock.listen(10)
        self.clients = []
        self.sock.settimeout(0.1)
        self.server_lock = threading.Lock()
        on_press_key('q', lambda _: self.close())
        
    def activate_server(self):
        self.online = True
        while self.online:
            try:
                with self.server_lock:
                    s, _ = self.sock.accept()
                    handler = ClientHandler(s, self.rsa_key)
                    self.clients.append(handler)
                    handler.start()
            except socket.timeout:
                pass
            except socket.error as e:
                print(f"Socket error: {e}")

    def close(self):
        with self.server_lock:
            self.online = False

            for client in self.clients:
                client.connected = False
            for client in self.clients:
                client.join()
        print("Server closed")
                
                
class ClientHandler(threading.Thread):
    def __init__(self, soc, rsa_key):
        super().__init__()
        self.crypto = ServerCrypto(rsa_key)
        self.soc = soc

        self.connected = True
        self.ai = pickle.load(open('main_model.pkl', 'rb')) # Load the model
        self.db_orm = img_db_orm.ImagesORM()
        with db_lock:
            self.db_orm.create_tables()
    
    def run(self):
        try:
            self.handshake()
        except Exception as e:
            print(f"Handshake failed: {e}")
            self.connected = False
            return
        self.soc.settimeout(0.1)
        self.business_logic()

    def handshake(self):
        protocol.send_by_size(self.soc, self.crypto.get_public())
        self.crypto.decrypt_aes_key(protocol.recv_by_size(self.soc), protocol.recv_by_size(self.soc))
        # Get aes key and aes iv (for cbc) and give them to crypto object)
        self.send(protocol.ACK_START)

    def send(self, *msg):
        msg = protocol.format_message(msg)
        protocol.send_by_size(self.soc, self.crypto.encrypt(msg))

    def recv(self):
        rdata = protocol.recv_by_size(self.soc)
        decrypted_data = self.crypto.decrypt(rdata)
        return protocol.unformat_message(decrypted_data)

    def business_logic(self):
        while self.connected:
            try:
                try:
                    request = self.recv()
                except ValueError:
                    # Handle the case where the data is not valid
                    request = b''
                except ConnectionResetError:
                    request = b''
                if request == b'':
                    print("Client disconnected")
                    self.connected = False
                    continue
                opcode = request[0].decode()
                to_send = (protocol.ERROR, "4")
                if opcode == protocol.REQUEST_IMAGE:
                    # request[1] is the image name
                    # request[2] is the image content
                    if len(request) != 3:
                        to_send = (protocol.ERROR, "3")
                    elif len(request[2]) > protocol.MAX_FILE_SIZE:
                        to_send = (protocol.ERROR, "2")
                    elif not is_valid_image(request[2]):
                        to_send = (protocol.ERROR, "1")
                    else:
                        num, confidence = self.identify_num(request[2])
                        to_send = (protocol.IMAGE_IDENTIFIED, num, str(confidence))
                elif opcode == protocol.REQUEST_IMAGES:
                    files = self.db_orm.get_all_images_files()
                    to_send = self.build_return_images_msg(files)
                elif opcode == protocol.REQUEST_IMAGES_BY_DIGIT:
                    digit = request[1].decode()
                    files = self.db_orm.get_image_by_digit_files(digit)
                    to_send = self.build_return_images_msg(files)
                self.send(*to_send)
            except socket.timeout:
                pass

    @staticmethod
    def build_return_images_msg(files):
        msg_lst = []
        for file in files:
            msg_lst.append(file[0])
            msg_lst.append(file[1])
            msg_lst.append(file[2])
            msg_lst.append(str(file[3]))
        msg_lst = [protocol.RETURN_IMAGES] + msg_lst
        return msg_lst

    def identify_num(self, picture_content):
        image_array = image_to_2d_array(picture_content)
        prediction = self.ai.forward(image_array)
        class_index = np.argmax(prediction[0])
        confidence = float(prediction[0][class_index])
        with db_lock:
            self.db_orm.process_and_store(picture_content, str(class_index), confidence)

        return str(class_index), confidence

def is_valid_image(bytes_data):
    try:
        with Image.open(io.BytesIO(bytes_data)) as img:
            img.verify()  # Verifies it is an image, doesn't decode full data
        return True
    except (IOError, SyntaxError):
        return False


def thicken_digit_pil(pil_img, kernel_size=(2, 2), iterations=1):
    # Convert to grayscale NumPy array
    img_np = np.array(pil_img.convert("L"))

    # Binarize if not already (thresholding)
    _, binary_img = cv2.threshold(img_np, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Create kernel and apply dilation
    kernel = np.ones(kernel_size, np.uint8)
    dilated = cv2.dilate(binary_img, kernel, iterations=iterations)

    # Convert back to PIL Image
    return Image.fromarray(dilated)

def image_to_2d_array(image_content):
    """
    Convert the image content to a 2D NumPy array suitable for the model.
    also does preprocessing on the image
    :param image_content:
    :return:
    """
    # Load the image from the file content
    image_file = io.BytesIO(image_content)
    image = Image.open(image_file)

    # Convert the image to grayscale
    image = image.convert('L')
    # Resize the image to 28x28 pixels
    image = image.resize((28, 28))
    # Invert the image (255 - pixel value)
    image = Image.eval(image, lambda x: 255 - x)

    image = thicken_digit_pil(image, kernel_size=(2, 2), iterations=1)

    # Save the grayscale image to the Downloads directory
    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'try.png')
    image.save(downloads_path)


    # Convert the image to a NumPy array
    image_array = np.array(image)

    # Normalize the pixel values to be between 0 and 1
    image_array = image_array / 255.0
    image_array = image_array.reshape(1, 1, 28, 28)  # Reshape to (1, 1, 28, 28) for the model

    return image_array


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
        padded_data = pad(plaintext.encode(), AES.block_size)
        ciphertext = cipher.encrypt(padded_data)

        return ciphertext

    def decrypt(self, encrypted_text):
        if not self.aes_key or not self.aes_iv:
            raise ValueError("AES key and IV must be set before decryption.")

        cipher = AES.new(self.aes_key, AES.MODE_CBC, self.aes_iv)
        decrypted_padded = cipher.decrypt(encrypted_text)
        plaintext = unpad(decrypted_padded, AES.block_size)

        return plaintext.decode()
