import os
import socket
import sys

from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal, QThreadPool, QTimer
from PyQt5.QtWidgets import QMainWindow, QPushButton, QTextEdit, QWidget, QVBoxLayout, QApplication, QLineEdit, \
    QHBoxLayout, QLabel, QFileDialog

from PyQt5.QtCore import QRunnable, QObject, pyqtSignal

from customWidgets import Dialog
from gui import Ui_MainWindow
import traceback


class Signals(QObject):
    finished = pyqtSignal(tuple)


class Worker(QRunnable):
    def __init__(self, fun, *args, **kwargs):
        super(Worker, self).__init__()
        # store argument for further processing
        self.fun = fun
        self.args = args
        self.kwargs = kwargs
        self.signals = Signals()

    def run(self):
        try:
            result = self.fun(*self.args, **self.kwargs)
            # self.signals.finished.emit(result)
        except socket.error as e:
            print(e)
            print("Connrction Aborted")
        except Exception as e:
            # Get the traceback as a string
            tb_str = traceback.format_exception(*sys.exc_info())
            # Extract the line number from the traceback string
            print(tb_str)
            line_number = tb_str[-2].split(',')[1]
            print(f'Error occurred on line {line_number}')


class MyApp(QMainWindow, Ui_MainWindow):
    # start = pyqtSignal()
    discoveredSignal = pyqtSignal()
    notDiscoveredSignal = pyqtSignal()
    startDiscoveryResponseSignal = pyqtSignal()
    noResponseSignal = pyqtSignal()
    startReceivingCapability1 = pyqtSignal()
    startReceivingCapability2 = pyqtSignal()
    incomingTransfer = pyqtSignal()
    establishConnectionStart = pyqtSignal()

    def __init__(self):
        super(MyApp, self).__init__()
        self.path = []
        self.sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.soc3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.application_id = "APP1"
        self.setupUi(self)
        # self.initUI()
        self.discoveredDevices = []
        self.discovery = False
        self.connected = False
        self.bind_port = 5356
        self.data_transfer_port = 5355
        self.receiveStart = QTimer()
        # self.receiveStart.timeout.connect(self.timeOverflow)
        self.receiveStart.setSingleShot(True)
        self.overflow = False
        self.overflowDuration = 5000
        self.threadpool = QThreadPool()
        self.allowDiscovery = False
        self.transferDialog = Dialog(self)
        self.exitApp = False
        self.fileRecvCount = "0"
        self.recvDirectory = "./"
        self.selfIP = socket.gethostbyname(socket.gethostname())

        self.appIdInput.setPlaceholderText("Enter application ID (default: APP1)")
        self.appIdInput.textChanged.connect(self.set_application_id)
        self.discoverBtn.clicked.connect(self.startDiscover)
        self.allowDiscoveryCheckbox.stateChanged.connect(self.setAllowDiscovery)
        self.sendBtn.clicked.connect(self.sendFileSelect)
        # self.start.connect(self.getResponseAfterDiscoveryBroadcastStart)
        self.discoveredSignal.connect(self.discovered)
        self.notDiscoveredSignal.connect(self.notDiscovered)
        self.startDiscoveryResponseSignal.connect(self.DiscoveryResponse)
        self.noResponseSignal.connect(self.noResponse)
        self.startReceivingCapability1.connect(self.receiveHandshake)
        self.startReceivingCapability2.connect(self.startReceiveHandshake)
        self.transferDialog.startBtnClicked.connect(self.startReceiving)
        self.transferDialog.cancelBtnClicked.connect(self.cancelTransferStart)
        self.incomingTransfer.connect(lambda: self.transferDialog.exec_())
        self.establishConnectionStart.connect(self.establishConnection)
        # self.transferDialog.

    # def initUI(self):
    #     self.setWindowTitle("SMS1")
    #     self.discover_button = QPushButton("Discover", self)
    #     self.allow_button = QPushButton("Allow", self)
    #     self.message_box = QTextEdit(self)
    #     self.connected_device = QLineEdit(self)
    #     self.application_id_input = QLineEdit()
    #     self.application_id_input.setPlaceholderText("Enter application ID (default: APP1)")
    #     self.application_id_input.textChanged.connect(self.set_application_id)
    #     self.appIdLabel = QLabel("Application ID")
    #     self.connectedDeviceLabel = QLabel("Connected Device")
    #
    #     self.appIdLabel.setBuddy(self.application_id_input)
    #     self.connectedDeviceLabel.setBuddy(self.connected_device)
    #
    #     self.connected_device.setReadOnly(True)
    #     layout1 = QHBoxLayout()
    #     layout1.addWidget(self.discover_button)
    #     layout1.addWidget(self.allow_button)
    #
    #     self.message_box.setReadOnly(True)
    #     self.centralWidget = QWidget(self)
    #     layout = QVBoxLayout(self.centralWidget)
    #     # layout.addWidget(self.discover_button)
    #     layout2 = QHBoxLayout()
    #     layout2.addWidget(self.appIdLabel)
    #     layout2.addWidget(self.application_id_input)
    #     layout.addLayout(layout2)
    #     layout3 = QHBoxLayout()
    #     layout3.addWidget(self.connectedDeviceLabel)
    #     layout3.addWidget(self.connected_device)
    #     layout.addLayout(layout3)
    #     layout.addLayout(layout1)
    #     # layout.addWidget(self.connected_device)
    #     layout.addWidget(self.message_box)
    #     self.setCentralWidget(self.centralWidget)
    #     self.start.connect(self.startReceiving)
    #     self.discover_button.clicked.connect(self.discover)

    def setAllowDiscovery(self):
        if self.allowDiscoveryCheckbox.isChecked():
            self.allowDiscovery = True
            self.startDiscoveryResponseSignal.emit()
        else:
            self.allowDiscovery = False

    def sendFileSelect(self):
        if self.discovery and self.connected:
            fileDialog = QFileDialog()
            fileDialog.setFileMode(QFileDialog.AnyFile)
            self.path = fileDialog.getOpenFileNames(self, "Select one or more files to send", "", "All Files (*)")
            if self.path[1]:
                print(self.path)
                fileNames = []
                for i in self.path[0]:
                    temp = i.split("/")
                    print(temp[-1])
                    fileNames.append(temp[-1])
                    self.selectedFileListWidget.addItem(temp[-1])
                self.sendFileWorkerStart(fileNames)

    def sendFileWorkerStart(self, fileNames):
        self.worker = Worker(self.sendFileStart, fileNames)
        self.threadpool.start(self.worker)

    def sendFileStart(self, fileNames):
        print("sendFileStart")
        self.startSendHandshake(fileNames)

    def establishConnection(self):
        try:
            self.soc3.connect((self.discoveredDevices[-1][1][0], self.data_transfer_port))
            self.connected = True
            self.messageDisplay.append("Connected to " + self.discoveredDevices[-1][1][0])
        except Exception as e:
            print(e)
        except socket.timeout:
            print("Connection timed out")
            self.messageDisplay.append("Connection timed out")

    def startSendHandshake(self, fileNames):
        print("startHandshake")
        if self.connected:
            command1 = "File_transfer_request"
            command2 = f":{len(fileNames)}:"
            command3 = ";".join(fileNames)
            command = command1 + command2 + command3
            print("command: ", command)
            temp = command.encode()
            self.soc3.sendall(temp)
            command = self.soc3.recv(1024).decode()
            # cmd1, fileCount, temp = command.split(":")
            # fileNames = temp.split(";")
            if command == "File_transfer_Accepted":
                self.messageDisplay.append("File transfer started")
                self.send()
                print("File transfer competed")
                # self.soc3.close()
            elif command == "File_transfer_Reject":
                self.messageDisplay.append("File transfer rejected")
                # self.soc3.close()

    def send(self):
        print("send")
        for file in self.path[0]:
            self.sendFile(file)

    def sendFile(self, file):
        size = os.path.getsize(file)
        fileName = file.split("/")[-1]
        self.soc3.send(fileName.encode())  # send file name
        ack = self.soc3.recv(1024).decode()  # wait for acknowledgement
        if ack == "ACK":
            self.soc3.send(str(size).encode())  # send file size
        ack = self.soc3.recv(1024).decode()  # wait for acknowledgement
        print("File info sent")
        print("Ack: ", ack)
        if ack == "ACK":
            with open(file, "rb") as f:
                c = 0
                while c <= size:
                    data = f.read(1024)
                    if not data:
                        break
                    self.soc3.send(data)
                    c += len(data)
                    print("Sent: ", c)

    def startReceiveHandshake(self):
        # ip = self.discoveredDevices[-1][1][0]
        self.soc4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc4.bind((self.selfIP, self.data_transfer_port))
        self.soc4.settimeout(2)
        self.soc4.listen(1)
        self.establishConnectionStart.emit()
        self.receiveHandshakeStart1()

    def receiveHandshakeStart1(self):
        worker = Worker(self.receiveHandshakeStart2)
        self.threadpool.start(worker)

    def receiveHandshakeStart2(self):
        self.acceptConnection()
        self.receiveHandshake()

    def acceptConnection(self):
        try:
            self.recvFile_conn, addr = self.soc4.accept()
        except socket.timeout:
            # print("timeout")
            if not self.exitApp:
                self.acceptConnection()
            self.soc4.close()
        except Exception as e:
            # Get the traceback as a string
            tb_str = traceback.format_exception(*sys.exc_info())
            # Extract the line number from the traceback string
            print(tb_str)
            line_number = tb_str[-2].split(',')[1]
            print(f'Error occurred on line {line_number}')

    def receiveHandshake(self):
        # print("startReceiveHandshake")
        try:
            command = self.recvFile_conn.recv(1024).decode()
            cmd1, self.fileRecvCount, temp = command.split(":")
            fileNames = temp.split(";")
            if cmd1 == "File_transfer_request":
                print("command: ", command)
                for i in fileNames:
                    self.transferDialog.incomingTransferList.addItem(i)
                self.incomingTransfer.emit()
        except socket.error as e:
            if "abort" in str(e) or "closed" in str(e):
                print("Connection aborted")
            else:
                raise e

            # self.soc4.close()

    def startReceiving(self):
        worker = Worker(self.receive)
        self.threadpool.start(worker)

    # def replyTransferList(self):
    # get selected files from transferDialog
    # selectedFiles1 = []
    # temp = []
    # for i in range(self.transferDialog.incomingTransferList.count()):
    #     temp.append(self.transferDialog.incomingTransferList.item(i).text())
    #     if self.transferDialog.incomingTransferList.item(i).isSelected():
    #         selectedFiles1.append(self.transferDialog.incomingTransferList.item(i).text())
    # if len(selectedFiles1) == 0:
    #     selectedFiles1 = temp
    # print("selectedFiles1: ", selectedFiles1)
    # self.receive()

    def receive(self):
        self.recvFile_conn.sendall("File_transfer_Accepted".encode())
        print("startTransfer")
        self.messageDisplay.append("File transfer started")
        for i in range(int(self.fileRecvCount)):
            self.receiveFile()
        self.messageDisplay.append("File transfer completed")

    def receiveFile(self):
        print("In receiveFile")
        fileName = self.recvFile_conn.recv(1024).decode()
        self.recvFile_conn.sendall("ACK".encode())
        fileSize = int(self.recvFile_conn.recv(1024).decode())
        self.recvFile_conn.sendall("ACK".encode())
        print("fileName: ", fileName)
        print("fileSize: ", fileSize)
        with open(self.recvDirectory + fileName, "wb") as f:
            c = 0
            while c <= fileSize:
                data = self.recvFile_conn.recv(1024)
                if not data:
                    break
                f.write(data)
                c += len(data)
                print("Received: ", c)
        print("After transfer")
    # def replyWithTransferList(self, fileNames):
    #     command1 = "File_transfer_Accepted"
    #     # command2 = f":{len(fileNames)}:"
    #     # command3 = ";".join(fileNames)
    #     # command = command1 + command2 + command3
    #     self.recvFile_conn.sendall(command1.encode())

    def cancelTransferStart(self):
        print("cancelTransfer")
        worker = Worker(self.cancelTransfer)
        self.threadpool.start(worker)

    def cancelTransfer(self):
        self.recvFile_conn.send("File_transfer_Reject".encode())
        self.receiveHandshake()
        # self.startReceivingCapability1.emit()

    def set_application_id(self, text):
        self.application_id = text
        print(self.application_id)

    def DiscoveryResponse(self):  # respond to broadcast discovery request
        if self.allowDiscovery:  # only if discovery is allowed
            self.worker = Worker(self.startDiscoveryResponse)
            # self.worker.signals.finished.connect(self.discovered)
            self.threadpool.start(self.worker)

    def startDiscoveryResponse(self):
        # Allow reuse of the socket
        self.sock2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Set the socket to allow broadcast packets
        self.sock2.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Bind the socket to the local IP address and the same port as the broadcast packet
        self.sock2.bind(("", self.bind_port))
        self.sock2.settimeout(3)
        # Receive broadcast packet
        try:
            data, addr = self.sock2.recvfrom(1024)
            data = data.decode()
            msg = data.split(":")
            if msg[0] == "Hello, network! from":
                response_data = "Hello, I am device:" + self.application_id
                response_data = response_data.encode()
                self.sock2.sendto(response_data, addr)
                device = msg[1]
                self.discoveredDevices.append((device, addr))
                print("Discovered device: ", addr)
                self.discoveredSignal.emit()
        except socket.timeout:
            print("Discovery response timeout")
            self.noResponseSignal.emit()
        except Exception as e:
            # Get the traceback as a string
            tb_str = traceback.format_exception(*sys.exc_info())
            # Extract the line number from the traceback string
            print(tb_str)
            line_number = tb_str[-2].split(',')[1]
            print(f'Error occurred on line {line_number}')

    def startDiscover(self):
        self.worker = Worker(self.discover)
        self.threadpool.start(self.worker)

    def discover(self):  # send broadcast discovery request
        # only  if app is not responding to discovery request, means it is capable of sending discovery request
        # sending discovery request and discovery response are mutually exclusive
        if not self.allowDiscovery:
            # Create a UDP socket
            self.sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Allow reuse of the socket
            self.sock1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Set the socket to allow broadcast packets
            self.sock1.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            # Bind the socket to the local IP address and a port
            self.sock1.bind((self.selfIP, self.bind_port))
            # Set a timeout so the socket does not block indefinitely when trying to receive data.
            self.sock1.settimeout(2)

            msg = "Hello, network! from:" + self.application_id
            msg = msg.encode()
            # Send a broadcast packet to the network
            self.sock1.sendto(msg, ("<broadcast>", self.bind_port))
            # self.start.emit()
            self.getResponseAfterDiscoveryBroadcast()

    # def getResponseAfterDiscoveryBroadcastStart(self):  # get device details after sending discovery request
    #     self.worker = Worker(self.getResponseAfterDiscoveryBroadcast)
    #     # self.worker.signals.finished.connect(self.discovered)
    #     self.threadpool.start(self.worker)
    #     # self.message_box.append("Started receiving")
    #     self.messageDisplay.append("Started receiving")

    def getResponseAfterDiscoveryBroadcast(self):
        # Receive responses from other devices on the network
        count = 0
        # self.receiveStart.start(self.overflowDuration)
        # print("Timer is started: ", self.receiveStart.isActive())
        self.messageDisplay.append("Started receiving")
        while True:
            try:
                data, addr = self.sock1.recvfrom(1024)
                count += 1
                # print("Received= ", addr[0])
                data = data.decode()
                res = data.split(":")
                # print("Received message ", res)
                if res[0] == "Hello, I am device" and addr[0] != self.selfIP:
                    self.discoveredDevices.append((res[1], addr))
                    self.discoveredSignal.emit()
                    self.sock1.close()
                    break
                # if addr[0] != socket.gethostbyname(socket.gethostname()):
                #     # if addr[0] != "192.168.247.1":
                #     break
                # print("overflow:", self.overflow)
                # if not self.receiveStart.isActive():
                #     self.notDiscoveredSignal.emit()
                #     break
                # if count == 2:
                #     break
            except socket.timeout:
                self.notDiscoveredSignal.emit()
                self.sock1.close()
                break
            except Exception as e:
                # Get the traceback as a string
                tb_str = traceback.format_exception(*sys.exc_info())
                # Extract the line number from the traceback string
                print(tb_str)
                line_number = tb_str[-2].split(',')[1]
                print(f'Error occurred on line {line_number}')

    def timeOverflow(self):
        print("overflowed")
        self.overflow = True

    def discovered(self):
        self.messageDisplay.append("Discovered")
        deviceName, addr = self.discoveredDevices[-1]
        # data, addr = msg
        # self.discoveredDevices.append(addr)
        print("Received message from", addr)
        self.messageDisplay.append("Received message from " + str(addr))
        print("Device name: ", deviceName)
        # self.connected_device.setText(deviceName)
        self.coonectedDeviceDisplay.setText(deviceName)
        self.discovery = True
        self.startReceivingCapability2.emit()

    def notDiscovered(self):
        self.messageDisplay.append("Not discovered any device")

    def noResponse(self):
        self.messageDisplay.append("No Incoming Request")
        self.allowDiscoveryCheckbox.setChecked(False)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        # self.sock.close()
        self.exitApp = True
        try:
            self.recvFile_conn.close()
        except Exception as e:
            print(e)

        # self.sock1.close()
        # self.sock2.close()
        # self.soc3.close()
        # self.soc4.close()
        # self.recvFile_conn.close()
        # self.threadpool.waitForDone()
        self.threadpool.clear()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())
