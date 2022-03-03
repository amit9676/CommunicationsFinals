import socket
import threading
import pickle
import os
import time
from Server.ServerGUI import ServerGUI


class SingleClient:
    """
    this class represent single client
    we use this "shallow" class to stock fields of same client within one obj
    """

    def __init__(self, id, client, name):
        self.id = id  # serial num
        self.client_sock = client  # socket_tcp with the client
        self.name = name  # name of client (string)

        # flag: True - part of the clients in the chat room:
        #       False - connected client, but didnt loged yet to the chat room
        self.active = False


class Server:
    """
    this class is a SINGLETON
    from its name, this is the server class
    the server opens TCP sockets and allow to clients to connect
    all the clients are
    """

    def __init__(self):
        """ constructor """
        # basic fields
        self.ports = {9091: True}
        self.__host = "127.0.0.1"  # ip of server (local!)
        self.__port = 9090
        self.active = True
        # check option if it fails

        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
        self.__server.bind((self.__host, self.__port))  # activate socket
        self.__server.listen(15)  # gap of users to be logged in in parallel
        self.clients_list = []
        self.threads_list = []  # all the open threads
        self.files = ["one", "two", "three"]  # files in the server

        # ------- const gui of server ----------
        self.gui = ServerGUI(self)
        self.GuiThread = threading.Thread(target=self.gui.basicGUI)
        self.GuiThread.daemon = True
        self.GuiThread.start()
        # ------- end of gui issues -----------

        self.activate()

    def send_broadcast_tcp(self, packet):
        """
        sending via tcp socket (broadcast msg - msg to all active clients)
        :param single_client:  address client
        :param packet: tupple (String-type of message, message_data)
        """
        data_string = pickle.dumps(packet)
        c = None
        try:
            for client in self.clients_list:
                c = client
                if c.active == True:
                    c.client_sock.send(data_string)
        except Exception as e:
            self.terminate_client(c)
            if len(self.clients_list) > 0:
                self.send_broadcast_tcp(packet)
            else:
                return

    def send_private_tcp(self, packet, address):
        """
        sending via tcp socket (private msg - msg to specific client)
        :param address: whom to be sent
        :param packet: tupple to be sent
        :return: True - sent, False - didnt sent
        """
        data_string = pickle.dumps(packet)
        for c in self.clients_list:
            if (address == c.name):
                try:
                    c.client_sock.send(data_string)
                    return True
                except Exception as e:
                    self.terminate_client(c)
                    break
            return False

    def terminate_client(self, client: SingleClient):
        """
        connection with client is done, free all the data of that client
        :param client: the relevant client
        """
        client.client_sock.close()  # close sockets

        # gui issues
        notification = str(client.name) + " left the chat"
        self.gui.insertUpdates(notification)
        self.clients_list.remove(client)

        # notify users
        self.updateUsers()

    def activate(self):
        """
        activating the client
        waiting to users to log in
        """
        print('Ready to serve..')
        counter = 1

        while self.active:
            try:
                client, address = self.__server.accept()  # waiting for client to connect
                newClient = SingleClient(counter, client, "undefined")  # stock client data
                self.clients_list.append(newClient)
                th = threading.Thread(target=self.clientListen, args=(client,))  # listening to client messages
                th.daemon = True
                th.start()
            except:
                print("Server Disconnected")

    def endServer(self):
        """
        closing server and all of its connection
        """
        packet_serverDown = ("serverDown",)

        self.send_broadcast_tcp(packet_serverDown)  # inform client that server is down
        self.active = False

        for single_client in self.clients_list:  # closing all clients sockets
            single_client.client_sock.close()

        self.__server.close()
        exit(0)

    def updateUsers(self):
        """
        arrange and send update to users about all the loged in clients
        """
        list = ["update"]
        for c in self.clients_list:  # make list of all active clients
            if c.active == True:
                list.append(c.name)

        self.send_broadcast_tcp(list)  # send the update to all the client users

    def validate(self, name, requester: SingleClient):
        """
        validate process, verify that client name is valid and can be connect
        :param name: name that client_user decided
        :param requester: which client
        :return: False if name is taken, True - user can get that name
        """
        for c in self.clients_list:
            if c.active == True and c.name == name:  # there is name taken?
                return False

        # edit requester client fields
        requester.active = True
        requester.name = name
        return True

    def fetchFile(self, filename, client, requester):
        size = os.path.getsize("Files/" + filename + ".txt")
        segments = {}
        s = 0
        try:
            with open("Files/" + filename + ".txt", "rb") as file:
                c = 0
                while c <= size:
                    data = file.read(1024)
                    if not data:
                        # print("!!")
                        break
                    segments[s] = data
                    s += 1
                    c += len(data)
            self.fileSender(client, filename, size, s, segments, requester)
        except Exception as e:
            print(str(e))

    def portAssigner(self):
        t = 0
        for p in self.ports.keys():
            if (self.ports[p]):
                self.ports[p] = False
                return p
            else:
                t = p

        t += 1
        self.ports[t] = False
        return t

    def fileSender(self, client, filename, size, numberOfSegments, segments, requester):
        # print(f"nof: {numberOfSegments}")
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        threadLock = threading.Lock()
        threadLock.acquire()
        port = self.portAssigner()
        threadLock.release()
        host = "127.0.0.2"
        udp.bind((host, port))
        packet = ("udp", filename, size, numberOfSegments, host, port)
        data_string = pickle.dumps(packet)
        client.send(data_string)

        message, address = udp.recvfrom(1024)  # expect ("ready", time.time())
        currentTime = time.time()
        # future note - do something if initial upd establishment fails

        """----------------------------------------------- ALGORITHM ------------------------------------------------"""

        openeddata = pickle.loads(message)
        rtt = (currentTime - openeddata[1]) * 3
        parameters = [1, 0, 32, 16]  # cwindow counter, ackCounter, maxWindow, therehold
        proceedOrCnacel = [1]

        ackThread = threading.Thread(target=self.ackReciever, args=(
            parameters, currentTime, rtt, udp, segments, proceedOrCnacel, requester, filename))
        ackThread.daemon = True
        ackThread.start()
        k = 0
        while (len(segments) > 0):

            parameters[1] = 0

            allKyes = []
            for key in segments.keys():
                allKyes.append(key)
            for i in range(0, parameters[0]):
                if (k == numberOfSegments // 2):
                    segment2 = ("halfway",)
                    data_string2 = pickle.dumps(segment2)
                    udp.sendto(data_string2, address)
                    while proceedOrCnacel[0] == 1:
                        pass
                    if (proceedOrCnacel[0] == 3):
                        self.endFileClosing(udp, host, port)
                        return
                k += 1
                if (i >= len(segments)):
                    break
                segment = (allKyes[i], segments[allKyes[i]])
                data_string = pickle.dumps(segment)
                udp.sendto(data_string, address)

                time.sleep(0.001)

            currentTime = time.time()

            time.sleep(rtt)
            # print(f"parametsrs: {parameters}")
            if (parameters[1] < parameters[0]):
                parameters[0] = max(1, parameters[0] // 4)  # func to reduce the window -> maximum(1, cwindow/2)
                # 3//2 = 1
                # 3/2 = 1.5
                pass
            elif (parameters[1] < parameters[3]):
                parameters[0] *= 2
            elif (parameters[1] < parameters[2]):
                parameters[0] += 1
            elif (parameters[1] == parameters[2]):
                pass
            else:
                parameters[0] = 1
                parameters[3] //= 2

        self.gui.insertUpdates(str(requester) + " completed download of " + str(filename))
        self.endFileClosing(udp, host, port)

    def ackReciever(self, parameters, currentTime, rtt, udp, segments, proceedOrCnacel, requester, filename):
        # while (parameters[1] < parameters[0] and time.time() - currentTime < (rtt * parameters[0])):
        while True:
            try:
                message, address = udp.recvfrom(1024)
            except:
                return
            ack = pickle.loads(message)
            if (ack[0] == "ack"):
                try:
                    del segments[ack[1]]
                    parameters[1] += 1
                except:
                    continue
                # if (parameters[1] == parameters[0]):
                #     print("flow")
            elif (ack[0] == "halfway"):
                if ack[1] == "proceed":
                    proceedOrCnacel[0] = 2
                else:
                    proceedOrCnacel[0] = 3
                    self.gui.insertUpdates(str(requester) + " canceled download of " + str(filename))
            else:
                break
        print("reciever Done")
        """----------------------------------------------- ALGORITHM ------------------------------------------------"""

    def endFileClosing(self, udp, host, port):
        notack = ("notack",)
        notack_data = pickle.dumps(notack)
        udp.sendto(notack_data, (host, port))
        print("done")
        udp.close()
        self.ports[port] = True

    def clientListen(self, client_socket):
        """
        this method will work for every new client that connected, for its entire life (as seprate thread)
        :param client_socket: relevant client
        """
        # looking for the SingleClient obj in the client_list via its socket (every socket is unique)
        currentClient = None
        for c in self.clients_list:
            if c.client_sock == client_socket:
                currentClient = c
                break

        while self.active:
            try:
                data = client_socket.recv(4096)  # waiting to recv msg
                packet = pickle.loads(data)  # xfer the bytes to message

                # "switch case": for every type of message, do chain of actions
                if (packet[0] == "broadcast"):  # broadcast
                    self.send_broadcast_tcp(packet)

                elif (packet[0] == "update"):  # update
                    self.updateUsers()

                elif packet[0] == "download":  # download
                    # starting in another thread the process of downloading with the client
                    fileSenderThread = threading.Thread(target=self.fetchFile,
                                                        args=(packet[1], client_socket, currentClient.name))
                    fileSenderThread.daemon = True
                    fileSenderThread.start()

                    self.gui.insertUpdates(
                        str(currentClient.name) + " downloading " + str(packet[1]))  # inform gui to print it

                elif (packet[0] == "filesRequest"):
                    # reply all the available files to be downloaded
                    packet = ("filesRequest", self.files)
                    self.send_private_tcp(packet, client_socket)

                elif (packet[0] == "private"):
                    if (self.send_private_tcp(packet, packet[2])):
                        self.send_private_tcp(packet, client_socket)
                    else:
                        error = ("error",)
                        self.send_private_tcp(error, client_socket)

                elif (packet[0] == "validate"):
                    answer = None
                    if self.validate(packet[1], currentClient) == True:
                        answer = ("validate", True)

                        # to gui, print validate data
                        joiner = str(currentClient.name) + " has joined the chat"
                        self.gui.insertUpdates(joiner)
                        # end gui command

                    else:
                        answer = ("validate", False)
                    self.send_private_tcp(answer, client_socket)

            except Exception as e:
                print(str(e))
                self.terminate_client(currentClient)
                break
