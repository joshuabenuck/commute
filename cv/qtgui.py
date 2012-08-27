import cv2
import numpy
import sys
from PyQt4 import QtGui, QtCore
from matplotlib import pyplot
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

"""
Next steps:
    - Create histogram widget.
      * Show range info
      * Show bigger image
      * Enable inverse
      * Create histogram stack
      * Apply histogram range to image
      * Show different types of histograms
    - Threshold an image
      * Show b/w thresholded result
      * Show color result
    - Ability to load multiple images.

Minor things:
    - Don't create duplicate thresholds
    - Clean up parameter panel
    - Fix default window size

Goal:
------------
| Load Images
------------
| Image 1 | Image 2 | Image 3 | Operation | Run | Show Result |
| Result 1 | Result 2 | Result 3 | Next Operation | Run |
------------

Operations:
    - Threshold, Blur, Expand, Collapse, Change color space, subtract, add
    - Compute variable, Histogram
"""

class MplCanvas(FigureCanvas):
    def __init__(self, img):
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        self.axes.hist(img.flatten(), 256)
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self,
                QtGui.QSizePolicy.Expanding,
                QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.setMinimumSize(300, 300)

def getHistogram(img):
    histSize = [256]
    hranges = [0.0, 255.0]
    ranges = hranges
    channels = [0]
    mask = numpy.ones(1).astype('uint8')
    return cv2.calcHist([img.astype('uint8')], channels, 
             None, histSize, ranges)

def getHistogramImage(img):
    hist = getHistogram(img)
    (minVal, maxVal, _, _) = cv2.minMaxLoc(hist)
    histImg = numpy.zeros((256, 256, 1), numpy.uint8)
    hpt = 0.9 * 256
    for h in range(0,256):
        binVal = hist[h]
        intensity = binVal * hpt / maxVal
        cv2.line(histImg, (h, 256), (h, 256 - intensity), 255)
    return histImg

def convertImage(img):
    if len(img.shape) == 2 or img.shape[2] == 1:
        img = cv2.cvtColor(img, cv2.cv.CV_GRAY2RGB)
    else:
        img = cv2.cvtColor(img, cv2.cv.CV_BGR2RGB)
    scale = 1
    h, w = img.shape[:2]
    if w > 1000:
        scale = 7
    qimg = QtGui.QImage(img.data, w, h, QtGui.QImage.Format_RGB888)
    qimg = qimg.scaled(w/scale, h/scale)
    qpix = QtGui.QPixmap.fromImage(qimg)
    qlabel = QtGui.QLabel()
    qlabel.setPixmap(qpix)
    return qlabel

images = []
class MainWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent=parent)
        self.layout = QtGui.QVBoxLayout()
        windowWidget = QtGui.QWidget()
        windowWidget.setLayout(self.layout)

        scroll = QtGui.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(windowWidget)

        windowLayout = QtGui.QVBoxLayout()
        windowLayout.addWidget(scroll)

        img = cv2.imread("LightBall.jpg")
        self.addImagePanel(img)
        self.setWindowTitle("OpenCV Image Pipeline Editor")
        self.setLayout(windowLayout)

    def addMainPanel(self, widget):
        row = QtGui.QHBoxLayout()
        row.addWidget(widget)
        self.addControlPanel(row, images[:1][0])
        self.layout.addLayout(row)

    def addImagePanel(self, img):
        global images
        images.append(img)
        self.addMainPanel(convertImage(img))

    def addControlPanel(self, row, img):
        paramPanel = QtGui.QVBoxLayout()
        items = [
            "None", "Histogram", "ToGray", "ToBlackAndWhite", "Threshold"]
        paramPanel.addWidget(QtGui.QLabel(text="Operation:"),
                alignment=QtCore.Qt.AlignTop)
        ops = QtGui.QComboBox()
        ops.addItems(items)
        ops.currentIndexChanged['QString'].connect(self.onChange)
        paramPanel.addWidget(ops)
        self.run = QtGui.QPushButton(text="+",
            clicked=lambda event: self.performOperation(img, ops.currentText()))
                                     
        paramPanel.addWidget(self.run)
        row.addLayout(paramPanel)

    def performOperation(self, img, name):
        print "Performing operation: %s"%(name)
        if name == "ToGray":
            result = cv2.cvtColor(img, cv2.cv.CV_BGR2GRAY)
            self.addImagePanel(result)
            return
        if name == "Histogram":
            self.addMainPanel(MplCanvas(img))
            return

    def onChange(self, selection):
        if selection == "Histogram":
            pass
        else:
            pass
        print "Selected Item %s"%(selection)

if __name__ == "__main__":
    app = QtGui.QApplication([])
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
