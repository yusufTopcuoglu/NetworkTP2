# -*- coding: utf8 -*-

import socket
import threading
import socketserver
import sys
from struct import *
import struct
import time
import hashlib

# Threaded TCP Server class which inherits Mixin Threading and TCP Server
# This server manages requests in an asynchronous way

# Global variables
nextseqnum = 1
base = 1
wnd_size = 10
snd_pkt = []
sample_rtt = 0
estimated_rtt = 0
dev_rtt = 0
sent_time = 0
is_acked = True
received_time = 0
# initial value of 1 second is recommended [RFC 6298]
timeout_interval = 1.0

# local ip and port numbers
# tcp_internet_address_sour    = ("127.0.0.1", 5000)
# udp_internet_address_to_r1   = ("127.0.0.1", 5001)
# udp_internet_address_from_r1 = ("127.0.0.1", 6003)
# udp_internet_address_to_r2   = ("127.0.0.1", 5002)
# udp_internet_address_from_r2 = ("127.0.0.1", 6004)

# Geni ip and port numbers
tcp_internet_address_sour    = ("10.10.1.2", 5000)
udp_internet_address_to_r1   = ("10.10.3.2", 5001)
udp_internet_address_from_r1 = ("10.10.2.1", 6001)
udp_internet_address_to_r2   = ("10.10.5.2", 5002)
udp_internet_address_from_r2 = ("10.10.4.1", 6002)

lock = threading.Lock()


class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class ThreadingUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass


def update_estimated_rtt():
    global estimated_rtt
    global sample_rtt
    sample_rtt = received_time - sent_time
    if base == 1:
        estimated_rtt = sample_rtt
        return
    # recommended alpha is 0.125
    estimated_rtt = 0.875 * estimated_rtt + 0.125 * sample_rtt


def update_dev_rtt():
    global dev_rtt
    global sample_rtt
    global estimated_rtt
    # The recommended value of β is 0.25
    dev_rtt = 0.75 * dev_rtt + 0.25 * abs(sample_rtt - estimated_rtt)


def update_timeout_interval():
    global timeout_interval
    global estimated_rtt
    global dev_rtt
    update_estimated_rtt()
    update_dev_rtt()
    timeout_interval = estimated_rtt + 4 * dev_rtt


def start_timer():
    global timer
    stop_timer()
    timer.start()


def stop_timer():
    global timer
    timer.cancel()
    timer = threading.Timer(timeout_interval, timeout)


def timeout():
    start_timer()
    print("time out happened")
    # Creates a udp socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if base == nextseqnum:
        stop_timer()
    else:
        for i in range(base, nextseqnum):
            if i % 2 == 0:
                sock.sendto(snd_pkt[i - 1], udp_internet_address_to_r1)
            else:
                sock.sendto(snd_pkt[i - 1], udp_internet_address_to_r2)


# check sum field is 16 byte and at the end of the file
def is_corrupt(packet):
    length = len(packet)
    check_sum_size = calcsize('32s')
    control_part, check_sum = struct.unpack(str(length-check_sum_size) + "s32s", packet)
    return check_sum != get_check_sum(control_part).encode()


def get_check_sum(data):
    hash_md5 = hashlib.md5()
    hash_md5.update(data)
    return hash_md5.hexdigest()


def make_pkt(flag, rcvpckt):
    pck_without_check_sum = struct.pack("ii", nextseqnum, flag) + rcvpckt
    return pck_without_check_sum + struct.pack("32s", get_check_sum(pck_without_check_sum).encode())


timer = threading.Timer(timeout_interval, timeout)


# Listens tcp client(source) and gets the packet
# Forwards the packet to the destination over r1 and r2
class ThreadingTCPRequestHandler(socketserver.BaseRequestHandler):
    # Overrides handle method
    def handle(self):
        global nextseqnum
        global base
        global snd_pkt
        global wnd_size
        global udp_internet_address_to_r1
        global udp_internet_address_to_r2
        global sent_time
        global is_acked

        # read the whole packet and prepare snd_pck
        rcvpckt = self.request.recv(900)
        # packet structure (seq_number, flag, data, check_sum)
        while rcvpckt:
            snd_pkt.append(make_pkt(0, rcvpckt))
            nextseqnum += 1
            rcvpckt = self.request.recv(900)

        # append FIN packet to the end
        snd_pkt.append(make_pkt(1, b''))

        nextseqnum = 1
        # Creates a udp socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        total_packet_count = len(snd_pkt)
        print(total_packet_count)
        try:
            while True:
                global lock
                lock.acquire()
                if nextseqnum > total_packet_count:
                    lock.release()
                    print("whole packet is sent")
                    stop_timer()
                    break
                if nextseqnum < base + wnd_size:
                    if is_acked:
                        is_acked = False
                        sent_time = time.time()
                    if nextseqnum % 2 == 0:
                        # sent packet to destination over router 1
                        sock.sendto(snd_pkt[nextseqnum - 1], udp_internet_address_to_r1)
                    else:
                        # sent packet to destination over router 2
                        sock.sendto(snd_pkt[nextseqnum - 1], udp_internet_address_to_r2)
                    if base == nextseqnum:
                        start_timer()
                    nextseqnum += 1
                lock.release()
                time.sleep(0.01)

        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        finally:
            # Closes the socket after handling is done
            sock.close()


# This handler works every incoming packet from both r1 and r2
class ThreadingUDPRequestHandler(socketserver.BaseRequestHandler):
    # Overrides handle method
    def handle(self):
        global nextseqnum
        global base
        global is_acked
        global received_time

        packet = self.request[0]
        ack_num, check_sum = struct.unpack("i32s", packet)
        global lock
        lock.acquire()
        is_acked = True
        received_time = time.time()
        update_timeout_interval()
        if not is_corrupt(packet):
            base = ack_num + 1
            print("ack received  base = ", base, "next sequence number = ", nextseqnum)
            if base == nextseqnum:
                stop_timer()
            else:
                start_timer()

        lock.release()


if __name__ == "__main__":
    print("Broker server is initiated.")
    count = 0
    # The address that will listen tcp client

    # Creating servers
    tcp_server = ThreadingTCPServer(tcp_internet_address_sour, ThreadingTCPRequestHandler)
    udp_server_from_r1 = ThreadingUDPServer(udp_internet_address_from_r1, ThreadingUDPRequestHandler)
    udp_server_from_r2 = ThreadingUDPServer(udp_internet_address_from_r2, ThreadingUDPRequestHandler)

    # Manager thread for tcp_server which creates a new thread for each request
    tcp_server_thread = threading.Thread(target=tcp_server.serve_forever)
    udp_server__thread_from_r1 = threading.Thread(target=udp_server_from_r1.serve_forever)
    udp_server__thread_from_r2 = threading.Thread(target=udp_server_from_r2.serve_forever)

    # Flags it as a Daemon Thread
    tcp_server_thread.daemon = True
    udp_server_from_r1.daemon = True
    udp_server_from_r2.daemon = True
    # Starts the thread’s activity.
    tcp_server_thread.start()
    udp_server__thread_from_r1.start()
    udp_server__thread_from_r2.start()

    input()

    # Closes the tcp_server
    # Tell the serve_forever() loop to stop and wait until it does.
    tcp_server.shutdown()
    udp_server_from_r1.shutdown()
    udp_server_from_r2.shutdown()
    # Clean up the server.
    tcp_server.server_close()
    udp_server_from_r1.server_close()
    udp_server_from_r2.server_close()
