import socket
import sys
import json
import threading
import re

from table import ClientTable
from message import MessageTypes, MessageStates, createMessage

class Client:
    def __init__(self, nickname, server_address, server_port, port):
        self.nickname = nickname
        self.server_address = server_address
        self.server_port = server_port
        self.port = port
        self.table = None
        self.client_socket = None
        self.running = True

    def _send_message(self, target_client, message):
        if target_client == self.nickname:
            print("Error: trying to send message to self")
            return

        entry = self.table.lookup_client(target_client)
        if not entry:
            print("Error: client {} not found in table".format(target_client))
            return

        target_address = tuple(entry['address'])
        try:
            self.client_socket.sendto(json.dumps(createMessage(
                MessageTypes.SEND,
                MessageStates.REQUEST,
                {
                    'message': message
                }
            )), target_address)
        except socket.error:
            self._print("Error: socket error while sending message")
            return


    def _process_input(self, user_input):
        split_data = user_input.split()
        if len(split_data) == 3 and split_data[0] == "send":
            self._send_message(split_data[1], split_data[2])

    def _input(self):
        while self.running:
            user_input = raw_input(">>> ")
            self._process_input(user_input)

    def stop(self):
        print "Stopping"
        self.running = False
        self.client_socket.close()
        print "Socket closed"

    def register(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (self.server_address, self.server_port)

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
            sent = self.client_socket.sendto(serialized, self.server_address)
        except socket.error:
            print >>sys.stderr, '>>> [Socket error - exiting ]'
            self.client_socket.close()

    def _deserialize_json(self, data):
        try:
            data = json.loads(data)
            return data
        except Exception:
            raise Exception

    def _print(self, string):
        sys.stdout.write("{}\n>>> ".format(string))
        sys.stdout.flush()

    def _handle(self, message, address):
        message = self._deserialize_json(message)
        messageType = message['type']
        messageState = message['state']
        messageData = message['data']

        print message

        if messageType == MessageTypes.BROADCAST and messageState == MessageStates.SUCCESS:
            if not self.table:
                self.table = ClientTable()
                self._print('[Welcome, You are registered.]')
            self.table.update(messageData)
            self._print('[Client table updated.]')

        else:
            return {
                'type': MessageTypes.UNKNOWN,
                'state': MessageStates.FAILURE
            }

    def _run(self):
        input_thread = threading.Thread(target=self._input)
        input_thread.daemon = True
        input_thread.start()

        while self.running:
            try:
                message, address = self.client_socket.recvfrom(10000)
                handle_thread = threading.Thread(target=self._handle, args=[message, address])
                handle_thread.start()
                handle_thread.join()
            except socket.error:
                print >>sys.stderr, '>>> [Socket error - exiting ]'
                self.stop()
            except KeyboardInterrupt:
                print "Keyboard Interrupt"
                self.stop()



    def start(self, prompt=True):
        self.in_prompt = prompt
        self.register()
        self._run()



