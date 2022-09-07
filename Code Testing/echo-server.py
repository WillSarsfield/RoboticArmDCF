import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = "192.168.56.1"  # Standard loopback interface address (localhost)
PORT = 6181  # Port to listen on (non-privileged ports are > 1023)
print(HOST)
s.bind((HOST, PORT))

while True:
    if input() == "listen":
        listen = True
    else:
        listen = False

    if listen == True:
        s.listen(5)
        clientsocket, addr = s.accept()
        msg = "FC  L3-1|PosSC|1.03"
        print(f"{msg} sent to to {addr}")
        clientsocket.send(bytes(msg, "utf-8"))
        clientsocket.close()
        listen = False
