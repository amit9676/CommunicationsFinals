from tkinter import *


class ServerGUI:
    """
    this class is the server GUI
    its opens a window that print occures a.k.a logs
    """
    def __init__(self, server):
        """ constructor """
        self.my_server = server

    def basicGUI(self):
        """
        based on tkinter
        simple window that allows the user to see the server occures
        """
        self.__root = Tk()
        self.__widthSize = 500
        self.__HeightSize = 200
        self.__root.title("Server")
        self.__root.geometry(str(self.__widthSize) + "x" + str(self.__HeightSize))
        self.__root.resizable(False, False)
        self.__t = Text(self.__root, width=60, height=11)
        self.__t.insert(INSERT, "Server is running\n")  # --add text here--
        self.__t.configure(state="disabled", cursor="arrow")
        self.__t.place(x=5, y=5)
        self.__root.protocol("WM_DELETE_WINDOW", self.my_server.endServer)
        self.__root.mainloop()

    def insertUpdates(self, message):
        """
        there is update that shall be represented to the user
        :message: is the String that shall be printed at the window screen
        """
        self.__t.configure(state="normal", cursor="arrow")
        self.__t.insert(INSERT, str(message) + "\n")  # --add text here--
        self.__t.configure(state="disabled", cursor="arrow")
