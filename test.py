import cv2
import time

cap = cv2.VideoCapture(0)
time.sleep(1)

while True:
    ret, frame = cap.read()

    cv2.imshow('Video Capture', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()