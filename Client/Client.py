import socket
import threading
import ClientGUI
from tkinter import *

Host = "127.0.0.1"
PORT = 9090

# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.connect((Host,PORT))
# print("connect")
# while True:



class Client:
    def __init__(self):
        print("hi")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((Host,PORT))
        self.isActive = True
        self.GuiDone = False
        self.gui = None
        print("connect")
        self.GuiThread = threading.Thread(target=self.basicGUI)
        #self.GuiThread.daemon = True


        self.recieveThread = threading.Thread(target=self.recieve)
        self.recieveThread.daemon = True
        self.GuiThread.start()
        self.recieveThread.start()



    def write(self, message):
        self.sock.send(message.encode("utf-8"))


    def basicGUI(self):
        self.root2 = Tk()
        self.root2.title("Client")
        self.root2.geometry("855x500")
        self.root2.resizable(False, False)
        self.t2 = Text(self.root2,width=110, height=17)
        self.t2.insert(INSERT,"amit1") # --add text here--
        self.t2.configure(state="disabled", cursor="arrow")
        self.t2.place(x=5,y=45)
        self.eMsg = Entry(self.root2, width=85, borderwidth=1)
        self.eMsg.place(x=216,y=345,height=25)
        self.snd = Button(self.root2,text="Send", height=1,width=11, command=self.sendMessageOut,fg="blue", bg="pink").place(x=746,y=345,height=25)
        self.root2.protocol("WM_DELETE_WINDOW", self.stop)
        self.GuiDone = True
        self.root2.mainloop()

    def sendMessageOut(self):
        message = self.eMsg.get()
        self.write(message)

    def insertMessage(self,message):
        self.t2.configure(state="normal", cursor="arrow")
        self.t2.insert(INSERT,"\n" + str(message)) # --add text here--
        self.t2.configure(state="disabled", cursor="arrow")

    def guiCreate(self):
        self.gui = ClientGUI.GUI(self)

    def stop(self):
        self.isActive = False
        self.root2.destroy()
        self.sock.close()
        exit(0)

    def recieve(self):
        while self.isActive:
            try:
                data = self.sock.recv(1024)
                if self.GuiDone:
                    self.insertMessage(data.decode("utf-8"))
            except:
                self.sock.close()
                break

c = Client()
