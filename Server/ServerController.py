from Server import ServerGUI, MainServer
import threading


class ServerController:
    def __init__(self):
        self.__active = False
        self.__Server = MainServer.Server(self)
        self.ServerThread = threading.Thread(target=self.activate)
        self.ServerThread.daemon = True
        self.ServerThread.start()

        self.__GUI = ServerGUI

    def activeTrue(self):
        self.__active = True

    def activeFalse(self):

        self.__Server.active = False
        self.__active = False

    def createThread(self):
        while not self.__active:
            pass
        self.activate()

    def activate(self):
        while True:
            if self.__active:
                self.__Server.active = True
                self.__Server.initilize()

    def deActivate(self):
        if self.__Server.active:
            self.__Server.active = False

    def updateClients(self, data):
        self.__GUI.displayData()
