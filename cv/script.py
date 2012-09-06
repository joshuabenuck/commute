Purple2.jpg,Purple3.jpg,LightBall.jpg,DarkBall.jpg,RedAndYellow.jpg,BlueAndPurple.jpg,FourBalls.jpg
im.thumbnail((500, 500), Image.ANTIALIAS)
ry = numpy.array(im)
gray = numpy.array(Image.fromarray(ry).convert('L'))
hist = histogram(gray)
#gray = hue(ry)
#(gray, _) = histeq(gray)
#sobelX = cv2.Sobel(gray,cv2.CV_8U, 1, 0, ksize=3, scale=0.4, delta=128)
#sobelY = cv2.Sobel(gray,cv2.CV_8U, 0, 1, ksize=3, scale=0.4, delta=128)

#cv::Sobel(image,sobelX,CV_16S,1,0);
#cv::Sobel(image,sobelY,CV_16S,0,1);
#sobelX = cv2.Sobel(gray, cv2.CV_16S, 1, 0)
#sobelY = cv2.Sobel(gray, cv2.CV_16S, 0, 1)

#sobel = numpy.abs(sobelX) + numpy.abs(sobelY)
#(sobelMin, sobelMax, _, _) = cv2.minMaxLoc(sobel)

#-alpha*sobel + 255
#sobel.convertTo(sobelImage,CV_8U,-255./sobmax,255);
#sobel = numpy.array(-255/sobelMax*sobel+255, dtype='uint8')
#cv::threshold(sobelImage, sobelThresholded, threshold, 255, cv::THRESH_BINARY);
#(_, sobelThresholded) = cv2.threshold(sobel, 245, 255, cv2.THRESH_BINARY)
# Need to introspect tuple assignments to get rid of the line below.
#sobelThresholded = sobelThresholded

# cv::Canny(image, contours, 125, 350);
canny = cv2.Canny(gray, 200, 400)

gray = cv2.GaussianBlur(gray, (5, 5), 1.5)
#sobelThresholded = cv2.GaussianBlur(sobelThresholded, (5, 5), 1.5)
#cv::HoughCircles(image, circles, CV_HOUGH_GRADIENT,
#2, // accumulator resolution (size of the image / 2)
#50, // minimum distance between two circles
#200, // Canny high threshold
#100, // minimum number of votes
#25, 100); // min and max radius

#stdout.writelines(sobelThresholded.shape.__str__())
#cv2.HoughCircles(image, method, dp, minDist[, circles[, param1[, param2[, minRadius[, maxRadius]]]]]) circles
#_circles = cv2.HoughCircles(sobel, cv2.cv.CV_HOUGH_GRADIENT, 2, 50, param1=200, param2=100, minRadius=50, maxRadius=100)
_circles2 = cv2.HoughCircles(gray, cv2.cv.CV_HOUGH_GRADIENT, 2, 50, param1=250, param2=100, minRadius=25, maxRadius=200)
#if _circles != None:
#  for circle in _circles[0]:
#    cv2.circle(ry, (circle[0], circle[1]), circle[2], (255), 5)
if _circles2 != None:
  for circle in _circles2[0]:
    cv2.circle(ry, (circle[0], circle[1]), circle[2], (0, 255, 0), 5)
    #stdout.write(circle[0] + " " + circle[1] + " " + circle[2] + "\n")
    #stdout.write(circle[0].__str__() + "\n")
