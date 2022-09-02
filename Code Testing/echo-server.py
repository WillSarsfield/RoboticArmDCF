import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#HOST = socket.gethostname()  # Standard loopback interface address (localhost)
#PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
s.bind((socket.gethostname(), 6181))
s.listen(5)
clientsocket, addr = s.accept()
print(f"Connection to {addr} establshed")
msg = input()
if msg == "1":
    msg = "FC  L3-1|PosSC|1.03"
elif msg == "0":
    msg = "FC  L3-1|PosSC|0.03"
msg = (f"{len(msg):<10}"+msg)
clientsocket.send(bytes(msg, "utf-8"))
clientsocket.close()
