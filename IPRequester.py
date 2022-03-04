from tkinter import *

class IPRequester:

    def __init__(self):
        self.globali = ""

    def GUIItSelf(self,text):
        self.root1 = Tk()
        self.initGui = True  # flag, represent this is initialize process
        # alot of vars of the gui
        self.root1.title("Enter name")
        self.root1.geometry("250x120")
        self.root1.resizable(False, False)

        ipAddress = Label(self.root1, text="Enter ip").place(x=105, y=5)
        self.nameIP = Entry(self.root1, width=37, borderwidth=1)
        self.nameIP.place(x=10, y=35)

        self.IPInfo = StringVar()
        self.IPInfo.set(text)
        self.chosenIP = Label(self.root1, textvariable=self.IPInfo)
        self.chosenIP.place(x=10, y=55)
        self.IPEnter = Button(self.root1, text="Enter", height=1, width=12, command=self.destroy, fg="blue",
                                bg="pink")
        self.IPEnter.place(x=78, y=90)

        self.root1.protocol("WM_DELETE_WINDOW")  # if window closed in place of inputed name, shut down client
        self.root1.mainloop()

    def destroy(self):
        self.globali = self.nameIP.get()
        self.root1.destroy()

    def proceed(self,text):
        """
        part of Validate phase
        this funct waiting to the user input that represent his name
        deliver the user input to the server via the client
        the purpose is to complete the Validate phase
        """
        self.GUIItSelf(text)
        return self.globali