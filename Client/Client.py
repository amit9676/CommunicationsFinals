import socket
import threading
import ClientGUI
from tkinter import *
import pickle
import time

Host = "127.0.0.1"
PORT = 9090


# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.connect((Host,PORT))
# print("connect")
# while True:


class Client:
    def __init__(self):
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
        self.nameRequest()
        self.write(self.name)

        self.GuiDone = False
        self.gui = None
        print("connect")
        self.GuiThread = threading.Thread(target=self.basicGUI)
        # self.GuiThread.daemon = True

        self.updateThread = threading.Thread(target=self.requestInitialData)
        self.updateThread.daemon = True

        self.GuiThread.start()

        self.updateThread.start()

    def nameRequest(self):
        self.root1 = Tk()
        self.root1.title("Enter name")
        self.root1.geometry("180x120")
        self.root1.resizable(False, False)
        name = Label(self.root1, text="Enter name").place(x=55, y=5)
        self.nameBox = Entry(self.root1, width=25, borderwidth=1)
        self.nameBox.place(x=10, y=35)
        self.chosenName = Label(self.root1, text="")
        self.chosenName.place(x=10, y=55)
        nameEnter = Button(self.root1, text="Enter", height=1, width=12, command=self.proceed, fg="blue",
                           bg="pink").place(x=42, y=90)
        self.root1.protocol("WM_DELETE_WINDOW", self.stop)
        self.root1.mainloop()

    def proceed(self):
        # self.name = self.nameBox.get()
        # self.root1.destroy()

        self.confirmedName = "Waiting"
        self.name = self.nameBox.get()
        if self.name == "":
            self.chosenName.configure(text="please choose a name")
            return
        packet = ("validate", self.name)
        data_string = pickle.dumps(packet)
        self.sock.send(data_string)
        while self.confirmedName == "Waiting":
            pass
        print(self.confirmedName)
        # self.chosenName.configure(text="chosen name already in use")
        if self.confirmedName == "True":
            self.root1.destroy()
        else:
            self.chosenName.configure(text="chosen name already in use")

    def write(self, message):
        pass
        # self.sock.send(message.encode("utf-8"))
        # server method

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

    def basicGUI(self):
        self.root2 = Tk()
        self.root2.title("chatroom - " + self.name)
        self.root2.geometry("955x530")
        self.root2.resizable(False, False)
        self.chatLabel = Label(self.root2, text='chat', font=("lucida", 13)).place(x=1, y=5)
        self.chatLabel2 = Label(self.root2, text='active users', font=("lucida", 13)).place(x=671, y=5)

        self.t1 = Text(self.root2, width=30, height=25)
        # self.t1.insert(INSERT,"go")
        # self.t2.insert(INSERT,"amit1") # --add text here--
        self.t1.configure(state="disabled", cursor="arrow")
        self.t1.place(x=675, y=30)

        self.t2 = Text(self.root2, width=80, height=17)
        # self.t2.insert(INSERT,"amit1") # --add text here--
        self.t2.configure(state="disabled", cursor="arrow")
        self.t2.place(x=5, y=30)

        sendTo = Label(self.root2, text='send to:', font=("lucida", 11)).place(x=3, y=320)
        self.sendToEntry = Entry(self.root2, width=25, borderwidth=1)
        self.sendToEntry.place(x=65, y=320, height=25)
        sendToNote = Label(self.root2, text='*to send to specific user, enter the user name, to broadcast'
                                            ' - keep the input field empty', font=("lucida", 8)).place(x=3, y=350)

        messageLabel = Label(self.root2, text='message:', font=("lucida", 11)).place(x=3, y=385)
        self.eMsg = Entry(self.root2, width=85, borderwidth=1)
        # self.eMsg.insert(0, "enter message here")
        self.eMsg.place(x=5, y=407, height=25)

        # variable = StringVar(self.root2)
        # variable.set("one") # default value
        # w = OptionMenu(self.root2, variable, "one", "two", "three")
        # w.place(x=225,y=300)

        self.snd = Button(self.root2, text="Send", height=1, width=11, command=self.sendMessageOut, fg="blue",
                          bg="pink").place(x=563, y=407, height=25)

        sendTo = Label(self.root2, text='download file:', font=("lucida", 11)).place(x=3, y=460)

        self.filesNames = [""]
        self.variable = StringVar(self.root2)
        self.variable.set("loading") # default value
        self.w = OptionMenu(self.root2,  self.variable, ())
        self.w.place(x=115,y=455)
        self.download = Button(self.root2, text="Download", height=1, width=13, command=self.download, fg="blue",
                          bg="pink").place(x=203, y=457, height=25)

        self.root2.protocol("WM_DELETE_WINDOW", self.stop)
        self.GuiDone = True
        self.root2.mainloop()
        # gui method

    def sendMessageOut(self):
        message = self.eMsg.get()
        addressee = self.sendToEntry.get()
        self.sendToServer(message, addressee)
        # gui method


    def requestInitialData(self):
        while not self.GuiDone:
            pass
        packet1 = ("update",)
        packet2 = ("filesRequest",)

        data_string1 = pickle.dumps(packet1)
        data_string2 = pickle.dumps(packet2)
        try:
            self.sock.send(data_string1)
            time.sleep(0.001)
            self.sock.send(data_string2)
        except:
            print("connection lost with the server, closing the client...")
            self.stop()

    def insertMessage(self, message):
        self.t2.configure(state="normal", cursor="arrow")
        self.t2.insert(INSERT, str(message) + "\n")  # --add text here--
        self.t2.configure(state="disabled", cursor="arrow")
        # gui method

    def insertUsers(self, packet):
        self.t1.configure(state="normal", cursor="arrow")
        self.t1.delete('1.0', END)
        for p in range(1, len(packet)):
            self.t1.insert(INSERT, str(packet[p]) + "\n")  # --add text here--
        self.t1.configure(state="disabled", cursor="arrow")

    def displayFiles(self):
        print("here")
        self.w['menu'].delete(0,'end')
        for opt in self.files:
            self.w['menu'].add_command(label=opt, command=lambda x=opt: self.setFilesAid(x))
        self.variable.set(self.files[0])
        self.currentFile = self.files[0]

    def setFilesAid(self, inputa):
        self.variable.set(inputa)
        self.currentFile = inputa

    def download(self):
        packet = ("download",self.currentFile)
        data_string = pickle.dumps(packet)
        try:
            self.sock.send(data_string)
        except:
            print("connection lost with the server, closing the client...")
            self.stop()

    def udp(self,filename,size,sizeOfSegments, host, port):
        udp = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        reqTime = time.time()
        packet = ("ready", reqTime)
        data_string = pickle.dumps(packet)
        udp.sendto(data_string,(host,port))


        #message, address = udp.recvfrom(1024)
        #openeddata = pickle.loads(message)
        #print(f"data = {openeddata}")
        segments = {}
        #recieverThread = threading.Thread(target=self.recieveFile, args=(filename, size, udp,sizeOfSegments,host,port,segments))
        #recieverThread.daemon = True
        #recieverThread.start()
        self.recieveFile(filename, size, udp,sizeOfSegments,host,port,segments)

        #udp.close()


    def recieveFile(self, filename,size,udp,sizeOfSegments,host,port,segments):
        #print(filename)
        #print(size)
        #print(sizeOfSegments)
        #print(segments)
        while len(segments) < sizeOfSegments:
            #print(1)
            message, address = udp.recvfrom(1124)
            #print(2)
            segment = pickle.loads(message)
            segments[segment[0]] = segment[1]
            response = ("ack",segment[0])
            data_string = pickle.dumps(response)
            udp.sendto(data_string,(host,port))
            #print(f"sent {response}")
        #print("done")
        #print(segments)
        udp.close()
        self.create(filename,segments)

    def create(self, filename,segments):
        try:
            with open("TestDirectory/"+filename+".txt", "wb") as file:
                for i in range (0,len(segments)):
                    file.write(segments[i])
            print("server completed transfering data")
        except Exception as e:
            print(str(e))

    def guiCreate(self):
        self.gui = ClientGUI.GUI(self)

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
                if packet[0] == "broadcast" and self.GuiDone:
                    self.insertMessage(packet[1] + " (broadcast): " + packet[2])
                elif packet[0] == "private" and self.GuiDone:
                    if self.name == packet[1]:
                        self.insertMessage(packet[1] + " (to " + packet[2] + "): " + packet[3])
                    else:
                        self.insertMessage(packet[1] + " (to you): " + packet[3])
                elif packet[0] == "error" and self.GuiDone:
                    self.insertMessage("message could not be sent")
                elif packet[0] == "filesRequest":
                    print("!!")
                    self.files = packet[1]
                    self.displayFiles()
                elif packet[0] == "update":
                    self.insertUsers(packet)
                elif packet[0] == "udp":
                    tempThread = threading.Thread(target=self.udp,args=(packet[1],packet[2],packet[3],packet[4],packet[5]))
                    tempThread.daemon = True
                    tempThread.start()
                    #self.udp(packet[1], packet[2])
                elif packet[0] == "validate":
                    if (packet[1] == True):
                        self.confirmedName = "True"
                    else:
                        self.confirmedName = "False"

            except:
                self.sock.close()
                break


c = Client()
