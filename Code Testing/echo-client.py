import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = "192.168.56.1"  # The server's hostname or IP address
PORT = 6181  # The port used by the server
print(HOST)
s.connect((HOST, PORT))
msg = s.recv(64)
message = str(msg)
message = message[2:-1]
print(message)
#fullMsg = ""
#newMsg = True
#While True:
#    msg = s.recv(16)
#    if newMsg:
#        #print(f"new message length: {msg[:10]}")
#        msgLen = int(msg[:10])
#        newMsg = False
#    fullMsg += msg.decode("utf-8")
#    if len(fullMsg) - 10 == msgLen:
#        # print("msg recieved")
#        print(fullMsg[10:])
#        break  