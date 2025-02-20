# General Protocol Constants
HOST = "127.0.0.1"  # Server address
PORT = 6627         # Communication port
SIZE_OF_SIZE = 12   # Size of the size feild in the beginning of the message
#Message Codes (OPCODES)
ACK_START = b'GKSC' # server got key from client and is ready to start communication
REQUEST_IMAGE = b'RIPP'







DEBUG_FLAG = True
def __recv_amount(sock, size=SIZE_OF_SIZE):
    buffer = b''
    while size:
        new_bufffer = sock.recv(size)
        if not new_bufffer:
            return b''
        buffer += new_bufffer
        size -= len(new_bufffer)
    return buffer


def recv_by_size(sock, return_type="bytes"):
    data = b''
    data_len = int(__recv_amount(sock, SIZE_OF_SIZE))
    # code handle the case of data_len 0
    data = __recv_amount(sock, data_len)
    __log("Receive", data)
    if return_type == "string":
        return data.decode()
    
    return data


def send_by_size(sock, data):
    if len(data) == 0:
        return
    if type(data) != bytes:
        data = data.encode()
    len_data = str(len(data)).zfill(SIZE_OF_SIZE).encode()
    data = len_data + data
    sock.sendall(data)
    __log("Sent", data)
    
def __log(prefix, data, max_to_print=100):
    if not DEBUG_FLAG:
        return
    data_to_log = data[:max_to_print]
    if type(data_to_log) == bytes:
        try:
            data_to_log = data_to_log.decode()
        except (UnicodeDecodeError, AttributeError):
            pass
    print(f"\n{prefix}({len(data)})>>>{data_to_log}")