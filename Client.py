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

    # def nameRequest(self):
    #     self.root1 = Tk()
    #     self.initGui = True
    #     self.root1.title("Enter name")
    #     self.root1.geometry("180x120")
    #     self.root1.resizable(False, False)
    #     name = Label(self.root1, text="Enter name").place(x=55, y=5)
    #     self.nameBox = Entry(self.root1, width=25, borderwidth=1)
    #     self.nameBox.place(x=10, y=35)
    #     self.chosenName = Label(self.root1, text="")
    #     self.chosenName.place(x=10, y=55)
    #     self.nameEnter = Button(self.root1, text="Enter", height=1, width=12, command=self.proceed, fg="blue",
    #                        bg="pink")
    #     self.nameEnter.place(x=42, y=90)
    #     self.root1.protocol("WM_DELETE_WINDOW", self.stop)
    #     self.root1.mainloop()

    def send_packet(self, packet):
        try:
            data_string = pickle.dumps(packet)
            self.sock.send(data_string)
        except:
            print("connection lost with the server, closing the client...")
            self.stop()

    # def proceed(self):
    #     # self.name = self.nameBox.get()
    #     # self.root1.destroy()
    #
    #     self.confirmedName = "Waiting"
    #     self.name = self.gui.nameBox.get()
    #     if self.name == "":
    #         self.gui.chosenName.configure(text="please choose a name")
    #         return
    #     packet = ("validate", self.name)
    #     data_string = pickle.dumps(packet)
    #     self.sock.send(data_string)
    #     while self.confirmedName == "Waiting":
    #         pass
    #     print(self.confirmedName)
    #     # self.chosenName.configure(text="chosen name already in use")
    #     if self.confirmedName == "True":
    #         self.root1.destroy()
    #     else:
    #         self.chosenName.configure(text="chosen name already in use")

    # def write(self, message):
    #     pass
    #     # self.sock.send(message.encode("utf-8"))
    #     # server method

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
        except:
            print("connection lost with the server, closing the client...")
            self.stop()

    # def basicGUI(self):
    #     self.root2 = Tk()
    #     self.root2.title("chatroom - " + self.name)
    #     self.root2.geometry("955x530")
    #     self.root2.resizable(False, False)
    #     self.chatLabel = Label(self.root2, text='chat', font=("lucida", 13)).place(x=1, y=5)
    #     self.chatLabel2 = Label(self.root2, text='active users', font=("lucida", 13)).place(x=671, y=5)
    #
    #     self.t1 = Text(self.root2, width=30, height=25)
    #     # self.t1.insert(INSERT,"go")
    #     # self.t2.insert(INSERT,"amit1") # --add text here--
    #     self.t1.configure(state="disabled", cursor="arrow")
    #     self.t1.place(x=675, y=30)
    #
    #     self.t2 = Text(self.root2, width=80, height=17)
    #     # self.t2.insert(INSERT,"amit1") # --add text here--
    #     self.t2.configure(state="disabled", cursor="arrow")
    #     self.t2.place(x=5, y=30)
    #
    #     sendTo = Label(self.root2, text='send to:', font=("lucida", 11)).place(x=3, y=320)
    #     self.sendToEntry = Entry(self.root2, width=25, borderwidth=1)
    #     self.sendToEntry.place(x=65, y=320, height=25)
    #     sendToNote = Label(self.root2, text='*to send to specific user, enter the user name, to broadcast'
    #                                         ' - keep the input field empty', font=("lucida", 8)).place(x=3, y=350)
    #
    #     messageLabel = Label(self.root2, text='message:', font=("lucida", 11)).place(x=3, y=385)
    #     self.eMsg = Entry(self.root2, width=85, borderwidth=1)
    #     # self.eMsg.insert(0, "enter message here")
    #     self.eMsg.place(x=5, y=407, height=25)
    #
    #     # variable = StringVar(self.root2)
    #     # variable.set("one") # default value
    #     # w = OptionMenu(self.root2, variable, "one", "two", "three")
    #     # w.place(x=225,y=300)
    #
    #     self.snd = Button(self.root2, text="Send", height=1, width=11, command=self.sendMessageOut, fg="blue",
    #                       bg="pink")
    #     self.snd.place(x=563, y=407, height=25)
    #
    #     sendTo = Label(self.root2, text='download file:', font=("lucida", 11)).place(x=3, y=460)
    #
    #     self.filesNames = [""]
    #     self.variable = StringVar(self.root2)
    #     self.variable.set("loading") # default value
    #     self.w = OptionMenu(self.root2,  self.variable, ())
    #     self.w.place(x=115,y=455)
    #     self.downloadButton = Button(self.root2, text="Download", height=1, width=13, command=self.download, fg="blue",
    #                       bg="pink")
    #     self.downloadButton.place(x=203, y=457, height=25)
    #
    #     self.downloadingInfo = StringVar()
    #     self.downloadingInfo.set("")
    #     self.downloadingLabel = Label(self.root2, textvariable= self.downloadingInfo, font=("lucida", 11)).place(x=3, y=490)
    #
    #     self.root2.protocol("WM_DELETE_WINDOW", self.stop)
    #     self.GuiDone = True
    #     self.root2.mainloop()
    #     # gui method

    def halfway(self):
        self.paused = Label(self.root2, text='downloading paused..', font=("lucida", 11))
        self.paused.place(x=253, y=490)
        self.bb = Button(self.root2, text="proceed", command=lambda: self.halfway2(2), height=1, width=13, fg="blue",
                         bg="pink")
        self.bb.place(x=413, y=488, height=25)
        self.cc = Button(self.root2, text="cancel", command=lambda: self.halfway2(3), height=1, width=13, fg="blue",
                         bg="pink")
        self.cc.place(x=533, y=488, height=25)

    def halfway2(self, condition):
        self.stupidCondition = condition
        self.paused.destroy()
        self.bb.destroy()
        self.cc.destroy()
        if self.stupidCondition == 3:
            self.downloadButton["state"] = "normal"

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
        
        try:
            self.send_packet(packet1)
            time.sleep(0.001)
            self.send_packet(packet2)
        except:
            print("connection lost with the server, closing the client...")
            self.stop()

    # def insertMessage(self, message):
    #     self.t2.configure(state="normal", cursor="arrow")
    #     self.t2.insert(INSERT, str(message) + "\n")  # --add text here--
    #     self.t2.configure(state="disabled", cursor="arrow")
    #     # gui method
    #
    # def insertUsers(self, packet):
    #     self.t1.configure(state="normal", cursor="arrow")
    #     self.t1.delete('1.0', END)
    #     for p in range(1, len(packet)):
    #         self.t1.insert(INSERT, str(packet[p]) + "\n")  # --add text here--
    #     self.t1.configure(state="disabled", cursor="arrow")

    def insertFileTransferData(self, info):
        self.downloadingInfo.set(info)

    def displayFiles(self):
        print("here")
        self.w['menu'].delete(0, 'end')
        for opt in self.files:
            self.w['menu'].add_command(label=opt, command=lambda x=opt: self.setFilesAid(x))
        self.variable.set(self.files[0])
        self.currentFile = self.files[0]

    def setFilesAid(self, inputa):
        self.variable.set(inputa)
        self.currentFile = inputa

    def download(self):
        packet = ("download", self.currentFile)
        data_string = pickle.dumps(packet)
        self.downloadButton["state"] = "disabled"
        try:
            self.sock.send(data_string)
        except:
            print("connection lost with the server, closing the client...")
            self.stop()

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
                self.halfway()
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

    # def guiCreate(self):
    #     self.gui = ClientGUI.GUI(self)

    def disable(self):
        if self.initGui:
            self.chosenName.configure(text="server is down")
            self.nameEnter["state"] = "disabled"
        elif self.gui.GuiDone:
            print("mm")
            self.insertMessage("server is down")
            self.snd["state"] = "disabled"
            self.downloadButton["state"] = "disabled"

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
                    self.displayFiles()
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


            except:
                print("closing :-(")
                self.sock.close()
                break


c = Client()
