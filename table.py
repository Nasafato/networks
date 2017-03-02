import pprint
import json


class ClientTable:
    def __init__(self):
        self.table = {}

    def register_client(self, name, address, port):
        self.table[name] = {
            'name': name,
            'address': address,
            'port': port
        }
        return self.table

    def update(self, new_table):
        self.table = new_table

    def deregister_client(self, name):
        del self.table[name]
        return self.table

    def get_entries(self):
        return self.table.values()

    def __repr__(self):
        return pprint.pformat(self.table)