# -*- coding: utf8 -*-
import threading
import socketserver
from struct import *
import struct
import hashlib


# Threaded UDP Server class which inherits Mixin Threading and UDP Server
# This server manages requests in an asynchronous way
# The difference from ThreadedTCPServer is because UDP is connectionless instead of maintaining connection
# this class only receives the data and closes the socket

lock = threading.Lock()


# packet structure is (seq number, checksum)
def make_pkt():
    global exp_seq_number
    pck_without_check_sum = struct.pack("i", exp_seq_number)
    response_packet = pck_without_check_sum + struct.pack("32s", get_check_sum(pck_without_check_sum).encode())
    return response_packet


# returns if packet's sequence number is equal to expected sequence number
def has_seq_num(packets_seq_number):
    global exp_seq_number
    return packets_seq_number == exp_seq_number


# return md5 od the data
def get_check_sum(data):
    hash_md5 = hashlib.md5()
    hash_md5.update(data)
    return hash_md5.hexdigest()


# check sum field is 32 byte and at the end of the file
def is_corrupt(packet):
    length = len(packet)
    check_sum_size = calcsize('32s')
    control_part, check_sum = struct.unpack(str(length-check_sum_size) + "s32s", packet)
    return check_sum != get_check_sum(control_part).encode()


class ThreadingUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass


# Listens udp client and gets the packet
class ThreadingUDPRequestHandler(socketserver.BaseRequestHandler):
    # Overrides handle method
    def handle(self):
        # Gets the data from router1 and router2 wrt. IP and Port numbers
        rcvpkt = self.request[0]
        length = len(rcvpkt)

        # Obtain socket
        sock = self.request[1]

        # Gets length of header
        header_length = calcsize('ii32s')

        # Divides received packet
        # received packet structure (seq_number, flag, data, check_sum)
        packets_seq_number, finish_flag, data, check_sum = \
            struct.unpack("ii" + str(length - header_length) + "s" + "32s", rcvpkt)

        # Hold the lock
        lock.acquire()

        global exp_seq_number
        global sndpkt
        global result

        if has_seq_num(packets_seq_number) and (not is_corrupt(rcvpkt)):
            # not corrupted and has expected sequence number
            print("incoming seq number ", packets_seq_number, ", expected seq number  ", exp_seq_number)
            # has expected seq number and not corrupted
            # Determine packet is finished or not
            if finish_flag:
                # whole file is finished
                print("whole packet is received")
                wr_file = open("output.txt", "wb")
                # write data to output.txt
                wr_file.write(result)
                # reset result for new incoming files
                result = b''
                # make ACK
                sndpkt = make_pkt()
                exp_seq_number += 1
                # Send ACK message to client address
                if packets_seq_number % 2 == 0:
                    sock.sendto(sndpkt, udp_to_r1_address)
                else:
                    sock.sendto(sndpkt, udp_to_r2_address)

            else:
                # make ACK
                sndpkt = make_pkt()
                exp_seq_number += 1
                # concatenate new data to previously comings
                result += data
                # Send ACK message to client address
                if packets_seq_number % 2 == 0:
                    sock.sendto(sndpkt, udp_to_r1_address)
                else:
                    sock.sendto(sndpkt, udp_to_r2_address)
        else:
            # Corrupt or seq number does not match
            # Send the old ACK message
            if packets_seq_number % 2 == 0:
                sock.sendto(sndpkt, udp_to_r1_address)
            else:
                sock.sendto(sndpkt, udp_to_r2_address)

        # Release the lock
        lock.release()


# Globals
exp_seq_number = 0
sndpkt = make_pkt()
exp_seq_number += 1
result = b''

# local port and ip address
# udp_from_r1_address = ("127.0.0.1", 5003)
# udp_to_r1_address = ("127.0.0.1", 6001)
# udp_from_r2_address = ("127.0.0.1", 5004)
# udp_to_r2_address = ("127.0.0.1", 6002)

# remote port and ip addresses
udp_from_r1_address = ("10.10.3.2", 5001)
udp_to_r1_address   = ("10.10.2.1", 6001)
udp_from_r2_address = ("10.10.5.2", 5002)
udp_to_r2_address   = ("10.10.4.1", 6002)

if __name__ == "__main__":

    print("Destination server is initiated.")

    # The addresses that will listen udp client

    # Creates servers for UDP
    udp_r1_server = ThreadingUDPServer(udp_from_r1_address, ThreadingUDPRequestHandler)
    udp_r2_server = ThreadingUDPServer(udp_from_r2_address, ThreadingUDPRequestHandler)

    # Manager thread for udp_server which creates a new thread for each request
    udp_r1_server_thread = threading.Thread(target=udp_r1_server.serve_forever)
    udp_r2_server_thread = threading.Thread(target=udp_r2_server.serve_forever)

    # Flags it as a Daemon Thread
    udp_r1_server_thread.daemon = True
    udp_r2_server_thread.daemon = True

    # Starts the thread’s activity.
    udp_r1_server_thread.start()
    udp_r2_server_thread.start()

    input()

    # Closes udp_servers
    # Tell the serve_forever() loop to stop and wait until it does.
    udp_r1_server.shutdown()
    udp_r2_server.shutdown()

    # Clean up the servers.
    udp_r1_server.server_close()
    udp_r2_server.server_close()
