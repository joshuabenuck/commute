from opencv.cv import *
from opencv.highgui import *
import time
import sys

counter = 0
size = None
def initCamera():
	global size
	camera = cvCreateCameraCapture(1)
	if not camera:
		print "Could not open webcam!"
		sys.ext(1)
	cvSetCaptureProperty(camera, CV_CAP_PROP_FRAME_WIDTH, 320)
	cvSetCaptureProperty(camera, CV_CAP_PROP_FRAME_HEIGHT, 240)
	frame = cvQueryFrame(camera)
	if frame is not None:
		w = frame.width
		h = frame.height
		print "%d %d"%(w, h)
		size = cvSize(w, h)
	time.sleep(1)
	return camera

def readFrom(filename):
	global size
	camera = cvCreateFileCapture(filename)
	if not camera:
		print "Could not open file!"
		sys.ext(1)
	cvSetCaptureProperty(camera, CV_CAP_PROP_FRAME_WIDTH, 320)
	cvSetCaptureProperty(camera, CV_CAP_PROP_FRAME_HEIGHT, 240)
	frame = cvQueryFrame(camera)
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
cvNamedWindow("Modified", CV_WINDOW_AUTOSIZE)
cvMoveWindow("Modified", 300, 100)
#camera = initCamera()
camera = readFrom("test1.avi")
hsvImage = cvCreateImage(size, IPL_DEPTH_8U, 3)
output = cvCreateImage(size, IPL_DEPTH_8U, 1)
output2 = cvCreateImage(size, IPL_DEPTH_8U, 1)
minH = cvCreateTrackbar("Min H", "Modified",   0, 255, lambda x: 1)
maxH = cvCreateTrackbar("Max H", "Modified",  43, 255, lambda x: 1)
minS = cvCreateTrackbar("Min S", "Modified",  49, 255, lambda x: 1)
maxS = cvCreateTrackbar("Max S", "Modified", 134, 255, lambda x: 1)
minV = cvCreateTrackbar("Min V", "Modified", 149, 255, lambda x: 1)
maxV = cvCreateTrackbar("Max V", "Modified", 255, 255, lambda x: 1)
#minH = cvCreateTrackbar("Min H", "Modified",   5, 255, lambda x: 1)
#maxH = cvCreateTrackbar("Max H", "Modified",  27, 255, lambda x: 1)
#minS = cvCreateTrackbar("Min S", "Modified", 135, 255, lambda x: 1)
#maxS = cvCreateTrackbar("Max S", "Modified", 255, 255, lambda x: 1)
#minV = cvCreateTrackbar("Min V", "Modified", 103, 255, lambda x: 1)
#maxV = cvCreateTrackbar("Max V", "Modified", 255, 255, lambda x: 1)
storage = cvCreateMemStorage(0)
while 1:
	#print time.asctime()
	image = captureImage(camera)
	cvCvtColor(image, hsvImage, CV_BGR2HSV)
	hsvMin = cvScalar(
		cvGetTrackbarPos("Min H", "Modified"),
		cvGetTrackbarPos("Min S", "Modified"),
		cvGetTrackbarPos("Min V", "Modified"), 0)
	hsvMax = cvScalar(
		cvGetTrackbarPos("Max H", "Modified"), 
		cvGetTrackbarPos("Max S", "Modified"), 
		cvGetTrackbarPos("Max V", "Modified"), 255)
	cvInRangeS(hsvImage, hsvMin, hsvMax, output)
	cvSmooth(output, output2, CV_GAUSSIAN, 3, 3)
	cvErode(output, output2)
	circles = cvHoughCircles(output, storage, CV_HOUGH_GRADIENT, 1, 
		output.height / 2, 100, 20, 1, 900)
	for i in range(circles.total):
		circle = circles[i]
		#print circle[2]
		cvCircle(image, cvPoint(
			cvRound(circle[0]), cvRound(circle[1])),
			cvRound(circle[2]), cvScalar(0, 255, 0), -1, 8, 0)
		cvCircle(output, cvPoint(
			cvRound(circle[0]), cvRound(circle[1])),
			cvRound(circle[2]), cvScalar(0, 255, 0), 1, 8, 0)
	cvShowImage("Original", image)
	cvShowImage("Modified", output)
	cvWaitKey(125)
	#hsv_frame = cvCreateImage(size, IPL_DEPTH_8U, 3)
	#cvSmooth(image, hsv_frame, CV_GAUSSIAN, 3, 3)
	#cvSaveImage("smoothed.jpg", hsv_frame)
