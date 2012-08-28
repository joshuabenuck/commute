import cv2
import numpy
import sys
from pylab import setp
from matplotlib import pyplot
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from flask import Flask, url_for, send_file, jsonify
from PIL import Image
import imtools

"""
Next steps:
    - Add paramIndex and radio button support.
    - Move source images into different directory.
    - Put output images in directory based on session id.
    - Choose Image from source images.
    - Rerun stack when source image is changed.
    - Isolate color component: HSV and RGB.
    - Merge grayscale with isolate operation?
    - Histogram Equalization.
    - RGB Histogram
    - HSV Histogram
      * Fix Hue range. Should be 180 and not 300.
    - Blur
    X Change previous operation drop downs to read only.
    X Make it possible to remove the last result.
    X Allow a different source for an op.
    X Denoise
    - Create histogram widget.
      X Show range info
      X Show bigger image
      X Enable inverse
      * Create histogram stack
      * Apply histogram range to image
      * Show different types of histograms
    - Threshold an image
      X Show b/w thresholded result
      * Show color result
    - Ability to load multiple images.
      * May need to change drop down label to "source images".

Minor things:
    X Don't create duplicate thresholds
    X Clean up parameter panel
    X Fix default window size

Goal:
------------
| Load Images
------------
| Image 1 | Image 2 | Image 3 | Operation | Run | Show Result |
| Result 1 | Result 2 | Result 3 | Next Operation | Run |

im[i,:] = im[j,:]     # set the values of row i with values from row j
im[:,i] = 100         # set all values in column i to 100
im[:100,:50].sum()    # the sum of the values of the first 100 rows and 50 columns
im[50:100,50:100]     # rows 50-100, columns 50-100 (100th not included)
im[i].mean()          # average of row i
im[:,-1]              # last column
im[-2,:] (or im[-2])  # second to last row
------------

Operations:
    - Threshold, Blur, Expand, Collapse, Change color space, subtract, add
    - Compute variable, Histogram
"""

def html(body):
    print "<html><body>", body, "</body></html>"

app = Flask(__name__)
app.debug = True

@app.route("/")
def welcome():
    return "Hi!"

@app.route("/image/<name>")
def image(name):
    print "Returning image:", name
    return send_file(name, mimetype="image/jpeg")

@app.route("/grayscale/<name>/<id>")
def grayscale(name, id):
    print "Converting image to grayscale:", name
    grayscaleName = "grayscale." + id + ".jpg"
    Image.open(name).convert('L').save(grayscaleName)
    return image(grayscaleName)

@app.route("/hue/<name>/<id>")
def hue(name, id):
    hueName  = "hue." + id + ".jpg"
    img = numpy.array(Image.open(name))
    img = cv2.cvtColor(img, cv2.cv.CV_RGB2HSV)
    Image.fromarray(img[...,0]).save(hueName)
    return image(hueName)

@app.route("/invert/<name>/<id>")
def invert(name, id):
    print "Inverting image:", name
    invertName = "invert." + id + ".jpg"
    im = numpy.array(Image.open(name).convert('L'));
    # Apparently, this can also be done by "255 - im".
    im = cv2.bitwise_not(im);
    Image.fromarray(im).save(invertName);
    return image(invertName)

@app.route("/histogram/<name>/<id>")
def histogram(name, id):
    img = numpy.array(Image.open(name))
    fig = Figure()
    axes = fig.add_subplot(111)
    
    if len(img.shape) == 2 or img.shape[2:][0] == 1:
        axes.hist(img.flatten(), 300, color='blue', edgecolor='none')
    else:
        img = cv2.cvtColor(img, cv2.cv.CV_RGB2HSV)
        axes.hist([img[...,0], img[...,1], img[...,2]], 128, color=['red', 'green', 'blue'], edgecolor='none')
        axes.legend(('Hue', 'Saturation', 'Value'))
        #axes.legend(('Red', 'Green', 'Blue'))
    # If hsv, should look something like this.
    # axes.hist([img[...,0], img[...,1], img[...,2]], 300, color=['r','g','b'])
    axes.grid(True)
    setp(axes.get_yticklabels(), visible=False)
    filename = "histogram." + id + ".jpg"
    canvas = FigureCanvas(fig)
    canvas.print_figure(filename)
    return image(filename)

@app.route("/inrange/<name>/<id>/<int:rfrom>/<int:rto>")
def inrange(name, id, rfrom, rto):
    im = numpy.array(Image.open(name).convert('L'))
    im = cv2.inRange(im, numpy.array([rfrom]), numpy.array([rto]))
    thresholdName = "inrange." + id + ".jpg"
    Image.fromarray(im).save(thresholdName)
    return image(thresholdName)

@app.route("/threshold/<name>/<id>/<int:rfrom>/<int:rto>/<type>")
def threshold(name, id, rfrom, rto, type):
    im = numpy.array(Image.open(name).convert('L'))
    (_, im) = cv2.threshold(im, rfrom, rto, cv2.THRESH_BINARY)
    thresholdName = "threshold." + id + ".jpg"
    Image.fromarray(im).save(thresholdName)
    return image(thresholdName)

@app.route("/denoise/<name>/<id>")
def denoise(name, id):
    im = numpy.array(Image.open(name).convert('L'))
    (im, _) = imtools.denoise(im, im)
    denoiseName = "denoise." + id + ".jpg"
    Image.fromarray(im).convert("RGB").save(denoiseName)
    return image(denoiseName)

if __name__ == "__main__":
    app.run()
