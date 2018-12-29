# -*- coding: utf8 -*-
import socket
import sys
import datetime

# This message will be sent.

file_object = open("input.txt", "rb")


# MESSAGE = "Temperature: 37.3 celsius ,Pressure: 10000 bar"
# print("'" + MESSAGE + "'" + " will be sent.")

# Creates a TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Creates a tuple that includes host IP and port number
# address = ("10.10.1.2", 5000)
address = ("127.0.0.1", 5000)


try:
    # establishes a connection to the server
    sock.connect(address)
    # send its message
    print('Sent Time: ' + datetime.datetime.now().strftime("%Y/%m/%d ") + str(datetime.datetime.now().time()))

    MESSAGE = file_object.read(970)
    count = 0
    while MESSAGE:
        count += 1
        sock.send(MESSAGE)
        MESSAGE = file_object.read(970)
except Exception as e:
    # prints error and its line number
    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
finally:
    # closes the socket
    sock.close()
