import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#HOST = socket.gethostname()  # The server's hostname or IP address
#PORT = 65432  # The port used by the server
s.connect((socket.gethostname(), 6181))
fullMsg = ""
newMsg = True
while True:
    msg = s.recv(16)
    if newMsg:
        #print(f"new message length: {msg[:10]}")
        msgLen = int(msg[:10])
        newMsg = False
    fullMsg += msg.decode("utf-8")
    if len(fullMsg) - 10 == msgLen:
        # print("msg recieved")
        print(fullMsg[10:])
        break  