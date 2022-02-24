import socket
import threading
import pickle


class SingleClient:
    def __init__(self, id, client, name):
        self.id = id
        self.client = client
        self.name = name
        self.active = False


class Server:
    def __init__(self):
        self.__host = "127.0.0.1"
        self.__port = 9090
        self.active = True
        # check option if it fails
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.bind((self.__host, self.__port))
        self.__server.listen(15)
        self.clients = []
        self.threads = []
        self.files = ["one", "two", "three"]

        self.activate()

    def initilize(self):
        self.activate()

    def terminate_client(self, client):
        print("terminate client of: ", client.name)
        self.clients.remove(client)
        client.client.close()
        self.updateUsers()

    def activate(self):
        print('Ready to serve..')
        counter = 1

        while self.active:
            client, address = self.__server.accept()
            newClient = SingleClient(counter, client, "undefined")
            self.clients.append(newClient)
            th = threading.Thread(target=self.clientListen, args=(client,))
            th.start()

            # client.send("name".encode("utf-8"))
            # name = client.recv(1024)
            # newClient = SingleClient.SingleClient(counter,client,name.decode('utf-8'))
            # self.clients.append(newClient)

            # print(f"connection established with {newClient.name}")
            # counter+=1
            # print(str(len(self.clients)))

            # print("thread count" + str(threading.active_count()))

        print("connection closed")
        self.endServer()

    def endServer(self):
        self.__server.close()

    def updateUsers(self):
        list = []
        list.append("update")
        for c in self.clients:
            if c.active == True:
                list.append(c.name)
        for c in self.clients:
            if c.active == True:
                data_string = pickle.dumps(list)
                try:
                    c.client.send(data_string)
                except:
                    self.terminate_client(c)
                    break

    def private(self, packet):
        addresee = packet[2]
        for c in self.clients:
            if addresee == c.name:
                data_string = pickle.dumps(packet)
                try:
                    c.client.send(data_string)
                    return True
                except:
                    self.terminate_client(c)
                    break
        return False

    def broadcast(self, packet):
        data_string = pickle.dumps(packet)
        for c in self.clients:
            try:
                c.client.send(data_string)
            except:
                self.terminate_client(c)

    def validate(self, name, requester):
        for c in self.clients:
            if c.active == True and c.name == name:
                return False
        requester.active = True
        requester.name = name
        return True

    def download(self):
        pass

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
                if (packet[0] == "broadcast"):
                    self.broadcast(packet)
                elif (packet[0] == "update"):
                    self.updateUsers()
                elif packet[0] == "download":
                    print(packet[1])
                    self.download()
                elif (packet[0] == "filesRequest"):
                    packet = ("filesRequest", self.files)
                    files = pickle.dumps(packet)
                    client.send(files)
                elif (packet[0] == "private"):
                    if (self.private(packet)):
                        data = pickle.dumps(packet)
                        client.send(data)
                    else:
                        error = ("error",)
                        data = pickle.dumps(error)
                        client.send(data)
                elif (packet[0] == "validate"):
                    answer = None
                    if self.validate(packet[1], currentClient) == True:
                        answer = ("validate", True)

                    else:
                        answer = ("validate", False)
                    data = pickle.dumps(answer)
                    client.send(data)
                # print(this)
                # print(":):)!")
                # message = currentClient.name + ": " + client.recv(1024).decode('utf-8')
                # self.broadcast(message)
                # if message == "out":
                #     print("clie")
                #     self.clients.remove(client)
                # else:
                #     self.broadcast(message)
            except:
                self.terminate_client(currentClient)
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
