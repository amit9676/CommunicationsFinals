import socket
import threading
import pickle
import ClientGUI

Host = "127.0.0.1"
PORT = 9090


# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.connect((Host,PORT))
# print("connect")
# while True:


class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((Host, PORT))
        self.recieveThread = threading.Thread(target=self.recieve)
        self.recieveThread.daemon = True
        self.isActive = True
        self.recieveThread.start()
        # self.nameRequestThread = threading.Thread(target=self.recieve)
        # self.recieveThread.daemon = True

        self.name = ""
        self.files = [""]

        self.gui_obj = ClientGUI.GUIClient(self)
        # self.nameRequest()
        # self.write(self.name)
        self.GuiDone = False
        self.gui = None
        self.GuiThread = threading.Thread(target=self.gui_obj.run())
        # self.GuiThread.daemon = True

        self.updateThread = threading.Thread(target=self.requestInitialData)
        self.updateThread.daemon = True

        self.updateThread.start()
        self.GuiThread.start()



        print("connect")

    def send_packet(self, packet):
        try:
            data_string = pickle.dumps(packet)
            self.sock.send(data_string)
        except:
            print("connection lost with the server, closing the client...")
            self.stop()

    def sendToServer(self, message, addresse):
        # server method
        if addresse == "":
            packet = ("broadcast", self.name, message)
        else:
            packet = ("private", self.name, addresse, message)
        self.send_packet(packet)

    def requestInitialData(self):
        while not self.GuiDone:
            pass
        packet1 = ("update",)
        packet2 = ("filesRequest",)
        self.send_packet(packet1)
        self.send_packet(packet2)


    # def guiCreate(self):
    #     self.gui = ClientGUI.GUI(self)

    def download(self, currentFile):
        packet = ("download", currentFile)
        self.send_packet(packet)

    def stop(self):
        self.isActive = False
        # self.root2.destroy()
        # self.root1.destroy()
        self.sock.close()
        exit(0)

    def requestInitialData(self):
        while not self.GuiDone:
            pass
        packet1 = ("update",)
        packet2 = ("filesRequest",)
        self.send_packet(packet1)
        self.send_packet(packet2)

    def recieve(self):
        # main function to recieve data from server
        # arr = ("key word", "data")
        # data_string = pickle.dumps(arr)
        # self.sock.send(data_string)
        while self.isActive:
            try:
                data = self.sock.recv(1024)
                packet = pickle.loads(data)
                if packet[0] == "broadcast" and self.GuiDone:
                    self.gui_obj.insertMessage(packet[1] + " (broadcast): " + packet[2])
                elif packet[0] == "private" and self.GuiDone:
                    if self.name == packet[1]:
                        self.gui_obj.insertMessage(packet[1] + " (to " + packet[2] + "): " + packet[3])
                    else:
                        self.gui_obj.insertMessage(packet[1] + " (to you): " + packet[3])
                elif packet[0] == "error" and self.GuiDone:
                    self.gui_obj.insertMessage("message could not be sent")
                elif packet[0] == "filesRequest":
                    self.files = packet[1]
                    self.gui_obj.displayFiles()

                    print(self.files)
                elif packet[0] == "update":
                    self.gui_obj.insertUsers(packet)
                elif packet[0] == "validate":
                    if packet[1] == True:
                        self.gui_obj.confirmedName = "True"
                    else:
                        self.gui_obj.confirmedName = "False"

            except:
                self.sock.close()
                break


if __name__ == '__main__':
    # Server = Server.ServerController.ServerController()
    client = Client()
