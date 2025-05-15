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
from PIL import Image
import io


class Client(threading.Thread):
    def __init__(self, dest_ip, dest_port=protocol.PORT, gui_callback=None):
        super().__init__()
        self.dest = (dest_ip, dest_port)
        self.sock = socket.socket()
        self.request_queue = queue.Queue()
        self.connected = False
        self.crypto = ClientCrypto()
        self.gui_callback = gui_callback

    def connect(self):
        self.sock.connect(self.dest)
        self.handshake()

    def run(self):
        self.activate()

    def handshake(self):
        rsa_public = protocol.recv_by_size(self.sock)
        encrypted_aes_key, aes_iv = self.crypto.encrypted_key_iv(rsa_public)
        protocol.send_by_size(self.sock, encrypted_aes_key)
        protocol.send_by_size(self.sock, aes_iv)
        return_message = self.recv()
        if return_message[0].decode() == protocol.ACK_START:
            self.connected = True
            print("Handshake successful")

    def queue_task(self, task_code ,*args):
        self.request_queue.put((task_code, args))

    def activate(self):
        while self.connected:
            task = self.request_queue.get()
            if task is None:
                break
            task_code, args = task
            try:
                to_recv = self.handle_task(task_code, args)
            except ConnectionError as e:
                print(f"Connection error: {e}")
                self.connected = False
                self.gui_callback.display_result("Server disconnected", message_type="error")
                break
            if to_recv:
                try:
                    response = self.recv()
                    self.business_logic(response)
                except Exception as e:
                    print(f"Error receiving data: {e}")
                    self.connected = False
                    self.gui_callback.display_result("Server disconnected", message_type="error")
                    break

    def recv_files_process(self, amount_of_files):
        """
        This function is used to receive files from the server
        :param amount_of_files: the number of files to receive
        :return: None
        """
        images = []
        finished_process = False
        for i in range(amount_of_files):
            msg = self.recv()
            opcode = msg[0].decode()
            if opcode == protocol.RETURN_FILES_END:
                finished_process = True
                break
            elif opcode == protocol.IMAGE_FILE_RETURN:
                image_list = msg[1:]
                id = image_list[0].decode()
                image_content = image_list[1]
                image_file = io.BytesIO(image_content)
                image = Image.open(image_file)
                digit = image_list[2].decode()
                confidence = float(image_list[3].decode())
                images.append((id, image, digit, confidence))
        if not finished_process:
            msg = self.recv()
            opcode = msg[0].decode()
            if opcode == protocol.RETURN_FILES_END:
                finished_process = True
        return images

    def business_logic(self, response):
        opcode = response[0].decode()
        if opcode == protocol.IMAGE_IDENTIFIED:
            self.gui_callback.display_result("The server predicts: " + response[1].decode() + "\nwith confidence: " + response[2].decode())
        if opcode == protocol.RETURN_IMAGES:
            images = self.recv_files_process(int(response[1].decode()))

            self.gui_callback.display_images(images)
        if opcode == protocol.ERROR:
            error_code = response[1].decode()
            if error_code in protocol.error_messages:
                error_message = protocol.error_messages[error_code]
            else:
                error_message = "Unknown error"
            self.gui_callback.display_result(error_message, message_type="error")
        if opcode == protocol.LOG_IN_APPROVED:
            self.gui_callback.gui_set_logged_in_user(response[1].decode())
        if opcode == protocol.LOG_IN_DENIED:
            self.gui_callback.display_result("Log in denied", message_type="error")
        if opcode == protocol.SIGN_UP_APPROVED:
            self.gui_callback.display_result("Sign up approved", message_type="result")
        if opcode == protocol.SIGN_UP_DENIED:
            self.gui_callback.display_result("Sign up denied- username is already taken", message_type="error")


    @staticmethod
    def convert_image_string_to_tuple(image_string_list):
        """
        converts the list of strings representing images to a list of tuples, that makes it easier to work with
        """
        img_lst = []
        for i in range(0,len(image_string_list),4):
            id = image_string_list[i].decode()
            image_content = image_string_list[i+1]
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file)
            digit = image_string_list[i+2].decode()
            confidence = float(image_string_list[i+3].decode())
            img_lst.append((id, image, digit, confidence))
        return img_lst

    def send_file(self, file_path):
        self.queue_task(protocol.REQUEST_IMAGE, file_path)

    def request_sign_up(self, username, password):
        self.queue_task(protocol.SIGN_UP_REQUEST, username, password)

    def request_log_in(self, username, password):
        self.queue_task(protocol.LOG_IN_REQUEST, username, password)

    def request_images(self, digit=None):
        if digit is None:
            self.queue_task(protocol.REQUEST_IMAGES)
        else:
            self.queue_task(protocol.REQUEST_IMAGES_BY_DIGIT, digit)

    def handle_task(self, task_code, args):
        """
        Handle the task based on the task code and arguments.
        :param task_code: a string representing the task code
        :param args: the arguments for the task
        :return: should the client recv a message
        """
        if task_code == protocol.REQUEST_IMAGE:
            file_name = args[0].split('/')[-1]
            if not os.path.exists(args[0]):
                self.gui_callback.display_result(f"File {args[0]} does not exist.", message_type="error")
                return False
            with open(args[0], 'rb') as file:
                file_content = file.read()
            if len(file_content) > protocol.MAX_FILE_SIZE:
                self.gui_callback.display_result(f"File {args[0]} is too large", message_type="error")
                return False

            self.send(protocol.REQUEST_IMAGE, file_name, file_content)
        if task_code == protocol.REQUEST_IMAGES:
            self.send(protocol.REQUEST_IMAGES)
        if task_code == protocol.REQUEST_IMAGES_BY_DIGIT:
            digit = args[0]
            self.send(protocol.REQUEST_IMAGES_BY_DIGIT, digit)
        if task_code == protocol.SIGN_UP_REQUEST:
            username = args[0]
            password = args[1]
            if len(username) == 0 or len(password) == 0:
                self.gui_callback.display_result("Username or password cannot be empty", message_type="error")
                return False
            self.send(protocol.SIGN_UP_REQUEST, username, password)
        if task_code == protocol.LOG_IN_REQUEST:
            username = args[0]
            password = args[1]
            if len(username) == 0 or len(password) == 0:
                self.gui_callback.display_result("Username or password cannot be empty", message_type="error")
                return False
            self.send(protocol.LOG_IN_REQUEST, username, password)
        return True

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
