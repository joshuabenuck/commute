from cv import *

capture = CaptureFromCAM(0)
GrabFrame(capture)
image = RetrieveFrame(capture)
window = NamedWindow("Test")
ShowImage("Test", image)
StartWindowThread()
while 1:
    key = WaitKey(100)
    if key == 27: break
    if key == 32:
        del image
        GrabFrame(capture)
        image = RetrieveFrame(capture)
        ShowImage("Test", image)
del image
del window
del capture
