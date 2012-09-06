import cv2
import numpy
import sys
from pylab import setp
from matplotlib import pyplot
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib import cm
from flask import Flask, url_for, send_file, jsonify, request, make_response
from PIL import Image
import imtools
import traceback
import ast
from StringIO import StringIO

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

def any_response(data):
    response = make_response(data)
    origin = request.headers.get('Origin', '')
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

def writeImages(index, imageVars, scope):
    imagesList = []
    for name in imageVars:
        contents = scope[name]
        #print name, type(contents)
        filename = "run.%d.%s.jpg"%(index, name)
        if isinstance(contents, numpy.ndarray):
            image = Image.fromarray(saveWithAxes(contents))
            if len(contents.shape) == 2:
                image = image.convert("RGB")
            image.save(filename)
            imagesList.append(filename)
            continue
        if hasattr(contents, "thumbnail"):
            contents.save(filename)
            imagesList.append(filename)
            continue
    return imagesList

def getImageVars(module):
    imageVars = []
    for stmt in module.body:
        if type(stmt) == ast.Assign:
            if not hasattr(stmt.targets[0], "id"):
                continue
            name = stmt.targets[0].id
            if name in imageVars: imageVars.remove(name)
            # Don't display images with _ as first char.
            if name.find("_") == 0: continue
            imageVars.append(name)
    return imageVars

@app.route("/run")
def run():
    stdout = StringIO()
    script = request.args["script"]
    with open("script.py", "w") as f:
        f.write(script)
    images = script.split("\n")[0].split(",")
    script = "\n".join(script.split("\n")[1:])
    scope = {
        "numpy":numpy, "Image":Image, "cv2":cv2,
        "hue":hue, "hsv":hsv, "histeq":histeq,
        "inrange":inrange,
        "histogram":histogram,
        "invert":invert,
        "stdout":stdout
    }
    arrayType = type(numpy.array(1))
    imageType = type(Image.open("LightBall.jpg"))
    rows = []
    try:
        module = ast.parse(script)
        imageVars = getImageVars(module)
        index = 0
        for image in images:
            # May need to clear out scope between runs...
            fullScript = "im=Image.open(\"%s\")\n%s" %(
                    image, script)
            exec fullScript in scope
            imagesList = writeImages(index, imageVars, scope)
            rows.append(imagesList)
            index = index + 1
    except Exception, e:
        return make_response((traceback.format_exc(e), 500, None))
    return jsonify({"rows":rows,
                    "stdout":stdout.getvalue()})

@app.route("/get-script")
def getScript():
    return send_file("script.py")

@app.route("/image/<name>")
def image(name):
    #print "Returning image:", name
    return send_file(name, mimetype="image/jpeg")

@app.route("/grayscale/<name>/<id>")
def grayscale(name, id):
    #print "Converting image to grayscale:", name
    grayscaleName = "grayscale." + id + ".jpg"
    Image.open(name).convert('L').save(grayscaleName)
    return image(grayscaleName)

def hsv(img):
    hsvimg = cv2.cvtColor(img, cv2.cv.CV_RGB2HSV)
    return numpy.copy(hsvimg)

def hue(img):
    hsvimg = hsv(img)
    return numpy.copy(hsvimg[...,0])

def histeq(im,nbr_bins=256):
  """  Histogram equalization of a grayscale image. """
  # get image histogram
  imhist,bins = numpy.histogram(im.flatten(),
          nbr_bins,normed=True)
  cdf = imhist.cumsum() # cumulative distribution function
  cdf = 255 * cdf / cdf[-1] # normalize

  # use linear interpolation of cdf to find new pixel values
  im2 = numpy.interp(im.flatten(),bins[:-1],cdf)

  return im2.reshape(im.shape), cdf

def invert(im):
    # Apparently, this can also be done by "255 - im".
    im = cv2.bitwise_not(im);
    return im

def saveWithAxes(img):
    fig = Figure()
    axes = fig.add_subplot(111)
    axes.imshow(img, cmap=cm.Greys_r)
    canvas = FigureCanvas(fig)
    # TODO: Need to find a way to avoid this hack!
    canvas.print_jpg("run.img.tmp.jpg")
    return numpy.array(Image.open("run.img.tmp.jpg"))

def histogram(img):
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
    canvas = FigureCanvas(fig)
    canvas.print_jpg("run.hist.tmp.jpg")
    return Image.open("run.hist.tmp.jpg")

def inrange(im, rfrom, rto):
    im = cv2.inRange(im, numpy.array([rfrom]), numpy.array([rto]))
    return im

def threshold(im, rfrom, rto, type):
    (_, im) = cv2.threshold(im, rfrom, rto, cv2.THRESH_BINARY)
    return im

def denoise(im):
    (im, _) = imtools.denoise(im, im)
    # May need to convert to RGB
    return im

if __name__ == "__main__":
    app.run()
