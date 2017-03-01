import socket
import sys


class Client:
    def __init__(self, nickname, server_address, port, server_port):
        self.in_prompt = False
        self.nickname = nickname
        self.server_address = server_address
        self.port = port
        self.server_port = server_port

    def register(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (self.server_address, self.server_port)
        message = "Test message from client to server"

        try:
            print >>sys.stderr, 'sending "%s"' % message
            sent = sock.sendto(message, server_address)

            print >>sys.stderr, 'waiting to receive'
            data, server = sock.recvfrom(4096)
            print "received message: {}".format(data)


        finally:
            print >>sys.stderr, 'closing socket'
            sock.close()


    def start(self):
        self.in_prompt = True
        self.register()
        while self.in_prompt:
            user_input = raw_input(">>> ")


