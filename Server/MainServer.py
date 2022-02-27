import socket
import threading
import pickle
import os
import time


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
            try:
                client, address = self.__server.accept()
                newClient = SingleClient(counter, client, "undefined")
                self.clients.append(newClient)
                th = threading.Thread(target=self.clientListen, args=(client,))
                th.start()
            except:
                print("Server Disconnected")

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

    def fetchFile(self, filename, client):
        size = os.path.getsize("Files/"+filename+".txt")
        segments = {}
        s=0
        try:
            with open("Files/"+filename+".txt", "rb") as file:
                c = 0
                while c <= size:
                    data = file.read(1024)
                    if not data:
                        #print("!!")
                        break
                    segments[s] = data
                    s+=1
                    c+= len(data)
            self.fileSender(client,filename,size,s,segments)
        except Exception as e:
            print(str(e))

    def fileSender(self, client, filename,size,numberOfSegments,segments):
        #print(f"nof: {numberOfSegments}")
        udp = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        port = 9091
        host = "127.0.0.2"
        udp.bind((host, port))
        packet = ("udp",filename,size,numberOfSegments, host,port)
        data_string = pickle.dumps(packet)
        client.send(data_string)


        message, address = udp.recvfrom(1024) #expect ("ready", time.time())
        currentTime = time.time()
        #future note - do something if initial upd establishment fails

        openeddata = pickle.loads(message)
        rtt = (currentTime - openeddata[1]) * 3

        while(len(segments) > 0):
            print(len(segments))
            for item in segments:
                segment = (item,segments[item])
                data_string = pickle.dumps(segment)
                udp.sendto(data_string,address)
                time.sleep(0.001)
            aidThread = threading.Thread(target=self.fileSenderAid, args=(udp,segments))
            aidThread.daemon = True
            aidThread.start()
            currentTime = time.time()
            while(time.time() - currentTime <= rtt):
                time.sleep(rtt/10)

            notack = ("notack",)
            notack_data = pickle.dumps(notack)
            udp.sendto(notack_data,(host,port))
            #print(len(segments))
            time.sleep(0.001)



        print("done")
        udp.close()

    def fileSenderAid(self, udp,segments):
        keyword = "ack"
        while keyword == "ack":
            try:
                message, address = udp.recvfrom(1024)
            except:
                return
            ack = pickle.loads(message)
            if(ack[0] == "ack"):
                del segments[ack[1]]
            else:
                keyword = "notack"
                break

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
                    print("here....")
                    self.updateUsers()
                elif packet[0] == "download":
                    self.fetchFile(packet[1],client)
                    #self.download(client)
                elif (packet[0] == "filesRequest"):
                    packet = ("filesRequest", self.files)
                    print("here..")
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
            except Exception as e:
                #print(str(e))
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
