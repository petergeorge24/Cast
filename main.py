import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QListWidget, QMessageBox
from PyQt5.QtGui import QPalette, QColor
from pychromecast import get_chromecasts
import threading

class CastController:
    def __init__(self, cast_device):
        self.cast_device = cast_device

    def start(self):
        # Modify this method to start screen sharing with the selected device
        print(f"Sharing screen with {self.cast_device}")

def discover_cast_devices():
    return get_chromecasts()

class DeviceSelectionApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Device Selection')
        self.setGeometry(100, 100, 400, 400)

        palette = QPalette()
        gradient = QPalette()
        gradient.setColor(QPalette.Window, QColor(135, 206, 250))
        gradient.setColor(QPalette.WindowText, QColor(0, 0, 0))
        self.setPalette(gradient)

        layout = QVBoxLayout()

        device_label = QLabel('Select devices to share screen:')
        layout.addWidget(device_label)

        self.cast_devices = discover_cast_devices()
        device_names = [getattr(device, 'name', 'Unknown') for device in self.cast_devices] if self.cast_devices else []

        self.device_listbox = QListWidget()
        self.device_listbox.setSelectionMode(QListWidget.MultiSelection)
        self.device_listbox.addItems(device_names)
        layout.addWidget(self.device_listbox)

        start_button = QPushButton('Start Casting', self)
        start_button.clicked.connect(self.start_casting_thread)
        layout.addWidget(start_button)

        exit_button = QPushButton('Exit', self)
        exit_button.clicked.connect(self.on_exit)
        layout.addWidget(exit_button)

        self.selected_device_indices = []

        self.setLayout(layout)

    def start_casting_thread(self):
        selected_devices = [self.cast_devices[i] for i in range(self.device_listbox.count()) if self.device_listbox.item(i).isSelected()]
        self.start_casting(selected_devices)

    def start_casting(self, selected_devices):
        for device in selected_devices:
            cast_controller = CastController(device)
            cast_controller.start()

    def on_exit(self):
        reply = QMessageBox.question(self, 'Exit', 'Do you really want to exit?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            sys.exit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DeviceSelectionApp()
    ex.show()
    sys.exit(app.exec_())
