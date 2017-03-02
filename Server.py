import socket
import sys
import json
from table import ClientTable
from message import MessageTypes, MessageStates, createMessage

class Server:
    def __init__(self, port):
        self.port = port
        self.table = ClientTable()

    def _register_client(self, data, address):
        new_table = self.table.register_client(data['name'], address, data['port'])
        print "Registering client {} at {}:{}".format(data['name'], address, data['port'])
        print "New table is {}".format(new_table)

    def _deregister_client(self, name):
        new_table = self.table.deregister_client(name)

    def _deserialize_json(self, data):
        try:
            data = json.loads(data)
            return data
        except Exception:
            raise Exception

    def _handle_message(self, message, address):
        messageType = message['type']
        messageState = message['state']
        messageData = message['data']

        print "Handling message {}".format(message)

        if messageType == MessageTypes.REGISTER and messageState == MessageStates.REQUEST:
            self._register_client(messageData, address)
            return {
                'type': MessageTypes.REGISTER,
                'state': MessageStates.SUCCESS
            }
        else:
            return {
                'type': MessageTypes.UNKNOWN,
                'state': MessageStates.FAILURE
            }

    def start(self):
        # print "Server starting!"
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = ('localhost', self.port)
        # print >>sys.stderr, 'starting up on %s port %s' % server_address
        sock.bind(server_address)

        while True:
            # print >>sys.stderr, '\nwaiting to receive message'
            message, address = sock.recvfrom(10000)
            message = self._deserialize_json(message)
            response = self._handle_message(message, address)
            # print >>sys.stderr, 'received %s bytes from %s' % (len(data), address)
            # print >>sys.stderr, data
            # if data:
            sent = sock.sendto(json.dumps(response), address)
            # print >>sys.stderr, 'sent %s bytes back to %s' % (sent, address)