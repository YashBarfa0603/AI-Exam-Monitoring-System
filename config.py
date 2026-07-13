CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
YOLO_MODEL_PATH = "yolov8n.pt"
YOLO_CONFIDENCE_THRESHOLD = 0.45

WATCHED_CLASSES = {
    "person": "person",
    "cell phone": "mobile phone",
    "book": "suspicious object",
    "laptop": "suspicious object",
}

MAX_ALLOWED_PERSONS = 1

BOX_COLORS = {
    "mobile phone": (0, 0, 255),
    "suspicious object": (0, 140, 255),
    "person": (255, 180, 0),
}


MAX_FACES_TO_DETECT = 3
HEAD_TURN_SENSITIVITY = 0.15
HEAD_DOWN_SENSITIVITY = 0.20
MIN_FACE_SIZE_RATIO = 0.03

EYE_GAZE_SENSITIVITY = 0.18

LOOKING_AWAY_LIMIT_SECONDS = 3.0
FACE_MISSING_LIMIT_SECONDS = 2.0
FRAMES_NEEDED_TO_CONFIRM = 8

RISK_POINTS = {
    "mobile_phone": 45,
    "multiple_people": 40,
    "face_missing": 35,
    "looking_away": 20,
    "suspicious_object": 15,
}

SAFE_MAX_SCORE = 30
WARNING_MAX_SCORE = 60

# DASHBOARD
STATUS_COLORS = {
    "SAFE": (0, 200, 0),
    "WARNING": (0, 200, 255),
    "ALERT": (0, 0, 255),
}

#ESP32 
ESP32_ENABLED = True
ESP32_SERIAL_PORT = "COM4" #write your ESP32 serial port here
ESP32_BAUD_RATE = 115200

#ESP32 WIFI
ESP32_WIFI_MODE = True
ESP32_WIFI_IP = "192.168.4.1" #write your ESP32 IP address here
ESP32_WIFI_PORT = 80
