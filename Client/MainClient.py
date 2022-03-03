import socket
import threading
import pickle
import time
import ClientGUI

Host = "127.0.0.1"
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
            self.test_const()
        else:
            self.real_const()


    def real_const(self):
        """
                constructor of client
                connecting to the server via TCP connection
                construct the gui and hold a pointer to the gui obj of the client
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

        # const gui and init name for client stage
        self.initGui = True  # flag, init == initialize process
        self.confirmedName = "Waiting"  # flag for validation name of client
        self.gui = ClientGUI.GUI(self)
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
        this func asks the server for 2 details: who is the active users rn in the chat and which files is available to be downloaded rn
        :return:
        """
        while not self.gui.GuiDone:  # guiDone is flag, waiting for gui window to be constructed
            pass
        packet1 = ("update",)
        packet2 = ("filesRequest",)
        self.send_packet_tcp(packet1)
        time.sleep(0.001)
        self.send_packet_tcp(packet2)

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

    def udp(self, filename, size, sizeOfSegments, host, port):
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
        udp.sendto(data_string, (host, port))

        segments = {}
        self.recieveFile(filename, size, udp, sizeOfSegments, host, port, segments)

        udp.close()  # end of progress

    def recieveFile(self, filename, size, udp, sizeOfSegments, host, port, segments):
        # print(f"active threads: {threading.active_count()}")
        """
        responsible to get the packets of file from the server and
                resend to the server "ack" for each segment that has been arrived successfully
        :param filename: String_name
        :param size: in bytes of the downloading file
        :param udp: socket
        :param sizeOfSegments: how many segments the file gonna split into
        :param host: server ip
        :param port: of the connection
        :param segments: dict that gonna hold all the segments of the file
        """
        counter = 0  # how many segments arrived

        while len(segments) < sizeOfSegments:
            # iterating as long as the file keep downloading
            message, address = udp.recvfrom(1124)  # waiting to recv packet from server
            segment = pickle.loads(message)

            # updating gui, how many bytes has been downloaded
            status = "downloading " + str(counter * 1024) + "/" + str(size) + " bytes"
            self.gui.downloadingInfo.set(status)

            if (segment[0] == "halfway"):  # got to halfway of size of download
                # condition switch: 1 == waiting to client to click proceed/cancel, 2 == user
                # clicked proceed, 3 == user clicked cancel

                self.gui.halfway()
                while self.cancel_proceed_switch == 1:
                    time.sleep(0.01)  # little side note avoiding from iterating with full power of the CPU
                    pass

                if (self.cancel_proceed_switch == 2):
                    halfWayAnswer = ("halfway", "proceed")
                    halfWayData = pickle.dumps(halfWayAnswer)
                    udp.sendto(halfWayData, (host, port))
                    self.cancel_proceed_switch = 1

                if (self.cancel_proceed_switch == 3):
                    halfWayAnswer = ("halfway", "cancel")
                    halfWayData = pickle.dumps(halfWayAnswer)
                    udp.sendto(halfWayData, (host, port))
                    udp.close()
                    self.gui.downloadingInfo.set("download canceled")
                    self.cancel_proceed_switch = 1
                    return

            else:  # send ack since we got the packet
                segments[segment[0]] = segment[1]
                response = ("ack", segment[0])
                data_string = pickle.dumps(response)
                udp.sendto(data_string, (host, port))
                counter += 1

            time.sleep(
                0.001)  # avoid from common bug - recv can merge bet 2 packets if its recived in the exact same time

        self.create(filename, segments)  # recv ended, shall merge the segments to one file

    def create(self, filename, segments):
        """
        connect all the packets and make from them the whole file <3
        :param filename: string_name
        :param segments: dictionary, all the packets arranged as: key - serial number of the packet, value - the content
        """
        try:
            lastchar = "a"
            with open("TestDirectory/" + filename + ".txt", "wb") as file:  # open new file
                for i in range(0, len(segments)):  # loop over all the segments and copy the contents
                    file.write(segments[i])
                    if (i == len(segments) - 1):
                        lastchar = segments[i][-1]

            # transfer the data to gui to represent it
            self.gui.downloadingInfo.set("file downloaded, last byte is " + str(lastchar))
            self.gui.downloadButton["state"] = "normal"

        except Exception as e:
            print(str(e))

    def stop(self):
        """
        terminate the Client
        """
        self.isActive = False
        self.sock.close()
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
                print(packet)
                if packet[
                    0] == "broadcast" and self.gui.GuiDone:  # command to gui to print the data as broadcast message
                    self.gui.insertMessage(packet[1] + " (broadcast): " + packet[2])
                elif packet[0] == "private" and self.gui.GuiDone:  # command to gui to print the data as private message
                    if self.name == packet[1]:
                        self.gui.insertMessage(packet[1] + " (to " + packet[2] + "): " + packet[3])
                    else:
                        self.gui.insertMessage(packet[1] + " (to you): " + packet[3])
                elif packet[
                    0] == "error" and self.gui.GuiDone:  # command to gui to notify user: invalid message has been sent
                    self.gui.insertMessage("message could not be sent")
                elif packet[0] == "filesRequest":  # start process of downloading file
                    self.files = packet[1]
                    self.gui.displayFiles()
                elif packet[
                    0] == "update":  # an update of details from the server, command to gui to represent it to user
                    self.gui.insertUsers(packet)
                elif packet[
                    0] == "udp":  # server is ready to start downloading process, shall xfer community to udp connection (start new thread for downloading file)
                    tempThread = threading.Thread(target=self.udp,
                                                  args=(packet[1], packet[2], packet[3], packet[4], packet[5]))
                    tempThread.daemon = True
                    tempThread.start()
                    # self.udp(packet[1], packet[2])
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
        pass


c = Client(1)
