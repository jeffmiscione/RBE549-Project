# RBE549-Project
Doc and Koala tracking project from RBE549 Computer Vision during the fall 2015 semester

============================= Main Program =============================

The main program is the findDolls.py file. This requires tuning files that are specified below. NOTE: These values are heavily dependant upon lighting conditions and may need to be re-tuned).



============================= Tuning Files =============================

whiteThresholdSettings.txt
blackThresholdSettings.txt
hsvBeltSettings.txt
hsvJacketSettings.txt
noseHThresholdSettings.txt
noseLThresholdSettings.txt



========================= Re-tuning Procedure =========================

Run the koalaThresholdTuner.py file with a webcam equipped computer. Use this to tune the koala nose threshold values for the current light condition. Slide the save slider to the right when acceptable values have been determined.

Run the hsvBeltSettings.py file with a webcam equipped computer. Use this to tune the hsv threshold values for Doc's belt. Slide the save slider to the right when acceptable values have been determined.

Run the hsvJacketSettings.py file with a webcam equipped computer. Use this to tune the hsv threshold values for Doc's Jacket. Slide the save slider to the right when acceptable values have been determined.
