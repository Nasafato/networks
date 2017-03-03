import unittest
import json

def enum(**enums):
    return type('Enum', (), enums)

MessageTypes = enum(REGISTER='REGISTER',
    DEREGISTER='DEREGISTER',
    BROADCAST='BROADCAST',
    OFFLINE='OFFLINE',
    UPDATE='UPDATE',
    SAVE='SAVE',
    SEND='SEND',
    DEREG='DEREG',
    MESSAGES='MESSAGES',
    UNKNOWN='UNKNOWN')

MessageStates = enum(REQUEST='REQUEST', RESPONSE='RESPONSE', SUCCESS='SUCCESS', FAILURE='FAILURE')

class MessageTypesTestCase(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(MessageTypes.REGISTER, 'REGISTER')
        self.assertEqual(MessageTypes.DEREGISTER, 'DEREGISTER')
        self.assertEqual(MessageTypes.UPDATE, 'UPDATE')

class CreateMessageTestCase(unittest.TestCase):
    def test_registration(self):
        messageType = MessageTypes.REGISTER
        messageState = MessageStates.REQUEST
        messageData = {
            'client_name': 'testClient',
            'client_port': 2000
        }

        targetMessage = json.dumps({
            'type': MessageTypes.REGISTER,
            'state': MessageStates.REQUEST,
            'data': messageData,
        })

        self.assertEqual(createMessage(messageType, messageState, messageData), targetMessage)

def createMessage(messageType, messageState, messageData):
    return json.dumps({
        'type': messageType,
        'state': messageState,
        'data': messageData,
    })

if __name__ == "__main__":
    unittest.main()


