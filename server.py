import socket
import sys
import json
import threading
from table import ClientTable
from message import MessageTypes, MessageStates, createMessage

class Server:
    def __init__(self, port):
        self.port = port
        self.table = ClientTable()
        self.server_socket = None
        self.server_address = None
        self.running = True

    def signal_handler(self, signum, frame):
        print "Signal"
        if self.server_socket:
            print "Closing server socket"
            self.server_socket.close()

    def _register_client(self, data, address):
        new_table = self.table.register_client(data['name'], address, data['port'])
        # print "Registering client {} at {}:{}".format(data['name'], address, data['port'])
        # print "New table is {}".format(new_table)

    def _deregister_client(self, name):
        new_table = self.table.deregister_client(name)

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
            return {
                'type': MessageTypes.REGISTER,
                'state': MessageStates.SUCCESS
            }
        else:
            return {
                'type': MessageTypes.UNKNOWN,
                'state': MessageStates.FAILURE
            }

    def _handle_message(self, message, address):
        message = self._deserialize_json(message)
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
                handle_thread.join()
                print "Thread joined!"
            except socket.error:
                print >>sys.stderr, 'Error while receiving/sending'
            except KeyboardInterrupt:
                print "Stopped running"
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