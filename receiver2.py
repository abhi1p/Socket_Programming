import socket

# Create a socket on the receiving device
receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the receiving device's IP address and a port
receiver_socket.bind(("192.168.1.197", 5000))

# Listen for incoming connections
receiver_socket.listen()

# Accept an incoming connection
connection, address = receiver_socket.accept()

# Receive the message
received_message = connection.recv(1024).decode()
print("Received message:", received_message)

# Close the socket
receiver_socket.close()
