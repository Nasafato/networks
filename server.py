import socket
import sys
import pprint
import json
import threading
import pprint
from table import ClientTable
from message import MessageTypes, MessageStates, createMessage

class SaveMessageException(Exception):
    pass

class ClientExistsException(Exception):
    pass

class Server:
    def __init__(self, port):
        self.port = port
        self.table = ClientTable()
        self.server_socket = None
        self.server_address = None
        self.running = True

    def _register_client(self, data, address):
        name = data['name']
        port = data['port']
        client_lookup = self.table.lookup_client(name)
        if client_lookup and client_lookup['status'] == 'ONLINE':
            raise ClientExistsException("Registering client that is still online")

        self.table.register_client(data['name'], address, data['port'])

    def _deregister_client(self, data):
        if 'offline_client' in data:
            client_name = data['offline_client']
        else:
            client_name = data['dereg_name']
        self.table.deregister_client(client_name)
        if 'message' in data:
            self._save_offline_message(data)

    def _save_offline_message(self, data):
        message = data['message']
        client_name = data['sender_name']
        if not self.table.is_client_offline(client_name):
            raise SaveMessageException("Client {} exists!!".format(client_name))

        self.table.save_offline_message(client_name, message)

    def _broadcast_table(self):
        try:
            for entry in self.table.get_entries():
                client_address = entry['address']
                # print "Broadcasting to {}".format(client_address)
                response = createMessage(
                    MessageTypes.BROADCAST,
                    MessageStates.SUCCESS,
                    self.table.table
                )
                sent = self.server_socket.sendto(response, client_address)
                # print sent
        except socket.error:
            print "Couldn't send to client"

    def _deserialize_json(self, data):
        try:
            data = json.loads(data)
            return data
        except Exception:
            raise Exception

    def _send_offline_messages(self, data, address):
        name = data['name']
        messages = self.table.get_offline_messages(name)
        if not messages:
            return

        try:
            self.server_socket.sendto(createMessage(
                MessageTypes.MESSAGES,
                MessageStates.SUCCESS,
                {
                    'messages': messages
                }
            ), address)
        except socket.error, msg:
            print "Error sending messags: {}".format(msg)

        self.table.clear_messages(name)

    def _get_response(self, message, address):
        # pprint.pprint(message)
        messageType = message['type']
        messageState = message['state']
        messageData = message['data']

        if messageType == MessageTypes.REGISTER and messageState == MessageStates.REQUEST:
            try:
                self._send_offline_messages(messageData, address)
                self._register_client(messageData, address)
                self._broadcast_table()
                return createMessage(
                    MessageTypes.REGISTER,
                    MessageStates.SUCCESS,
                    self.table.table
                )
            except ClientExistsException, msg:
                return createMessage(
                    MessageTypes.REGISTER,
                    MessageStates.FAILURE,
                    {
                        'error': str(msg)
                    }
                )
        elif messageType == MessageTypes.OFFLINE and messageState == MessageStates.REQUEST:
            self._deregister_client(messageData)
            self._broadcast_table()
            return createMessage(
                MessageTypes.OFFLINE,
                MessageStates.SUCCESS,
                messageData,
            )
        elif messageType == MessageTypes.SAVE and messageState == MessageStates.REQUEST:
            try:
                self._save_offline_message(messageData)
                return createMessage(MessageTypes.SAVE, MessageStates.SUCCESS, {})
            except SaveMessageException, msg:
                print "Failed to save message"
                self._broadcast_table()
                return createMessage(MessageTypes.SAVE, MessageStates.FAILURE, { 'error': str(msg)})
        elif messageType == MessageTypes.DEREG and messageState == MessageStates.REQUEST:
            try:
                self._deregister_client(messageData)
                self._broadcast_table()
                return createMessage(MessageTypes.DEREG, MessageStates.SUCCESS,
                        messageData)
            except Exception, msg:
                print "Some sort of exception {}".format(msg)
                return createMessage(MessageTypes.DEREG, MessageStates.FAILURE,
                        messageData)
        else:
            return createMessage(
                MessageTypes.UNKNOWN,
                MessageStates.FAILURE,
                {}
            )

    def _handle_message(self, message, address):
        message = self._deserialize_json(message)
        response = self._get_response(message, address)
        # print address

        if response:
            # print response
            sent = self.server_socket.sendto(response, address)

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
        host = socket.gethostbyname(socket.gethostname())
        self.server_address = (host, self.port)
        self.server_socket.bind(self.server_address)
        self._run()

if __name__ == "__main__":
    server = Server(1043)
    server.start()
