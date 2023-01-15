import socket
import sys

from PyQt5.QtWidgets import QApplication, QLineEdit, QPushButton, QVBoxLayout, QWidget, QTextEdit, QLabel, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QTextCursor


class ReceiveThread(QThread):
    message_received = pyqtSignal(str)

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.bind((self.host, self.port))
        self.listen_socket.listen()

    def run(self):
        # self.listen_socket.bind((self.host, self.port))
        # self.listen_socket.listen()
        conn, addr = self.listen_socket.accept()
        with conn:
            message_received = False
            while not message_received:
                data = conn.recv(1024).decode()
                if data:
                    self.message_received.emit(data)
                    message_received = True
                else:
                    print("No message received.")


class SendReceiveMessage(QWidget):
    def __init__(self):
        super().__init__()
        self.listen_thread = None
        self.receive_port = 5001
        self.target_port = 5000
        self.target_ip = "localhost"
        self.receive_ip = "localhost"
        self.last_msg = []
        self.initUI()
        self.application_id = "APP1"  # Unique identifier for this application

    def initUI(self):
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
        self.target_port_input.setPlaceholderText("Enter target port (default: 5000)")
        self.message_box.setReadOnly(True)
        self.receive_port_input.setPlaceholderText("Enter receive port (default: 5001)")
        self.receive_ip_input = QLineEdit(self)
        self.receive_ip_input.setPlaceholderText("Enter receive IP address (default: localhost)")
        self.receive_ip_input.editingFinished.connect(self.set_receive_ip)
        self.receive_port_input.editingFinished.connect(self.set_receive_port)
        self.target_port_input.editingFinished.connect(self.set_target_port)
        self.target_ip_input.editingFinished.connect(self.set_target_ip)
        self.start_button.clicked.connect(self.startListening)
        self.stop_button.clicked.connect(self.stopListening)
        # self.target_ip_input.setText("localhost")

        layout = QVBoxLayout(self)
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

        self.setLayout(layout)
        self.setWindowTitle("SMS2")
        self.show()

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.send_message)
        self.count = 0

    def startListening(self):
        if self.listen_thread is None:
            self.listen_thread = ReceiveThread(self.receive_ip, self.receive_port)
            self.listen_thread.message_received.connect(self.display_message)
            self.listen_thread.start()
            self.message_box.append("Listening on port " + str(self.receive_port))

    def stopListening(self):
        if self.listen_thread and self.listen_thread.isRunning():
            self.listen_thread.listen_socket.close()
            self.listen_thread.listen_socket = None
            self.listen_thread.terminate()
            self.listen_thread = None
            self.message_box.append("Stopped listening on port " + str(self.receive_port))

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
            # text = self.target_ip_input.text()
            # if text:
            #     target_ip = text
            # else:
            #     target_ip = "localhost"
            #
            # text = self.target_port_input.text()
            # if text:
            #     target_port = int(text)
            # else:
            #     target_port = self.target_port
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
                    self.timer.start(2500)
                except socket.gaierror:
                    print("Invalid IP address.")
                    self.message_box.append("Invalid IP address.\nPlease enter a valid IP address.")
                except Exception as e:
                    print(e)
                    self.message_box.append("Error occurred.\nPlease try again.")

    def display_message(self, message):
        sender_id, message = message.split(":", 1)
        # local_ip = socket.gethostbyname(socket.gethostname())
        # if sender_ip == "127.0.0.1" and sender_id != self.application_id:
        cursor = QTextCursor(self.message_box.document())
        cursor.movePosition(QTextCursor.End)
        self.message_box.setTextCursor(cursor)
        self.message_box.append("Received message: " + message + "\n")

    def closeEvent(self, event):
        self.close()


app = QApplication([])
send_receive_message = SendReceiveMessage()
sys.exit(app.exec_())
