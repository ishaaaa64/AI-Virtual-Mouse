import cv2
import time

from hand_detector import HandDetector


MODEL_PATH = "hand_landmarker.task"


# Create hand detector
detector = HandDetector(MODEL_PATH)


# Open camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Camera could not be opened.")
    exit()


print("Hand detection started!")
print("Press Q to exit.")


start_time = time.time()
frame_count = 0


while True:

    success, frame = cap.read()

    if not success:
        print("ERROR: Could not read camera frame.")
        break

    # Mirror image
    frame = cv2.flip(frame, 1)

    # Increase frame counter
    frame_count += 1

    # Calculate timestamp
    timestamp_ms = int(
        (time.time() - start_time) * 1000
    )

    # Detect hand
    result = detector.detect(
        frame,
        timestamp_ms
    )

    # Check if hand detected
    if result.hand_landmarks:

        cv2.putText(
            frame,
            "HAND DETECTED",
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        # Get first hand
        hand = result.hand_landmarks[0]

        # Draw all 21 landmark points
        for landmark in hand:

            x = int(landmark.x * frame.shape[1])
            y = int(landmark.y * frame.shape[0])

            cv2.circle(
                frame,
                (x, y),
                5,
                (0, 255, 0),
                -1
            )

    else:

        cv2.putText(
            frame,
            "NO HAND DETECTED",
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )

    # Show camera
    cv2.imshow(
        "AI Virtual Mouse - Hand Detection",
        frame
    )

    # Quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# Cleanup
cap.release()
cv2.destroyAllWindows()

detector.close()

print("Hand detection stopped.")