# Create an SFTP client
import paramiko as paramiko

transport = paramiko.Transport(('hostname', 22))
transport.connect(username='username', password='password')
sftp = transport.open_sftp_client()

# Receive the file name and size
file_name = sftp.recv(1024).decode()
file_size = int(sftp.recv(1024).decode())
# Receive the file
with open(file_name, 'wb') as f:
    sftp.getfo(file_name, f)

# Close the SFTP client
sftp.close()
transport.close()
