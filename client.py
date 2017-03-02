import socket
import sys
import json
import threading

from table import ClientTable
from message import MessageTypes, MessageStates, createMessage

class Client:
    def __init__(self, nickname, server_address, server_port, port):
        self.nickname = nickname
        self.server_address = server_address
        self.server_port = server_port
        self.port = port
        self.client_socket = None
        self.running = True

    def _input(self):
        while self.running:
            user_input = raw_input(">>> ")

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
        print "{}\n>>> ".format(string)

    def _handle(self, message, address):
        message = self._deserialize_json(message)
        messageType = message['type']
        messageState = message['state']
        messageData = message['data']

        if messageType == MessageTypes.BROADCAST and messageState == MessageStates.SUCCESS:
            self._print(messageData)
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



