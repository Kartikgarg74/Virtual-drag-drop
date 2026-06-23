# Virtual Drag Drop project
# cvzone model used 1.4.1

import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import numpy as np

# Camera resolution constants
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

# Detection and gesture constants
DETECTION_CONFIDENCE = 1.0
NUM_RECTANGLES = 5
RECT_SPACING = 250
RECT_START_X = 150
RECT_START_Y = 150
GESTURE_DISTANCE_THRESHOLD = 40
OVERLAY_ALPHA = 0.5

# Drawing color
color = (255, 0, 255)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit(1)

cap.set(3, CAMERA_WIDTH)
cap.set(4, CAMERA_HEIGHT)

detector = HandDetector(detectionCon=DETECTION_CONFIDENCE)


class DragRect:
    def __init__(self, posCenter, size=None):
        if size is None:
            size = [200, 200]
        self.posCenter = posCenter
        self.size = size

    def update(self, cursor):
        cx, cy = self.posCenter
        w, h = self.size

        # If the index finger tip is in the rectangle region
        if cx - w // 2 < cursor[0] < cx + w // 2 and cy - h // 2 < cursor[1] < cy + h // 2:
            self.posCenter = cursor


# For multiple rectangles
rectList = []
for x in range(NUM_RECTANGLES):
    rectList.append(DragRect([x * RECT_SPACING + RECT_START_X, RECT_START_Y]))

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    img = detector.findHands(img)
    lmsList, _ = detector.findPosition(img)

    if lmsList and len(lmsList) > 12:
        result = detector.findDistance(8, 12, img, draw=False)
        if result is not None:
            dist, _, _ = result

            if dist < GESTURE_DISTANCE_THRESHOLD:
                cursor = lmsList[8]  # index finger tip landmark
                for rect in rectList:
                    rect.update(cursor)

    # Draw transparent overlay
    imgNew = np.zeros_like(img, np.uint8)
    for rect in rectList:
        cx, cy = rect.posCenter
        w, h = rect.size
        cv2.rectangle(imgNew, (cx - w // 2, cy - h // 2), (cx + w // 2, cy + h // 2), color, cv2.FILLED)
        cvzone.cornerRect(imgNew, (cx - w // 2, cy - h // 2, w, h), 20, rt=0)

    out = img.copy()
    mask = imgNew.astype(bool)
    out[mask] = cv2.addWeighted(img, OVERLAY_ALPHA, imgNew, 1 - OVERLAY_ALPHA, 0)[mask]

    cv2.imshow("Image", out)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
