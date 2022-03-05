import socket
import threading
import pickle
import time
import tkinter.filedialog

import IPRequester
from Client import ClientGUI

Host = "localhost"
PORT = 9090


class Client:
    """
    this class represent a Client obj.

    ----------------    general info: -----------------

    the class connected to the Server, via TCP socket for every kind of communication beside downloading files.
        for downloading files, the Client opens a dedicated UDP socket with the server that support this proccess
        the client contact only with the server and not with another clients directly!!

    ---------------- supported operations: ------------------
    operations that the client supports with the server:
        1. start connection with the server, basis on TCP socket
        2. Validate - identification of the user, the user input his name to be able to log into the chat room of the server
        3. updates - can get via "push" messages from the server update about new messages and users, but also can ask for those updates.
        4. files request - can ask the server to start download an available files from the server
        5. error - can notify the server about errors that occured.
        6. udp - shall xfer communication to udp to start downloading file with server
        7. shut down - server is down
        8. sending and receiving brodcast and private messages
    """

    def __init__(self, flag):
        if (flag == 0):
            self.flag = 0
            self.test_const()
        else:
            self.flag = 1
            self.real_const()

    def real_const(self):
        """
                constructor of client
                connecting to the server via TCP connection
                construct the gui and hold a pointer to the gui obj of the client
                """


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

                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
                self.sock.connect((self.__host, self.__port))  # activate socket
                # gap of users to be logged in in parallel
                ipConfirmed = True
            except:
                ipText = "Connection failed, please try again"



        # open socket and connect to server
        #self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.sock.connect((Host, PORT))

        # recieve thread is always listening to new packets that can be get from server
        self.recieveThread = threading.Thread(target=self.receive)
        self.recieveThread.daemon = True
        self.isActive = True  # flag, activity of client
        self.recieveThread.start()
        self.name = ""  # this var holds the client name

        # vars for downloading proccess
        self.files = [""]
        self.currentFile = ""
        self.cancel_proceed_switch = 1  # condition switch: 1 == waiting to client to click proceed/cancel, 2 == user
        # clicked proceed, 3 == user clicked cancel

        # const gui and init name for client stage
        self.initGui = True  # flag, init == initialize process
        self.confirmedName = "Waiting"  # flag for validation name of client
        self.gui = ClientGUI.GUI(self)
        self.gui.nameRequest()
        self.initGui = False
        print("connect")
        self.GuiThread = threading.Thread(target=self.gui.basicGUI)

        # "had peami" thread. start once within the constructing of the connection with the server and const the gui
        self.updateThread = threading.Thread(target=self.requestInitialData)
        self.updateThread.daemon = True

        # activate threads
        self.GuiThread.start()
        self.updateThread.start()

    def requestInitialData(self):
        """
        this function activates once, only with creating the client obj, its gui, and starting the connection with the server
        this func asks the server for 2 details: who is the active users right now
        in the chat and which files are available to be downloaded right now
        :return:
        """
        while not self.gui.GuiDone:  # guiDone is flag, waiting for gui window to be constructed
            pass
        initialPacket = ("initialStart",)
        self.send_packet_tcp(initialPacket)

    def send_packet_tcp(self, packet):
        """
        given a packet, the function send it to the server, sending via the tcp socket
        :param packet: packet is a tupple of two obj, packet[0] - string, represent the action we request from the server, packet[1] - the data
        """
        try:
            data_string = pickle.dumps(packet)
            self.sock.send(data_string)
        except Exception as e:
            print(str(e))
            self.stop()

    def sendToServer(self, message, address):
        """
        this function is activating from the gui, via the user commands.
        sending the msg to the server, telling the server to deliver it to the address
        :param message: string
        :param address: string_name of the client, if this string is empty, this means broadcast msg
        """
        if address == "":
            packet = ("broadcast", self.name, message)
        else:
            packet = ("private", self.name, address, message)
        self.send_packet_tcp(packet)

    def ackRecieverUdp(self, udp, host, port, segments,fileAcceptingMode,size):
        """this function purpose is to listen to all incoming udp packets, and because
        communication may not always be relaiable, there are lots of them"""
        try:
            while fileAcceptingMode[0] != 3: #while we are accepting packets..
                message, address = udp.recvfrom(1124)  # waiting to recv packet from server
                packet = pickle.loads(message)
                if(packet[0] == "ack"):
                    #server knows we are connected, start recieving files!
                    fileAcceptingMode[0] = 1
                elif(packet[0] == "halfway"):
                    """server stopped sending, now client has to choose if to proceed file tansfer,
                    or cancel it"""
                    fileAcceptingMode[0] = 2
                    response = ("halfwayAck",)
                    data_string = pickle.dumps(response)
                    udp.sendto(data_string, (host, port))
                elif(packet[0] == "proceedAck"):
                    """server now knows client chose to proceed file transfer"""
                    fileAcceptingMode[0] = 1
                else:
                    """file data packet, add it to the collection"""
                    fileAcceptingMode[0] = 1
                    self.filePackedReieved(segments,packet,udp,host,port,size)
        except:
            pass


    def callrecieverThread(self,udp,host,port,segments,fileAcceptingMode,size):
        """activate seperate thread to function above"""
        ackThread = threading.Thread(target=self.ackRecieverUdp, args=(udp, host, port, segments,
                                                                       fileAcceptingMode,size))
        ackThread.daemon = True
        ackThread.start()

    def filePackedReieved(self,segments,segment,udp,host,port,size):
        """when udp packet is recieved, add it to list, and send ack to server"""
        segments[segment[0]] = segment[1]

        # updating gui, how many bytes has been downloaded
        currentsize = min(len(segments) * 1024,size)
        status = "downloading " + str(currentsize) + "/" + str(size) + " bytes"
        self.gui.downloadingInfo.set(status)

        response = ("ack", segment[0])
        data_string = pickle.dumps(response)
        udp.sendto(data_string, (host, port))

    def udp(self, filename, size, sizeOfSegments, host, port, fileExt):
        """
        open udp socket with the server and start to execute the recive file progress
        :param filename: string, which file we would like to download
        :param size: size of file
        :param sizeOfSegments: to how many "pieces" the file gonna be splited
        :param host: server ip
        :param port: to connect
        """
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # create socket
        reqTime = time.time()  # stamp of time of start, help for server cals

        # prepare packet
        packet = ("ready", reqTime)
        data_string = pickle.dumps(packet)

        # send packet
        print("client sent")
        fileAcceptingMode = [0]
        """current file transfer mode"""
        #0 = not established udp yet
        #1 recieving files
        #2 = waiting, proceed or cancel
        #3 = we are done accepting packets

        segments = {}
        self.callrecieverThread(udp, host, port, segments,fileAcceptingMode,size)
        #activate seperate thread for udp listener

        """the reason this while loop is nesesary, is because the udp packet may get lost,
        so as long we didnt get any ack from the server, we repeatedly send ready packet
        every second"""
        while(fileAcceptingMode[0] == 0):
            udp.sendto(data_string, (host, port))
            time.sleep(1)


        self.recieveFile(filename, size, udp, sizeOfSegments, host, port, segments, fileExt,fileAcceptingMode)
        """this function manage the recieving operation, works with the same time with the
        ackRecieverUdp function"""

        udp.close()  # end of progress

    def recieveFile(self, filename, size, udp, sizeOfSegments, host, port, segments, fileExt,fileAcceptingMode):
        # print(f"active threads: {threading.active_count()}")
        """
        responsible manage the file recieving operation
        :param filename: String_name
        :param size: in bytes of the downloading file
        :param udp: socket
        :param sizeOfSegments: how many segments the file gonna split into
        :param host: server ip
        :param port: of the connection
        :param segments: dict that gonna hold all the segments of the file
        """

        while len(segments) < sizeOfSegments:
            # iterating as long as the file keep downloading


            if (fileAcceptingMode[0] == 2):  # got to halfway of size of download
                # condition switch: 1 == waiting to client to click proceed/cancel, 2 == user
                # clicked proceed, 3 == user clicked cancel
                self.gui.halfway()
                fileAcceptingMode[0] = 2
                while self.cancel_proceed_switch == 1:
                    time.sleep(0.01)  # little side note avoiding from iterating with full power of the CPU
                    pass

                if (self.cancel_proceed_switch == 2):
                    halfWayAnswer = ("halfway", "proceed")
                    halfWayData = pickle.dumps(halfWayAnswer)
                    udp.sendto(halfWayData, (host, port))

                    """because communication may be unstable - we might need to send serveral
                     notfications to the server that we wish to proceed"""
                    while fileAcceptingMode[0]==2:
                        udp.sendto(halfWayData, (host, port))
                        time.sleep(1)

                    self.cancel_proceed_switch = 1

                if (self.cancel_proceed_switch == 3):
                    halfWayAnswer = ("halfway", "cancel")
                    halfWayData = pickle.dumps(halfWayAnswer)
                    udp.sendto(halfWayData, (host, port))
                    udp.close()
                    self.gui.downloadingInfo.set("download canceled")
                    self.cancel_proceed_switch = 1
                    fileAcceptingMode[0] = 3
                    return

            time.sleep(
                0.001)  # avoid from common bug - recv can merge bet 2 packets if its recived in the exact same time

        fileAcceptingMode[0] = 3
        self.create(filename, segments, fileExt)  # recv ended, shall merge the segments to one file

    def create(self, filename, segments, fileExt):
        """
        connect all the packets and make from them the whole file <3
        :param filename: string_name
        :param segments: dictionary, all the packets arranged as: key - serial number of the packet, value - the content
        """
        # for key in segments.keys():
        #     print(key)
        try:
            filePath = tkinter.filedialog.asksaveasfilename(
                                                            filetypes=[("Text file",".txt"),
                                                                       ("Photo",".jpg"),
                                                                       ("All files",".*"),])
            lastchar = "a"
            try:
                with open(filePath, "wb") as file:  # open new file
                    for i in range(0, len(segments)):
                        # loop over all the segments and copy the contents
                        file.write(segments[i])
                        if (i == len(segments) - 1):
                            lastchar = segments[i][-1]

                # transfer the data to gui to represent it
                self.gui.downloadingInfo.set("file downloaded, last byte is " + str(lastchar))
            except Exception as e:
                print("im here")
                print(str(e))
                self.gui.downloadingInfo.set("download canceled")
            self.gui.downloadButton["state"] = "normal"

        except Exception as e:
            print(str(e))

    def stop(self):
        """
        terminate the Client
        """
        self.isActive = False
        self.sock.close()
        if self.flag != 0:
            exit(0)

    def receive(self):
        """
        this function waiting to receive msg from the server.
        after receving a packet, the function will direct the message via its purpose
            * reminder: packet[0] represent the content of the data, so we can categorize the needed task from this field
        """
        while self.isActive:
            # options for packet[0]: broadcase, private, error, filesRequest, update, udp, validate, shut down
            try:
                data = self.sock.recv(1024)
                packet = pickle.loads(data)
                if packet[0] == "broadcast" and self.gui.GuiDone:  # command to gui to print the data as broadcast message
                    self.gui.insertMessage(packet[1] + " (broadcast): " + packet[2])
                elif packet[0] == "private" and self.gui.GuiDone:  # command to gui to print the data as private message
                    if self.name == packet[1]:
                        self.gui.insertMessage(packet[1] + " (to " + packet[2] + "): " + packet[3])
                    else:
                        self.gui.insertMessage(packet[1] + " (to you): " + packet[3])
                elif packet[0] == "error" and self.gui.GuiDone:  # command to gui to notify user: invalid message has been sent
                    self.gui.insertMessage("message could not be sent")
                elif packet[0] == "downloadFailed" and self.gui.GuiDone:  # command to gui to notify user: invalid message has been sent
                    self.gui.insertMessage("download attempt failed, please try again")
                    self.gui.downloadButton["state"] = "normal"
                # elif packet[0] == "filesRequest":  # start process of downloading file
                #     print("recieved")
                #     self.files = packet[1]
                #     self.gui.displayFiles()
                elif packet[0] == "update":  # an update of details from the server, command to gui to represent it to user
                    self.gui.insertUsers(packet[1])
                elif packet[0] == "initialData":
                    self.gui.insertUsers(packet[2])
                    self.files = packet[1]
                    self.gui.displayFiles()
                elif packet[0] == "udp":  # server is ready to start downloading process, shall xfer community to udp connection (start new thread for downloading file)
                    tempThread = threading.Thread(target=self.udp,
                                                  args=(packet[1], packet[2], packet[3], packet[4], packet[5],packet[6]))
                    tempThread.daemon = True
                    tempThread.start()
                elif packet[0] == "validate":  # validate process
                    if (packet[1] == True):
                        self.confirmedName = "True"
                    else:
                        self.confirmedName = "False"
                elif packet[0] == "serverDown":  # server got shut down
                    self.gui.disable()
                    self.gui.insertUsers(packet)

            except Exception as e:
                print(str(e))
                self.sock.close()
                break

    def test_const(self):
        """
                constructor of client for TESTS ONLY!!!!
        """
        # open socket and connect to server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((Host, PORT))

        # recieve thread is always listening to new packets that can be get from server
        self.recieveThread = threading.Thread(target=self.receive)
        self.recieveThread.daemon = True
        self.isActive = True  # flag, activity of client
        self.recieveThread.start()
        self.name = ""  # this var holds the client name

        # vars for downloading proccess
        self.files = [""]
        self.currentFile = ""
        self.cancel_proceed_switch = 1  # condition switch: 1 == waiting to client to click proceed/cancel, 2 == user
        # clicked proceed, 3 == user clicked cancel

        self.insertMessage = True
        self.insertUsers = 'update'
        class dummy_GUI:
            def __init__(self, client):
                self.downloadButton = None
                self.downloadingInfo = None
                self.GuiDone = False
                self.initGui = True
                self.initGui = False
                self.client = client

            def insertMessage(self, param):
                self.client.insertMessage = True

            def halfway(self):
                pass

            def disable(self):
                pass

            def insertUsers(self, packet):
                self.client.insertUsers = packet[0]

            def displayFiles(self):
                pass

        self.gui = dummy_GUI(self)
        # const gui and init name for client stage
        self.initGui = True  # flag, init == initialize process
        self.confirmedName = "Waiting"  # flag for validation name of client
        self.initGui = False


if __name__ == '__main__':
    c = Client(1)
