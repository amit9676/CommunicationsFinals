from tkinter import *
from tkinter.ttk import Progressbar

class GUI:
    def __init__(self, clientMain):
        self.clientMain = clientMain
        self.root2 = Tk()
        self.root2.title("Client")
        self.root2.geometry("855x500")
        self.root2.resizable(False, False)
        self.LoginButton = Button(self.root2,text="Login", height=1,width=8, command=self.myClick,fg="blue", bg="pink").grid(padx=5, pady=5, column=0,row=0)
        self.labelName = Label(self.root2, text="name").grid(padx=15,column=1,row=0)
        self.e = Entry(self.root2, width=20, borderwidth=1).grid(column=2,row=0)
        self.labelName2 = Label(self.root2, text="address").grid(padx=15,column=3,row=0)
        self.e = Entry(self.root2, width=20, borderwidth=1).grid(column=4,row=0)
        self.showOnline = Button(self.root2,text="show online", height=1,width=12, command=self.myClick,fg="blue", bg="pink").grid(padx=15, pady=5, column=5,row=0)
        self.clear = Button(self.root2,text="Clear", height=1,width=12, command=self.myClick,fg="blue", bg="pink").grid(padx=7, pady=5, column=6,row=0)
        self.someCheck = Checkbutton(self.root2).grid(padx=8, pady=5, column=7,row=0)
        self.showServerFiles = Button(self.root2,text="show server files", height=1,width=13, command=self.myClick,fg="blue", bg="pink").grid(padx=5, pady=5, column=8,row=0)
        self.t2 = Text(self.root2,width=110, height=17)
        self.t2.insert(INSERT,"amit1") # --add text here--
        self.t2.configure(state="disabled", cursor="arrow")
        self.t2.place(x=5,y=45)

        slider = Scale(self.root2, showvalue=0).place(x=830,y=45,height=280)
        to = Label(self.root2, text="To").place(x=5,y=325)
        messag = Label(self.root2, text="Message").place(x=215,y=325)
        eTo = Entry(self.root2, width=30, borderwidth=1).place(x=5,y=345,height=25)
        self.eMsg = Entry(self.root2, width=85, borderwidth=1)
        self.eMsg.place(x=216,y=345,height=25)
        snd = Button(self.root2,text="Send", height=1,width=11, command=self.sendMessageOut,fg="blue", bg="pink").place(x=746,y=345,height=25)

        SFN = Label(self.root2, text="Server File Name").place(x=5,y=390)
        CFN = Label(self.root2, text="Client File Name (save as...)").place(x=265,y=390)
        eSFN = Entry(self.root2, width=40, borderwidth=1).place(x=5,y=410,height=25)
        eCFN = Entry(self.root2, width=77, borderwidth=1).place(x=268,y=410,height=25)
        prcd = Button(self.root2,text="Proceed", height=1,width=11, command=self.myClick,fg="blue", bg="pink").place(x=746,y=410,height=25)
        progras = Progressbar(self.root2,orient=HORIZONTAL,length=100,mode="determinate").place(x=5,y=455,width=300)
        self.root2.protocol("WM_DELETE_WINDOW", self.clientMain.stop)
        self.clientMain.GuiDone = True
        self.root2.mainloop()


    def initilize(self):
        self.root2.mainloop()


    def myClick(self):
        print("bye")
        #for item in data:
        #self.__t.insert(INSERT,item) # --add text here--

    def insertMessage(self,message):
        self.t2.configure(state="normal", cursor="arrow")
        self.t2.insert(INSERT,"\n" + str(message)) # --add text here--
        self.t2.configure(state="disabled", cursor="arrow")

    def sendMessageOut(self):
        message = self.eMsg.get()
        self.clientMain.write(message)

