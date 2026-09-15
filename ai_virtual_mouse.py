
import cv2
import time
import os
import sys
import pickle
import pyautogui

from collections import deque, Counter

# ==========================================
# PROJECT PATHS
# ==========================================

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from hand_tracking.hand_detector import HandDetector
from mouse.mouse_controller import MouseController


# ==========================================
# PATHS
# ==========================================

MODEL_PATH = os.path.join(
    PROJECT_ROOT,
    "dataset",
    "gesture_model.pkl"
)

HAND_MODEL_PATH = os.path.join(
    PROJECT_ROOT,
    "hand_tracking",
    "hand_landmarker.task"
)


# ==========================================
# SETTINGS
# ==========================================

SMOOTHING = 0.20

CONFIDENCE_THRESHOLD = 0.70

HISTORY_SIZE = 7
STABLE_COUNT = 5

CLICK_COOLDOWN = 0.70

DRAG_HOLD_TIME = 0.70


# ==========================================
# CHECK MODEL
# ==========================================

if not os.path.exists(MODEL_PATH):

    print("ERROR: gesture_model.pkl not found.")
    print("Please train the model first.")
    exit()


# ==========================================
# LOAD ML MODEL
# ==========================================

with open(MODEL_PATH, "rb") as file:

    model = pickle.load(file)


print()
print("==============================")
print("      AI VIRTUAL MOUSE")
print("==============================")
print()

print("ML model loaded successfully.")


# ==========================================
# HAND DETECTOR
# ==========================================

detector = HandDetector(HAND_MODEL_PATH)


# ==========================================
# MOUSE
# ==========================================

mouse = MouseController(
    smoothing=SMOOTHING
)


# ==========================================
# CAMERA
# ==========================================

cap = cv2.VideoCapture(0)


if not cap.isOpened():

    print("ERROR: Camera could not be opened.")

    detector.close()

    exit()


# ==========================================
# VARIABLES
# ==========================================

start_time = time.time()

gesture_history = deque(
    maxlen=HISTORY_SIZE
)

previous_gesture = "NO HAND"

last_right_click_time = 0

previous_scroll_y = None

dragging = False

pinch_start_time = None

left_click_done = False


# ==========================================
# FINGERTIPS
# ==========================================

fingertip_indices = [
    4,
    8,
    12,
    16,
    20
]


# ==========================================
# STABLE GESTURE FUNCTION
# ==========================================

def get_stable_gesture(history):

    if len(history) < HISTORY_SIZE:

        return "WAITING"


    counts = Counter(history)

    gesture, count = counts.most_common(1)[0]


    if count >= STABLE_COUNT:

        return gesture


    return "UNCERTAIN"


# ==========================================
# RESET ACTION STATE
# ==========================================

def reset_action_state():

    global pinch_start_time
    global left_click_done
    global previous_scroll_y

    pinch_start_time = None

    left_click_done = False

    previous_scroll_y = None


# ==========================================
# START
# ==========================================

print()
print("AI Virtual Mouse started!")
print()

print("MOVE        -> Index finger")
print("LEFT CLICK  -> Thumb + Index pinch")
print("RIGHT CLICK -> Thumb + Middle pinch")
print("SCROLL      -> Index + Middle")
print("DRAG        -> Hold Thumb + Index")
print("PAUSE       -> Fist")
print()

print("Press Q to exit.")
print()


# ==========================================
# MAIN LOOP
# ==========================================

while True:

    success, frame = cap.read()


    if not success:

        print("ERROR: Could not read camera.")

        break


    # Mirror camera

    frame = cv2.flip(
        frame,
        1
    )


    # ======================================
    # TIMESTAMP
    # ======================================

    timestamp_ms = int(
        (time.time() - start_time) * 1000
    )


    # ======================================
    # HAND DETECTION
    # ======================================

    result = detector.detect(
        frame,
        timestamp_ms
    )


    gesture = "NO HAND"

    stable_gesture = "NO HAND"

    confidence = 0.0


    # ======================================
    # HAND FOUND
    # ======================================

    if result.hand_landmarks:

        hand = result.hand_landmarks[0]


        # ==================================
        # CREATE FEATURES
        # ==================================

        features = []

        for landmark in hand:

            features.append(
                landmark.x
            )

            features.append(
                landmark.y
            )


        # ==================================
        # ML PREDICTION
        # ==================================

        prediction = model.predict(
            [features]
        )

        gesture = prediction[0]


        probabilities = model.predict_proba(
            [features]
        )

        confidence = max(
            probabilities[0]
        )


        # ==================================
        # CONFIDENCE FILTER
        # ==================================

        if confidence >= CONFIDENCE_THRESHOLD:

            gesture_history.append(
                gesture
            )

            stable_gesture = get_stable_gesture(
                gesture_history
            )

        else:

            stable_gesture = "UNCERTAIN"


        # ==================================
        # INDEX FINGER
        # ==================================

        index_tip = hand[8]


        # ==================================
        # PAUSE
        # ==================================

        if stable_gesture == "PAUSE":

            # Stop everything

            if dragging:

                mouse.stop_drag()

                dragging = False


            reset_action_state()

            previous_gesture = "PAUSE"


        # ==================================
        # MOVE
        # ==================================

        elif stable_gesture == "MOVE":

            # If drag is active,
            # continue dragging

            mouse.move_cursor(
                index_tip.x,
                index_tip.y
            )


            # Reset click timer

            if previous_gesture != "LEFT_CLICK":

                reset_action_state()


            previous_gesture = "MOVE"


        # ==================================
        # LEFT CLICK / DRAG
        # ==================================

        elif stable_gesture == "LEFT_CLICK":

            now = time.time()


            # --------------------------------
            # FIRST PINCH
            # --------------------------------

            if pinch_start_time is None:

                pinch_start_time = now

                left_click_done = False


            # --------------------------------
            # HOW LONG PINCHED?
            # --------------------------------

            hold_time = (
                now - pinch_start_time
            )


            # --------------------------------
            # DRAG
            # --------------------------------

            if (
                hold_time >= DRAG_HOLD_TIME
                and not dragging
            ):

                mouse.start_drag()

                dragging = True


            # --------------------------------
            # MOVE WHILE DRAGGING
            # --------------------------------

            if dragging:

                mouse.move_cursor(
                    index_tip.x,
                    index_tip.y
                )


            previous_gesture = "LEFT_CLICK"


        # ==================================
        # RIGHT CLICK
        # ==================================

        elif stable_gesture == "RIGHT_CLICK":

            now = time.time()


            # Only trigger when gesture
            # changes INTO right click

            if (
                previous_gesture
                != "RIGHT_CLICK"
            ):

                if (
                    now - last_right_click_time
                    > CLICK_COOLDOWN
                ):

                    mouse.right_click()

                    last_right_click_time = now


            reset_action_state()

            previous_gesture = "RIGHT_CLICK"


        # ==================================
        # SCROLL
        # ==================================

        elif stable_gesture == "SCROLL":

            current_y = (
                hand[8].y
                +
                hand[12].y
            ) / 2


            if previous_scroll_y is None:

                previous_scroll_y = current_y


            difference = (
                previous_scroll_y
                -
                current_y
            )


            previous_scroll_y = current_y


            if abs(difference) > 0.004:

                amount = int(
                    difference * 120
                )


                amount = max(
                    -6,
                    min(6, amount)
                )


                if amount != 0:

                    mouse.scroll(
                        amount
                    )


            reset_action_state()

            # Restore scroll variable

            previous_scroll_y = current_y

            previous_gesture = "SCROLL"


        # ==================================
        # UNCERTAIN
        # ==================================

        elif stable_gesture == "UNCERTAIN":

            # Don't perform ANY action.

            pass


        # ==================================
        # WAITING
        # ==================================

        elif stable_gesture == "WAITING":

            pass


        # ==================================
        # DRAW FINGERTIPS
        # ==================================

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
    # NO HAND
    # ======================================

    else:

        gesture_history.clear()

        stable_gesture = "NO HAND"

        previous_scroll_y = None


        # ==================================
        # IMPORTANT:
        # RELEASE DRAG
        # ==================================

        if dragging:

            mouse.stop_drag()

            dragging = False


        reset_action_state()

        previous_gesture = "NO HAND"


    # ======================================
    # DISPLAY STATUS
    # ======================================

    status = stable_gesture


    if dragging:

        status = "DRAGGING"


    cv2.putText(
        frame,
        f"Gesture: {status}",
        (20, 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 255, 0),
        2
    )


    cv2.putText(
        frame,
        f"Confidence: {confidence * 100:.1f}%",
        (20, 85),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )


    if dragging:

        cv2.putText(
            frame,
            "DRAG ACTIVE",
            (20, 125),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )

    else:

        cv2.putText(
            frame,
            "AI MODE - Press Q to exit",
            (20, 125),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )


    # ======================================
    # SHOW WINDOW
    # ======================================

    cv2.imshow(
        "AI Virtual Mouse - Stable ML",
        frame
    )


    # ======================================
    # EXIT
    # ======================================

    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


# ==========================================
# SAFETY RELEASE
# ==========================================

if dragging:

    mouse.stop_drag()


# ==========================================
# CLOSE
# ==========================================

cap.release()

cv2.destroyAllWindows()

detector.close()


print()
print("==============================")
print("AI VIRTUAL MOUSE STOPPED")
print("==============================")

