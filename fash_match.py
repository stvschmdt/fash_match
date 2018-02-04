# ----------------------------------------
# fash_match
#
# Created 2-3-2018
#
# Author: Steve Schmidt
# ----------------------------------------

import glob
import os
import wx
from wx.lib.pubsub import pub as Publisher
import csv
import sys


global lovelist
global hatelist
global love
global hate
########################################################################
class ViewerPanel(wx.Panel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        global dirname
        wx.Panel.__init__(self, parent)
        
        width, height = wx.DisplaySize()
        self.picPaths = glob.glob(dirname + '/' + "*.jpg")

        self.currentPicture = 0
        self.totalPictures = 0
        self.photoMaxSize = height - 200
        Publisher.subscribe(self.updateImages, ("update images"))
        #self.updateImages('')
        #self.slideTimer = wx.Timer(None)
        #self.slideTimer.Bind(wx.EVT_TIMER, self.update)
        
        self.layout()
        
    #----------------------------------------------------------------------
    def layout(self):
        """
        Layout the widgets on the panel
        """
        
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        img = wx.Image(self.photoMaxSize,self.photoMaxSize)
        self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, 
                                         wx.Bitmap(img))
        self.mainSizer.Add(self.imageCtrl, 0, wx.ALL|wx.CENTER, 5)
        self.imageLabel = wx.StaticText(self, label="")
        self.mainSizer.Add(self.imageLabel, 0, wx.ALL|wx.CENTER, 5)
        
        btnData = [("Not Me!", btnSizer, self.onPrevious), ("Love It!", btnSizer, self.onNext)]
        for data in btnData:
            label, sizer, handler = data
            self.btnBuilder(label, sizer, handler)
            
        self.mainSizer.Add(btnSizer, 0, wx.CENTER)
        self.SetSizer(self.mainSizer)
        self.updateImages('')
            
    #----------------------------------------------------------------------
    def btnBuilder(self, label, sizer, handler):
        """
        Builds a button, binds it to an event handler and adds it to a sizer
        """
        btn = wx.Button(self, label=label)
        btn.Bind(wx.EVT_BUTTON, handler)
        sizer.Add(btn, 0, wx.ALL|wx.CENTER, 5)
        
    #----------------------------------------------------------------------
    def loadImage(self, image):
        """"""
        image_name = os.path.basename(image)
        img = wx.Image(image, wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        W = img.GetWidth()
        H = img.GetHeight()
        if W > H:
            NewW = self.photoMaxSize
            NewH = self.photoMaxSize * H / W
        else:
            NewH = self.photoMaxSize
            NewW = self.photoMaxSize * W / H
        img = img.Scale(NewW,NewH)

        self.imageCtrl.SetBitmap(wx.Bitmap(img))
        self.imageLabel.SetLabel(image_name[:7])
        self.Refresh()
        
    #----------------------------------------------------------------------
    def nextPicture(self):
        """
        Loads the next picture in the directory
        """
        global love
        global lovelist
        lovelist.append(self.picPaths[self.currentPicture])
        love += 1
        if self.currentPicture == self.totalPictures-1:
            self.Close()
            #self.currentPicture = 0
        else:
            self.currentPicture += 1
        self.loadImage(self.picPaths[self.currentPicture])
        
    #----------------------------------------------------------------------
    def previousPicture(self):
        """
        Displays the previous picture in the directory
        """
        global hate
        global hatelist
        hatelist.append(self.picPaths[self.currentPicture])
        hate += 1
        if self.currentPicture == self.totalPictures-1:
            self.Close()
            #self.currentPicture = 0
        else:
            self.currentPicture += 1
        #if self.currentPicture == 0:
            #self.currentPicture = self.totalPictures - 1
        #else:
            #self.currentPicture -= 1
        self.loadImage(self.picPaths[self.currentPicture])
        
    #----------------------------------------------------------------------
    def update(self, event):
        """
        Called when the slideTimer's timer event fires. Loads the next
        picture from the folder by calling th nextPicture method
        """
        self.nextPicture()
        
    #----------------------------------------------------------------------
    def updateImages(self, msg):
        """
        Updates the picPaths list to contain the current folder's images
        """
        global dirname
        self.picPaths = glob.glob(dirname + '/' + "*.jpg")
        self.totalPictures = len(self.picPaths)
        self.loadImage(self.picPaths[0])
        
    #----------------------------------------------------------------------
    def onNext(self, event):
        """
        Calls the nextPicture method
        """
        self.nextPicture()
    
    #----------------------------------------------------------------------
    def onPrevious(self, event):
        """
        Calls the previousPicture method
        """
        self.previousPicture()
    
    #----------------------------------------------------------------------
    def onSlideShow(self, event):
        """
        Starts and stops the slideshow
        """
        btn = event.GetEventObject()
        label = btn.GetLabel()
        if label == "Slide Show":
            self.slideTimer.Start(3000)
            btn.SetLabel("Stop")
        else:
            self.slideTimer.Stop()
            btn.SetLabel("Slide Show")
        
       
########################################################################
class ViewerFrame(wx.Frame):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        global dirname
        wx.Frame.__init__(self, None, title="Fash Match")
        panel = ViewerPanel(self)
        self.folderPath = dirname + "/"
        Publisher.subscribe(self.resizeFrame, ("resize"))
        
        self.initToolbar()
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Show()
        self.sizer.Fit(self)
        self.Center()
        
        
    #----------------------------------------------------------------------
    def initToolbar(self):
        """
        Initialize the toolbar
        """
        self.toolbar = self.CreateToolBar()
        self.toolbar.SetToolBitmapSize((16,16))

        #open_ico = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, (16,16))
        #openTool = self.toolbar.AddTool(wx.ID_ANY, open_ico, "Open", "Open an Image Directory")
        #self.Bind(wx.EVT_MENU, self.onOpenDirectory, openTool)

        self.toolbar.Realize()
        #self.toolbar = self.CreateToolBar()
        #self.toolbar.SetToolBitmapSize((16,16))
        self.toolbar.Realize()
        
    #----------------------------------------------------------------------
    def onOpenDirectory(self, event):
        """
        Opens a DirDialog to allow the user to open a folder with pictures
        """
        self.folderPath = 'images/'
        picPaths = glob.glob(self.folderPath + "*.jpg")
        
        Publisher.sendMessage('updateImages')
        
    #----------------------------------------------------------------------
    def resizeFrame(self, msg):
        """"""
        self.sizer.Fit(self)
        
#----------------------------------------------------------------------

def write_list(data, num, filename):
    with open(filename, 'wb') as f:
        writer = csv.writer(f)
        writer.writerow([num])
        for d in data:
            writer.writerow([d])



if __name__ == "__main__":
    global hate
    global love
    global lovelist
    global hatelist
    global dirname
    if len(sys.argv) > 1:
        dirname = sys.argv[1]
    else:
        dirname = 'fashion'
    love = 0
    hate = 0
    lovelist = []
    hatelist = []
    app = wx.App()
    frame = ViewerFrame()
    app.MainLoop()
    write_list(lovelist, str(len(lovelist)), 'loves.txt')
    write_list(hatelist, str(len(hatelist)), 'hates.txt')
    
