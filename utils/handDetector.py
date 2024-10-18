import mediapipe as mp
import numpy as np


class HandDetector:
    def __init__(self, static_image_mode=False, max_num_hand=2,
                min_detection_confidence=0.5, min_tracking_confidence=0.3):
        self.hands = mp.solutions.hands.Hands(static_image_mode,
                                              max_num_hand,
                                              1,
                                              min_detection_confidence,
                                              min_tracking_confidence)
        self.hand_landmarks = []
        self.label = []

    def detect_hands(self, img):
        results = self.hands.process(img)
        if results.multi_hand_landmarks:
            h, w, _ = img.shape
            num_hands = len(results.multi_hand_landmarks)

            for i in range(num_hands):
                lm_list = list()
                handedness = results.multi_handedness[i]
                hand_landmarks = results.multi_hand_landmarks[i]
                wrist_z = hand_landmarks.landmark[0].z

                for lm in hand_landmarks.landmark:
                    cx = int(lm.x * w)
                    cy = int(lm.y * h)
                    cz = int((lm.z - wrist_z) * w)
                    lm_list.append([cx, cy, cz])

                label = handedness.classification[0].label.lower()
                lm_array = np.array(lm_list)
                self.hand_landmarks.append(lm_array)
                self.label.append(label)

    def init_landmarks(self):
        self.hand_landmarks = []
        self.label = []
