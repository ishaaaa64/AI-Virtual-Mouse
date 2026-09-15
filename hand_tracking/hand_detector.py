import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class HandDetector:

    def __init__(self, model_path):

        # Create the base options
        base_options = python.BaseOptions(
            model_asset_path=model_path
        )

        # Create hand landmarker options
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Create the hand landmarker
        self.detector = vision.HandLandmarker.create_from_options(
            options
        )

    def detect(self, frame, timestamp_ms):

        # MediaPipe expects RGB image
        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        # Convert OpenCV frame to MediaPipe image
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # Detect hand landmarks
        result = self.detector.detect_for_video(
            mp_image,
            timestamp_ms
        )

        return result

    def close(self):

        self.detector.close()