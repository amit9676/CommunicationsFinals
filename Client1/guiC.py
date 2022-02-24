from tkinter import *


class GUIClient:
    def __init__(self, client):
        self.GuiDone = True
        self.snd = Button(self.root2, text="Send", height=1, width=11, command=self.sendMessageOut, fg="blue",
                          bg="pink").place(x=563, y=407, height=25)
        self.eMsg = Entry(self.root2, width=85, borderwidth=1)
        self.sendToEntry = Entry(self.root2, width=25, borderwidth=1)
        self.t2 = Text(self.root2, width=80, height=17)
        self.t1 = Text(self.root2, width=30, height=25)
        self.chatLabel2 = Label(self.root2, text='active users', font=("lucida", 13)).place(x=671, y=5)
        self.chatLabel = Label(self.root2, text='chat', font=("lucida", 13)).place(x=1, y=5)
        self.root2 = Tk()
        self.nameBox = Entry(self.root1, width=25, borderwidth=1)
        self.chosenName = Label(self.root1, text="")
        self.root1 = Tk()
        self.confirmedName = ""
        self.my_client = client
        self.nameRequest()

    def nameRequest(self):
        self.root1.title("Enter name")
        self.root1.geometry("180x120")
        self.root1.resizable(False, False)
        name = Label(self.root1, text="Enter name").place(x=55, y=5)
        self.nameBox.place(x=10, y=35)
        self.chosenName.place(x=10, y=55)
        nameEnter = Button(self.root1, text="Enter", height=1, width=12, command=self.proceed, fg="blue",
                           bg="pink").place(x=42, y=90)
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
        # data_string = pickle.dumps(packet)
        # self.sock.send(data_string)
        self.my_client.send_packet(packet)
        while self.confirmedName == "Waiting":
            pass
        print(self.confirmedName)
        # self.chosenName.configure(text="chosen name already in use")
        if self.confirmedName == "True":
            self.root1.destroy()
        else:
            self.chosenName.configure(text="chosen name already in use")

    def basicGUI(self):
        self.root2.title("chatroom - " + self.name)
        self.root2.geometry("955x450")
        self.root2.resizable(False, False)

        # self.t1.insert(INSERT,"go")
        # self.t2.insert(INSERT,"amit1") # --add text here--
        self.t1.configure(state="disabled", cursor="arrow")
        self.t1.place(x=675, y=30)

        # self.t2.insert(INSERT,"amit1") # --add text here--
        self.t2.configure(state="disabled", cursor="arrow")
        self.t2.place(x=5, y=30)

        sendTo = Label(self.root2, text='send to:', font=("lucida", 11)).place(x=3, y=320)
        self.sendToEntry.place(x=65, y=320, height=25)
        sendToNote = Label(self.root2, text='*to send to specific user, enter the user name, to broadcast'
                                            ' - keep the input field empty', font=("lucida", 8)).place(x=3, y=350)

        messageLabel = Label(self.root2, text='message:', font=("lucida", 11)).place(x=3, y=385)
        # self.eMsg.insert(0, "enter message here")
        self.eMsg.place(x=5, y=407, height=25)

        # variable = StringVar(self.root2)
        # variable.set("one") # default value
        # w = OptionMenu(self.root2, variable, "one", "two", "three")
        # w.place(x=225,y=300)

        self.root2.protocol("WM_DELETE_WINDOW", self.my_client.stop())
        self.root2.mainloop()
        # gui method

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

    def sendMessageOut(self):
        message = self.eMsg.get()
        addressee = self.sendToEntry.get()
        self.my_client.sendToServer(message, addressee)
        # gui method
