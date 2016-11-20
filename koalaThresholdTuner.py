import cv2
import numpy as np

cap = cv2.VideoCapture(0)   # start video connection

# CANNY SETUP
#=============================================
def nothing(x):
    pass

cv2.namedWindow('Threshold')

# create trackbars for color change
cv2.createTrackbar('Value', 'Threshold', 122, 255, nothing)
cv2.createTrackbar('Blur', 'Threshold', 1, 10, nothing)
cv2.createTrackbar('Save White Settings', 'Threshold', 0, 1, nothing)
cv2.createTrackbar('Save Black Settings', 'Threshold', 0, 1, nothing)
cv2.createTrackbar('Save NoseL Settings', 'Threshold', 0, 1, nothing)
cv2.createTrackbar('Save NoseH Settings', 'Threshold', 0, 1, nothing)
#=============================================

whiteSaved = False
blackSaved = False
noseLSaved = False
noseHSaved = False

while(True):
    ret, frame = cap.read()    # Capture frame-by-frame
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # get current positions of trackbars
    thresholdValue = cv2.getTrackbarPos('Value', 'Threshold')
    blur = cv2.getTrackbarPos('Blur', 'Threshold')
    saveWhite = cv2.getTrackbarPos('Save White Settings', 'Threshold')
    saveBlack = cv2.getTrackbarPos('Save Black Settings', 'Threshold')
    saveNoseL = cv2.getTrackbarPos('Save NoseL Settings', 'Threshold')
    saveNoseH = cv2.getTrackbarPos('Save NoseH Settings', 'Threshold')

    if blur != 0:
        frame = cv2.GaussianBlur(frame, ksize=(0, 0), sigmaX=blur)

    # =========Basic Thresholds===========
    ret,frame = cv2.threshold(frame,thresholdValue,255,cv2.THRESH_BINARY)
    # ====================================

    cv2.imshow('Threshold', frame)

    if whiteSaved is False and saveWhite == 1:
        whiteSaved = True
        thresholdSettingsFile = open("whiteThresholdSettings.txt", "w")
        thresholdSettingsFile.write(str(thresholdValue) + "\n")
        thresholdSettingsFile.write(str(blur) + "\n")
        thresholdSettingsFile.close()
        print('White Settings Saved')

    if blackSaved is False and saveBlack == 1:
        blackSaved = True
        thresholdSettingsFile = open("blackThresholdSettings.txt", "w")
        thresholdSettingsFile.write(str(thresholdValue) + "\n")
        thresholdSettingsFile.write(str(blur) + "\n")
        thresholdSettingsFile.close()
        print('Black Settings Saved')

    if noseLSaved is False and saveNoseL == 1:
        noseLSaved = True
        thresholdSettingsFile = open("noseLThresholdSettings.txt", "w")
        thresholdSettingsFile.write(str(thresholdValue) + "\n")
        thresholdSettingsFile.write(str(blur) + "\n")
        thresholdSettingsFile.close()
        print('Nose Low Settings Saved')

    if noseHSaved is False and saveNoseH == 1:
        noseHSaved = True
        thresholdSettingsFile = open("noseHThresholdSettings.txt", "w")
        thresholdSettingsFile.write(str(thresholdValue) + "\n")
        thresholdSettingsFile.write(str(blur) + "\n")
        thresholdSettingsFile.close()
        print('Nose High Settings Saved')

    if cv2.waitKey(1) & 0xFF == ord('q'):   # end the program by pressing q
        break


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
