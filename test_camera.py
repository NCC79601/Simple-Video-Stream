import cv2
import time

cap = cv2.VideoCapture(1)
time.sleep(1)

while True:
    ret, frame = cap.read()
    if not ret:
        print('Camera offline. Exiting...')
        break
    cv2.imshow('Video Capture', frame)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
