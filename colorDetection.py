import cv2
import numpy as np
import time
from platform import system
from gpiozero import PWMLED, Button
import os

def nothing(a):
    pass

l_h, l_s, l_v = 0, 0, 230 # 0, 0, 0
u_h, u_s, u_v = 255, 255, 255 # 255, 255, 80

l_b = np.array([l_h, l_s, l_v])
u_b = np.array([u_h, u_s, u_v])

powerButton = Button(26, pull_up = True, bounce_time = None)
emergencyButton = None

redLed = PWMLED(25)
greenLed = PWMLED(24)
blueLed = PWMLED(23)

leftM = PWMLED(12)
rightM = PWMLED(13)

speed = 0.2
P = 1
centerPosition = 380

exposure = 15
minArea = 5000

displayWindows = 1

if system() == "Windows":
    linux = 0
else:
    linux = 1

print(linux)

cv2.namedWindow("Camera", cv2.WINDOW_AUTOSIZE)

if displayWindows:
    cv2.namedWindow("Value Editor")
    cv2.createTrackbar("Color", "Value Editor", 230, 255, nothing)
    cv2.createTrackbar("Exposure", "Value Editor", exposure, 400, nothing)
    cv2.createTrackbar("Min Area", "Value Editor", minArea, 30000, nothing)

if linux:
    capture = cv2.VideoCapture(0, cv2.CAP_V4L2)

    capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1) # Disable auto exposure
else:
    capture = cv2.VideoCapture(0)

    capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0) # Disable auto exposure

capture.set(cv2.CAP_PROP_AUTO_WB, 0) # Disable auto white balance
capture.set(cv2.CAP_PROP_EXPOSURE, exposure)

while True:
    #loopStartTime = time.time() * 1000

    if displayWindows:
        l_v = cv2.getTrackbarPos("Color", "Value Editor")
        l_b = np.array([l_h, l_s, l_v])
        exposure = cv2.getTrackbarPos("Exposure", "Value Editor")
        '''if not linux:
            exposure -= 8'''
        capture.set(cv2.CAP_PROP_EXPOSURE, exposure)
        minArea = cv2.getTrackbarPos("Min Area", "Value Editor")

    ret, frame = capture.read()

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, l_b, u_b)

    cnts, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if len(cnts) > 0:

        c = max(cnts, key = cv2.contourArea)

        if cv2.contourArea(c) > minArea:
            cv2.drawContours(frame, [c], -1, (255, 0, 0), 3)
            M = cv2.moments(c)
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            (x, y, w, h) = cv2.boundingRect(c)

            if displayWindows:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.circle(frame, (cx, cy), 7, (255, 255, 255), -1)
                cv2.putText(frame, f"{cx} {cy}", (cx - 20, cy - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            #print(f"{cx} {cy}")
            
            error = cx - centerPosition
            error = max(-centerPosition, min(centerPosition, error))
            error /= centerPosition
            errorP = P * error
            errorL = max(0, min(1, errorP))
            errorR = max(-1, min(0, errorP))
            print(f"{error}\t{errorL}\t{errorR}\t{(1 - errorL) * speed}\t{(1 + errorR) * speed}")

            leftM.value = (1 - errorL) * speed
            rightM.value = (1 + errorR) * speed

            '''
            if pos < 50 and pos > -50:
                print("F")
                leftM.value = 0.2
                rightM.value = 0.2
            elif pos < -50:
                print("L")
                leftM.value = 0.2
                rightM.value = 0.0
            else:
                print("R")
                leftM.value = 0.0
                rightM.value = 0.2'''

            redLed.off()
            greenLed.on()
            blueLed.off()
        else:
            print("No line")
            redLed.off()
            greenLed.off()
            blueLed.on()
            
            leftM.off()
            rightM.off()
    else:
        print("No line")
        redLed.off()
        greenLed.off()
        blueLed.on()
        
        leftM.off()
        rightM.off()

    if displayWindows:
        res = cv2.bitwise_and(frame, frame, mask = mask)
 
        cv2.imshow("Camera", frame)
        cv2.imshow("Mask", mask)
        cv2.imshow("Result", res)

    if powerButton.is_pressed:
        redLed.on()
        greenLed.off()
        blueLed.off()
        leftM.off()
        rightM.off()

        print("Power button pressed! Release to cancel shutdown")

        time.sleep(5)

        if powerButton.is_pressed:
            os.system("shutdown")
            break
        else:
            print("Power button released. Shutdown cancelled")

    if cv2.waitKey(5) == ord('q'):
        break

    #loopEndTime = time.time() * 1000
    #print(loopEndTime - loopStartTime)
    
    '''
    waitTime = 0

    if loopEndTime - loopStartTime < 50:
        waitTime = 50 - (loopEndTime - loopStartTime)
        time.sleep(waitTime / 1000)
    else:
        print(loopEndTime - loopStartTime)

    #print(str(loopEndTime - loopStartTime) + " " + str(waitTime))
    '''
    
capture.release()
cv2.destroyAllWindows()
