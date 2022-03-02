import socket
import threading
from tkinter import *
import pickle
import time

import GUI

Host = "127.0.0.1"
PORT = 9090


# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.connect((Host,PORT))
# print("connect")
# while True:


class Client:

    def __init__(self):
        """
        constructor of client
        connecting to the server via TCP connection
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((Host, PORT))
        self.recieveThread = threading.Thread(target=self.recieve)
        self.recieveThread.daemon = True
        self.isActive = True
        self.recieveThread.start()
        # self.nameRequestThread = threading.Thread(target=self.recieve)
        # self.recieveThread.daemon = True

        self.name = ""
        self.files = [""]
        self.currentFile = ""

        self.initGui = True

        self.confirmedName = "Waiting"
        self.gui = GUI.GUI(self)
        # self.nameRequest()
        self.initGui = False
        # self.write(self.name)

        self.stupidCondition = 1

        # self.GuiDone = False
        # self.gui = None

        print("connect")
        self.GuiThread = threading.Thread(target=self.gui.basicGUI)
        # self.GuiThread.daemon = True

        self.updateThread = threading.Thread(target=self.requestInitialData)
        self.updateThread.daemon = True

        self.GuiThread.start()

        self.updateThread.start()
        print("ended const")

    def send_packet_tcp(self, packet):
        try:
            data_string = pickle.dumps(packet)
            self.sock.send(data_string)
        except Exception as e:
            print(str(e))
            self.stop()

    def sendToServer(self, message, addresse):
        # server method
        packet = None
        if addresse == "":
            packet = ("broadcast", self.name, message)
        else:
            packet = ("private", self.name, addresse, message)
        data_string = pickle.dumps(packet)
        try:
            self.sock.send(data_string)
        except Exception as e:
            print(str(e))
            self.stop()

    def sendMessageOut(self):
        message = self.gui.eMsg.get()
        addressee = self.gui.sendToEntry.get()
        self.sendToServer(message, addressee)
        # gui method

    def requestInitialData(self):
        while not self.gui.GuiDone:
            pass
        packet1 = ("update",)
        packet2 = ("filesRequest",)
        self.send_packet_tcp(packet1)
        time.sleep(0.001)
        self.send_packet_tcp(packet2)

    def insertFileTransferData(self, info):
        self.gui.downloadingInfo.set(info)

    def setFilesAid(self, inputa):
        self.gui.variable.set(inputa)
        self.currentFile = inputa

    def download(self):
        packet = ("download", self.currentFile)
        self.gui.downloadButton["state"] = "disabled"
        self.send_packet_tcp(packet)

    def udp(self, filename, size, sizeOfSegments, host, port):
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        reqTime = time.time()
        packet = ("ready", reqTime)
        data_string = pickle.dumps(packet)
        udp.sendto(data_string, (host, port))

        # message, address = udp.recvfrom(1024)
        # openeddata = pickle.loads(message)
        # print(f"data = {openeddata}")
        segments = {}
        # recieverThread = threading.Thread(target=self.recieveFile, args=(filename, size, udp,sizeOfSegments,host,port,segments))
        # recieverThread.daemon = True
        # recieverThread.start()
        self.recieveFile(filename, size, udp, sizeOfSegments, host, port, segments)

        # udp.close()

    def recieveFile(self, filename, size, udp, sizeOfSegments, host, port, segments):
        print(f"active threads: {threading.active_count()}")
        # print(filename)
        # print(size)
        # print(sizeOfSegments)
        # print(segments)
        # self.insertFileTransferData("downloading")
        # time.sleep(10)
        counter = 0
        # sendAcks = threading.Thread(target=self.ackSender, args=(udp))
        # sendAcks.daemon = True
        # sendAcks.start()
        while len(segments) < sizeOfSegments:
            message, address = udp.recvfrom(1124)
            status = "downloading " + str(counter * 1024) + "/" + str(size) + " bytes"
            self.insertFileTransferData(status)
            counter += 1
            # print(2)
            segment = pickle.loads(message)
            if (segment[0] == "halfway"):
                print("halfway")
                self.gui.halfway()
                while self.stupidCondition == 1:
                    pass
                if (self.stupidCondition == 2):
                    halfWayAnswer = ("halfway", "proceed")
                    halfWayData = pickle.dumps(halfWayAnswer)
                    udp.sendto(halfWayData, (host, port))
                    self.stupidCondition = 1
                if (self.stupidCondition == 3):
                    halfWayAnswer = ("halfway", "cancel")
                    halfWayData = pickle.dumps(halfWayAnswer)
                    udp.sendto(halfWayData, (host, port))
                    udp.close()
                    self.insertFileTransferData("download canceled")
                    self.stupidCondition = 1
                    return
            else:
                segments[segment[0]] = segment[1]
                response = ("ack", segment[0])
                data_string = pickle.dumps(response)
                udp.sendto(data_string, (host, port))

            time.sleep(0.001)
            # print(f"sent {response}")
        # print("done")
        # print(segments)
        udp.close()

        self.create(filename, segments)

    # def ackSender(self,udp):
    # pass

    def create(self, filename, segments):
        try:
            lastchar = "a"
            with open("TestDirectory/" + filename + ".txt", "wb") as file:
                for i in range(0, len(segments)):
                    file.write(segments[i])
                    if (i == len(segments) - 1):
                        lastchar = segments[i][-1]
            print(lastchar)
            print("server completed transfering data")
            # byte = lastchar.encode("utf-8")
            self.insertFileTransferData("file downloaded, last byte is " + str(lastchar))
            self.gui.downloadButton["state"] = "normal"
        except Exception as e:
            print(str(e))

    def stop(self):
        self.isActive = False
        # self.root2.destroy()
        # self.root1.destroy()
        self.sock.close()
        exit(0)

    def recieve(self):
        # main function to recieve data from server
        # arr = ("key word", "data")
        # data_string = pickle.dumps(arr)
        # self.sock.send(data_string)
        while self.isActive:
            try:
                data = self.sock.recv(1024)
                packet = pickle.loads(data)
                print(packet)
                if packet[0] == "broadcast" and self.gui.GuiDone:
                    self.gui.insertMessage(packet[1] + " (broadcast): " + packet[2])
                elif packet[0] == "private" and self.gui.GuiDone:
                    if self.name == packet[1]:
                        self.gui.insertMessage(packet[1] + " (to " + packet[2] + "): " + packet[3])
                    else:
                        self.gui.insertMessage(packet[1] + " (to you): " + packet[3])
                elif packet[0] == "error" and self.gui.GuiDone:
                    self.gui.insertMessage("message could not be sent")
                elif packet[0] == "filesRequest":
                    self.files = packet[1]
                    self.gui.displayFiles()
                elif packet[0] == "update":
                    self.gui.insertUsers(packet)
                elif packet[0] == "udp":
                    tempThread = threading.Thread(target=self.udp,
                                                  args=(packet[1], packet[2], packet[3], packet[4], packet[5]))
                    tempThread.daemon = True
                    tempThread.start()
                    # self.udp(packet[1], packet[2])
                elif packet[0] == "validate":
                    if (packet[1] == True):
                        self.confirmedName = "True"
                        print("true")
                    else:
                        self.confirmedName = "False"
                        print("false")
                elif packet[0] == "serverDown":
                    self.gui.disable()
                    self.gui.insertUsers(packet)


            except Exception as e:
                print(str(e))
                print("closing :-(")
                self.sock.close()
                break


c = Client()
