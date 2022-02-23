import socket
import threading

class Server:
    def __init__(self):
        self.__host = "127.0.0.1"
        self.__port = 9090
        self.active = True
        #check option if it fails
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.bind((self.__host,self.__port))
        self.__server.listen()
        self.clients = []
        self.threads = []

        self.activate()




    def initilize(self):
        self.activate()

    def activate(self):
        print('Ready to serve..')
        counter = 1

        while self.active:

            client, address = self.__server.accept()
            self.clients.append(client)
            client.send("amit".encode("utf-8"))
            #
            print(f"connection established with str({address})")
            print(str(len(self.clients)))
            th =threading.Thread(target=self.clientListen, args=(client,))
            th.start()
            print("thread count" + str(threading.active_count()))

        print("connection closed")
        self.endServer()

    def endServer(self):
        self.__server.close()

    def broadcast(self,message):
        for c in self.clients:
            c.send(message.encode("utf-8"))

    def clientListen(self, client):
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                self.broadcast(message)
            except:
                #self.clients.remove(client)
                client.close()







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
