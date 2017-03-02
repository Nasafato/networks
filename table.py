import pprint
from collections import defaultdict
import json

class ClientTable:
    def __init__(self):
        self.table = {}
        self.message_table = defaultdict([])

    def register_client(self, name, address, port):
        self.table[name] = {
            'name': name,
            'address': address,
            'port': port,
            'status': 'ONLINE'
        }
        return self.table

    def update(self, new_table):
        self.table = new_table

    def lookup_client(self, name):
        if name in self.table:
            return self.table[name]
        else:
            return None

    def deregister_client(self, name):
        self.table[name]['status'] = 'OFFLINE'
        return self.table

    def save_offline_message(self, name, message):
        self.message_table[name].append(message)

    def get_offline_messages(self, name):
        return self.message_table[name]

    def get_entries(self):
        return self.table.values()

    def __repr__(self):
        return pprint.pformat(self.table)