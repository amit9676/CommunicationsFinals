from tkinter import *


class GUI:
    """
    this class represent the GUI of the Client object
    the gui supports:
        1. Validate Phase (init name)
        2. sending broadcast and private message
        3. downloading files from the server
    the gui is always updated about new messages and the online users
    """

    def __init__(self, client):
        """
        constructor
        :param client: the client obj that the gui represent
        """
        self.client = client

        # this is flags for the "init name" proccess of the user
        self.GuiDone = False
        self.initGui = True
        self.nameRequest()
        self.initGui = False

    def nameRequest(self):
        """
        part of Validate phase
        this function create a window that askss to user to input his name,
            to continue the process of connecting the server and raise up the gui chat
        """
        self.root1 = Tk()
        self.initGui = True  # flag, represent this is initialize process
        # alot of vars of the gui
        self.root1.title("Enter name")
        self.root1.geometry("180x120")
        self.root1.resizable(False, False)

        name = Label(self.root1, text="Enter name").place(x=55, y=5)
        self.nameBox = Entry(self.root1, width=25, borderwidth=1)
        self.nameBox.place(x=10, y=35)
        self.chosenName = Label(self.root1, text="")
        self.chosenName.place(x=30, y=55)
        self.nameEnter = Button(self.root1, text="Enter", height=1, width=12, command=self.proceed, fg="blue",
                                bg="pink")
        self.nameEnter.place(x=42, y=90)

        self.root1.protocol("WM_DELETE_WINDOW",
                            self.client.stop)  # if window closed in place of inputed name, shut down client
        self.root1.mainloop()

    def proceed(self):
        """
        part of Validate phase
        this funct waiting to the user input that represent his name
        deliver the user input to the server via the client
        the purpose is to complete the Validate phase
        """
        self.client.name = self.nameBox.get()
        if self.client.name == "":
            self.chosenName.configure(text="please choose a name")
            return
        packet = ("validate", self.client.name)
        self.client.send_packet_tcp(packet)  # send to server the input from user
        while self.client.confirmedName == "Waiting":  # waiting to server respond
            pass

        # True == user name is valid, end of the Validate phase
        # False == user name is already taken, shall input new username
        if self.client.confirmedName == "True":
            self.root1.destroy()
        else:
            self.chosenName.configure(text="chosen name already in use")

    def basicGUI(self):
        """
        after the Validate Phase, and client have stable connection with the server, raising up the chat gui
        this window is gonna be on as long as the user didnt exited it
        even if server is down, the chat window wont close, its will notify to the user that "server is down"
        """
        self.root2 = Tk()

        # ---------------- chat window ----------------
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

        self.snd = Button(self.root2, text="Send", height=1, width=11, command=self.sendMessageOut, fg="blue",
                          bg="pink")
        self.snd.place(x=563, y=407, height=25)

        # ------------------- files gui ----------------------
        sendTo = Label(self.root2, text='download file:', font=("lucida", 11)).place(x=3, y=460)

        self.filesNames = [""]
        self.variable = StringVar(self.root2)
        self.variable.set("loading")  # default value
        self.w = OptionMenu(self.root2, self.variable, ())
        self.w.place(x=115, y=455)
        self.downloadButton = Button(self.root2, text="Download", height=1, width=13, command=self.download,
                                     fg="blue",
                                     bg="pink")
        self.downloadButton.place(x=203, y=457, height=25)

        self.downloadingInfo = StringVar()
        self.downloadingInfo.set("")
        self.downloadingLabel = Label(self.root2, textvariable=self.downloadingInfo, font=("lucida", 11)).place(x=3,
                                                                                                                y=490)

        self.root2.protocol("WM_DELETE_WINDOW", self.client.stop)  # closing the gui window -> closing the client
        self.GuiDone = True  # flag, gui is closed
        self.root2.mainloop()

    def insertMessage(self, message):
        """
        responsible to update the chat panel within a new message(represent it) that got to the client
        :param message: String represent the message
        """
        self.t2.configure(state="normal", cursor="arrow")
        self.t2.insert(INSERT, str(message) + "\n")  # --add text here--
        self.t2.configure(state="disabled", cursor="arrow")
        # gui method

    def insertUsers(self, packet):
        """
        this function responsible to update the users list in the gui "users" panel
        :param packet: tupple, indexes 1 and forward is users names
        """
        self.t1.configure(state="normal", cursor="arrow")
        self.t1.delete('1.0', END)
        for p in range(1, len(packet)):
            self.t1.insert(INSERT, str(packet[p]) + "\n")  # --add text here--
        self.t1.configure(state="disabled", cursor="arrow")

    def sendMessageOut(self):
        """
        user pressed to send message, prepare data to be sent via the client
        """
        message = self.eMsg.get()  # msg itself
        address = self.sendToEntry.get()  # who to send it to
        self.client.sendToServer(message, address)

    """ ----------------------------- files functions ------------------------------------------------"""

    def halfway(self):
        """
        when a file downloading got to halfway
        this function is being called and raising up the option to continue the downloading or cancel it
        """
        self.paused = Label(self.root2, text='downloading paused..', font=("lucida", 11))
        self.paused.place(x=253, y=490)
        self.proceed_button = Button(self.root2, text="proceed", command=lambda: self.halfway2(2), height=1, width=13,
                                     fg="blue",
                                     bg="pink")
        self.proceed_button.place(x=413, y=488, height=25)
        self.cancel_button = Button(self.root2, text="cancel", command=lambda: self.halfway2(3), height=1, width=13,
                                    fg="blue",
                                    bg="pink")
        self.cancel_button.place(x=533, y=488, height=25)

    def halfway2(self, condition):
        """
        this function being called to end the representaion of the downloading file process since its got to its end
        :param condition: two options, condition == 2 is end of download, condition == 3 is download canceled
        """
        self.client.cancel_proceed_switch = condition
        self.paused.destroy()
        self.proceed_button.destroy()
        self.cancel_button.destroy()
        if self.client.cancel_proceed_switch == 3:
            self.downloadButton["state"] = "normal"

    def disable(self):
        """
        if server got shutted down while the client is on, initializing the gui in accordance
            in example: print server is down, and disabling few of the buttons
        """
        if self.initGui:  # basic GUI is off (while the Validate phase)
            self.chosenName.configure(text="server is down")
            self.nameEnter["state"] = "disabled"
        elif self.GuiDone:  # basic GUI is on, (after the Validate phase)
            self.insertMessage("server is down")
            self.snd["state"] = "disabled"
            self.downloadButton["state"] = "disabled"

    def setFilesAid(self, inputa):
        """
        replacing the choosen file in the text box and updating the client about that
        :param inputa: file name
        """
        self.variable.set(inputa)
        self.client.currentFile = inputa

    def displayFiles(self):
        """
        responsible to represent the choosen file from the file list that available to be downloaded
        """
        print("here")
        self.w['menu'].delete(0, 'end')
        for opt in self.client.files:
            self.w['menu'].add_command(label=opt, command=lambda x=opt: self.setFilesAid(x))
        self.variable.set(self.client.files[0])
        self.client.currentFile = self.client.files[0]

    def download(self):
        """
        if the user pressed on "download" button, this function will activate the client to send via tcp a msg to server, asking to download this file
        after this function, the server and client would start a udp connection, for the downloading process
        :return:
        """
        packet = ("download", self.client.currentFile)
        self.downloadButton["state"] = "disabled"
        self.client.send_packet_tcp(packet)
