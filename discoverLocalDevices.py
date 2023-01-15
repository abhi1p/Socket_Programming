import socket
import sys

from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal, QThreadPool, QTimer
from PyQt5.QtWidgets import QMainWindow, QPushButton, QTextEdit, QWidget, QVBoxLayout, QApplication, QLineEdit, \
    QHBoxLayout, QLabel, QFileDialog

from PyQt5.QtCore import QRunnable, QObject, pyqtSignal
from gui import Ui_MainWindow


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
        except Exception as e:
            print(e)


class MyApp(QMainWindow, Ui_MainWindow):
    start = pyqtSignal()
    discoveredSignal = pyqtSignal()
    notDiscoveredSignal = pyqtSignal()
    startDiscoveryResponseSignal = pyqtSignal()
    noResponseSignal = pyqtSignal()
    startReceivingCapability = pyqtSignal()

    def __init__(self):
        super(MyApp, self).__init__()
        self.application_id = "APP1"
        self.setupUi(self)
        # self.initUI()
        self.discoveredDevices = []
        self.connected = False
        self.bind_port = 5355
        self.data_transfer_port = 5356
        self.receiveStart = QTimer()
        # self.receiveStart.timeout.connect(self.timeOverflow)
        self.receiveStart.setSingleShot(True)
        self.overflow = False
        self.overflowDuration = 5000
        self.threadpool = QThreadPool()
        self.allowDiscovery = False

        self.appIdInput.setPlaceholderText("Enter application ID (default: APP1)")
        self.appIdInput.textChanged.connect(self.set_application_id)
        self.discoverBtn.clicked.connect(self.discover)
        self.allowDiscoveryCheckbox.stateChanged.connect(self.setAllowDiscovery)
        self.sendBtn.clicked.connect(self.sendFileSelect)
        self.start.connect(self.getResponseAfterDiscoveryBroadcastStart)
        self.discoveredSignal.connect(self.discovered)
        self.notDiscoveredSignal.connect(self.notDiscovered)
        self.startDiscoveryResponseSignal.connect(self.DiscoveryResponse)
        self.noResponseSignal.connect(self.noResponse)
        self.startReceivingCapability.connect(self.startReceiveHandshake)

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
        fileDialog = QFileDialog()
        fileDialog.setFileMode(QFileDialog.AnyFile)
        path = fileDialog.getOpenFileNames(self, "Select one or more files to send", "", "All Files (*)")
        if path[1]:
            print(path)
            fileNames = []
            for i in path[0]:
                temp = i.split("/")
                print(temp[-1])
                fileNames.append(temp[-1])
            self.sendFileWorkerStart(fileNames)

    def sendFileWorkerStart(self, fileNames):
        self.worker = Worker(self.sendFileStart, fileNames)
        self.threadpool.start(self.worker)

    def sendFileStart(self, fileNames):
        print("sendFileStart")
        self.startSendHandshake(fileNames)

    def startSendHandshake(self, fileNames):
        print("startHandshake")
        self.soc3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc3.connect(self.discoveredDevices[-1][1])

        command1 = "File_transfer_request"
        command2 = f":{len(fileNames)}:"
        command3 = ";".join(fileNames)
        command = command1 + command2 + command3
        print("command: ", command)
        temp = command.encode()
        self.soc3.sendall(temp)
        # print(temp.__sizeof__())
        # self.soc3.send(.encode())

    def startReceiveHandshake(self):
        print("startReceiveHandshake")
        self.soc4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip = self.discoveredDevices[-1][1][0]
        self.soc4.bind((ip, 5000))
        self.soc4.listen(1)
        conn, addr = self.soc4.accept()
        command = conn.recv(1024).decode()
        print("command: ", command)
        self.soc4.close()

    def set_application_id(self, text):
        self.application_id = text
        print(self.application_id)

    def DiscoveryResponse(self):  # respond to broadcast discovery request
        if self.allowDiscovery:  # only if discovery is allowed
            self.worker = Worker(self.startDiscoveryResponse)
            # self.worker.signals.finished.connect(self.discovered)
            self.threadpool.start(self.worker)

    def startDiscoveryResponse(self):
        self.sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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

    def discover2(self):
        interfaces = socket.getaddrinfo(host=socket.gethostname(), port=None, family=socket.AF_INET)
        allips = [ip[-1][0] for ip in interfaces]

        msg = b"Hello, network!"
        # self.start.emit()
        while True:

            # for ip in allips:
            for i in range(1):
                # print(f'sending on {ip}')
                self.sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
                self.sock1.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                self.sock1.bind(("192.168.1.116", 0))
                self.sock1.sendto(msg, ("<broadcast>", 5355))
                # sock.close()
            break

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
            self.sock1.bind((socket.gethostbyname(socket.gethostname()), self.bind_port))
            # Set a timeout so the socket does not block indefinitely when trying to receive data.
            self.sock1.settimeout(2)

            msg = "Hello, network! from:" + self.application_id
            msg = msg.encode()
            # Send a broadcast packet to the network
            self.sock1.sendto(msg, ("<broadcast>", self.bind_port))
            self.start.emit()

    def getResponseAfterDiscoveryBroadcastStart(self):  # get device details after sending discovery request
        self.worker = Worker(self.getResponseAfterDiscoveryBroadcast)
        # self.worker.signals.finished.connect(self.discovered)
        self.threadpool.start(self.worker)
        # self.message_box.append("Started receiving")
        self.messageDisplay.append("Started receiving")

    def getResponseAfterDiscoveryBroadcast(self):
        # Receive responses from other devices on the network
        count = 0
        # self.receiveStart.start(self.overflowDuration)
        # print("Timer is started: ", self.receiveStart.isActive())
        while True:
            try:
                data, addr = self.sock1.recvfrom(1024)
                count += 1
                # print("Received= ", addr[0])
                data = data.decode()
                res = data.split(":")
                # print("Received message ", res)
                if res[0] == "Hello, I am device" and addr[0] != socket.gethostbyname(socket.gethostname()):
                    self.discoveredDevices.append((res[1], addr))
                    self.discoveredSignal.emit()
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
                break

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
        self.startReceivingCapability.emit()

    def notDiscovered(self):
        self.messageDisplay.append("Not discovered any device")

    def noResponse(self):
        self.messageDisplay.append("No Incoming Request")
        self.allowDiscoveryCheckbox.setChecked(False)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        # self.sock.close()
        self.threadpool.waitForDone()
        self.threadpool.clear()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())
