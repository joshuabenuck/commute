im = numpy.array(Image.open("LightBall.jpg"))
gray = numpy.array(Image.fromarray(im).convert('L'))
invert = cv2.bitwise_not(gray)
h = hue(im)
histo = histogram(h)