import argparse
import re
import unittest

class ArgsException(Exception):
    pass

def main():
    parse_command_line()

def parse_command_line():
    parser = create_parser()
    args = parser.parse_args()
    print(args)
    if args.server:
        print("Server started")
    elif args.client:
        print("Client started")
    else:
        raise Exception("No arguments")


def create_parser():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-s", "--server", help="Start server")
    group.add_argument("-c", "--client", help="Start client",
        nargs=4,
        action="store")
    return parser

def extract_client_args(result):
    client_name = result.client[0]
    server_address = result.client[1]
    server_port = result.client[2]
    client_port = result.client[3]

    ip_address_pattern = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')

    if not ip_address_pattern.match(server_address):
        raise ArgsException

    return {
        'client_name': client_name,
        'server_address': server_address,
        'server_port': server_port,
        'client_port': client_port
    }

class RegexTestCase(unittest.TestCase):
    def setUp(self):
        self.ip_address_pattern = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')

    def test_ip_address(self):
        match = self.ip_address_pattern.match("192.168.1.1")
        self.assertEqual(match.group(), "192.168.1.1")

    def test_bad_ip_address(self):
        match = self.ip_address_pattern.match("192.168..1")
        self.assertIsNone(match)

class CommandLineTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = create_parser()

    def test_server(self):
        args = ["-s", "1234"]
        result = self.parser.parse_args(args)
        self.assertEqual(result.server, "1234")

    def test_client(self):
        args = ["-c", "testName", "198.123.75", "1024", "2000"]
        result = self.parser.parse_args(args)
        self.assertEqual(result.client[0], "testName")
        self.assertEqual(result.client[1], "198.123.75")
        self.assertEqual(result.client[2], "1024")
        self.assertEqual(result.client[3], "2000")

    def test_extract_client_args(self):
        args = ["-c", "testName", "198.123.75.45", "1024", "2000"]
        result = self.parser.parse_args(args)
        extracted_results = extract_client_args(result)
        self.assertEqual(extracted_results['client_name'], "testName")
        self.assertEqual(extracted_results['server_address'], "198.123.75.45")
        self.assertEqual(extracted_results['server_port'], "1024")
        self.assertEqual(extracted_results['client_port'], "2000")

    def test_validate_client_args(self):
        args = self.parser.parse_args("-c abc 112341 1024 1024".split())
        self.assertRaises(ArgsException, extract_client_args, args)

        args = self.parser.parse_args("-c abc 192.168..1 1024 1024".split())
        self.assertRaises(ArgsException, extract_client_args, args)

        args = self.parser.parse_args("-c abc 19268..1 1024 1024".split())
        self.assertRaises(ArgsException, extract_client_args, args)



if __name__ == "__main__":
    unittest.main()
    # main()