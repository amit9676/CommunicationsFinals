import socket
import threading

Host = "127.0.0.1"
PORT = 9090
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((Host,PORT))
print("connect")
while True:
    pass



# class Client:
#     def __init__(self, host, port):
#         self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.sock.connect((host,port))
#         print("connect")
#         #thread = threading.Thread(target=self.recieve)
#         while True:
#             pass
#
#
#     def gui(self):
#         pass
#
#     def recieve(self):
#         pass


