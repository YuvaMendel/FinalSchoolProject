import base64
# General Protocol Constants
HOST = "127.0.0.1"  # Server address
PORT = 6627         # Communication port
SIZE_OF_SIZE = 7   # Size of the size field in the beginning of the message
MAX_FILE_SIZE = 3000000  # Maximum file size (1MB)
CLIENT_TIMEOUT = 2  # Timeout for client operations in seconds
SEPERATOR = '~'     # Seperator for the fields of the message
# Message Codes (OPCODES)
ACK_START = 'GKSC'  # server got key from client and is ready to start communication
REQUEST_IMAGE = 'RIPP'  # client request image recognition
IMAGE_IDENTIFIED = 'RIPR'  # server identified image
ERROR = 'ERRR'  # server error
REQUEST_IMAGES = 'RIHP'  # client requests images that have been recognized (from the database)
REQUEST_IMAGES_BY_DIGIT = 'RIHD'  # client requests images that have been recognized by digit

RETURN_IMAGES = 'RIHL'  # server returns images from database (starts return process)
IMAGE_FILE_RETURN = 'RILF'  # returns a image file (the "RETURN_IMAGES" send the amount of "IMAGE_FILE_RETURN" messages)
RETURN_FILES_END = 'RIHE'  # end of the return process

SIGN_UP_REQUEST = 'CRSU'  # client requests to  sign up
SIGN_UP_APPROVED = 'CRSA'  # server approved the sign up request
SIGN_UP_DENIED = 'CRSD'  # server denied the sign up request
LOG_IN_REQUEST = 'CRSI'  # client requests to sign in
LOG_IN_APPROVED = 'CRLA'  # server approved the sign in request
LOG_IN_DENIED = 'CRFD'  # server denied the sign in request


# Error Codes
error_messages = {"1": "Image format not recognized/supported",
                  "2": "File is too large",
                  "3": "Invalid request",
                  "4": "General_error"}

DEBUG_FLAG = True


def __recv_amount(sock, size=SIZE_OF_SIZE):
    """
    Receive a specific amount of data from a socket.
    :param sock: a socket to receive data from
    :param size: size of the data to receive, default is SIZE_OF_SIZE
    :return: data received from the socket as bytes
    """
    buffer = b''
    while size:
        new_bufffer = sock.recv(size)
        if not new_bufffer:
            return b''
        buffer += new_bufffer
        size -= len(new_bufffer)
    return buffer


def recv_by_size(sock, return_type="bytes"):
    """
    Receive data from a socket by size.
    :param sock: socket to receive data from
    :param return_type: type of data to return, either "bytes" or "string"
    :return: data received from the socket, either as bytes or string
    """
    data = b''
    data_len = int(__recv_amount(sock, SIZE_OF_SIZE))
    # code handle the case of data_len 0
    data = __recv_amount(sock, data_len)
    __log("Receive", data)
    if return_type == "string":
        return data.decode()
    
    return data


def send_by_size(sock, data, max_chunk_size=4096):
    """
    Send data to a socket by size.
    :param sock: socket to send data to
    :param data: data to send, can be a string or bytes
    :param max_chunk_size: chunk size to send data in, default is 4096 bytes
    :return:
    """
    if len(data) == 0:
        return
    if type(data) != bytes:
        data = data.encode()
    len_data = str(len(data)).zfill(SIZE_OF_SIZE).encode()
    data = len_data + data
    total_sent = 0
    while total_sent < len(data):
        end = min(total_sent + max_chunk_size, len(data))
        chunk = data[total_sent:end]
        sent = sock.send(chunk)
        if sent == 0:
            raise RuntimeError("socket connection broken")
        total_sent += sent
    __log("Sent", data)


def format_message(args):
    """
    Format a message by encoding each argument in base64 and joining them with SEPERATOR.
    :param args: arguments to format, can be a list or tuple of strings or bytes
    :return: string with base64 encoded parts separated by SEPERATOR
    """
    args = list(args)
    for i in range(len(args)):
        if type(args[i]) == str:
            args[i] = args[i].encode()

    base64_args = [base64.b64encode(arg).decode() for arg in args]
    return SEPERATOR.join(base64_args)


def unformat_message(msg):
    """
    Unformat a message that was formatted with format_message.
    :param msg: the message to unformat, should be a string with base64 encoded parts separated by SEPERATOR
    :return: a list of bytes, each element is the decoded base64 string from the message
    """
    split_msg = msg.split(SEPERATOR)
    return [(base64.b64decode(s.encode())) for s in split_msg]

    
def __log(prefix, data, max_to_print=100):
    """
    Log data to the console if DEBUG_FLAG is set.
    :param prefix: prefix for the log message
    :param data: data to log, can be a string or bytes
    :param max_to_print: maximum number of characters to print from the data
    :return:
    """
    if not DEBUG_FLAG:
        return
    data_to_log = data[:max_to_print]
    if type(data_to_log) == bytes:
        try:
            data_to_log = data_to_log.decode()
        except (UnicodeDecodeError, AttributeError):
            pass
    print(f"\n{prefix}({len(data)})>>>{data_to_log}")

