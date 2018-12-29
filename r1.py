# -*- coding: utf8 -*-
import socket
import threading
import socketserver
import sys

# Threaded UDP Server class which inherits Mixin Threading and UDP Server
# This server manages requests in an asynchronous way
# The difference from ThreadedTCPServer is because UDP is connectionless instead of maintaining connection
# this class only receives the data and closes the socket


class ThreadingUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass


# This handler works for every incoming request from broker
# Listens udp client and gets the packet
# Forwards packet to the udp client(destination)
class ThreadingUDPRequestHandler(socketserver.BaseRequestHandler):

    # Overrides handle method
    def handle(self):
        # Gets the data from the broker
        data = self.request[0]
        # print("data received", data)

        # Creates a udp socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            global udp_internet_address_to_dest
            # sock.sendto(data, ("10.10.3.2", 5003))
            sock.sendto(data, udp_internet_address_to_dest)

        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        finally:
            # Closes the socket after handling is done
            sock.close()


# This handler works for every incoming request from destination
# Listens udp client and gets the packet
# Forwards packet to the udp client(broker)
class ThreadingUDPRequestHandler2(socketserver.BaseRequestHandler):

    # Overrides handle method
    def handle(self):
        # Gets the data from the broker
        data = self.request[0]
        # print("data received", data)

        # Creates a udp socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            global udp_internet_address_to_brok
            # sock.sendto(data, ("10.10.3.2", 5003))
            sock.sendto(data, udp_internet_address_to_brok)

        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        finally:
            # Closes the socket after handling is done
            sock.close()


udp_internet_address_from_brok = ("127.0.0.1", 5001)
udp_internet_address_to_brok = ("127.0.0.1", 6003)
udp_internet_address_from_dest = ("127.0.0.1", 6001)
udp_internet_address_to_dest = ("127.0.0.1", 5003)


if __name__ == "__main__":
    print("Router 1 server is initiated.")

    # The address that will listen udp client
    # udp_internet_address = ("10.10.2.2", 5001)

    # Create server for UDP
    udp_server_from_brok = ThreadingUDPServer(udp_internet_address_from_brok, ThreadingUDPRequestHandler)
    udp_server_from_dest = ThreadingUDPServer(udp_internet_address_from_dest, ThreadingUDPRequestHandler2)

    # Manager thread for udp_server which creates a new thread for each request
    udp_server_thread_from_brok = threading.Thread(target=udp_server_from_brok.serve_forever)
    udp_server_thread_from_dest = threading.Thread(target=udp_server_from_dest.serve_forever)

    # Flags it as a Daemon Thread
    udp_server_thread_from_brok.daemon = True
    udp_server_thread_from_dest.daemon = True
    # Starts the thread’s activity.
    udp_server_thread_from_brok.start()
    udp_server_thread_from_dest.start()

    input()

    # Closes udp_server
    # Tell the serve_forever() loop to stop and wait until it does.
    udp_server_from_brok.shutdown()
    udp_server_from_dest.shutdown()
    # Clean up the server.
    udp_server_from_brok.server_close()
    udp_server_from_dest.server_close()
