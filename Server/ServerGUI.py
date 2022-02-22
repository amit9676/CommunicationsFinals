

##from tkinter.ttk import *
from tkinter import *
from tkinter.ttk import Progressbar
class GUI:
    def __init__(self, controller):
        print("??")
        self.__root = Tk()
        self.__controller = controller
        self.__widthSize = 500
        self.__HeightSize = 200
        self.__root.geometry(str(self.__widthSize) + "x" + str(self.__HeightSize))
        self.__root.resizable(False, False)
        self.__myButton = Button(self.__root,text="start", height=2,width=8, command=controller.activeTrue,fg="blue", bg="pink").grid(padx=5, pady=5)
        self.__myButton2 = Button(self.__root,text="stop", height=2,width=8, command=controller.activeFalse,fg="blue", bg="pink").grid(padx=5, pady=5)
        self.__t = Text(self.__root,width=50, height=12)
        self.__t.insert(INSERT,"amit") # --add text here--
        self.__t.configure(state="disabled", cursor="arrow")
        self.__t.place(x=75, y=5)
        self.__root.mainloop()





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




#e = Entry(root, width=67, borderwidth=5).place(x=80,y=5,height=190)
#e.pack()
#e.get()