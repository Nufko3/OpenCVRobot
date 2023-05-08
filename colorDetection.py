import cv2
import numpy as np
#import time

def nothing(a):
    pass

l_h, l_s, l_v = 0, 0, 230 # 0, 0, 0
u_h, u_s, u_v = 255, 255, 255 # 255, 255, 80

exposure = 40 #-9
minArea = 2000

displayWindows = 1

cv2.namedWindow("Camera", cv2.WINDOW_AUTOSIZE)

if displayWindows:
    cv2.namedWindow("Value Editor")
    cv2.createTrackbar("Color", "Value Editor", 230, 255, nothing)
    cv2.createTrackbar("Exposure", "Value Editor", 6, 30, nothing)
    cv2.createTrackbar("Min Area", "Value Editor", 2000, 3000, nothing)

capture = cv2.VideoCapture(1)

capture.set(cv2.CAP_PROP_AUTO_WB, 0.0) # Disable auto white balance
capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.0) # Disable auto exposure
capture.set(cv2.CAP_PROP_EXPOSURE, exposure)

while True:
    #loopStartTime = time.time() * 1000
    if displayWindows:
        l_v = cv2.getTrackbarPos("Color", "Value Editor")
        exposure = cv2.getTrackbarPos("Exposure", "Value Editor") - 15.0
        minArea = cv2.getTrackbarPos("Min Area", "Value Editor")
        #capture.set(cv2.CAP_PROP_EXPOSURE, exposure)
    
    ret, frame = capture.read()
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    l_b = np.array([l_h, l_s, l_v])
    u_b = np.array([u_h, u_s, u_v])
    
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
            print(f"{cx} {cy}")
    
    if displayWindows:
        res = cv2.bitwise_and(frame, frame, mask = mask)
 
        cv2.imshow("Camera", frame)
        cv2.imshow("Mask", mask)
        cv2.imshow("Result", res)
    
    if cv2.waitKey(5) == ord('q'):
        break

    '''
    loopEndTime = time.time() * 1000
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