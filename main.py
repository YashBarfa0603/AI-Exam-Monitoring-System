import cv2
import config
from camera import Camera
from object_detector import ObjectDetector
from face_tracker import FaceTracker
from eye_tracker import EyeTracker
from risk_analyzer import RiskAnalyzer
from esp32_connector import ESP32Connector


def draw_dashboard(frame, risk_result, face_data, gaze_direction):
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (350, 190), (30, 30, 30), -1)
    cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

    status = risk_result["status"]
    status_color = config.STATUS_COLORS.get(status, (255, 255, 255))
    status_text = "CHEATING ALERT" if status == "ALERT" else status

    lines = [
        (f"Status: {status_text}", status_color, 0.65),
        (f"Risk Score: {risk_result['score']}%", status_color, 0.55),
        (f"Persons Detected: {risk_result['person_count']}", (255, 255, 255), 0.5),
        (f"Face Present: {'Yes' if face_data['face_present'] else 'No'}", (255, 255, 255), 0.5),
        (f"Head Direction: {face_data['direction']}", (255, 255, 255), 0.5),
        (f"Eye Gaze: {gaze_direction}", (255, 255, 255), 0.5),
    ]

    y = 35
    for text, color, size in lines:
        cv2.putText(frame, text, (20, y), cv2.FONT_HERSHEY_SIMPLEX, size, color, 2)
        y += 24

    bar_x, bar_y, bar_w, bar_h = 20, y + 5, 310, 14
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (80, 80, 80), -1)
    filled_width = int(bar_w * (risk_result["score"] / 100))
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + filled_width, bar_y + bar_h), status_color, -1)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (200, 200, 200), 1)

    warning_y = 210
    for message in risk_result["messages"][:5]:
        cv2.putText(
            frame, f"! {message}", (20, warning_y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2
        )
        warning_y += 22

    return frame


def main():
    print("Starting AI Exam Monitoring System...")
    print("Press 'q' in the camera window to quit.\n")

    try:
        camera = Camera()
    except Exception as error:
        print(f"ERROR: {error}")
        return

    object_detector = ObjectDetector()
    face_tracker = FaceTracker()
    eye_tracker = EyeTracker()
    risk_analyzer = RiskAnalyzer()
    esp32 = ESP32Connector()

    while True:
        frame = camera.get_frame()
        if frame is None:
            print("Warning: couldn't read a frame from the camera. Retrying...")
            continue

        detections = object_detector.detect_objects(frame)
        person_count, phone_detected, suspicious_object_detected = object_detector.count_objects(detections)
        object_detector.draw_boxes(frame, detections)

        face_data = face_tracker.process(frame)
        face_tracker.draw_face_box(frame, face_data)

        gaze_result = eye_tracker.analyze(face_data["landmarks"])

        looking_away = gaze_result["looking_away"] or (
            face_data["face_present"]
            and face_data["direction"] in ("LEFT", "RIGHT")
            and not face_data["too_far"]
        )

        risk_result = risk_analyzer.update(
            phone_detected=phone_detected,
            person_count=person_count,
            suspicious_object_detected=suspicious_object_detected,
            face_present=face_data["face_present"],
            looking_away=looking_away,
        )

        esp32.send_status(risk_result["status"], risk_result["score"])

        draw_dashboard(frame, risk_result, face_data, gaze_result["gaze_direction"])
        cv2.imshow("AI Exam Monitoring System", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("Quitting...")
            break

    camera.release()
    face_tracker.close()
    esp32.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
