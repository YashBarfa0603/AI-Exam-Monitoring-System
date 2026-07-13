# object_detector.py — YOLO object detection

from ultralytics import YOLO
import cv2
import config


class ObjectDetector:
    def __init__(self):
        print("Loading YOLO model...")
        self.model = YOLO(config.YOLO_MODEL_PATH)
        print("YOLO model loaded successfully.")

    def detect_objects(self, frame):
        results = self.model(
            frame, verbose=False, conf=config.YOLO_CONFIDENCE_THRESHOLD
        )[0]

        detections = []

        for box in results.boxes:
            class_id = int(box.cls[0])
            yolo_class_name = results.names[class_id]

            if yolo_class_name not in config.WATCHED_CLASSES:
                continue

            our_label = config.WATCHED_CLASSES[yolo_class_name]
            confidence = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            detections.append({
                "label": our_label,
                "confidence": confidence,
                "box": (int(x1), int(y1), int(x2), int(y2)),
            })

        return detections

    def draw_boxes(self, frame, detections):
        for det in detections:
            x1, y1, x2, y2 = det["box"]
            color = config.BOX_COLORS.get(det["label"], (0, 255, 0))

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            label_text = f"{det['label']} {det['confidence'] * 100:.0f}%"
            cv2.putText(
                frame, label_text, (x1, max(20, y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2
            )

        return frame

    def count_objects(self, detections):
        person_count = 0
        phone_detected = False
        suspicious_detected = False

        for det in detections:
            if det["label"] == "person":
                person_count += 1
            elif det["label"] == "mobile phone":
                phone_detected = True
            elif det["label"] == "suspicious object":
                suspicious_detected = True

        return person_count, phone_detected, suspicious_detected
