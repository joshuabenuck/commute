from cv2 import *

capture = VideoCapture(0)
image = capture.read()
window = namedWindow("Test")
imshow("Test", image[1])
startWindowThread()
while 1:
    key = waitKey(100)
    if key == 27: break
    elif key == 32:
        del image
        image = capture.read()
        imshow("Test", image[1])
    elif key == 63234: # left
        pass
    elif key == 63235: # right
        pass
    elif key == 63232: # up
        pass
    elif key == 63233: # down
        pass
    elif key != -1:
        print int(key)
        
del image
del window
capture.release()

