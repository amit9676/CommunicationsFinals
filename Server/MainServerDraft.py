import socket
import threading


class Server:
    def __init__(self, controller):
        self.__controller = controller
        self.__host = "127.0.0.1"
        self.__port = 9090
        self.active = True
        # check option if it fails
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.bind((self.__host, self.__port))
        self.__server.listen()
        self.clients = []

    def initilize(self):
        self.activate()

    def activate(self):
        print('Ready to serve..')
        counter = 1

        while self.active:
            client, address = self.__server.accept()
            self.clients.append(counter)
            self.updateClients()
            #
            print("connection established")
        print("connection closed")
        self.endServer()

    def endServer(self):
        self.__server.close()

    def updateClients(self):
        self.__controller.updateClients(self.clients)

# while True:
#     print('Ready to serve...')
#     client, address = server.accept()
#     print("connection established")
#
# server.close()


# clients = []
#
# def sendToEveryone(message):
#     for c in clients:
#         c.send(message)
#
# def handle(client):
#     while True:
#         try:
#             client.recv(1024)
#         except:
#             pass
#
# def clientAccept():
#     while(True):
#         client, address = server.accept()
#         print(f"connected with {str(address)}")
#         clients.append(client)
#         client.send("connected".encode("utf-8"))
#         thread = threading.Thread(target=handle, arge=(client,))
