import socket
import sys
import json
from message import MessageTypes, createMessage

class Server:
    def __init__(self, port):
        self.port = port

    def start(self):
        print "Server starting!"
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = ('localhost', self.port)
        print >>sys.stderr, 'starting up on %s port %s' % server_address
        sock.bind(server_address)

        print "Server address is {}".format(server_address)

        while True:
            print >>sys.stderr, '\nwaiting to receive message'
            data, address = sock.recvfrom(10000)

            print >>sys.stderr, 'received %s bytes from %s' % (len(data), address)
            print >>sys.stderr, data

            if data:
                sent = sock.sendto(data, address)
                print >>sys.stderr, 'sent %s bytes back to %s' % (sent, address)