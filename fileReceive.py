import paramiko

transport = paramiko.Transport(('hostname', 22))
transport.connect(username='username', password='password')
sftp = transport.open_sftp_client()


def progress(transferred, toBeTransferred):
    print("Received: {0}\tOut of: {1}".format(transferred, toBeTransferred))


# Receive the file
file_path = 'example_remote.txt'
sftp.get(file_path, 'example_local.txt', callback=progress)

# Close the SFTP client
sftp.close()
transport.close()
