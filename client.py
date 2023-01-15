import socket

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.connect(("192.168.1.116", 5000))
soc.send("Socket testing".encode())
text = soc.recv(1024).decode()
print(f"Received: {text}")
soc.close()
print("Closed")
