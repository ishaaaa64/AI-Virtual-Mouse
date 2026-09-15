import cv2
import os
import sys
import time
import math
import joblib
import pyautogui

from collections import deque


# ==========================================
# PROJECT ROOT
# ==========================================

PROJECT_ROOT = os.path.dirname(
    os.path.abspath(__file__)
)

sys.path.insert(0, PROJECT_ROOT)


# ==========================================
# IMPORT
# ==========================================

from hand_tracking.hand_detector import HandDetector


# ==========================================
# PATHS
# ==========================================

HAND_MODEL_PATH = os.path.join(
    PROJECT_ROOT,
    "hand_tracking",
    "hand_landmarker.task"
)

GESTURE_MODEL_PATH = os.path.join(
    PROJECT_ROOT,
    "dataset",
    "final_gesture_model.pkl"
)


# ==========================================
# SETTINGS
# ==========================================

CONFIDENCE_THRESHOLD = 0.75

SMOOTHING = 0.15

CLICK_COOLDOWN = 0.70

SCROLL_COOLDOWN = 0.25

DRAG_HOLD_TIME = 0.70

HISTORY_SIZE = 5

STABLE_COUNT = 3

SCROLL_AMOUNT = 3


# ==========================================
# CHECK FILES
# ==========================================

if not os.path.exists(HAND_MODEL_PATH):

    print("ERROR: Hand model not found.")
    print(HAND_MODEL_PATH)
    exit()


if not os.path.exists(GESTURE_MODEL_PATH):

    print("ERROR: Gesture model not found.")
    print(GESTURE_MODEL_PATH)
    exit()


# ==========================================
# LOAD MODEL
# ==========================================

model = joblib.load(
    GESTURE_MODEL_PATH
)


# ==========================================
# HAND DETECTOR
# ==========================================

detector = HandDetector(
    HAND_MODEL_PATH
)


# ==========================================
# CAMERA
# ==========================================

cap = cv2.VideoCapture(0)


if not cap.isOpened():

    print(
        "ERROR: Camera could not be opened."
    )

    detector.close()

    exit()


# ==========================================
# SCREEN
# ==========================================

screen_width, screen_height = pyautogui.size()


# ==========================================
# NORMALIZATION
# ==========================================

def normalize_landmarks(values):

    landmarks = []

    for i in range(21):

        x = values[i * 2]

        y = values[i * 2 + 1]

        landmarks.append(
            (x, y)
        )


    wrist_x = landmarks[0][0]
    wrist_y = landmarks[0][1]


    relative = []

    for x, y in landmarks:

        relative_x = x - wrist_x
        relative_y = y - wrist_y

        relative.append(
            (
                relative_x,
                relative_y
            )
        )


    max_distance = 0

    for x, y in relative:

        distance = math.sqrt(
            x * x +
            y * y
        )

        if distance > max_distance:

            max_distance = distance


    if max_distance == 0:

        max_distance = 1


    normalized = []

    for x, y in relative:

        normalized.append(
            x / max_distance
        )

        normalized.append(
            y / max_distance
        )


    return normalized


# ==========================================
# CURSOR
# ==========================================

previous_x = None
previous_y = None


def move_cursor(hand):

    global previous_x
    global previous_y


    index_finger = hand[8]

    x = index_finger.x
    y = index_finger.y


    x = max(
        0.02,
        min(0.98, x)
    )

    y = max(
        0.02,
        min(0.98, y)
    )


    target_x = x * screen_width
    target_y = y * screen_height


    if previous_x is None:

        previous_x = target_x
        previous_y = target_y


    current_x = (
        previous_x
        +
        (target_x - previous_x)
        *
        SMOOTHING
    )


    current_y = (
        previous_y
        +
        (target_y - previous_y)
        *
        SMOOTHING
    )


    pyautogui.moveTo(
        int(current_x),
        int(current_y),
        duration=0
    )


    previous_x = current_x
    previous_y = current_y


# ==========================================
# GESTURE HISTORY
# ==========================================

gesture_history = deque(
    maxlen=HISTORY_SIZE
)


def get_stable_gesture():

    if len(gesture_history) < STABLE_COUNT:

        return None


    recent = list(
        gesture_history
    )[-STABLE_COUNT:]


    if all(
        gesture == recent[0]
        for gesture in recent
    ):

        return recent[0]


    return None


# ==========================================
# STATE
# ==========================================

last_timestamp_ms = 0

last_click_time = 0

last_scroll_time = 0

left_start_time = None

dragging = False


# ==========================================
# START
# ==========================================

print()
print("==============================")
print("     AI VIRTUAL MOUSE")
print("==============================")
print()

print("MOVE        -> Cursor")
print("LEFT_CLICK  -> Left click")
print("RIGHT_CLICK -> Right click")
print("SCROLL      -> Scroll")
print("PAUSE       -> Pause")
print("LEFT_CLICK hold -> Drag")
print()

print("Stability protection: ON")
print("Press Q to quit.")
print()


# ==========================================
# MAIN LOOP
# ==========================================

while True:

    success, frame = cap.read()


    if not success:

        print(
            "ERROR: Could not read camera."
        )

        break


    frame = cv2.flip(
        frame,
        1
    )


    # ======================================
    # TIMESTAMP
    # ======================================

    timestamp_ms = int(
        time.time() * 1000
    )


    if timestamp_ms <= last_timestamp_ms:

        timestamp_ms = (
            last_timestamp_ms + 1
        )


    last_timestamp_ms = timestamp_ms


    # ======================================
    # DETECT
    # ======================================

    result = detector.detect(
        frame,
        timestamp_ms
    )


    # ======================================
    # NO HAND
    # ======================================

    if not result.hand_landmarks:

        gesture_history.clear()


        if dragging:

            pyautogui.mouseUp()

            dragging = False


        left_start_time = None


        cv2.putText(
            frame,
            "NO HAND",
            (20, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 0, 255),
            3
        )


        cv2.imshow(
            "AI Virtual Mouse",
            frame
        )


        if cv2.waitKey(1) & 0xFF == ord("q"):

            break


        continue


    # ======================================
    # HAND
    # ======================================

    hand = result.hand_landmarks[0]


    values = []


    for landmark in hand:

        values.append(
            landmark.x
        )

        values.append(
            landmark.y
        )


    # ======================================
    # NORMALIZE
    # ======================================

    features = normalize_landmarks(
        values
    )


    # ======================================
    # PREDICT
    # ======================================

    prediction = model.predict(
        [features]
    )[0]


    probabilities = model.predict_proba(
        [features]
    )[0]


    confidence = max(
        probabilities
    )


    # ======================================
    # CONFIDENCE FILTER
    # ======================================

    if confidence < CONFIDENCE_THRESHOLD:

        prediction = "UNKNOWN"


    # ======================================
    # ADD HISTORY
    # ======================================

    gesture_history.append(
        prediction
    )


    stable_gesture = get_stable_gesture()


    # ======================================
    # STABLE GESTURE
    # ======================================

    if stable_gesture == "MOVE":

        move_cursor(hand)


    # ======================================
    # LEFT CLICK / DRAG
    # ======================================

    if stable_gesture == "LEFT_CLICK":

        current_time = time.time()


        if left_start_time is None:

            left_start_time = current_time


        hold_time = (
            current_time
            -
            left_start_time
        )


        # Start drag after holding

        if (
            hold_time >= DRAG_HOLD_TIME
            and
            not dragging
        ):

            pyautogui.mouseDown()

            dragging = True


    else:

        # Gesture changed/released

        if left_start_time is not None:

            hold_time = (
                time.time()
                -
                left_start_time
            )


            # Normal click

            if (
                hold_time < DRAG_HOLD_TIME
                and
                not dragging
                and
                stable_gesture is not None
            ):

                if (
                    time.time()
                    -
                    last_click_time
                    >= CLICK_COOLDOWN
                ):

                    pyautogui.click()

                    last_click_time = (
                        time.time()
                    )


            # Drop

            if dragging:

                pyautogui.mouseUp()

                dragging = False


            left_start_time = None


    # ======================================
    # RIGHT CLICK
    # ======================================

    if stable_gesture == "RIGHT_CLICK":

        if (
            time.time()
            -
            last_click_time
            >= CLICK_COOLDOWN
        ):

            pyautogui.rightClick()

            last_click_time = (
                time.time()
            )


            # Clear history so one gesture
            # doesn't repeatedly click

            gesture_history.clear()


    # ======================================
    # SCROLL
    # ======================================

    if stable_gesture == "SCROLL":

        if (
            time.time()
            -
            last_scroll_time
            >= SCROLL_COOLDOWN
        ):

            pyautogui.scroll(
                SCROLL_AMOUNT
            )

            last_scroll_time = (
                time.time()
            )


    # ======================================
    # PAUSE
    # ======================================

    if stable_gesture == "PAUSE":

        pass


    # ======================================
    # DISPLAY
    # ======================================

    display_gesture = (
        stable_gesture
        if stable_gesture is not None
        else prediction
    )


    display_text = (
        f"{display_gesture} "
        f"{confidence * 100:.1f}%"
    )


    cv2.putText(
        frame,
        display_text,
        (20, 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 255, 0),
        3
    )


    # ======================================
    # DRAG STATUS
    # ======================================

    if dragging:

        cv2.putText(
            frame,
            "DRAGGING",
            (20, 85),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 255),
            3
        )


    # ======================================
    # FINGERTIPS
    # ======================================

    fingertip_indices = [
        4,
        8,
        12,
        16,
        20
    ]


    for index in fingertip_indices:

        landmark = hand[index]


        x = int(
            landmark.x
            *
            frame.shape[1]
        )


        y = int(
            landmark.y
            *
            frame.shape[0]
        )


        cv2.circle(
            frame,
            (x, y),
            7,
            (0, 255, 0),
            -1
        )


    # ======================================
    # SHOW
    # ======================================

    cv2.imshow(
        "AI Virtual Mouse",
        frame
    )


    # ======================================
    # QUIT
    # ======================================

    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


# ==========================================
# SAFETY
# ==========================================

if dragging:

    pyautogui.mouseUp()


cap.release()

cv2.destroyAllWindows()

detector.close()


print()
print("==============================")
print(" AI VIRTUAL MOUSE STOPPED")
print("==============================")