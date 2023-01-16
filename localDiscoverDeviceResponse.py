import socket

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Allow reuse of the socket
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Set the socket to allow broadcast packets
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Bind the socket to the local IP address and the same port as the broadcast packet
sock.bind(('192.168.1.140', 5001))

# Receive broadcast packet
data, addr = sock.recvfrom(1024)

# Print the received data
print("Received broadcast packet from", addr)
print(data)

# Send a response packet back to the sender
response_data = b"Hello, I am device XYZ"
sock.sendto(response_data, addr)
