import socket
import threading
from Client import SingleClient
import pickle

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

            #client.send("name".encode("utf-8"))
            name = client.recv(1024)
            newClient = SingleClient.SingleClient(counter,client,name.decode('utf-8'))
            self.clients.append(newClient)

            print(f"connection established with {newClient.name}")
            counter+=1
            print(str(len(self.clients)))
            th =threading.Thread(target=self.clientListen, args=(client,))
            th.start()
            #print("thread count" + str(threading.active_count()))

        print("connection closed")
        self.endServer()

    def endServer(self):
        self.__server.close()


    def updateUsers(self):
        list = []
        list.append("update")
        for c in self.clients:
            list.append(c.name)
        for c in self.clients:
            data_string = pickle.dumps(list)
            c.client.send(data_string)

    def broadcast(self,packet):
        data_string = pickle.dumps(packet)
        for c in self.clients:
            c.client.send(data_string)

    def clientListen(self, client):
        currentClient = None
        for c in self.clients:
            if c.client == client:
                currentClient = c
                break

        while True:
            try:
                data = client.recv(4096)
                packet = pickle.loads(data)
                if(packet[0] == "broadcast"):
                    self.broadcast(packet)
                elif(packet[0] == "update"):
                    self.updateUsers()
                #elif(packet[0] == "validate"):
                    #self.validate(packet[1])
                #print(this)
                #print(":):)!")
                #message = currentClient.name + ": " + client.recv(1024).decode('utf-8')
                #self.broadcast(message)
                # if message == "out":
                #     print("clie")
                #     self.clients.remove(client)
                # else:
                #     self.broadcast(message)
            except:
                self.clients.remove(currentClient)
                client.close()
                self.updateUsers()
                break







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
