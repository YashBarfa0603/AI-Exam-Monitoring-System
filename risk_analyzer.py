import time
import config


class RiskAnalyzer:
    def __init__(self):
        self.phone_streak = 0
        self.multiple_people_streak = 0
        self.suspicious_object_streak = 0
        self.face_missing_since = None
        self.current_score = 0.0

    def update(self, phone_detected, person_count, suspicious_object_detected,
               face_present, looking_away):

        now = time.time()

    
        self.phone_streak = self.phone_streak + 1 if phone_detected else 0

        too_many_people = person_count > config.MAX_ALLOWED_PERSONS
        self.multiple_people_streak = self.multiple_people_streak + 1 if too_many_people else 0

        self.suspicious_object_streak = (
            self.suspicious_object_streak + 1 if suspicious_object_detected else 0
        )

        #Confirm violations
        needed = config.FRAMES_NEEDED_TO_CONFIRM
        confirmed_phone = self.phone_streak >= needed
        confirmed_multiple_people = self.multiple_people_streak >= needed
        confirmed_suspicious_object = self.suspicious_object_streak >= needed

        if face_present:
            self.face_missing_since = None
            confirmed_face_missing = False
        else:
            if self.face_missing_since is None:
                self.face_missing_since = now
            seconds_missing = now - self.face_missing_since
            confirmed_face_missing = seconds_missing >= config.FACE_MISSING_LIMIT_SECONDS

        confirmed_looking_away = looking_away

        # risk score 
        target_score = 0
        messages = []

        if confirmed_phone:
            target_score += config.RISK_POINTS["mobile_phone"]
            messages.append("Mobile phone detected")

        if confirmed_multiple_people:
            target_score += config.RISK_POINTS["multiple_people"]
            messages.append(f"Multiple people in frame ({person_count})")

        if confirmed_face_missing:
            target_score += config.RISK_POINTS["face_missing"]
            messages.append("Face not visible")

        if confirmed_looking_away:
            target_score += config.RISK_POINTS["looking_away"]
            messages.append("Looking away from screen")

        if confirmed_suspicious_object:
            target_score += config.RISK_POINTS["suspicious_object"]
            messages.append("Suspicious object detected (book/laptop)")

        target_score = min(target_score, 100)

        # Smooth the score
        self.current_score = self.current_score + 0.3 * (target_score - self.current_score)
        self.current_score = max(0.0, min(100.0, self.current_score))

        #  Determine
        if self.current_score <= config.SAFE_MAX_SCORE:
            status = "SAFE"
        elif self.current_score <= config.WARNING_MAX_SCORE:
            status = "WARNING"
        else:
            status = "ALERT"

        return {
            "score": round(self.current_score, 1),
            "status": status,
            "messages": messages,
            "person_count": person_count,
        }
