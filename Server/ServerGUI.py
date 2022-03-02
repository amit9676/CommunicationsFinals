##from tkinter.ttk import *
from tkinter import *
from tkinter.ttk import Progressbar


class ServerGUI:
    def __init__(self, server):
        self.my_server = server

    def basicGUI(self):
        self.__root = Tk()
        self.__widthSize = 500
        self.__HeightSize = 200
        self.__root.geometry(str(self.__widthSize) + "x" + str(self.__HeightSize))
        self.__root.resizable(False, False)
        self.__t = Text(self.__root, width=60, height=11)
        self.__t.insert(INSERT, "Server is running\n")  # --add text here--
        self.__t.configure(state="disabled", cursor="arrow")
        self.__t.place(x=5, y=5)
        self.__root.protocol("WM_DELETE_WINDOW", self.my_server.endServer)
        self.__root.mainloop()

    def insertUpdates(self, message):
        self.__t.configure(state="normal", cursor="arrow")
        self.__t.insert(INSERT, str(message) + "\n")  # --add text here--
        self.__t.configure(state="disabled", cursor="arrow")

# root = Tk()
# controller = ServerController.ServerController()
# widthSize = 500
# HeightSize = 200
# root.geometry(str(widthSize) + "x" + str(HeightSize))
# root.resizable(False, False)
#
# myButton = Button(root,text="start", height=2,width=8, command=controller.activate(),fg="blue", bg="pink").grid(padx=5, pady=5)
# myButton2 = Button(root,text="stop", height=2,width=8, command=controller.deActivate(),fg="blue", bg="pink").grid(padx=5, pady=5)
#
# t = Text(root,width=50, height=12)
# t.insert(INSERT,"amit") # --add text here--
# t.configure(state="disabled", cursor="arrow")
# t.place(x=75, y=5)
#
#
# root.mainloop()


# e = Entry(root, width=67, borderwidth=5).place(x=80,y=5,height=190)
# e.pack()
# e.get()
