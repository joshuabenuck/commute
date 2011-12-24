from opencv.cv import *
from opencv.highgui import *
import time
import sys

counter = 0
size = None
fps = 6
def initCamera():
	global size
	global fps
	camera = cvCreateCameraCapture(1)
	if not camera:
		print "Could not open webcam!"
		sys.exit(1)
	cvSetCaptureProperty(camera, CV_CAP_PROP_FRAME_WIDTH, 320)
	cvSetCaptureProperty(camera, CV_CAP_PROP_FRAME_HEIGHT, 240)
	frame = cvQueryFrame(camera)
	#fps = cvGetCaptureProperty(camera, CV_CAP_PROP_FPS)
	if frame is not None:
		w = frame.width
		h = frame.height
		print "%d %d"%(w, h)
		size = cvSize(w, h)
	time.sleep(1)
	return camera

def captureImage(camera):
	global counter
	frame = cvQueryFrame(camera)
	cvSaveImage("images/test%d.jpg"%counter, frame)
	counter+=1
	if counter >= 1000: counter = 0
	if not frame:
		print "Couldn't grab frame."
		sys.exit(1)
	return frame

cvNamedWindow("Original", CV_WINDOW_AUTOSIZE)
cvMoveWindow("Original", 100, 100)
camera = initCamera()
writer = cvCreateVideoWriter("test.avi", CV_FOURCC('M','J','P','G'), fps, size)
while 1:
	#print time.asctime()
	image = captureImage(camera)
	#cvCvtColor(image, hsvImage, CV_BGR2HSV)
	cvShowImage("Original", image)
	cvWriteFrame(writer, image)
	cvWaitKey(33)
