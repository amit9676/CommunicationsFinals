import pickle
import socket
import time
from unittest import TestCase

from Client.MainClient import Client
from Server.MainServer import Server
from tests.dummy_objects import dummy_server


class TestClient(TestCase):

    def test_request_initial_data(self):
        """
            check that function send the needed packet
        """
        time.sleep(2)
        server_test = dummy_server()
        server_test.operate_tcp(2)
        client_test = Client(0)
        client_test.gui.GuiDone = True
        time.sleep(0.01)
        client_test.requestInitialData()
        time.sleep(0.01)
        self.assertEqual('update', server_test.packet1[0])
        self.assertEqual('filesRequest', server_test.packet2[0])
        client_test.isActive = False
        client_test.stop()
        server_test.server.close()

    def test_send_packet_tcp(self):
        """
            check that function send the needed packet
        """
        time.sleep(2)
        server_test = dummy_server()
        server_test.operate_tcp(1)
        client_test = Client(0)
        client_test.gui.GuiDone = True
        time.sleep(0.01)
        client_test.send_packet_tcp(('broadcast', "hi world"))
        time.sleep(0.01)
        self.assertEqual('broadcast', server_test.packet1[0])
        self.assertEqual('hi world', server_test.packet1[1])
        client_test.isActive = False
        client_test.stop()
        server_test.server.close()

    def test_send_to_server(self):
        """
            check that function send the needed packet
        """
        time.sleep(2)
        server_test = dummy_server()
        server_test.operate_tcp(1)
        client_test = Client(0)
        client_test.gui.GuiDone = True
        time.sleep(0.01)
        client_test.sendToServer("hi world", "")
        time.sleep(0.01)
        self.assertEqual('broadcast', server_test.packet1[0])
        client_test.isActive = False
        server_test.server.close()
        client_test.stop()

    def test_stop(self):
        """ check that the client stops """
        time.sleep(2)
        server_test = dummy_server()
        server_test.operate_tcp(1)
        client_test = Client(0)
        client_test.gui.GuiDone = True
        server_test.th.join(0.5)
        packet = ('broadcast',)
        time.sleep(0.01)
        server_test.send_packet(packet, client_test.sock)
        time.sleep(0.01)
        client_test.stop()
        try:
            client_test.sock.send(pickle.dumps(packet))
            self.fail()
        except:
            server_test.server.close()
            pass

    def test_receive(self):
        """
            check that function send the needed packet
        """
        time.sleep(2)
        server_test = dummy_server()
        server_test.operate_tcp(1)
        client_test = Client(0)
        client_test.gui.GuiDone = True
        server_test.th.join(0.5)
        time.sleep(0.01)
        packet = ('broadcast',)
        server_test.send_packet(packet, client_test.sock)
        time.sleep(0.01)
        packet = ('private',)
        server_test.send_packet(packet, client_test.sock)
        time.sleep(0.05)
        self.assertTrue(client_test.insertMessage)
        self.assertEqual('update', client_test.insertUsers)
        client_test.isActive = False
        client_test.stop()
        server_test.server.close()
