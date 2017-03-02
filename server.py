import socket
import sys
import json
import threading
import pprint
from table import ClientTable
from message import MessageTypes, MessageStates, createMessage

class SaveMessageException(Exception):
    pass

class Server:
    def __init__(self, port):
        self.port = port
        self.table = ClientTable()
        self.server_socket = None
        self.server_address = None
        self.running = True

    def _register_client(self, data, address):
        new_table = self.table.register_client(data['name'], address, data['port'])

    def _deregister_client(self, data):
        client_name = data['offline_client']
        self.table.deregister_client(client_name)

    def _save_offline_message(self, data):
        message = data['message']
        client_name = data['offline_client']
        if self.table.is_client_offline(client_name):
            raise SaveMessageException("Client is not offline")

        self.table.save_offline_message(client_name, message)

    def _broadcast_table(self):
        try:
            for entry in self.table.get_entries():
                client_address = entry['address']
                print "Broadcasting to {}".format(client_address)
                response = {
                    'type': MessageTypes.BROADCAST,
                    'state': MessageStates.SUCCESS,
                    'data': self.table.table
                }
                sent = self.server_socket.sendto(json.dumps(response), client_address)
                print sent
        except socket.error:
            print "Couldn't send to client"

    def _deserialize_json(self, data):
        try:
            data = json.loads(data)
            return data
        except Exception:
            raise Exception

    def _get_response(self, message, address):
        messageType = message['type']
        messageState = message['state']
        messageData = message['data']

        if messageType == MessageTypes.REGISTER and messageState == MessageStates.REQUEST:
            self._register_client(messageData, address)
            self._broadcast_table()
            return {
                'type': MessageTypes.REGISTER,
                'state': MessageStates.SUCCESS,
                'data': self.table.table
            }
        elif messageType == MessageTypes.OFFLINE and messageState == MessageStates.REQUEST:
            self._deregister_client(messageData)
            self._broadcast_table()
            return {
                'type': MessageTypes.OFFLINE,
                'state': MessageStates.SUCCESS,
                'data': messageData,
            }
        elif messageType == MessageTypes.SAVE and messageState == MessageStates.REQUEST:
            try:
                self._save_offline_message(self, messageData)
                return createMessage(MessageTypes.SAVE, MessageStates.SUCCESS, {})
            except SaveMessageException:
                return createMessage(MessageTypes.SAVE, MessageStates.FAILURE, {})
        else:
            return {
                'type': MessageTypes.UNKNOWN,
                'state': MessageStates.FAILURE,
                'data': None
            }

    def _handle_message(self, message, address):
        message = self._deserialize_json(message)
        print message
        response = self._get_response(message, address)

        if response:
            self.server_socket.sendto(json.dumps(response), address)

    def _run(self):
        while self.running:
            print >>sys.stderr, '\nwaiting to receive message'
            try:
                message, address = self.server_socket.recvfrom(10000)
                handle_thread = threading.Thread(target=self._handle_message, args=[message, address])
                handle_thread.start()
            except socket.error:
                print >>sys.stderr, 'Error while receiving/sending'
            except KeyboardInterrupt:
                self.stop()

    def stop(self):
        self.running = False

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = ('localhost', self.port)
        self.server_socket.bind(self.server_address)
        self._run()

if __name__ == "__main__":
    server = Server(1043)
    server.start()