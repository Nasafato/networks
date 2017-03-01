import socket
import sys
import json

from message import MessageTypes, createMessage

class Client:
    def __init__(self, nickname, server_address, server_port, port):
        self.in_prompt = False
        self.nickname = nickname
        self.server_address = server_address
        self.server_port = server_port
        self.port = port

    def register(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (self.server_address, self.server_port)

        message = createMessage(
            MessageTypes.REGISTER,
            {
                'client_name': self.nickname,
                'client_port': self.port
            }
        )

        serialized = json.dumps(message)

        try:
            sent = sock.sendto(serialized, server_address)
            data, server = sock.recvfrom(4096)
        finally:
            print >>sys.stderr, '>>> [Welcome, You are registered.]'
            sock.close()


    def start(self):
        self.in_prompt = True
        self.register()
        while self.in_prompt:
            user_input = raw_input(">>> ")


