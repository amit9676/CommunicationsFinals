# from tkinter import *
# #from tkinter.ttk import *
# from tkinter.ttk import Progressbar
#
# root = Tk()
# widthSize = 500
# HeightSize = 200
# root.geometry(str(widthSize) + "x" + str(HeightSize))
# root.resizable(False, False)
#
#
# def myClick():
#     pass
#
#
# def display():
#     pass
#     #myLabel = Label(root, text=e.get())
#     #myLabel.pack()
#
# def secondWindow():
#     root2 = Tk()
#     root2.title("Client2")
#     root2.geometry("855x500")
#     root2.resizable(False, False)
#     LoginButton = Button(root2,text="Login", height=1,width=8, command=myClick,fg="blue", bg="pink").grid(padx=5, pady=5, column=0,row=0)
#     labelName = Label(root2, text="name").grid(padx=15,column=1,row=0)
#     e = Entry(root2, width=20, borderwidth=1).grid(column=2,row=0)
#     labelName2 = Label(root2, text="address").grid(padx=15,column=3,row=0)
#     e = Entry(root2, width=20, borderwidth=1).grid(column=4,row=0)
#     showOnline = Button(root2,text="show online", height=1,width=12, command=myClick,fg="blue", bg="pink").grid(padx=15, pady=5, column=5,row=0)
#     clear = Button(root2,text="Clear", height=1,width=12, command=myClick,fg="blue", bg="pink").grid(padx=7, pady=5, column=6,row=0)
#     someCheck = Checkbutton(root2).grid(padx=8, pady=5, column=7,row=0)
#     showServerFiles = Button(root2,text="show server files", height=1,width=13, command=myClick,fg="blue", bg="pink").grid(padx=5, pady=5, column=8,row=0)
#     t2 = Text(root2,width=110, height=17)
#     t2.insert(INSERT,"amit") # --add text here--
#     t2.configure(state="disabled", cursor="arrow")
#     t2.place(x=5,y=45)
#     slider = Scale(root2, showvalue=0).place(x=830,y=45,height=280)
#     to = Label(root2, text="To").place(x=5,y=325)
#     messag = Label(root2, text="Message").place(x=215,y=325)
#     eTo = Entry(root2, width=30, borderwidth=1).place(x=5,y=345,height=25)
#     eMsg = Entry(root2, width=85, borderwidth=1).place(x=216,y=345,height=25)
#     snd = Button(root2,text="Send", height=1,width=11, command=myClick,fg="blue", bg="pink").place(x=746,y=345,height=25)
#
#     SFN = Label(root2, text="Server File Name").place(x=5,y=390)
#     CFN = Label(root2, text="Client2 File Name (save as...)").place(x=265,y=390)
#     eSFN = Entry(root2, width=40, borderwidth=1).place(x=5,y=410,height=25)
#     eCFN = Entry(root2, width=77, borderwidth=1).place(x=268,y=410,height=25)
#     prcd = Button(root2,text="Proceed", height=1,width=11, command=myClick,fg="blue", bg="pink").place(x=746,y=410,height=25)
#     progras = Progressbar(root2,orient=HORIZONTAL,length=100,mode="determinate").place(x=5,y=455,width=300)
#
#     root2.mainloop()
#
#
# myButton = Button(root,text="start", height=2,width=8, command=secondWindow,fg="blue", bg="pink").grid(padx=5, pady=5)
#
# t = Text(root,width=50, height=12)
# t.insert(INSERT,"amit") # --add text here--
# t.configure(state="disabled", cursor="arrow")
# t.place(x=75, y=5)
#
# #e = Entry(root, width=67, borderwidth=5).place(x=80,y=5,height=190)
# #e.pack()
# #e.get()
# root.mainloop()
