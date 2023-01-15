import socket

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.bind(("192.168.1.116", 5355))
soc.listen()
print("test")
con, addr = soc.accept()

# print("test2")
print(f"Connected to {addr}")
text = con.recv(1024).decode()
print(f"Received: {text}")
con.sendall("Success test".encode())
con.close()
#soc.close()
print("Closed")