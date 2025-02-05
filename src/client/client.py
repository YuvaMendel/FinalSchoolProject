import socket
class Client:
    def __init__(self, dest_ip, dest_port):
        self.dest = (dest_ip, dest_port)
        self.sock = None
    def connect():
        self.sock = socket.socket()
        self.sock.connect(self.dest)
        print(connected)