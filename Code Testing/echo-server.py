import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = "192.168.56.1"  # Standard loopback interface address (localhost)
PORT = 6181  # Port to listen on (non-privileged ports are > 1023)
print(HOST)
s.bind((HOST, PORT))
s.listen(5)
clientsocket, addr = s.accept()
print(f"Connection to {addr} establshed")
msg = "FC  L3-1|PosSC|1.03"
clientsocket.send(bytes(msg, "utf-8"))
clientsocket.close()
