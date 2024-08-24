import sys
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QLabel, QWidget
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from vidstream import StreamingServer, ScreenShareClient
import socket

class ServerThread(QThread):
    server_started = pyqtSignal(str)

    def run(self):
        try:
            host = StreamingServer('0.0.0.0', 8080)
            host.start_server()
            local_ip = self.get_local_ip()
            self.server_started.emit(local_ip)

        except Exception as e:
            print(f"Error in ServerThread: {e}")

    def get_local_ip(self):
        try:
            # Get the local IP address of the machine
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except socket.error:
            return 'localhost'

class ScreenSharingApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.server_thread = None

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Screen Sharing App')

        start_server_button = QPushButton('Start Server', self)
        start_server_button.clicked.connect(self.start_server)

        start_stream_button = QPushButton('Start Screen Share', self)
        start_stream_button.clicked.connect(self.start_stream)

        stop_button = QPushButton('Stop Server', self)
        stop_button.clicked.connect(self.stop_server)

        self.ip_label = QLabel(self)
        self.ip_label.setAlignment(Qt.AlignCenter)
        self.ip_label.setText("")

        vbox = QVBoxLayout()
        vbox.addWidget(start_server_button)
        vbox.addWidget(start_stream_button)
        vbox.addWidget(stop_button)
        vbox.addWidget(self.ip_label)

        central_widget = QWidget()
        central_widget.setLayout(vbox)
        self.setCentralWidget(central_widget)

    def start_server(self):
        try:
            # Check if the server thread is already running
            if self.server_thread is not None and self.server_thread.isRunning():
                print("Server is already running.")
                return

            # Start the server thread
            self.server_thread = ServerThread()
            self.server_thread.server_started.connect(self.on_server_started)
            self.server_thread.start()

        except Exception as e:
            print(f"Error starting server: {e}")

    def on_server_started(self, local_ip):
        self.ip_label.setText(f"Server running. Connect to http://{local_ip}:8080 to view the shared screen.")

    def start_stream(self):
        try:
            # Use the actual IP address of the machine running the server
            host_ip = self.server_thread.get_local_ip()

            # Start screen sharing in a separate thread
            threading.Thread(target=self.start_screen_share, args=(host_ip,)).start()

        except Exception as e:
            print(f"Error starting screen share: {e}")

    def start_screen_share(self, host_ip):
        try:
            sender = ScreenShareClient(host_ip, 8080)
            sender.start_stream()

        except Exception as e:
            print(f"Error in screen share: {e}")

    def stop_server(self):
        try:
            # Stop the server by setting the flag
            if self.server_thread is not None:
                self.server_thread.quit()
                self.server_thread.wait()

        except Exception as e:
            print(f"Error stopping server: {e}")

def main():
    app = QApplication(sys.argv)
    screen_sharing_app = ScreenSharingApp()
    screen_sharing_app.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
