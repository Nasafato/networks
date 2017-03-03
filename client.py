import socket
import thread
import sys
import json
import threading
import re
import time

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
        self.ack_table = {}
        self.deregistering = False
        self.dereg_success = False
        self.dereg_tries = 0

    def _ack_request(self, target_client):
        self.ack_table[target_client] = 'NO_ACK'

    def _send_ack_response(self, address):
        try:
            sent = self.client_socket.sendto(createMessage(
                MessageTypes.SEND,
                MessageStates.RESPONSE,
                {
                    'responder_name': self.nickname
                }
            ), address)
        except socket.error:
            self._print("Error: socket error while sending ack")

    def _mark_client_offline(self, client_name, message):
        messageData =   {
            'offline_client': client_name,
            'message': message
        }
        try:
            sent = self.client_socket.sendto(createMessage(
                MessageTypes.OFFLINE,
                MessageStates.REQUEST,
                messageData
            ), self.server_address)
        except socket.error:
            self._print("Error: socket error while marking client {} offline".format(client_name))

    def _send_message(self, target_client, message):
        if target_client == self.nickname:
            print("Error: trying to send message to self")
            return

        entry = self.table.lookup_client(target_client)
        if not entry:
            print("Error: client {} not found in table".format(target_client))
            return

        if self.table.is_client_offline(target_client):
            try:
                sent = self.client_socket.sendto(createMessage(
                    MessageTypes.SAVE,
                    MessageStates.REQUEST,
                    {
                        'offline_client': target_client,
                        'message': message
                    }
                ), self.server_address)
            except socket.error:
                self._print("Error: socket error while sending message")
            finally:
                return

        target_address = tuple(entry['address'])
        try:
            sent = self.client_socket.sendto(createMessage(
                MessageTypes.SEND,
                MessageStates.REQUEST,
                {
                    'sender_name': self.nickname,
                    'message': message
                }
            ), target_address)
            self.ack_table[target_client] = 'NO_ACK'
        except socket.error:
            self._print("Error: socket error while sending message")
            return

        time.sleep(0.5)
        if self.ack_table[target_client] == 'ACKED':
            self.ack_table[target_client] == 'SUCCESS'
            self._print("[Message received by {}]".format(target_client))
            return

        self._mark_client_offline(target_client, message)

    def _dereg(self, client_name):
        print "Deregging {}".format(client_name)
        if not self.table.lookup_client(client_name):
            self._print("[ERROR: Client {} doesn't exist in table.]".format(client_name))
            return

        self.dereg_tries = 0
        self.deregistering = True
        while self.deregistering and self.dereg_tries < 5:
            try:
                sent = self.client_socket.sendto(createMessage(
                    MessageTypes.DEREG,
                    MessageStates.REQUEST,
                    {
                        'dereg_name': client_name
                    }
                ), self.server_address)
            except socket.error:
                print "Error: socket failed while sending dereg request"
            time.sleep(0.5)
            if (self.dereg_success == True):
                self._print('[You are Offline. Bye.]')
                self.deregistering = False
                self.dereg_tries = 0
                break

            self.dereg_tries += 1

        if not self.dereg_success:
            self._print('[Server not responding]')
            self._print('[Exiting]')

        self.dereg_success = False
        self.stop()

    def _process_input(self, user_input):
        split_data = user_input.split()
        if len(split_data) == 3 and split_data[0] == "send":
            self._send_message(split_data[1], split_data[2])
        elif len(split_data) == 2 and split_data[0] == "dereg":
            self._dereg(split_data[1])
        else:
            print "Error: invalid command"

    def _input(self):
        while self.running:
            user_input = raw_input(">>> ")
            self._process_input(user_input)

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

        try:
            sent = self.client_socket.sendto(message, self.server_address)
            message, address = self.client_socket.recvfrom(10000)
            self._handle(message, address)
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

    def _handle_ack(self, data, address):
        responder_name = data['responder_name']
        self.ack_table[responder_name] = 'ACKED'

    def _handle(self, message, address):
        message = self._deserialize_json(message)
        messageType = message['type']
        messageState = message['state']
        messageData = message['data']

        if messageType == MessageTypes.BROADCAST and messageState == MessageStates.SUCCESS:
            if not self.table:
                self.table = ClientTable()
                self._print('[Welcome, You are registered.]')
            self.table.update(messageData)
            self._print('[Client table updated.]')
        elif messageType == MessageTypes.SEND and messageState == MessageStates.REQUEST:
            self._send_ack_response(address)
            self._print('{}: {}'.format(messageData['sender_name'], messageData['message']))
        elif messageType == MessageTypes.SEND and messageState == MessageStates.RESPONSE:
            self._handle_ack(messageData, address)
        elif messageType == MessageTypes.SAVE and messageState == MessageStates.SUCCESS:
            self._print('[Messages received by the server and saved]')
        elif messageType == MessageTypes.OFFLINE and messageState == MessageStates.SUCCESS:
            self._print('[No ACK from {}, message sent to server.]'.format(messageData['offline_client']))
            self._print('[Messages received by the server and saved]')
        elif messageType == MessageTypes.REGISTER and messageState == MessageStates.FAILURE:
            self._print('[ERROR: client with that name already exists]')
            self.stop()
        elif messageType == MessageTypes.DEREG and messageState == MessageStates.SUCCESS:
            self.dereg_success = True
        else:
            return {
                'type': MessageTypes.UNKNOWN,
                'state': MessageStates.FAILURE,
                'data': None
            }
    def _listen(self):
        while self.running:
            try:
                message, address = self.client_socket.recvfrom(10000)
                handle_thread = threading.Thread(target=self._handle, args=[message, address])
                handle_thread.start()
            except socket.error:
                print >>sys.stderr, '>>> [Socket error - exiting ]'
                self.stop()

    def _run(self):
        input_thread = threading.Thread(target=self._input)
        input_thread.daemon = True
        input_thread.start()

        listen_thread = threading.Thread(target=self._input)
        listen_thread.daemon = True
        listen_thread.start()

        while self.running:
            time.sleep(1)

    def start(self, prompt=True):
        self.in_prompt = prompt
        self.register()
        self._run()

    def stop(self):
        self.running = False
        self.client_socket.close()
        thread.interrupt_main()
        exit(1)



