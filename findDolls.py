import cv2
import numpy as np

# DOC SETTINGS ====================================================================================
beltFoundTotalLowerLimit = 30    # lower limit of # of belt buckle points that need to be found to be considered a belt
beltFoundTotalUpperLimit = 65  # upper limit of # of belt buckle points that need to be found to be considered a belt
ratioLowerLimit = 5      # lower limit of ratio of circle perimeter to circle area (ideally 12.54)
ratioUpperLimit = 30     # upper limit of ratio of circle perimeter to circle area (ideally 12.54)
beltColorThreshold = 60  # belt pixels must be BELOW this value to be considered the belt
areaLowerLimit = 100     # smallest area the belt buckle can be to be considered a belt buckle
areaUpperLimit = 10000    # largest area the belt buckle can be to be considered a belt buckle
docThetaInterval = 2        # degree of rotation that is checked if black around the centerpoint
radiusOffset = .5      # determines how far away from the center of the belt buckle to look for the belt pixels
erosionKernelSize = 2           # 2 works size of kernel for morphological operations
dilationKernelSize = 2          # 2 works
# ================================================================================================

# KOALA SETTINGS =================================================================================
noseFoundTotalUpperLimit = 8
noseFoundTotalLowerLimit = 1
koalaThetaInterval = 5
radiusConstant = 1.2
# ================================================================================================

# CREATE MORPHOLOGY KERNELS ==================
erosionKernel = np.ones((erosionKernelSize,erosionKernelSize), np.uint8)
dilationKernel = np.ones((dilationKernelSize,dilationKernelSize), np.uint8)
# ============================================

# READ KOALA THRESHOLDS FILE =================
thresholdSettingsFile = open("whiteThresholdSettings.txt", "r")
white_point_threshold = int(thresholdSettingsFile.readline()) #110
thresholdSettingsFile = open("blackThresholdSettings.txt", "r")
black_point_threshold = int(thresholdSettingsFile.readline()) #55
thresholdSettingsFile = open("noseLThresholdSettings.txt", "r")
averageNoseIntensityUpper = int(thresholdSettingsFile.readline()) #63
thresholdSettingsFile = open("noseHThresholdSettings.txt", "r")
averageNoseIntensityLower = int(thresholdSettingsFile.readline()) #0
blurSigma = int(thresholdSettingsFile.readline()) #2
# ============================================

# READ BUCKLE CALIBRATION FILE ===============
hsvSettingsFile = open("hsvBeltSettings.txt", "r")
hsvBeltLow = np.array([int(hsvSettingsFile.readline()),int(hsvSettingsFile.readline()),int(hsvSettingsFile.readline())])
hsvBeltHigh = np.array([int(hsvSettingsFile.readline()),int(hsvSettingsFile.readline()),int(hsvSettingsFile.readline())])
beltBlur = int(hsvSettingsFile.readline())  #10
# ============================================

# READ JACKET CALIBRATION FILE ===============
hsvSettingsFile = open("hsvJacketSettings.txt", "r")
hsvJacketLow = np.array([int(hsvSettingsFile.readline()),int(hsvSettingsFile.readline()),int(hsvSettingsFile.readline())])
hsvJacketHigh = np.array([int(hsvSettingsFile.readline()),int(hsvSettingsFile.readline()),int(hsvSettingsFile.readline())])
jacketBlur = int(hsvSettingsFile.readline())  #10
# ============================================

# START VIDEO CAPTURE ========================
cap = cv2.VideoCapture(0)
# ============================================

# GET INITIAL FRAME AND DIMENSIONS ===========
ret, frame = cap.read()    # Capture frame-by-frame
height, width = frame.shape[:2]    # find image dimensions
# ============================================

def findDoc(image):
    docFound = False
    imgHSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)     # Convert image to HSV
    jacketHSVGaussian = cv2.GaussianBlur(imgHSV, ksize=(0, 0), sigmaX=jacketBlur)     # Blur color HSV image
    # ===========================================================================================

    # THRESHOLD HSV =============================================================================
    hsvThresh = cv2.inRange(imgHSV, hsvBeltLow, hsvBeltHigh)
    # ===========================================================================================

    # PERFORM OPENING ===========================================================================
    hsvThresh = cv2.erode(hsvThresh, erosionKernel, iterations = 5)     #3
    hsvThresh = cv2.dilate(hsvThresh, dilationKernel, iterations = 7)  #10
    # ===========================================================================================

    # BLUR THE MORPHED IMAGE ====================================================================
    hsvThresh = cv2.GaussianBlur(hsvThresh, ksize=(0, 0), sigmaX=beltBlur)     # Blur color HSV image
    # ===========================================================================================

    # THRESHOLD THE BLURRED IMAGE ===============================================================
    ret, hsvThresh = cv2.threshold(hsvThresh, 1, 255, cv2.THRESH_BINARY)
    # cv2.imshow('Thresholded Image', hsvThresh)
    # ===========================================================================================

    # FIND CONTOURS =============================================================================
    res, contours, hierarchy = cv2.findContours(hsvThresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # ===========================================================================================

    # FIND YELLOW CIRCLES =======================================================================
    yellowCenterPoints = [] # create empty array to fill up with yellow centerpoints
    for i in contours:      # look through all contours
        M = cv2.moments(i)  # get the moments of the contours
        if M['m00'] != 0:   # check if contour moment is not 0
            cx = int(M['m10']/M['m00'])     # find x coordinate of centroid
            cy = int(M['m01']/M['m00'])     # find y coordinate of centroid
            if (0 <= cx <= width) and (0 <= cy <= height):     # check if centerpoint is on frame
                circ = cv2.arcLength(i,True)    # find perimeter of contour
                area = cv2.contourArea(i)       # find area of contour
                ratio = ((circ*circ)/area)      # find ratio of circumference and area circle is 12.56
                if ratioLowerLimit < ratio < ratioUpperLimit:   # check if ratio is between acceptable limits (is it circly enough?)
                    if areaUpperLimit > area > areaLowerLimit:   # check if area is above minimum value
                        yellowCenterPoints.append((cx,cy,area))     # add centerpoint to list of yellow centerpoints
    # ===========================================================================================

    # FIND BLACK POINTS AROUND YELLOW CIRCLES ===================================================
    possibleMatches = []
    for i in yellowCenterPoints:
        cx = i[0]   # X centerpoint
        cy = i[1]   # Y centerpoint
        area = i[2] # blob area

        radius = int(radiusOffset * np.sqrt(area))  # create an offset for the belt check (sqrt is because area is a distance squared)

        beltFoundTotal = 0  # count of how many times the belt is found (black pixel is found)
        for theta in range(0, 360, docThetaInterval):
            theta = np.deg2rad(theta)   # convert to radians
            cxAdjust = cx + int(radius*np.cos(theta))   # create X point to check if it's a belt
            cyAdjust = cy + int(radius*np.sin(theta))   # create Y point to check if it's a belt

            # MAKE SURE RADIUS TO CHECK IS ON FRAME ========
            if cxAdjust >= width:
                cxAdjust = width - 1
            elif cxAdjust <= 0:
                cxAdjust = 0
            if cyAdjust >= height:
                cyAdjust = height - 1
            elif cyAdjust <= 0:
                cyAdjust = 0
            # =============================================

            # LOAD COAT CHECK VALUES =====================
            radiusH = jacketHSVGaussian[cyAdjust][cxAdjust][0]
            radiusS = jacketHSVGaussian[cyAdjust][cxAdjust][1]
            radiusV = jacketHSVGaussian[cyAdjust][cxAdjust][2]
            HL = hsvJacketLow[0]
            HH = hsvJacketHigh[0]
            SL = hsvJacketLow[1]
            SH = hsvJacketHigh[1]
            VL = hsvJacketLow[2]
            VH = hsvJacketHigh[2]
            # =============================================

            # CHECK IF RADIUS POINT IS A COAT PIXEL =======
            if (HL < radiusH < HH) and (SL < radiusS < SH) and (VL < radiusV < VH):
                beltFoundTotal = beltFoundTotal + 1 # count belt points found
                # cv2.circle(image,(cxAdjust,cyAdjust),2,(0, 0, 255),3)   # draws points on belt

        # DETERMINE IF YELLOW DOT IS A BELT BASED ON SURROUNDING PIXEL COUNT
        if beltFoundTotalUpperLimit > beltFoundTotal > beltFoundTotalLowerLimit:    # check if belt is found
            possibleMatches.append((cx,cy,area,beltFoundTotal))   # add found belt to list of matches

    if len(possibleMatches) > 0:
        docFound = True
        possibleMatches.sort(key=lambda tup: tup[3], reverse = True)
        cx = possibleMatches[0][0]   # X centerpoint
        cy = possibleMatches[0][1]   # Y centerpoint
        area = possibleMatches[0][2]
        drawData = (docFound, cx, cy, area)
    else:
        drawData = (False, 0, 0, 0)

    return drawData
    # ===========================================================================================

def findKoala(image):
    koalaFound = False

    # =========== Blur Image ===========
    image = cv2.GaussianBlur(image, ksize=(0, 0), sigmaX=blurSigma)

    # =========== Hough Circles ===========
    image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

    circles = cv2.HoughCircles(image=image,method=cv2.HOUGH_GRADIENT,dp=1 ,minDist=10 ,param1=50,param2=30,minRadius=5,maxRadius=50)

    possibleMatches = []
    blackCircles = []

    if circles is not None:
        circles = np.uint16(np.around(circles))

        # Determine if circles are black
        # =====================================
        for i in circles[0,:]:
            cx = i[0]
            cy = i[1]
            radius = i[2]
            mask = np.zeros((height,width), np.uint8)
            cv2.circle(mask, (cx,cy), radius, (255,255,255), -1, 8, 0 )
            mean_val = cv2.mean(image,mask)

            if averageNoseIntensityUpper > mean_val[0] > averageNoseIntensityLower:
                blackCircles.append((cx, cy, radius))
        # =====================================

        # Determine if black circles have white and black around them
        # =====================================
        for i in blackCircles:
            cx = i[0]
            cy = i[1]
            radius = i[2]
            test_radius = int(radiusConstant * radius)    #Find white points and black points around the Koala

            whiteFoundTotal = 0  # count of how many times the belt is found (black pixel is found)
            blackFoundTotal = 0  # count of how many times the belt is found (black pixel is found)

            for theta in range(0, 360, koalaThetaInterval):
                theta = np.deg2rad(theta)   # convert to radians
                test_point_x = cx + int(test_radius*np.cos(theta))   # create X point to check if it's a belt
                test_point_y = cy + int(test_radius*np.sin(theta))   # create Y point to check if it's a belt

                # make sure radius to check is on frame ========
                if test_point_x >= width:
                    test_point_x = width - 1
                elif test_point_x <= 0:
                    test_point_x = 0
                if test_point_y >= height:
                    test_point_y = height - 1
                elif test_point_y <= 0:
                    test_point_y = 0
                # =============================================

                test_point_colour = image[test_point_y, test_point_x]   # find intensity value of belt

                if test_point_colour > white_point_threshold:      # compare belt intensity to minimum value
                    whiteFoundTotal = whiteFoundTotal + 1 # count belt points found
                    # cv2.circle(frame,(test_point_x,test_point_y),2,(0,255,0),3)

                if test_point_colour < black_point_threshold:      # compare belt intensity to minimum value
                    blackFoundTotal = blackFoundTotal + 1 # count belt points found
                    # cv2.circle(frame,(test_point_x,test_point_y),2,(0,0,255),3)

            if whiteFoundTotal > 0 and blackFoundTotal > 0:
                ratio = whiteFoundTotal/blackFoundTotal
                if 10 > ratio > 1:
                    possibleMatches.append((cx, cy, whiteFoundTotal, blackFoundTotal, radius))
        # =====================================

    if len(possibleMatches) > 0:
        koalaFound = True
        possibleMatches.sort(key=lambda tup: tup[2], reverse = True)    # make the point with the most whiteFound values the first index
        cx = possibleMatches[0][0]   # X centerpoint of first index
        cy = possibleMatches[0][1]   # Y centerpoint of first index
        radius = possibleMatches[0][4]
        drawData = (koalaFound, cx, cy, radius)
    else:
        drawData = (koalaFound, 0, 0, 0)

    return drawData

while(True):
    ret, frame = cap.read()    # Capture frame-by-frame

    docInfo = findDoc(frame)
    koalaInfo = findKoala(frame)

    if docInfo[0]:  # check if Doc was found
        cx = docInfo[1]
        cy = docInfo[2]
        area = docInfo[3]
        cv2.rectangle(frame,(cx-int(2.5*np.sqrt(area)),cy-int(2.5*np.sqrt(area))),(cx+int(2.5*np.sqrt(area)),cy+int(2.5*np.sqrt(area))),(255,0,255),2)
        cv2.putText(frame,"Doc",(cx,cy),cv2.FONT_HERSHEY_PLAIN,3,(255,0,255),thickness=4) # Write 'Doc' on Doc

    if koalaInfo[0]:    # check if Koala was found
        cx = koalaInfo[1]
        cy = koalaInfo[2]
        radius = koalaInfo[3]
        scale = 8
        cv2.rectangle(frame,(cx-int(scale*radius),cy-int(scale*radius)),(cx+int(scale*radius),cy+int(scale*radius)),(255,255,23),2)
        cv2.putText(frame,"Koala",(cx,cy),cv2.FONT_HERSHEY_PLAIN,3,(255,255,23),thickness=4) # Write 'Koala' on Koala

    # DISPLAY IMAGE OF DOLLS ====================================================================
    cv2.imshow('Find Dolls',frame)
    # ===========================================================================================

    # EXIT PROGRAM ==============================================================================
    if cv2.waitKey(1) & 0xFF == ord('q'):   # end the program by pressing q
        break
    # ===========================================================================================

cap.release()   # When everything done, release the capture
cv2.destroyAllWindows() # Close windows
