import socket

# Create a socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to an IP address and port
s.bind(("192.168.1.116", 5000))

# Set the socket to listen for incoming connections
s.listen()

# Wait for a device to connect
conn, addr = s.accept()
print("Device connected:", addr)

# Close the socket
s.close()
