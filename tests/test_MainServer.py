import time
from unittest import TestCase

from Client.MainClient import Client
from Server.MainServer import Server


class TestServer(TestCase):
    def test_send_broadcast_tcp(self):
        """ test that the msg transfered from server to client """
        time.sleep(2)
        server_test = Server(0)
        client_test = Client(0)
        server_test.send_broadcast_tcp(('broadcast', ))
        server_test.endServer()
        client_test.stop()

    def test_private(self):
        """ test that the msg transfered from server to client """
        time.sleep(2)
        server_test = Server(0)
        client_test = Client(0)
        server_test.private(('private', None, '1'))
        server_test.endServer()
        client_test.stop()

    def test_terminate_client(self):
        """ check that the server removing client that got closed """
        time.sleep(5)
        server_test = Server(0)
        client_test = Client(0)
        server_test.terminate_client(server_test.clients_list[0])
        server_test.endServer()
        client_test.stop()

    def test_end_server(self):
        """ check that func is closing from endServer command"""
        time.sleep(2)
        server_test = Server(0)
        server_test.endServer()

    def test_update_users(self):
        """ check that func send update user """
        time.sleep(2)
        server_test = Server(0)
        client_test = Client(0)
        server_test.updateUsers()
        server_test.endServer()
        client_test.stop()

    def test_validate(self):
        """ check that func is sending packet of validate process """
        time.sleep(2)
        server_test = Server(0)
        client_test = Client(0)
        server_test.validate('check', server_test.clients_list[0])
        server_test.endServer()
        client_test.stop()

    def test_port_assigner(self):
        """ check that func returns the currect empty port """
        time.sleep(2)
        server_test = Server(0)
        client_test = Client(0)
        p = server_test.portAssigner()
        self.assertEqual(9091, p)
        server_test.endServer()
        client_test.stop()