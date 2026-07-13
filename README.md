# AI Exam Monitoring System (Beginner-Friendly Version)

A simple, real-time webcam exam-proctoring tool. Watches for mobile
phones, extra people, books/laptops, looking away, and a missing face —
then shows a live risk score on screen.

This version is written to be easy to read and learn from: plain
classes, simple dictionaries (no advanced Python features), and a
comment above almost every important line explaining *why*, not just
*what*.

## Project Files

```
exam_monitoring_system/
├── main.py            # Run this file. Connects everything together.
├── camera.py           # Opens your webcam and grabs frames.
├── object_detector.py  # Uses YOLO to spot phones / people / books.
├── face_tracker.py     # Uses MediaPipe to find faces + head direction.
├── eye_tracker.py       # Figures out which way the eyes are looking.
├── risk_analyzer.py    # Turns all the detections into a risk score.
├── config.py            # All the settings you might want to tweak.
└── requirements.txt
```

## How to Run It

1. Install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the program:
   ```bash
   python main.py
   ```

3. A window will open showing your webcam with a status panel in the
   top-left corner. Press **`q`** to quit.

The first time you run it, YOLO will automatically download a small
model file (`yolov8n.pt`, about 6 MB).

## How It Works (Step by Step)

1. **`camera.py`** grabs one image ("frame") from your webcam, 20-30
   times per second.
2. **`object_detector.py`** runs that frame through YOLO, an AI model
   that's already been trained to recognize everyday objects. We only
   keep the ones we care about: people, phones, books, laptops.
3. **`face_tracker.py`** uses MediaPipe to find the face in the frame
   and checks: Is there a face at all? More than one? Which way is the
   head turned?
4. **`eye_tracker.py`** looks at the position of the iris (the colored
   part of the eye) compared to the corners of the eye, to guess if the
   student is looking left, right, or straight ahead.
5. **`risk_analyzer.py`** is the decision-maker. It doesn't trust a
   single frame — a violation has to show up for several frames in a
   row (or for a few seconds) before it's counted. This avoids false
   alarms from things like a single blurry frame or a quick head scratch.
6. **`main.py`** ties it all together in a loop and draws the results
   on screen.

## Understanding the Risk Score

Every confirmed violation adds points (out of 100):

| Violation | Points |
|---|---|
| Mobile phone detected | 45 |
| Multiple people in frame | 40 |
| Face missing | 35 |
| Looking away for too long | 20 |
| Suspicious object (book/laptop) | 15 |

Final status:
- **0–30%** → SAFE
- **30–60%** → WARNING
- **60%+** → CHEATING ALERT

## Adjusting Settings

Everything you might want to change — how many seconds count as
"looking away", how sensitive the head-turn detection is, the risk
points, etc. — lives in `config.py`. You shouldn't need to edit any
other file to tune the system.

## ESP32 Hardware (LEDs + Buzzer + optional LCD)

The system can drive a physical alert panel: a red/yellow/green LED
and a buzzer.  A 16×2 I2C LCD is supported but **optional** — all LCD
code in the `.ino` file is commented out by default.

Everything is in **one single file**: `esp32_firmware/exam_monitor_esp32.ino`

On boot it automatically:
1. Runs a **hardware self-test** (cycles LEDs, beeps buzzer, scans I2C)
2. Enters monitoring mode (**Serial** or **WiFi**, based on a setting)

**Wiring**

| Component | Pin | ESP32 Pin |
|---|---|---|
| Red LED (Cheating) | Anode (+) | GPIO 23 (through 220Ω resistor) |
| | Cathode (-) | GND |
| Yellow LED (Warning) | Anode (+) | GPIO 18 (through 220Ω resistor) |
| | Cathode (-) | GND |
| Green LED (Safe) | Anode (+) | GPIO 19 (through 220Ω resistor) |
| | Cathode (-) | GND |
| Buzzer | + | GPIO 25 |
| | - | GND |
| 16x2 I2C LCD (optional) | VCC | VIN / 5V |
| | GND | GND |
| | SDA | GPIO 21 |
| | SCL | GPIO 22 |

### Serial (USB) mode — the default

1. Open `esp32_firmware/exam_monitor_esp32.ino` in the Arduino IDE.
2. Make sure `USE_WIFI` is set to `false` (this is the default).
3. Upload to the ESP32 and note the COM port.
4. In `config.py`, set:
   ```python
   ESP32_ENABLED = True
   ESP32_WIFI_MODE = False
   ESP32_SERIAL_PORT = "COM5"   # your actual port
   ```
5. Run `python main.py` — LEDs and buzzer will update live.

### WiFi mode (no USB cable needed during exams)

1. Open `esp32_firmware/exam_monitor_esp32.ino`.
2. Set `USE_WIFI` to `true`.
3. Replace `YOUR_WIFI_SSID` and `YOUR_WIFI_PASSWORD` with your
   actual WiFi credentials.
4. Upload to the ESP32.
5. Open Serial Monitor — it prints the ESP32's IP address.
6. In `config.py`, set:
   ```python
   ESP32_ENABLED = True
   ESP32_WIFI_MODE = True
   ESP32_WIFI_IP = "192.168.1.42"   # the IP from step 5
   ESP32_WIFI_PORT = 80
   ```
7. Run `python main.py` — status is sent over WiFi.
8. You can also open `http://192.168.1.42/` in a browser to check
   the current status.

### Don't have an LCD?

No problem — all LCD code is **commented out** by default.  LEDs and
buzzer work without it.  If you get an LCD later, uncomment the
`#include <LiquidCrystal_I2C.h>` line and the `lcd.___()` calls.

### Don't have Arduino IDE on this machine?

Copy the `esp32_firmware/` folder to a USB drive and upload from any
computer that has the Arduino IDE with ESP32 board support.

## Notes

- This tool is meant to assist a human proctor, not replace one — always
  have a person review flagged alerts.
- Works best in a well-lit room with the student facing the camera.
- If YOLO fails to load (e.g. no internet on first run), object
  detection (phone/person/book) won't work, but face and eye monitoring
  will still run.
- If the ESP32 isn't plugged in (or the IP/COM port is wrong), the
  Python program prints a one-time warning and keeps running normally —
  it never crashes because of a hardware problem.

