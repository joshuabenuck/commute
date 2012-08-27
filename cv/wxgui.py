import wx
import cv2
import numpy

"""
Next steps:
    - Show histogram for each image.
    - Create histogram widget.
    - Ability to load multiple images.

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
app = None
def setApp(thisapp):
    global app
    app=thisapp

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
    print img.shape
    if len(img.shape) == 2 or img.shape[2] == 1:
        img = cv2.cvtColor(img, cv2.cv.CV_GRAY2RGB)
    else:
        img = cv2.cvtColor(img, cv2.cv.CV_BGR2RGB)
    scale = 1
    h, w = img.shape[:2]
    if w > 1000:
        scale = 7
    wxbmp = wx.BitmapFromBuffer(w, h, img)
    return wx.BitmapFromImage(wx.ImageFromBitmap(wxbmp).Scale(w/scale, h/scale))

images = [
    # Image ImagePanel ControlPanel
]

def loadImage(path):
    img = cv2.imread(path)
    return convertImage(img)

def performOperation(img, name):
    print "Performing operation: %s"%(name)
    if name == "ToGray":
        result = cv2.cvtColor(img, cv2.cv.CV_BGR2GRAY)
        app.GetFrame().AddImagePanel(result)
        return
    if name == "Histogram":
        app.GetFrame().AddImagePanel(getHistogramImage(img))
        return

class HistogramParameters(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.Button(self, label="BlackAndWhite"))
        self.SetSizer(sizer)
        self.Fit()

class ControlPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize)
        self.ImagePanel = parent
        sizer = wx.GridBagSizer(wx.VERTICAL)
        self.sizer = sizer
        items = [
            "None", "Histogram", "ToGray", "ToBlackAndWhite", "Threshold"]
        #sizer.AddSpacer(5)
        sizer.Add(wx.StaticText(self, -1, "Operation:"), (1, 1))
        self.ops = wx.Choice(self, choices=items)
        sizer.Add(self.ops, (2, 1))
        #sizer.AddSpacer(5)
        self.run = wx.Button(self, label="+")
        self.paramPanel = None
        sizer.Add(self.run, (4, 1))
        self.Bind(wx.EVT_CHOICE, self.OnChoice, self.ops)
        self.Bind(wx.EVT_BUTTON, 
            lambda event: performOperation(self.ImagePanel.GetImage(),
                                     self.ops.GetStringSelection()), self.run)
        self.ops.SetSelection(0)
        self.SetSizer(sizer)

    def OnChoice(self, event):
        selection = self.ops.GetStringSelection()
        index = self.ops.GetSelection()
        if selection == "Histogram":
            self.paramPanel = HistogramParameters(self)
            self.sizer.Add(self.paramPanel, (3, 1))
            self.Layout()
        else:
            self.paramPanel.Destroy()
            self.Layout()
        print "Selected Item %d %s"%(index, selection)

class ImagePanel(wx.Panel):
    """
    This class displays an image along with all of the stats about the image
    such as resolution, color format, name, etc.
    """
    def __init__(self, parent, img, index):
        wx.Panel.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize)
        self.parent = parent
        self.index = index
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer = sizer
        self.img = img
        self.addImage(self.img)
        #self.addImage(getHistogramImage(self.img))
        sizer.Add(ControlPanel(self))
        self.SetBackgroundColour((255, 255, 255))
        self.SetSizer(sizer)

    def addImage(self, img):
        bmp = wx.StaticBitmap(self, bitmap=convertImage(img))
        self.sizer.Add(bmp)

    def GetImage(self):
        return self.img

class MyFrame(wx.Frame):
    def __init__(self, parent, id=wx.ID_ANY, title="",
        pos=wx.DefaultPosition, size=wx.DefaultSize,
        style=wx.DEFAULT_FRAME_STYLE,
        name="MyFrame"):
        super(MyFrame, self).__init__(parent, id, title,
            pos, size, style, name)
        # Attribute
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.AddImagePanel(cv2.imread("LightBall.jpg"))
        #sizer.AddSpacer(5);
        #sizer.Add(ImagePanel(self, "DarkBall.jpg"), 1, wx.EXPAND)
        self.SetBackgroundColour((0, 0, 0))
        self.SetSizerAndFit(self.sizer)

    def AddImagePanel(self, img):
        global images
        imagePanel = ImagePanel(self, img, len(images) - 1)
        images.append(imagePanel)
        self.sizer.Add(imagePanel, 1, wx.EXPAND)
        self.Fit()

class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, title="OpenCV Image Pipeline Editor")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        setApp(self)
        return True

    def GetFrame(self):
        return self.frame


if __name__ == "__main__":
    app = MyApp(False)
    app.MainLoop()
                
