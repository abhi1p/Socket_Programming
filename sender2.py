import socket

# Create a socket on the sending device
sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the sending device's IP address and a port
sender_socket.bind(("192.168.1.116", 5000))
receiver_address = ("192.168.1.197", 5000)
# Connect the socket to the receiving device's IP address and port
sender_socket.connect(receiver_address)
# sock = socket.create_connection(receiver_address)

# print("Connected to", sock.getpeername())
# Send the message
message = "Hello from the sender device."
sender_socket.sendall(message.encode())

# Close the socket
sender_socket.close()
