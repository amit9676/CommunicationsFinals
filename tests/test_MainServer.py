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
        time.sleep(0.01)
        try:
            server_test.send_broadcast_tcp(('broadcast', ))
        except:
            self.fail()
        server_test.endServer()
        time.sleep(0.01)
        client_test.stop()

    def test_private(self):
        """ test that the msg transfered from server to client """
        time.sleep(2)
        server_test = Server(0)
        client_test = Client(0)
        time.sleep(0.01)
        try:
            server_test.private(('private', None, '1'))
        except:
            self.fail()
        time.sleep(0.01)
        server_test.endServer()
        client_test.stop()

    def test_terminate_client(self):
        """ check that the server removing client that got closed """
        time.sleep(2)
        server_test = Server(0)
        client_test = Client(0)
        try:
            server_test.terminate_client(server_test.clients_list[0])
        except ValueError as e:
            pass
        except:
            self.fail()
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
        time.sleep(0.01)
        try:
            server_test.updateUsers()
        except:
            self.fail()
        time.sleep(0.01)
        server_test.endServer()
        client_test.stop()

    def test_validate(self):
        """ check that func is sending packet of validate process """
        time.sleep(2)
        server_test = Server(0)
        client_test = Client(0)
        time.sleep(0.01)
        try:
            server_test.validate('check', server_test.clients_list[0])
        except:
            self.fail()
        time.sleep(0.01)
        server_test.endServer()
        client_test.stop()

    def test_port_assigner(self):
        """ check that func returns the currect empty port """
        time.sleep(2)
        server_test = Server(0)
        client_test = Client(0)
        time.sleep(0.01)
        try:
            p = server_test.portAssigner()
        except:
            self.fail()
        self.assertEqual(9091, p)
        server_test.endServer()
        client_test.stop()