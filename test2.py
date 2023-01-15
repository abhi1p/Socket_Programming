import socket
import sys

from PyQt5.QtWidgets import QApplication, QLineEdit, QPushButton, QVBoxLayout, QWidget, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor


class ReceiveThread(QThread):
    message_received = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.target_ip = "localhost"
        self.target_port = 5001
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.target_ip, self.target_port))
        self.socket.listen()

    def run(self):
        while True:
            conn, addr = self.socket.accept()
            with conn:
                data = conn.recv(1024).decode()
                if data:
                    self.message_received.emit(data, addr[0])
                else:
                    print("No message received.")


class SendReceiveMessage(QWidget):
    def __init__(self):
        super().__init__()
        self.receive_thread = ReceiveThread()
        self.message_input = QLineEdit(self)
        self.message_box = QTextEdit(self)
        self.send_button = QPushButton("Send", self)
        self.initUI()
        self.application_id = "APP2"  # Unique identifier for this application

    def initUI(self):
        self.send_button.clicked.connect(self.send_message)
        self.message_box.setReadOnly(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.message_input)
        layout.addWidget(self.send_button)
        layout.addWidget(self.message_box)

        self.setLayout(layout)
        self.setWindowTitle("SMS2")
        self.show()

        self.receive_thread.message_received.connect(self.display_message)
        self.receive_thread.start()

    def send_message(self):
        message = self.message_input.text()
        target_ip = "localhost"
        target_port = 5000

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((target_ip, target_port))
            s.sendall((self.application_id + ":" + message).encode())
            self.message_input.clear()
            print("Sent")

    def display_message(self, message, sender_ip):
        sender_id, message = message.split(":", 1)
        # local_ip = socket.gethostbyname(socket.gethostname())
        if sender_ip == "127.0.0.1" and sender_id != self.application_id:
            cursor = QTextCursor(self.message_box.document())
            cursor.movePosition(QTextCursor.End)
            self.message_box.setTextCursor(cursor)
            self.message_box.append("Received message: " + message + "\n")

    def closeEvent(self, event):
        self.receive_thread.quit()
        self.close()


app = QApplication([])
send_receive_message = SendReceiveMessage()
sys.exit(app.exec_())
