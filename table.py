import pprint

class Entry:
    def __init__(self, name, address, port):
        self.name = name
        self.address = address
        self.port = port

    def __repr__(self):
        return pprint.pformat({
            'name': self.name,
            'address': self.address,
            'port': self.port
        })

class ClientTable:
    def __init__(self):
        self.table = {}

    def register_client(self, name, address, port):
        self.table[name] = Entry(name, address, port)
        return self.table

    def deregister_client(self, name):
        del self.table[name]
        return self.table

    def __repr__(self):
        return pprint.pformat(self.table)