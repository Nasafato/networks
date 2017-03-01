import unittest
import pickle

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

MessageTypes = enum('REGISTER', 'DEREGISTER', 'UPDATE')

class MessageTypesTestCase(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(MessageTypes.REGISTER, 0)
        self.assertEqual(MessageTypes.DEREGISTER, 1)
        self.assertEqual(MessageTypes.UPDATE, 2)

class CreateMessageTestCase(unittest.TestCase):
    def test_registration(self):
        messageType = MessageTypes.REGISTER
        messageData = {
            'client_name': 'testClient',
            'client_port': 2000
        }

        targetMessage = {
            'type': MessageTypes.REGISTER,
            'data': messageData,
        }

        self.assertEqual(createMessage(messageType, messageData), targetMessage)

def createMessage(messageType, messageData):
    return {
        'type': messageType,
        'data': messageData,
    }

if __name__ == "__main__":
    unittest.main()


