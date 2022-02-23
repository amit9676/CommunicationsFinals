import socket
import threading
import ClientGUI
from tkinter import *
import pickle


Host = "127.0.0.1"
PORT = 9090

# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.connect((Host,PORT))
# print("connect")
# while True:



class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((Host,PORT))
        self.recieveThread = threading.Thread(target=self.recieve)
        self.recieveThread.daemon = True
        self.isActive = True
        self.recieveThread.start()
        #self.nameRequestThread = threading.Thread(target=self.recieve)
        #self.recieveThread.daemon = True

        self.name = ""
        self.nameRequest()
        self.write(self.name)

        self.GuiDone = False
        self.gui = None
        print("connect")
        self.GuiThread = threading.Thread(target=self.basicGUI)
        #self.GuiThread.daemon = True




        self.updateThread = threading.Thread(target=self.requestUpdate)
        self.updateThread.daemon = True

        self.GuiThread.start()

        self.updateThread.start()




    def nameRequest(self):
        self.root1 = Tk()
        self.root1.title("Enter name")
        self.root1.geometry("140x120")
        self.root1.resizable(False, False)
        name = Label(self.root1, text="Enter name").place(x=30,y=5)
        self.nameBox = Entry(self.root1, width=20, borderwidth=1)
        self.nameBox.place(x=10,y=35)
        nameEnter = Button(self.root1,text="Enter", height=1,width=12, command=self.proceed,fg="blue", bg="pink").place(x=20,y=75)
        self.root1.mainloop()


    def proceed(self):
        self.name = self.nameBox.get()
        self.root1.destroy()

        # self.confirmedName = "Waiting"
        # self.name = self.nameBox.get()
        # packet = ("validate",self.name)
        # data_string = pickle.dumps(packet)
        # self.sock.send(data_string)
        # while(self.confirmedName == "Waiting"):
        #     pass
        # self.root1.destroy()

    def write(self, message):
        self.sock.send(message.encode("utf-8"))
        #server method

    def sendBroadcast(self, message):
        #server method
        packet = ("broadcast",self.name,message)
        data_string = pickle.dumps(packet)
        self.sock.send(data_string)




    def basicGUI(self):
        self.root2 = Tk()
        self.root2.title("Client")
        self.root2.geometry("955x450")
        self.root2.resizable(False, False)
        self.chatLabel = Label(self.root2, text='broadcast', font=("lucida", 13)).place(x=1,y=5)
        self.chatLabel2 = Label(self.root2, text='active users', font=("lucida", 13)).place(x=671,y=5)

        self.t1 = Text(self.root2,width=30, height=21)
        #self.t1.insert(INSERT,"go")
        #self.t2.insert(INSERT,"amit1") # --add text here--
        self.t1.configure(state="disabled", cursor="arrow")
        self.t1.place(x=675,y=30)


        self.t2 = Text(self.root2,width=80, height=17)
        #self.t2.insert(INSERT,"amit1") # --add text here--
        self.t2.configure(state="disabled", cursor="arrow")
        self.t2.place(x=5,y=30)
        self.eMsg = Entry(self.root2, width=85, borderwidth=1)
        #self.eMsg.insert(0, "enter message here")
        self.eMsg.place(x=5,y=345,height=25)
        self.snd = Button(self.root2,text="Send", height=1,width=11, command=self.sendMessageOut,fg="blue", bg="pink").place(x=563,y=345,height=25)
        self.root2.protocol("WM_DELETE_WINDOW", self.stop)
        self.GuiDone = True
        self.root2.mainloop()
        #gui method

    def sendMessageOut(self):
        message = self.eMsg.get()
        self.sendBroadcast(message)
        #gui method


    def requestUpdate(self):
        while self.GuiDone == False:
            pass
        print("here :0")
        packet = ("update",)
        data_string = pickle.dumps(packet)
        self.sock.send(data_string)


    def insertMessage(self,message):
        self.t2.configure(state="normal", cursor="arrow")
        self.t2.insert(INSERT,str(message) + "\n") # --add text here--
        self.t2.configure(state="disabled", cursor="arrow")
        #gui method

    def insertUsers(self,packet):
        print("??!?1")
        self.t1.configure(state="normal", cursor="arrow")
        self.t1.delete('1.0', END)
        for p in range(1,len(packet)):
            self.t1.insert(INSERT,str(packet[p]) + "\n") # --add text here--
        self.t1.configure(state="disabled", cursor="arrow")



    def guiCreate(self):
        self.gui = ClientGUI.GUI(self)

    def stop(self):
        self.isActive = False
        self.root2.destroy()
        self.sock.close()
        exit(0)

    def recieve(self):
        #main function to recieve data from server
        #arr = ("key word", "data")
        #data_string = pickle.dumps(arr)
        #self.sock.send(data_string)
        while self.isActive:
            try:
                data = self.sock.recv(1024)
                packet = pickle.loads(data)
                if packet[0] == "broadcast" and self.GuiDone:
                    self.insertMessage(packet[1] + ": " + packet[2])
                elif packet[0] == "update":
                    self.insertUsers(packet)
                #elif packet[0] == "validate":
                    #if(packet[1] == True):
                        #self.confirmedName = True

            except:
                self.sock.close()
                break


c = Client()
