from tkinter import *


class GUI:
    def __init__(self, client):
        self.client = client
        self.GuiDone = False
        self.initGui = True
        self.nameRequest()
        self.initGui = False

    def nameRequest(self):
        self.root1 = Tk()
        self.initGui = True
        self.root1.title("Enter name")
        self.root1.geometry("180x120")
        self.root1.resizable(False, False)
        name = Label(self.root1, text="Enter name").place(x=55, y=5)
        self.nameBox = Entry(self.root1, width=25, borderwidth=1)
        self.nameBox.place(x=10, y=35)
        self.chosenName = Label(self.root1, text="")
        self.chosenName.place(x=10, y=55)
        self.nameEnter = Button(self.root1, text="Enter", height=1, width=12, command=self.proceed, fg="blue",
                                bg="pink")
        self.nameEnter.place(x=42, y=90)
        self.root1.protocol("WM_DELETE_WINDOW", self.client.stop)
        self.root1.mainloop()

    def proceed(self):
        # self.name = self.nameBox.get()
        # self.root1.destroy()

        self.client.name = self.nameBox.get()
        if self.client.name == "":
            self.chosenName.configure(text="please choose a name")
            return
        packet = ("validate", self.client.name)
        self.client.send_packet_tcp(packet)
        while self.client.confirmedName == "Waiting":
            pass
        # self.chosenName.configure(text="chosen name already in use")
        if self.client.confirmedName == "True":
            self.root1.destroy()
        else:
            self.chosenName.configure(text="chosen name already in use")

    def basicGUI(self):
        self.root2 = Tk()
        self.root2.title("chatroom - " + self.client.name)
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

        self.snd = Button(self.root2, text="Send", height=1, width=11, command=self.client.sendMessageOut, fg="blue",
                          bg="pink")
        self.snd.place(x=563, y=407, height=25)

        sendTo = Label(self.root2, text='download file:', font=("lucida", 11)).place(x=3, y=460)

        self.filesNames = [""]
        self.variable = StringVar(self.root2)
        self.variable.set("loading")  # default value
        self.w = OptionMenu(self.root2, self.variable, ())
        self.w.place(x=115, y=455)
        self.downloadButton = Button(self.root2, text="Download", height=1, width=13, command=self.client.download,
                                     fg="blue",
                                     bg="pink")
        self.downloadButton.place(x=203, y=457, height=25)

        self.downloadingInfo = StringVar()
        self.downloadingInfo.set("")
        self.downloadingLabel = Label(self.root2, textvariable=self.downloadingInfo, font=("lucida", 11)).place(x=3,
                                                                                                                y=490)

        self.root2.protocol("WM_DELETE_WINDOW", self.client.stop)
        self.GuiDone = True
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

    """ ----------------------------- files functions ------------------------------------------------"""

    def halfway(self):
        self.paused = Label(self.root2, text='downloading paused..', font=("lucida", 11))
        self.paused.place(x=253, y=490)
        self.bb = Button(self.root2, text="proceed", command=lambda: self.halfway2(2), height=1, width=13, fg="blue",
                         bg="pink")
        self.bb.place(x=413, y=488, height=25)
        self.cc = Button(self.root2, text="cancel", command=lambda: self.halfway2(3), height=1, width=13, fg="blue",
                         bg="pink")
        self.cc.place(x=533, y=488, height=25)

    def disable(self):
        if self.initGui:
            self.chosenName.configure(text="server is down")
            self.nameEnter["state"] = "disabled"
        elif self.GuiDone:
            print("mm")
            self.insertMessage("server is down")
            self.snd["state"] = "disabled"
            self.downloadButton["state"] = "disabled"

    def halfway2(self, condition):
        self.client.stupidCondition = condition
        self.paused.destroy()
        self.bb.destroy()
        self.cc.destroy()
        if self.client.stupidCondition == 3:
            self.downloadButton["state"] = "normal"

    def displayFiles(self):
        print("here")
        self.w['menu'].delete(0, 'end')
        for opt in self.client.files:
            self.w['menu'].add_command(label=opt, command=lambda x=opt: self.client.setFilesAid(x))
        self.variable.set(self.client.files[0])
        self.client.currentFile = self.client.files[0]
