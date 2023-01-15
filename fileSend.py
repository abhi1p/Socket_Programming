import paramiko

# Create an SFTP client
transport = paramiko.Transport(('hostname', 22))
transport.connect(username='username', password='password')
sftp = transport.open_sftp_client()


def progress(transferred, toBeTransferred):
    print("Transferred: {0}\tOut of: {1}".format(transferred, toBeTransferred))


# Send the file
file_path = 'example.txt'
sftp.put(file_path, 'example_remote.txt', callback=progress)

# Close the SFTP client
sftp.close()
transport.close()
