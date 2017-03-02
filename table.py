import pprint
import json

class ClientTable:
    def __init__(self):
        self.table = {}

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

    def get_entries(self):
        return self.table.values()

    def __repr__(self):
        return pprint.pformat(self.table)