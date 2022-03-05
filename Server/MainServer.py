import socket
import threading
import pickle
import os
import time
from Server.ServerGUI import ServerGUI
import IPRequester


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

    def __init__(self, flag):
        if flag == 0:
            self.flag = 0
            self.test_const()
        else:
            self.flag = 1
            self.real_const()

    def real_const(self):
        """ constructor """
        # basic fields

        ipConfirmed = False
        ipText = ""
        while not ipConfirmed:
            try:
                ipRequest = IPRequester.IPRequester().proceed(ipText)
                if ipRequest == "":
                    return
                self.ports = {9091: True}
                self.__host = ipRequest  # ip of server (local!)
                self.__port = 9090
                self.active = True
                # check option if it fails

                self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
                self.__server.bind((self.__host, self.__port))  # activate socket
                  # gap of users to be logged in in parallel
                ipConfirmed = True
            except:
                ipText = "Connection failed, please try again"
        self.__server.listen(15)
        self.clients_list = []
        self.threads_list = []  # all the open threads
        self.files = os.listdir("Files") # get files names

        # ------- const gui of server ----------
        self.gui = ServerGUI(self)
        self.GuiThread = threading.Thread(target=self.gui.basicGUI)
        self.GuiThread.daemon = True
        self.GuiThread.start()
        # ------- end of gui issues -----------

        self.socketThread = threading.Thread(target=self.activate)
        self.socketThread.daemon = True
        self.socketThread.start()
        #self.activate()
        while self.active:
            time.sleep(0.1)

    def activate(self):
        """
        this function is PART OF THE CONSTRUCTOR!!!
        activating the client
        waiting to users to log in
        """
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
                if c.active == True or packet[0] == "serverDown":
                    c.client_sock.send(data_string)
        except Exception as e:
            self.terminate_client(c)
            if len(self.clients_list) > 0:
                self.send_broadcast_tcp(packet)
            else:
                return

    def private(self, packet):
        """
        sending message to specific client
        :param packet: tupple with the details, packet[0] - type, packet[1] - data, packet[2] - address
        :return: True for sent, False for unsent
        """
        address = packet[2]
        for c in self.clients_list:  # search for the address client
            if address == c.name:
                data_string = pickle.dumps(packet)
                try:
                    c.client_sock.send(data_string)
                    return True
                except:
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

    def endServer(self):
        """
        closing server and all of its connection
        """
        packet_serverDown = ("serverDown",)

        self.send_broadcast_tcp(packet_serverDown)  # inform client that server is down
        time.sleep(0.1)
        self.active = False

        for single_client in self.clients_list:  # closing all clients sockets
            single_client.client_sock.close()

        self.__server.close()
        if self.flag != 0:
            exit(0)

    def sendIinitialData(self):
        """
        arrange and send update to users about all the loged in clients
        """
        list = self.updateUsers()

        initialData = ("initialData", self.files,list)
        self.send_broadcast_tcp(initialData)  # send the update to all the client users

    def updateUsers(self):
        """
        arrange and send update to users about all the loged in clients
        """
        list = []
        for c in self.clients_list:  # make list of all active clients
            if c.active == True:
                list.append(c.name)

        return list

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

    def fetchFile(self, filename, fileExtension, client, requester):
        """
        start the executing of "downloading" process:
            this func open the choosen file, and split it to segments of 1024 bytes(1kb)
            ALL the segments stocked into a dict, marked with serial number (key from 0 to [file_size/1024])

        then, sending this segments to the "file sender" function which executing the algorithm
            that responsible on the sending flow and Congetion control
        :param filename: string name
        :param client: requester_socket
        :param requester:  single_client.name
        :return:
        """

        size = os.path.getsize("Files/" + filename + fileExtension)
        segments = {}
        s = 0
        try:
            with open("Files/" + filename + fileExtension, "rb") as file:  # reading bytes!
                c = 0
                while c <= size:
                    data = file.read(1024)  # 1kb
                    if not data:  # end of file
                        break
                    segments[s] = data  # set into the dict
                    s += 1
                    c += len(data)
        except Exception as e:
            print(str(e))

        self.fileSender(client, filename, size, s, segments,
                        requester, fileExtension)  # continue to send this file via the algorithm <3

    def portAssigner(self):
        """
        search for available port (which didnt taken) for the downloading process
        :return: available port
        """
        port_num = 0  # field in the list of ports that we gonna return to user
        for p in self.ports.keys():  # loop over all ports
            if (self.ports[p]):
                self.ports[p] = False
                return p
            else:
                port_num = p

        port_num += 1
        self.ports[port_num] = False
        return port_num

    def fileSender(self, client, filename, size, numberOfSegments, segments, requester, fileExt):
        """
        this func create udp socket with the client, and start to send the segments via the next algo

        Algorithm description:
        first, define few parameters: cwindow - how many packets the algo allow to send in one iterate
                                        ackcounter - how many acks received from client
                                        maxwindow - wont allow to cwindow to cross this limit of window
                                        threshold - from that point the increase of cwindow will be linear in place of exponential
            iterating over all segments for each iteration, do:
                1. trying to send "cwindow" amount of segments
                2. waiting to see if all of the segments received at the client (via get "ack")
                3. increase/decrease or no change of the cwindow via the next rules:
                        a. got ack to all the segments:
                            a.1 - cwindow < threshold -> cwindow size increase by 2 (*2)
                            a.2 - cwindow > threshold && cwindow < maxwindow -> cwindow size +1
                            a.3 cwindow > threshold && > maxwindow -> cwindow size unchanged
                        b. didnt got ack to all the segments:
                            decrease: maximum(1, cwindow/2)
                4. when all the segments received at the client -> notify about that to the client and close socket, free port


        :param client: tcp_socket of specific client
        :param filename: file_name
        :param size: file_size
        :param numberOfSegments: to how many segments we splited the file with the fetch_file func (constant parmeter)
        :param segments: dict with all the segments (represent the segments which didnt got ack)
        :param requester: client_name
        :return:
        """
        udp = None
        port = None
        host = self.__host
        try:
            # open udp socket
            udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # lock since we dont want a conflict on number of ports
            threadLock = threading.Lock()
            threadLock.acquire()
            port = self.portAssigner()  # init the free port number
            threadLock.release()

            host = self.__host  # ip for the udp connection
            udp.bind((host, port))  # activate socket
            packet = ("udp", filename, size, numberOfSegments, host, port, fileExt)  # prepare packet <- with details of the connection
            data_string = pickle.dumps(packet)
            client.send(data_string)
            message, address = udp.recvfrom(1024)  # expecting to: ("ready", time.time())
            serverAck = ("ack",)
            ackPcket = pickle.dumps(serverAck)
            udp.sendto(ackPcket, address)
            currentTime = time.time()

            """----------------------------------------------- ALGORITHM ------------------------------------------------"""

            opened_data = pickle.loads(message)
            rtt = (currentTime - opened_data[1]) * 3  # taking time of the first packet sent to get appx time
            parameters = [1, 0, 32, 16]  # cwindow counter, ackCounter, maxWindow, therehold
            proceedOrCnacel = [0]  # flag 1 == none occures about proceed/cancel  2 == proceed, means to continue the download, 3 == the client canceled the download

            ackThread = threading.Thread(target=self.ackReceiver, args=(
                parameters, udp, segments, proceedOrCnacel, requester, filename, fileExt))  # responsible to update about "ack" from client, look in decp of func
            ackThread.daemon = True
            ackThread.start()

            packet_sent_counter = 0
            while (len(segments) > 0):  # iterate as long as there is still segments that not got to the client
                parameters[1] = 0  # ackcounter = 0

                all_keys = []  # all segments that shall be sent
                for key in segments.keys():
                    all_keys.append(key)

                for i in range(0, parameters[0]):  # gonna send "cwindow" times of segments

                    if (packet_sent_counter == numberOfSegments // 2):  # got to halfway
                        segment2 = ("halfway",)
                        data_string2 = pickle.dumps(segment2)
                        udp.sendto(data_string2, address)
                        tt = 0
                        while proceedOrCnacel[0] == 0 or proceedOrCnacel[0] == 1:
                            if(proceedOrCnacel[0] == 0):
                                udp.sendto(data_string2, address)
                            time.sleep(1)

                        # if procOrCancel[0] == 2 - there is nothing to do, just continue!

                        if (proceedOrCnacel[0] == 3):  # canceled
                            self.endFileClosing(udp, host, port)  # terminate the downloading
                            return

                    packet_sent_counter += 1

                    if (i >= len(segments)):  # there is no segments to send anymore (for ex we window size is 10, but there was only 5 segments left)
                        break

                    #segment = (all_keys[i], segments[all_keys[i]])  # segment[0] - serial num, segment[1] - data
                    #data_string = pickle.dumps(segment)
                    #udp.sendto(data_string, address)

                    if all_keys[i] in segments:
                        segment = (all_keys[i], segments[all_keys[i]])  # segment[0] - serial num, segment[1] - data
                        data_string = pickle.dumps(segment)
                        udp.sendto(data_string, address)
                    else:
                        continue

                    time.sleep(0.001)  # avoid from common bug - recv can merge bet 2 packets if its recived in the exact same time

                time.sleep(rtt)  # let receiver the appx time to get the packets

                if (parameters[1] < parameters[0]):  # if number of acks < cwindow - means some acks were not recived
                    # parameters: cwindow counter, ackCounter, maxWindow, therehold
                    parameters[0] = max(1, parameters[0] // 4)   # func to reduce the window -> maximum(1, cwindow/2)
                    # 3//2 = 1
                    # 3/2 = 1.5
                    pass
                elif (parameters[1] < parameters[3]):  # if all acks recieved, and we are yet to reach threshold
                    parameters[0] *= 2
                elif (parameters[1] < parameters[2]):  # if all acks recieved, and we passed thresgold, but yet to
                    # reach max window
                    parameters[0] += 1
                elif (parameters[1] == parameters[2]):
                    pass
                else:
                    parameters[0] = 1
                    parameters[3] //= 2

            self.gui.insertUpdates(str(requester) + " completed download of " + str(filename + fileExt))  # print in gui
            self.endFileClosing(udp, host, port)  # "clean the mess", close socket, free port etc..

        except Exception as e:
            print(str(e))
            self.endFileClosing(udp, host, port)
            self.send_broadcast_tcp(("downloadFailed",))

    def ackReceiver(self, parameters, udp, segments, proceedOrCancel, requester, filename, fileExt):
        """
        orginizing "acks" from client
        this function help the algorithm to be updated at any moment about which segment pakcet got "ack" (sent successfully to the client)
        :param parameters: how many segments got ack till now
        :param udp: socket with the client
        :param segments: dict of all segments that didnt got ack yet
        :param proceedOrCancel: flag: 2 == proceed, means to continue the download, 3 == the client canceled the download
        :param requester: client name
        :param filename: file name
        :return:
        """
        while True:

            try:
                message, address = udp.recvfrom(1024)  # waiting to get packet from client
            except:
                return
            ack = pickle.loads(message)  # make that packet back to tupple
            if (ack[0] == "ack"):  # got ack from client
                try:
                    del segments[ack[1]]
                    parameters[1] += 1
                except:
                    continue

            elif (ack[0] == "halfwayAck"):
                """server knows client knows that client has to chose if to continue download
                or cancel it"""
                if proceedOrCancel[0] == 0:
                    proceedOrCancel[0] = 1
            elif (ack[0] == "halfway"):
                """server got response from client if to proceed or cancel file download"""
                if ack[1] == "proceed":
                    proceedOrCancel[0] = 2
                    proceedAckPacket = ("proceedAck",)
                    data_string = pickle.dumps(proceedAckPacket)
                    udp.sendto(data_string, address)
                else:
                    proceedOrCancel[0] = 3
                    self.gui.insertUpdates(str(requester) + " canceled download of " + str(filename + fileExt))
            elif(ack[0] == "ready"):
                """in case we got extra ready packets (as client may send more than one due to unstable
                communication), we ignore the extras"""
                pass
            else:
                break
        """----------------------------------------------- ALGORITHM ------------------------------------------------"""

    def endFileClosing(self, udp, host, port):
        """
        the server inform itself that the file download ended (soft way to inform thread without harsh interupt)
        :param udp: udp socket
        :param host: ip_server
        :param port: port_socket
        """
        self.ports[port] = True
        notack = ("notack",)
        notack_data = pickle.dumps(notack)
        udp.sendto(notack_data, (host, port))
        udp.close()


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
                    list = self.updateUsers()
                    packet = ("update",list)
                    self.send_broadcast_tcp(packet)

                elif packet[0] == "download":  # download
                    # starting in another thread the process of downloading with the client
                    fileNameandExtension = packet[1].split(".")
                    fileNameandExtension[1] = "." + fileNameandExtension[1]
                    fileSenderThread = threading.Thread(target=self.fetchFile,
                                                        args=(fileNameandExtension[0],fileNameandExtension[1], client_socket, currentClient.name))
                    fileSenderThread.daemon = True
                    fileSenderThread.start()
                    self.gui.insertUpdates(
                        str(currentClient.name) + " downloading " + str(packet[1]))  # inform gui to print it

                elif (packet[0] == "filesRequest"):
                    # reply all the available files to be downloaded
                    packet = ("filesRequest", self.files)
                    files = pickle.dumps(packet)
                    client_socket.send(files)

                elif(packet[0] == "initialStart"):
                    self.sendIinitialData()

                elif (packet[0] == "private"):
                    if (self.private(packet)):
                        data = pickle.dumps(packet)
                        client_socket.send(data)
                    else:
                        error = ("error",)
                        data = pickle.dumps(error)
                        client_socket.send(data)

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
                    data = pickle.dumps(answer)
                    client_socket.send(data)  # reply to client

            except Exception as e:
                print(str(e))
                self.terminate_client(currentClient)
                break

    def test_const(self):
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

        class dummy_GUI:
            def __init__(self, server):
                self.server = server

            def insertUpdates(self, notification):
                pass

        self.gui = dummy_GUI(self)

        thh = threading.Thread(target=self.activate)
        thh.start()
