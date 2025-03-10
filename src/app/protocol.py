import base64
# General Protocol Constants
HOST = "127.0.0.1"  # Server address
PORT = 6627         # Communication port
SIZE_OF_SIZE = 12   # Size of the size field in the beginning of the message
SEPERATOR = '~'     # Seperator for the fields of the message
#Message Codes (OPCODES)
ACK_START = 'GKSC' # server got key from client and is ready to start communication
REQUEST_IMAGE = 'RIPP'
IMAGE_IDENTIFIED = 'RIPR'







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
def format_message(args):
    args = list(args)
    for i in range(len(args)):
        if type(args[i]) == str:
            args[i] = args[i].encode()

    base64_args = [base64.b64encode(arg).decode() for arg in args]
    return SEPERATOR.join(base64_args)
def unformat_message(msg):
    split_msg = msg.split(SEPERATOR)
    return [(base64.b64decode(s.encode())) for s in split_msg]
    
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