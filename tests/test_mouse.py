import cv2
import time
import os
import sys


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

sys.path.insert(
    0,
    PROJECT_ROOT
)


# ============================================================
# IMPORTS
# ============================================================

from mouse.mouse_controller import MouseController
from hand_tracking.hand_detector import HandDetector
from gestures.gesture_detector import GestureDetector


# ============================================================
# MODEL
# ============================================================

MODEL_PATH = os.path.join(
    PROJECT_ROOT,
    "hand_tracking",
    "hand_landmarker.task"
)


# ============================================================
# OBJECTS
# ============================================================

mouse = MouseController(
    smoothing=0.12
)

gesture_detector = GestureDetector()

detector = HandDetector(
    MODEL_PATH
)


# ============================================================
# CAMERA
# ============================================================

cap = cv2.VideoCapture(0)


if not cap.isOpened():

    print("ERROR: Camera could not be opened.")

    detector.close()

    exit()


# ============================================================
# START
# ============================================================

print()
print("==========================================")
print("          AI VIRTUAL MOUSE")
print("==========================================")
print()
print("INDEX              -> MOVE")
print("THUMB + INDEX      -> LEFT CLICK")
print("THUMB + INDEX HOLD -> DRAG")
print("RELEASE            -> DROP")
print("THUMB + MIDDLE     -> RIGHT CLICK")
print("INDEX + MIDDLE     -> SCROLL")
print()
print("Press Q to exit.")
print("==========================================")
print()


# ============================================================
# TIMESTAMP
# ============================================================

start_time = time.time()


# ============================================================
# FINGERTIPS
# ============================================================

FINGERTIPS = {

    4: "THUMB",

    8: "INDEX",

    12: "MIDDLE",

    16: "RING",

    20: "PINKY"
}


# ============================================================
# COLOURS
# ============================================================

THUMB_COLOR = (255, 0, 255)

INDEX_COLOR = (255, 0, 0)

MIDDLE_COLOR = (0, 255, 0)

RING_COLOR = (0, 165, 255)

PINKY_COLOR = (0, 255, 255)


# ============================================================
# GET FINGER COLOR
# ============================================================

def get_finger_color(index):

    if index == 4:

        return THUMB_COLOR

    if index == 8:

        return INDEX_COLOR

    if index == 12:

        return MIDDLE_COLOR

    if index == 16:

        return RING_COLOR

    if index == 20:

        return PINKY_COLOR

    return (255, 255, 255)


# ============================================================
# MAIN LOOP
# ============================================================

try:

    while True:

        # ====================================================
        # CAMERA
        # ====================================================

        success, frame = cap.read()


        if not success:

            print(
                "ERROR: Could not read camera."
            )

            break


        # ====================================================
        # MIRROR
        # ====================================================

        frame = cv2.flip(
            frame,
            1
        )


        # ====================================================
        # TIMESTAMP
        # ====================================================

        timestamp_ms = int(
            (time.time() - start_time)
            * 1000
        )


        # ====================================================
        # HAND DETECTION
        # ====================================================

        result = detector.detect(
            frame,
            timestamp_ms
        )


        # ====================================================
        # HAND FOUND
        # ====================================================

        if result.hand_landmarks:

            hand = result.hand_landmarks[0]


            # =================================================
            # DRAW ONLY FINGERTIPS
            # =================================================

            for tip_index, finger_name in FINGERTIPS.items():

                tip = hand[tip_index]


                x = int(
                    tip.x *
                    frame.shape[1]
                )

                y = int(
                    tip.y *
                    frame.shape[0]
                )


                color = get_finger_color(
                    tip_index
                )


                # ---------------------------------------------
                # Fingertip dot
                # ---------------------------------------------

                cv2.circle(
                    frame,
                    (x, y),
                    9,
                    color,
                    -1
                )


                # ---------------------------------------------
                # White outline
                # ---------------------------------------------

                cv2.circle(
                    frame,
                    (x, y),
                    9,
                    (255, 255, 255),
                    2
                )


                # ---------------------------------------------
                # Coordinate text
                # ---------------------------------------------

                coordinate_text = (
                    f"{finger_name}: "
                    f"{tip.x:.2f}, {tip.y:.2f}"
                )


                cv2.putText(
                    frame,
                    coordinate_text,
                    (20, 280 + (
                        list(FINGERTIPS.keys()).index(
                            tip_index
                        ) * 30
                    )),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    color,
                    2
                )


            # =================================================
            # INDEX FINGER
            # =================================================

            index_finger = hand[8]


            # =================================================
            # SCROLL
            # =================================================

            if gesture_detector.scroll_mode(hand):

                # Stop drag if necessary

                if gesture_detector.dragging:

                    mouse.stop_drag()

                    gesture_detector.dragging = False


                gesture_detector.left_pinch_start = None


                scroll_amount = (
                    gesture_detector.get_scroll_amount(
                        hand
                    )
                )


                mouse.scroll(
                    scroll_amount
                )


                gesture_text = "SCROLL MODE"


            else:

                gesture_detector.reset_scroll()


                # =============================================
                # LEFT PINCH / DRAG
                # =============================================

                left_action = (
                    gesture_detector.update_left_pinch(
                        hand
                    )
                )


                # =============================================
                # START DRAG
                # =============================================

                if left_action == "START_DRAG":

                    mouse.start_drag()

                    print("DRAG START")

                    gesture_text = "DRAGGING"


                # =============================================
                # DRAGGING
                # =============================================

                elif left_action == "DRAGGING":

                    mouse.move_cursor(
                        index_finger.x,
                        index_finger.y
                    )

                    gesture_text = "DRAGGING"


                # =============================================
                # STOP DRAG
                # =============================================

                elif left_action == "STOP_DRAG":

                    mouse.stop_drag()

                    print("DROP")

                    gesture_text = "DROP"


                # =============================================
                # LEFT CLICK
                # =============================================

                elif left_action == "LEFT_CLICK":

                    mouse.left_click()

                    print("LEFT CLICK")

                    gesture_text = "LEFT CLICK"


                # =============================================
                # PINCHING
                # =============================================

                elif left_action in (
                    "PINCH_START",
                    "PINCHING"
                ):

                    gesture_text = "LEFT PINCH"


                # =============================================
                # RIGHT CLICK
                # =============================================

                else:

                    right_action = (
                        gesture_detector.update_right_pinch(
                            hand
                        )
                    )


                    if right_action == "RIGHT_CLICK":

                        mouse.right_click()

                        print("RIGHT CLICK")

                        gesture_text = "RIGHT CLICK"


                    elif right_action == "RIGHT_PINCH":

                        gesture_text = "RIGHT PINCH"


                    else:

                        # =====================================
                        # NORMAL MOVE
                        # =====================================

                        mouse.move_cursor(
                            index_finger.x,
                            index_finger.y
                        )

                        gesture_text = "MOVE MODE"


            # =================================================
            # STATUS
            # =================================================

            cv2.putText(
                frame,
                gesture_text,
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )


            cv2.putText(
                frame,
                "5 FINGERTIPS TRACKED",
                (20, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )


            # =================================================
            # LEGEND
            # =================================================

            cv2.putText(
                frame,
                "THUMB",
                (350, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                THUMB_COLOR,
                2
            )


            cv2.putText(
                frame,
                "INDEX",
                (350, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                INDEX_COLOR,
                2
            )


            cv2.putText(
                frame,
                "MIDDLE",
                (350, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                MIDDLE_COLOR,
                2
            )


            cv2.putText(
                frame,
                "RING",
                (350, 125),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                RING_COLOR,
                2
            )


            cv2.putText(
                frame,
                "PINKY",
                (350, 150),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                PINKY_COLOR,
                2
            )


        # ====================================================
        # NO HAND
        # ====================================================

        else:

            gesture_detector.reset_scroll()

            cv2.putText(
                frame,
                "NO HAND DETECTED",
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )


        # ====================================================
        # DISPLAY
        # ====================================================

        cv2.imshow(
            "AI Virtual Mouse",
            frame
        )


        # ====================================================
        # EXIT
        # ====================================================

        if cv2.waitKey(1) & 0xFF == ord("q"):

            break


finally:

    # Safety release
    if gesture_detector.dragging:

        mouse.stop_drag()


    cap.release()

    cv2.destroyAllWindows()

    detector.close()


print()
print("AI Virtual Mouse stopped.")