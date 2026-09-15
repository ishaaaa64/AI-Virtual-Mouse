import cv2


# Open the default laptop camera
cap = cv2.VideoCapture(0)

# Check if camera opened successfully
if not cap.isOpened():
    print("ERROR: Camera could not be opened.")
    exit()

print("Camera started successfully!")
print("Press Q to exit.")


while True:

    # Read one frame from camera
    success, frame = cap.read()

    # If frame was not captured
    if not success:
        print("ERROR: Could not read frame.")
        break

    # Flip the camera horizontally
    frame = cv2.flip(frame, 1)

    # Display the camera frame
    cv2.imshow("AI Virtual Mouse - Camera Test", frame)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# Release camera
cap.release()

# Close all OpenCV windows
cv2.destroyAllWindows()

print("Camera stopped.")