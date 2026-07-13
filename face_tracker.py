# face_tracker.py — MediaPipe face detection and head direction

import cv2
import mediapipe as mp
import config

NOSE_TIP = 1


class FaceTracker:
    def __init__(self):
        mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=config.MAX_FACES_TO_DETECT,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def process(self, frame):
        frame_height, frame_width = frame.shape[:2]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        if not results.multi_face_landmarks:
            return {
                "face_present": False,
                "face_count": 0,
                "multiple_faces": False,
                "too_far": False,
                "direction": "UNKNOWN",
                "landmarks": None,
                "box": None,
            }

        face_count = len(results.multi_face_landmarks)

        biggest_face_landmarks, box = self._find_biggest_face(
            results.multi_face_landmarks, frame_width, frame_height
        )

        too_far = self._is_too_far(box, frame_width, frame_height)
        direction = self._get_head_direction(biggest_face_landmarks, box)

        return {
            "face_present": True,
            "face_count": face_count,
            "multiple_faces": face_count > 1,
            "too_far": too_far,
            "direction": direction,
            "landmarks": biggest_face_landmarks,
            "box": box,
        }

    def _find_biggest_face(self, all_faces, frame_width, frame_height):
        biggest_area = -1
        biggest_landmarks_px = None
        biggest_box = (0, 0, 0, 0)

        for face in all_faces:
            points = [(lm.x * frame_width, lm.y * frame_height) for lm in face.landmark]

            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            x1, y1, x2, y2 = min(xs), min(ys), max(xs), max(ys)
            area = (x2 - x1) * (y2 - y1)

            if area > biggest_area:
                biggest_area = area
                biggest_landmarks_px = points
                biggest_box = (int(x1), int(y1), int(x2), int(y2))

        return biggest_landmarks_px, biggest_box

    def _is_too_far(self, box, frame_width, frame_height):
        x1, y1, x2, y2 = box
        face_area = (x2 - x1) * (y2 - y1)
        frame_area = frame_width * frame_height
        if frame_area == 0:
            return False
        return (face_area / frame_area) < config.MIN_FACE_SIZE_RATIO

    def _get_head_direction(self, landmarks_px, box):
        x1, y1, x2, y2 = box
        box_width = x2 - x1
        box_height = y2 - y1
        if box_width == 0 or box_height == 0:
            return "CENTER"

        center_x = x1 + box_width / 2
        center_y = y1 + box_height / 2

        nose_x, nose_y = landmarks_px[NOSE_TIP]

        horizontal_offset = (nose_x - center_x) / box_width
        vertical_offset = (nose_y - center_y) / box_height

        if horizontal_offset > config.HEAD_TURN_SENSITIVITY:
            return "RIGHT"
        if horizontal_offset < -config.HEAD_TURN_SENSITIVITY:
            return "LEFT"
        if vertical_offset > config.HEAD_DOWN_SENSITIVITY:
            return "DOWN"
        if vertical_offset < -config.HEAD_DOWN_SENSITIVITY:
            return "UP"
        return "CENTER"

    def draw_face_box(self, frame, face_data):
        if not face_data["face_present"] or face_data["box"] is None:
            return frame

        x1, y1, x2, y2 = face_data["box"]
        color = (0, 255, 255) if face_data["direction"] == "CENTER" else (0, 0, 255)

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)
        cv2.putText(
            frame, f"Head: {face_data['direction']}", (x1, max(15, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1
        )
        return frame

    def close(self):
        self.face_mesh.close()
