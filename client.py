import socket
import sys
import json
import threading

from table import ClientTable
from message import MessageTypes, MessageStates, createMessage

class Client:
    def __init__(self, nickname, server_address, server_port, port):
        self.in_prompt = False
        self.nickname = nickname
        self.server_address = server_address
        self.server_port = server_port
        self.port = port
        self.client_socket = None

    def register(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (self.server_address, self.server_port)

        message = createMessage(
            MessageTypes.REGISTER,
            MessageStates.REQUEST,
            {
                'name': self.nickname,
                'port': self.port
            }
        )

        serialized = json.dumps(message)

        try:
            sent = self.client_sock.sendto(serialized, server_address)
            data, server = sock.recvfrom(10000)
        except socket.error:
            print >>sys.stderr, '>>> [Socket error - exiting ]'
            sock.close()

    def _run(self):


    def start(self, prompt=True):
        self.in_prompt = prompt
        self.register()
        while self.in_prompt:
            user_input = raw_input(">>> ")


