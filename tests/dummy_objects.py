import pickle
import socket
import threading


class dummy_server:
    """
    represent dummy server
    hold the critical fields so we could check the client methods without const a real server
    """
    def __init__(self):
        # just vars
        self.conn, self.addr = None, None

    def operate_tcp(self, flag):
        """
        opens server socket_TCP
        run one of the accepting functions that shall connect to the client when its will raise up
        :param flag: 1,2 - amount of packet that shall be sent from client, 0 - just accept the connection but nothing more
        """
        self.host = "127.0.0.1"  # ip of server (local!)
        self.port = 9090
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
        self.server.bind((self.host, self.port))  # activate socket
        self.server.listen(15)  # gap of users to be logged in in parallel
        if flag == 1:
            self.th = threading.Thread(target=self.accepting1)  # listening to client messages
            self.th.start()
        elif flag == 2:
            self.th = threading.Thread(target=self.accepting2)  # listening to client messages
            self.th.start()
        elif flag == 0:
            self.th = threading.Thread(target=self.accepting0)  # listening to client messages
            self.th.start()

    def accepting0(self):
        """ as writen at operate_tcp function about flag = 0  """
        self.conn, self.addr = self.server.accept()

    def accepting1(self):
        """ as writen at operate_tcp function about flag = 1  """
        self.conn, self.addr = self.server.accept()
        self.data1 = self.conn.recv(4096)  # waiting to recv msg
        self.packet1 = pickle.loads(self.data1)  # xfer the bytes to message

    def accepting2(self):
        """ as writen at operate_tcp function about flag = 2  """
        self.conn, self.addr = self.server.accept()
        self.data1 = self.conn.recv(4096)  # waiting to recv msg
        self.packet1 = pickle.loads(self.data1)  # xfer the bytes to message
        self.data2 = self.conn.recv(4096)  # waiting to recv msg
        self.packet2 = pickle.loads(self.data2)  # xfer the bytes to message

    def send_packet(self, packet, client_sock: socket):
        """ send packet to socket that r a client waiting to reply"""
        data_string = pickle.dumps(packet)
        client_sock.send(data_string)