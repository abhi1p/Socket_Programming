# to make messaging app similiar to test.py using pyqt5 and socket programming but will use qthreadpool and qrunnable
# instead of qthread
import socket
import sys

from PyQt5.QtCore import QRunnable, pyqtSlot, QThreadPool, pyqtSignal, QObject, QTimer
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QWidget


class Signals(QObject):
    message_received = pyqtSignal(object)


class ReceiveThread(QRunnable):
    def __init__(self, port):
        super(ReceiveThread, self).__init__()
        self.port = port
        self.signals = Signals()

    @pyqtSlot()
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', self.port))
            s.listen()
            while True:
                conn, addr = s.accept()
                with conn:
                    print('Connected by', addr)
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        self.signals.message_received.emit(data.decode())


class MyApp(QMainWindow):
    message_received = pyqtSignal(str)

    def __init__(self):
        super(MyApp, self).__init__()
        self.initUI()
        self.threadpool = QThreadPool()
        self.receive_port = 5000
        self.target_port = 5001
        self.target_ip = "localhost"
        self.receive_ip = "localhost"
        self.application_id = "APP1"  # Unique identifier for this application
        self.count = 0
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.send_message)

    def initUI(self):
        self.setWindowTitle("SMS1")
        # self.setGeometry(100, 100, 300, 200)
        self.application_id_input = QLineEdit()
        self.target_ip_input = QLineEdit(self)
        self.target_port_input = QLineEdit(self)
        self.receive_port_input = QLineEdit(self)
        # self.receive_thread = ReceiveThread(self.receive_port)
        self.message_input = QTextEdit(self)
        self.message_box = QTextEdit(self)
        self.send_button = QPushButton("Send", self)
        self.start_button = QPushButton("Start", self)
        self.stop_button = QPushButton("Stop", self)
        self.message_input.setPlaceholderText("Enter message here")
        self.send_button.clicked.connect(self.send_message)
        self.target_ip_input.setPlaceholderText("Enter target IP address (default: localhost)")
        self.application_id_input.setPlaceholderText("Enter application ID (default: APP1)")
        self.application_id_input.textChanged.connect(self.set_application_id)
        self.target_port_input.setPlaceholderText("Enter target port (default: 5001)")
        self.message_box.setReadOnly(True)
        self.receive_port_input.setPlaceholderText("Enter receive port (default: 5000)")
        self.receive_ip_input = QLineEdit(self)
        self.receive_ip_input.setPlaceholderText("Enter receive IP address (default: localhost)")
        self.start_button.clicked.connect(self.start_receiving)
        self.stop_button.clicked.connect(self.stop_receiving)
        self.receive_ip_input.textEdited.connect(self.set_receive_ip)
        self.receive_port_input.textEdited.connect(self.set_receive_port)
        self.target_port_input.textEdited.connect(self.set_target_port)
        self.target_ip_input.textEdited.connect(self.set_target_ip)

        self.centralWidget = QWidget(self)
        layout = QVBoxLayout(self.centralWidget)
        layout.addWidget(self.application_id_input)
        layout.addWidget(self.message_input)
        layout.addWidget(self.target_ip_input)
        layout.addWidget(self.receive_ip_input)
        layout.addWidget(self.target_port_input)
        layout.addWidget(self.receive_port_input)
        layout2 = QHBoxLayout(self)
        layout2.addWidget(self.send_button)
        layout2.addWidget(self.start_button)
        layout2.addWidget(self.stop_button)
        layout.addLayout(layout2)
        layout.addWidget(self.message_box)
        # self.centralWidget.setLayout(layout)
        self.setCentralWidget(self.centralWidget)
        # self.setLayout(layout)
        # self.show()

    def set_receive_ip(self):
        text = self.receive_ip_input.text()
        if text:
            self.receive_ip = text
        else:
            self.receive_ip = "localhost"
        print(self.receive_ip)

    def set_receive_port(self):
        port = self.receive_port_input.text()
        if port:
            self.receive_port = int(port)
        else:
            self.receive_port = 5000
        print(self.receive_port)

    def set_target_port(self):
        port = self.target_port_input.text()
        if port:
            self.target_port = int(port)
        else:
            self.target_port = 5001
        print(self.target_port)

    def set_target_ip(self):
        port = self.target_ip_input.text()
        if port:
            self.target_ip = port
        else:
            self.target_ip = "localhost"
        print(self.target_ip)

    def set_application_id(self, text):
        self.application_id = text
        print(self.application_id)

    def send_message(self):
        message = self.message_input.toPlainText()
        if message:
            target_port = self.target_port
            target_ip = self.target_ip
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect((target_ip, target_port))
                    print("Connected to {}:{}".format(target_ip, target_port))
                    self.message_box.append("Connected to {}:{}".format(target_ip, target_port))
                    s.sendall((self.application_id + ":" + message).encode())
                    print("Message Sent\n\n")
                    self.message_box.append("Message Sent")
                    self.message_input.clear()
                except ConnectionRefusedError:
                    self.count += 1
                    print("Connection refused.")
                    # add message if connection refused for first time
                    # self.message_box.append("Connection Not available.\nWaiting for connection...")
                    if self.count == 1:
                        self.message_box.append("Connection Not available.\nWaiting for connection...")

                    if self.count == 5:
                        self.count = 0
                        self.message_box.append("No response from target.\nPlease try again later.")
                        return
                    self.timer.start(1500)
                except socket.gaierror:
                    print("Invalid IP address.")
                    self.message_box.append("Invalid IP address.\nPlease enter a valid IP address.")
                except Exception as e:
                    print(e)
                    self.message_box.append("Error occurred.\nPlease try again.")

    def start_receiving(self):
        self.receive_thread = ReceiveThread(self.receive_port)
        self.receive_thread.signals.message_received.connect(self.handle_message)
        self.threadpool.start(self.receive_thread)
        self.message_box.append("Listening on port " + str(self.receive_port))

    def stop_receiving(self):
        self.threadpool.clear()
        self.message_box.append("Stopped listening on port " + str(self.receive_port))

    def handle_message(self, message):
        self.message_box.append(message)

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())
