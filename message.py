import unittest
import pickle

def enum(**enums):
    return type('Enum', (), enums)

MessageTypes = enum(REGISTER='REGISTER',
    DEREGISTER='DEREGISTER',
    BROADCAST='BROADCAST',
    UPDATE='UPDATE',
    UNKNOWN='UNKNOWN')
MessageStates = enum(REQUEST='REQUEST', SUCCESS='SUCCESS', FAILURE='FAILURE')

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
            'state': MessageStates.REQUEST,
            'data': messageData,
        }

        self.assertEqual(createMessage(messageType, messageData), targetMessage)

def createMessage(messageType, messageState, messageData):
    return {
        'type': messageType,
        'state': messageState,
        'data': messageData,
    }

if __name__ == "__main__":
    unittest.main()


