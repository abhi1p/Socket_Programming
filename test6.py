import asyncio
import socket
import sys

from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QLineEdit, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QApplication
from functools import partial
from queue import Queue
from threading import Thread


class ReceiveThread(QThread):
    message_received = pyqtSignal(str)

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.bind((self.host, self.port))
        self.listen_socket.listen()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.retry_time = 5  # time in seconds to retry the connection
        self.retry_count = 0  # number of retries
        self.max_retries = 10  # maximum number of retries before stopping

    def stop(self):
        self.should_run = False

    def run(self):
        self.should_run = True
        asyncio.run(self.handle_connections())

    async def handle_connections(self):
        while self.should_run:
            try:
                self.listen_socket.bind((self.host, self.port))
                self.listen_socket.listen()
                conn, addr = self.listen_socket.accept()
                with conn:
                    data = conn.recv(4096).decode()
                    if data:
                        self.message_received.emit(data)
                        self.should_run = False
                    else:
                        print("No message received.")
            except ConnectionRefusedError:
                self.retry_count += 1
                if self.retry_count >= self.max_retries:
                    self.should_run = False
                    print("Connection refused. Max retries reached.")
                else:
                    self.retry_timer = QTimer()
                    self.retry_timer.setInterval(self.retry_time * 1000)
                    self.retry_timer.setSingleShot(True)
                    self.retry_timer.timeout.connect(self.handle_connections)
                    self.retry_timer.start()
                    print(f"Connection refused. Retrying in {self.retry_time} seconds...")


class ConnectionPool:
    def __init__(self, max_connections, host, port):
        self.max_connections = max_connections
        self.host = host
        self.port = port
        self.pool = Queue(max_connections)
        self.fill_pool()

    def fill_pool(self):
        for _ in range(self.max_connections):
            self.pool.put(self.create_connection())

    def create_connection(self):
        return socket.create_connection((self.host, self.port))

    def get_connection(self):
        return self.pool.get()

    def return_connection(self, conn):
        self.pool.put(conn)


class SendReceiveMessage(QWidget):
    def __init__(self):
        super().__init__()
        self.listen_thread = None
        self.receive_port = 5000
        self.target_port = 5001
        self.target_ip = "localhost"
        self.receive_ip = "localhost"
        self.application_id = "APP1"  # Unique identifier for this application

        self.connection_pool = ConnectionPool(5, self.target_ip, self.target_port)
        # ...

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
        self.target_port_input.setPlaceholderText("Enter target port (default: 5001)")
        self.message_box.setReadOnly(True)
        self.receive_port_input.setPlaceholderText("Enter receive port (default: 5000)")
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
        self.setWindowTitle("SMS1")
        self.show()

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.send_message)
        self.count = 0

    def send_message(self):
        conn = self.connection_pool.get_connection()
        # send message using conn
        self.connection_pool.return_connection(conn)

    def startListening(self):
        self.listen_thread = ReceiveThread(self.receive_ip, self.receive_port)
        self.listen_thread.message_received.connect(self.update_message_box)
        self.listen_thread.start()

    def update_message_box(self, message):
        self.message_box.append(f"{message}")

    def stopListening(self):
        self.listen_thread.stop()

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


app = QApplication([])
send_receive_message = SendReceiveMessage()
sys.exit(app.exec_())
