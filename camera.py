import cv2
import config


class Camera:

    def __init__(self):
        self.cap = cv2.VideoCapture(config.CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

        if not self.cap.isOpened():
            raise Exception(
                "Could not open the webcam. Make sure it is connected and "
                "not being used by another app."
            )

    def get_frame(self):
        success, frame = self.cap.read()
        if not success:
            return None
        frame = cv2.flip(frame, 1)
        return frame

    def release(self):
        self.cap.release()
