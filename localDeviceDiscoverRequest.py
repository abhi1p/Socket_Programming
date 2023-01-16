import socket
# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Allow reuse of the socket
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Set the socket to allow broadcast packets
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Bind the socket to the local IP address and a port
sock.bind(("192.168.1.116", 5001))

# Send a broadcast packet to the network
sock.sendto(b"Hello, network!", ("192.168.1.255", 5001))

# Receive responses from other devices on the network
# while True:
data, addr = sock.recvfrom(1024)
print("Received message from", addr)
data, addr = sock.recvfrom(1024)
print("Received message from", addr)
print(data)
