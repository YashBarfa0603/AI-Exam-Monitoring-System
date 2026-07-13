# esp32_connector.py — Sends status to ESP32 (Serial or WiFi)

import time
import config

try:
    import serial
    PYSERIAL_AVAILABLE = True
except ImportError:
    PYSERIAL_AVAILABLE = False

from urllib.request import urlopen, Request
from urllib.error import URLError


class ESP32Connector:
    def __init__(self):
        self.enabled = config.ESP32_ENABLED
        self.wifi_mode = getattr(config, "ESP32_WIFI_MODE", False)
        self.connection = None
        self.last_sent_time = 0.0
        self.last_status_sent = None
        self.consecutive_failures = 0
        self.max_failures = 5

        if not self.enabled:
            return

        if self.wifi_mode:
            self._init_wifi()
        else:
            self._init_serial()

    def _init_serial(self):
        if not PYSERIAL_AVAILABLE:
            print("WARNING: 'pyserial' not installed. Run: pip install pyserial")
            self.enabled = False
            return

        try:
            self.connection = serial.Serial(
                config.ESP32_SERIAL_PORT, config.ESP32_BAUD_RATE, timeout=1
            )
            time.sleep(2)
            print(f"Connected to ESP32 on {config.ESP32_SERIAL_PORT}")
        except Exception as error:
            print(f"WARNING: Could not connect to ESP32 ({error}). Hardware alerts disabled.")
            self.enabled = False

    def _init_wifi(self):
        ip = getattr(config, "ESP32_WIFI_IP", "192.168.1.100")
        port = getattr(config, "ESP32_WIFI_PORT", 80)
        self.wifi_url = f"http://{ip}:{port}/status"
        print(f"ESP32 WiFi mode — POST to {self.wifi_url}")

    def send_status(self, status, score):
        if not self.enabled:
            return

        now = time.time()
        if status == self.last_status_sent and (now - self.last_sent_time) < 1.0:
            return

        message = f"{status},{score:.0f}\n"

        if self.wifi_mode:
            self._send_wifi(message)
        else:
            self._send_serial(message)

        self.last_sent_time = now
        self.last_status_sent = status

    def _send_serial(self, message):
        try:
            self.connection.write(message.encode("utf-8"))
            self.consecutive_failures = 0
        except Exception as error:
            self.consecutive_failures += 1
            print(f"WARNING: Lost ESP32 connection ({error}). Failures: {self.consecutive_failures}/{self.max_failures}")
            if self.consecutive_failures >= self.max_failures:
                print("Disabling hardware alerts due to repeated failures.")
                self.enabled = False

    def _send_wifi(self, message):
        try:
            request = Request(self.wifi_url, data=message.encode("utf-8"), method="POST")
            request.add_header("Content-Type", "text/plain")
            urlopen(request, timeout=1.0)
            self.consecutive_failures = 0
        except URLError as error:
            self.consecutive_failures += 1
            print(f"WARNING: ESP32 unreachable ({error.reason}). Failures: {self.consecutive_failures}/{self.max_failures}")
            if self.consecutive_failures >= self.max_failures:
                print("Disabling WiFi alerts due to repeated failures.")
                self.enabled = False
        except Exception as error:
            self.consecutive_failures += 1
            print(f"WARNING: ESP32 WiFi error ({error}). Failures: {self.consecutive_failures}/{self.max_failures}")
            if self.consecutive_failures >= self.max_failures:
                print("Disabling WiFi alerts due to repeated failures.")
                self.enabled = False

    def close(self):
        if self.connection is not None:
            self.connection.close()
