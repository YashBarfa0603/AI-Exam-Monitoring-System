# eye_tracker.py — Iris-based gaze direction
import time
import numpy as np
import config

LEFT_EYE_LEFT_CORNER = 33
LEFT_EYE_RIGHT_CORNER = 133
RIGHT_EYE_LEFT_CORNER = 362
RIGHT_EYE_RIGHT_CORNER = 263

LEFT_IRIS_POINTS = [474, 475, 476, 477]
RIGHT_IRIS_POINTS = [469, 470, 471, 472]


class EyeTracker:
    def __init__(self):
        self.looking_away_start_time = None

    def analyze(self, landmarks_px):
        if landmarks_px is None or len(landmarks_px) < 478:
            self.looking_away_start_time = None
            return {"gaze_direction": "UNKNOWN", "looking_away": False}

        left_ratio = self._get_horizontal_ratio(
            landmarks_px, LEFT_EYE_LEFT_CORNER, LEFT_EYE_RIGHT_CORNER, LEFT_IRIS_POINTS
        )
        right_ratio = self._get_horizontal_ratio(
            landmarks_px, RIGHT_EYE_LEFT_CORNER, RIGHT_EYE_RIGHT_CORNER, RIGHT_IRIS_POINTS
        )

        if left_ratio is None or right_ratio is None:
            self.looking_away_start_time = None
            return {"gaze_direction": "UNKNOWN", "looking_away": False}

        average_ratio = (left_ratio + right_ratio) / 2
        direction = self._classify_direction(average_ratio)
        looking_away = self._update_timer(direction)

        return {"gaze_direction": direction, "looking_away": looking_away}

    def _get_horizontal_ratio(self, landmarks_px, left_corner_idx, right_corner_idx, iris_idx_list):
        left_corner = landmarks_px[left_corner_idx]
        right_corner = landmarks_px[right_corner_idx]

        iris_points = [landmarks_px[i] for i in iris_idx_list]
        iris_center_x = sum(p[0] for p in iris_points) / len(iris_points)

        eye_width = right_corner[0] - left_corner[0]
        if abs(eye_width) < 1e-6:
            return None

        ratio = (iris_center_x - left_corner[0]) / eye_width
        return float(np.clip(ratio, 0.0, 1.0))

    def _classify_direction(self, average_ratio):
        offset_from_center = average_ratio - 0.5
        if offset_from_center < -config.EYE_GAZE_SENSITIVITY:
            return "LEFT"
        if offset_from_center > config.EYE_GAZE_SENSITIVITY:
            return "RIGHT"
        return "CENTER"

    def _update_timer(self, direction):
        now = time.time()

        if direction in ("LEFT", "RIGHT"):
            if self.looking_away_start_time is None:
                self.looking_away_start_time = now
            time_spent_looking_away = now - self.looking_away_start_time
            return time_spent_looking_away >= config.LOOKING_AWAY_LIMIT_SECONDS
        else:
            self.looking_away_start_time = None
            return False
