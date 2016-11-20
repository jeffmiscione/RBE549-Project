import cv2
import numpy as np

cap = cv2.VideoCapture(0)   # start video connection

# HSV SETUP
#=============================================
def nothing(x):
    pass

cv2.namedWindow('HSV Tuner')
# create trackbars for color change
cv2.createTrackbar('Hue Low', 'HSV Tuner', 0, 180, nothing)
cv2.createTrackbar('Hue High', 'HSV Tuner', 180, 180, nothing)
cv2.createTrackbar('Saturation Low', 'HSV Tuner', 0, 255, nothing)
cv2.createTrackbar('Saturation High', 'HSV Tuner', 255, 255, nothing)
cv2.createTrackbar('Value Low', 'HSV Tuner', 0, 255, nothing)
cv2.createTrackbar('Value High', 'HSV Tuner', 255, 255, nothing)
cv2.createTrackbar('Blur', 'HSV Tuner', 0, 10, nothing)
cv2.createTrackbar('Belt/Jacket', 'HSV Tuner', 0, 1, nothing)
cv2.createTrackbar('Save Settings', 'HSV Tuner', 0, 1, nothing)
#=============================================

saved = False

while(True):
    ret, frame = cap.read()    # Capture frame-by-frame
    imgHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # get current positions of trackbars
    HueLow = cv2.getTrackbarPos('Hue Low', 'HSV Tuner')    # 35
    HueHigh = cv2.getTrackbarPos('Hue High', 'HSV Tuner')    # 35
    SaturationLow = cv2.getTrackbarPos('Saturation Low', 'HSV Tuner')  # 60
    SaturationHigh = cv2.getTrackbarPos('Saturation High', 'HSV Tuner')  # 60
    ValueLow = cv2.getTrackbarPos('Value Low', 'HSV Tuner')    # 143
    ValueHigh = cv2.getTrackbarPos('Value High', 'HSV Tuner')    # 143
    blur = cv2.getTrackbarPos('Blur', 'HSV Tuner')
    object = cv2.getTrackbarPos('Belt/Jacket', 'HSV Tuner')
    save = cv2.getTrackbarPos('Save Settings', 'HSV Tuner')

    hsvLow = np.array([HueLow,SaturationLow,ValueLow])
    hsvHigh = np.array([HueHigh,SaturationHigh,ValueHigh])

    # Blur image
    if blur != 0:
        imgHSV = cv2.GaussianBlur(imgHSV, ksize=(0, 0), sigmaX=blur)

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(imgHSV, hsvLow, hsvHigh)

    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(frame,frame, mask= mask)

    # Show mask
    cv2.imshow('HSV Tuner',mask)
    #=============================================

    if saved != True and save == 1 and object == 0:
        # save file here
        saved = True
        hsvSettingsFile = open("hsvBeltSettings.txt", "w")
        hsvSettingsFile.write(str(HueLow) + "\n")
        hsvSettingsFile.write(str(SaturationLow) + "\n")
        hsvSettingsFile.write(str(ValueLow) + "\n")
        hsvSettingsFile.write(str(HueHigh) + "\n")
        hsvSettingsFile.write(str(SaturationHigh) + "\n")
        hsvSettingsFile.write(str(ValueHigh) + "\n")
        hsvSettingsFile.write(str(blur) + "\n")
        hsvSettingsFile.close()
        print('Belt Settings Saved')
    elif saved != True and save == 1 and object == 1:
        saved = True
        hsvSettingsFile = open("hsvJacketSettings.txt", "w")
        hsvSettingsFile.write(str(HueLow) + "\n")
        hsvSettingsFile.write(str(SaturationLow) + "\n")
        hsvSettingsFile.write(str(ValueLow) + "\n")
        hsvSettingsFile.write(str(HueHigh) + "\n")
        hsvSettingsFile.write(str(SaturationHigh) + "\n")
        hsvSettingsFile.write(str(ValueHigh) + "\n")
        hsvSettingsFile.write(str(blur) + "\n")
        hsvSettingsFile.close()
        print('Jacket Settings Saved')

    if cv2.waitKey(1) & 0xFF == ord('q'):   # end the program by pressing q
        break


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
