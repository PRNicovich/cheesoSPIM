# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 14:20:06 2022

Lightweight video recorder using an arbitrary, Python-driven camera
GUI has window for acquired images
    buttons for live, record, snap, options
    Snap - take an image and prompt to save
    Live - stream images from camera as fast as possible
    Record - Live, but also stream to disk
    Options - set Record save path, exposure and gain options
    


@author: rusty
"""

import tkinter as tk
from tkinter import ttk, filedialog

import time
from cheesoSPIM_gui.utilities import cv2Camera as cam

from cheesoSPIM_gui.utilities.cheesoSPIMDriver import cheesoSPIM_driver as scopeController

from PIL import Image, ImageTk
from cv2 import medianBlur, VideoWriter_fourcc, VideoWriter, imwrite

import pathlib
import serial
import multiprocessing


scopePort = 'COM3'
cameraID = 0



def writeVideo(queue, paramDict):
    """
    Video write method
    Separate method to support multiprocessing
    
    Arguments:
        - queue = queue.Queue() or equivalent
                    Queue to pull frames from
        - paramDict = dict with keys = values:
                    'fileName' - str, file path of output
                    'frameRate' - float, frame rate of camera
                    'size' - tuple of ints, height x width
    """
    fourcc = VideoWriter_fourcc('M','J','P','G')    # Init format
    # Init openCV VideoWriter object
    videoObject = VideoWriter(str(paramDict['fileName']), 
                              fourcc,
                              paramDict['frameRate'],
                              paramDict['size'])

    while (True):
        # Pull last frame out of queue
        item = queue.get()

        if item is None: # Return from closed queue
            break # Get out of while loop
        else:
            # item returned.  Write to file.
            videoObject.write(item)
        
    # Executed after break call
    # Close videoObject file
    while videoObject.isOpened():
        videoObject.release()

    return



class vidRecorder:

    """
    Main GUI class
    """
    
    def __init__(self, parent):
        """
        Class initiator method
        Requires:
            parent - tkinter.Tk() object
        """
        self.parent = parent # Init w/ supplied parent object
        
        self.demoMode = False # True will skip camera start up
        
        
        # Start up 'scope connection
        if not(self.demoMode):
            self.serial = serial.Serial(scopePort, baudrate = 115200)
            time.sleep(2)
            self.scope = scopeController(self.serial)
        
        
        
        
        
        # Exposed options
        self.cameraParameters = {"autoExposure" : False, # Use camera autoexposure or no
                                 "autoGain" : True, # Use camera autogain or use supplied value
                                 "exposureTime" : 50, # milliseconds
                                 "gainValue" : 24, # dB, minGain to maxGain valid
                                 "maxExposure" : 2000, # milliseconds
                                 "minExposure" : 0.1, # milliseconds
                                 "minGain" : 0, # dB, 0 is min from AlliedVision camera
                                 "maxGain" : 24, # dB, 24 is max for AlliedVision camera
                                 "medianFilterSize" : 3, # pixels, must be odd
                                 "binning" : 2, # Pixel binning; 2 improves speed w/o much res loss
                                 "cropROI" : False, # Use full chip or no
                                 "laserPower" : 128, 
                                 "lensPosition" : 10, 
                                 "spin_bigStep" : 100, 
                                 "spin_smallStep" : 5,
                                 "lens_bigStep" : 100,
                                 "lens_smallStep" : 10} 
        # ^ Min/max values are specified here as hard-coded.  Could use a query instead if 
        # concerned values coded here are not OK for your camera
        
        self.parent.protocol("WM_DELETE_WINDOW",  self.haltAll) # If you close main window, shut it all down
        
        self.pathForSaving = pathlib.Path(__file__).parent.parent.parent / 'vids' # Init video record path
        self.iconsPath = pathlib.Path(__file__).parent / 'icons' # Init local icons path
        
        self.saveFileName = None # Init file name
        
        # Option flags 
        # Not exposed in GUI
        self.newImgOnSnap = True # Take image when 'Snap' button pressed
        self.saveOnSnap = True # Prompt to save file w/ Snap

        self.verbose = False # Print statements flag
        
        self.rawFrame = None # Init placeholder for most recent frame
        self.saveQueue = multiprocessing.Queue(maxsize = 100) # Init queue for files to save w/ multiprocessing thread

        self.isRecording = False # flag for live (False) vs record (True) stream
        
        self.parent.geometry("900x600") # Window size
        self.parent.title('Surgery recorder') # Window title

        # Start setting up GUI elements
        self.imgFrame = tk.Frame(self.parent, height = 486, width = 648) # Main window
        
        self.imgCanvas = tk.Canvas(self.imgFrame)    # Canvas for images
        self.imgCanvas.pack(fill = tk.BOTH, expand = tk.YES, anchor = tk.CENTER)
        self.img = tk.PhotoImage(file=str(self.iconsPath / "logo.png")) # Init image for canvas     
        self.label = tk.Label(self.imgCanvas, image = self.img, width = 648, height = 486) # Label goes in canvas
        self.label.pack(fill = tk.BOTH, expand = tk.YES, anchor = tk.CENTER)

        self.scopeFrame = tk.Frame(self.parent, height = 486, width = 200, relief = 'raised', borderwidth = 1)
        
        self.fillInScopeFrame()


        # Load icons from disk in self.iconsPath folder. 
        self.optIcon = tk.PhotoImage(file = str(self.iconsPath / "settings.png"))
        self.liveIcon = tk.PhotoImage(file = str(self.iconsPath / "play.png"))
        self.snapIcon = tk.PhotoImage(file = str(self.iconsPath / "snap.png"))
        self.rcdIcon = tk.PhotoImage(file = str(self.iconsPath / "record.png"))

        # scale icons to right size
        self.optIcon = self.optIcon.subsample(15, 15)
        self.liveIcon = self.liveIcon.subsample(15, 15)
        self.snapIcon = self.snapIcon.subsample(15, 15)
        self.rcdIcon = self.rcdIcon.subsample(15, 15)

        # Buttons frame at bottom of parent window
        self.frm = tk.Frame(self.parent, height = 100, width = 800, relief = tk.RAISED, borderwidth = 1)
        
        # Pack frames. Order matters.
        self.scopeFrame.pack(side = tk.RIGHT, fill = tk.BOTH, expand = True)
        self.frm.pack(side = tk.BOTTOM, fill = "x")
        self.imgFrame.pack(side = tk.TOP, fill = tk.BOTH, expand = True)
        
        
        
        # Options button
        self.optionsButton = tk.Button(self.frm, image = self.optIcon, command = self.doOptions)

        # Live button
        self.liveButton = tk.Button(self.frm, image = self.liveIcon)
        self.liveButtonState = False
        self.liveButton.config(command = lambda button = self.liveButton: self.doLive(button))

        # Record button
        self.recButton = tk.Button(self.frm, image = self.rcdIcon)
        self.recButtonState = False
        self.recButton.config(command = lambda button = self.recButton: self.doRecord(button))
        
        # Snap button
        self.snapButton = tk.Button(self.frm, image = self.snapIcon, command = self.doSnap)

        # Object to hold camera ID string in buttons frame
        self.camIDLabel = tk.Label(self.frm, text = "No camera detected")

        # Pack buttons in frame
        self.optionsButton.pack(side = tk.LEFT)
        self.recButton.pack(side = tk.RIGHT, ipadx = 10)
        self.snapButton.pack(side = tk.RIGHT, ipadx = 10)
        self.liveButton.pack(side = tk.RIGHT, ipadx = 10)

        self.camIDLabel.pack(side = tk.BOTTOM)
        

        """
        Launch camera
        """
        
        if not(self.demoMode): # If self.demoMode = True, then don't try to launch camera
        
            # Alias camera            
            self.camera = cam.camera()
            # Set camIDLabel string to show connected camera name + ID
            self.camIDstring = "{} - {}".format(self.camera.camName, self.camera.camID) # sprintf camera ID 
            self.camIDLabel['text'] = self.camIDstring
            
            # Method to set camera parameters from cameraParameters dict 
            self.camera.setParameters(self.cameraParameters)
            
            # Zero lens
            self.scope.lensAllIn()
            self.cameraParameters['lensPosition'] = 0

        # Init flag as False
        self.cameraAcquiring = False

        return # __init__
    
    
    def fillInScopeFrame(self):
        # Do all the work to add options in the scope frame in GUI
        
        # Exposure value set
        self.expValueFromBox = tk.StringVar(self.scopeFrame)
        self.expValueFromBox.set("{}".format(self.cameraParameters['exposureTime']))
        self.expValueBox = ttk.Entry(self.scopeFrame, 
                                   width = 10,
                                   textvariable = self.expValueFromBox)
        self.expValueBox.bind('<Key-Return>', self.expValueBoxAction) # Do action on 'Return' button w/ cursor here
        self.expValueBox.place(x = 160, y = 12)
        # Text label for exposure time
        self.expValueText = tk.Label(self.scopeFrame, text = "Exposure time (ms) :")
        self.expValueText.place(x = 12, y = 12)
        
        # Laser power set
        self.laserPowerFromBox = tk.StringVar(self.scopeFrame)
        self.laserPowerFromBox.set("{}".format(self.cameraParameters['laserPower']))
        self.laserPowerValueBox = ttk.Entry(self.scopeFrame, 
                                   width = 10,
                                   textvariable = self.laserPowerFromBox)
        self.laserPowerValueBox.bind('<Key-Return>', self.laserPowerAction) # Do action on 'Return' button w/ cursor here
        self.laserPowerValueBox.place(x = 160, y = 152)
        # Text label for laser power
        self.laserPowerText = tk.Label(self.scopeFrame, text = "Laser power :")
        self.laserPowerText.place(x = 12, y = 152)
        
        # Lens in out buttons
        # Load icons from disk in self.iconsPath folder. 
        self.outFastIcon = tk.PhotoImage(file = str(self.iconsPath / "ff_icon_R.png"))
        self.outSlowIcon = tk.PhotoImage(file = str(self.iconsPath / "fwd_icon_L.png"))
        self.inSlowIcon = tk.PhotoImage(file = str(self.iconsPath / "fwd_icon_R.png"))
        self.inFastIcon = tk.PhotoImage(file = str(self.iconsPath / "ff_icon_L.png"))

        # scale icons to right size
        self.outFastIcon = self.outFastIcon.subsample(15, 15)
        self.outSlowIcon = self.outSlowIcon.subsample(15, 15)
        self.inSlowIcon = self.inSlowIcon.subsample(15, 15)
        self.inFastIcon = self.inFastIcon.subsample(15, 15)
        
        # Rotation buttons
        self.outFastButton = tk.Button(self.scopeFrame, image = self.outFastIcon)
        self.outFastButton.config(command = lambda button = 'inFast': self.lensPushButton(button))
        
        self.outSlowButton = tk.Button(self.scopeFrame, image = self.outSlowIcon)
        self.outSlowButton.config(command = lambda button = 'inSlow': self.lensPushButton(button))
        
        self.inSlowButton = tk.Button(self.scopeFrame, image = self.inSlowIcon)
        self.inSlowButton.config(command = lambda button = 'outSlow': self.lensPushButton(button))
        
        self.inFastButton = tk.Button(self.scopeFrame, image = self.inFastIcon)
        self.inFastButton.config(command = lambda button = 'outFast': self.lensPushButton(button))
        
        self.outFastButton.place(x = 8, y = 330)
        self.outSlowButton.place(x = 53, y = 330)
        self.inSlowButton.place(x = 153, y = 330)
        self.inFastButton.place(x = 198, y = 330)
        
        self.lensText = tk.Label(self.scopeFrame, text = "-- Lens --")
        self.lensText.place(x = 98, y = 340)
        
        self.lensPositionText = tk.Label(self.scopeFrame, text = 'Lens @ {}'.format(self.cameraParameters['lensPosition']))
        self.lensPositionText.place(x = 98, y = 300)
        
        # rotation buttons
        # Load icons from disk in self.iconsPath folder. 
        self.leftFastIcon = tk.PhotoImage(file = str(self.iconsPath / "ff_icon_R.png"))
        self.leftSlowIcon = tk.PhotoImage(file = str(self.iconsPath / "fwd_icon_L.png"))
        self.rightSlowIcon = tk.PhotoImage(file = str(self.iconsPath / "fwd_icon_R.png"))
        self.rightFastIcon = tk.PhotoImage(file = str(self.iconsPath / "ff_icon_L.png"))

        # scale icons to right size
        self.leftFastIcon = self.leftFastIcon.subsample(15, 15)
        self.leftSlowIcon = self.leftSlowIcon.subsample(15, 15)
        self.rightSlowIcon = self.rightSlowIcon.subsample(15, 15)
        self.rightFastIcon = self.rightFastIcon.subsample(15, 15)
        
        
        
        # Rotation buttons
        self.leftFastButton = tk.Button(self.scopeFrame, image = self.leftFastIcon)
        self.leftFastButton.config(command = lambda button = 'leftFast': self.rotateButtonPush(button))
        
        self.leftSlowButton = tk.Button(self.scopeFrame, image = self.leftSlowIcon)
        self.leftSlowButton.config(command = lambda button = 'leftSlow': self.rotateButtonPush(button))
        
        self.rightSlowButton = tk.Button(self.scopeFrame, image = self.rightSlowIcon)
        self.rightSlowButton.config(command = lambda button = 'rightSlow': self.rotateButtonPush(button))
        
        self.rightFastButton = tk.Button(self.scopeFrame, image = self.rightFastIcon)
        self.rightFastButton.config(command = lambda button = 'rightFast': self.rotateButtonPush(button))
        
        self.leftFastButton.place(x = 8, y = 430)
        self.leftSlowButton.place(x = 53, y = 430)
        self.rightSlowButton.place(x = 153, y = 430)
        self.rightFastButton.place(x = 198, y = 430)
        
        self.rotateText = tk.Label(self.scopeFrame, text = "-- Spin --")
        self.rotateText.place(x = 98, y = 440)
        
        
        return
        
    
    def expValueBoxAction(self, val):
        """
        Action on 'return' button press in gain value box
        Check that input value is between minGain and maxGain
        If yes, reset to nearest bound
        
        If value is invalid (non-numeric) then reset to previous value
        """
        boxString = self.expValueFromBox.get() # String in text box
        
        try:
            boxVal = float(boxString) # attempt to convert to float
            reset = False # Init reset need

            if (boxVal > self.cameraParameters['maxExposure']): # input above max value
                
                boxVal = self.cameraParameters['maxExposure'] # input now = max value
                reset = True # going to reset
                
            elif (boxVal < self.cameraParameters['minExposure']): # input below min value
                
                boxVal = self.cameraParameters['minExposure'] # input now = min value
                reset = True # going to reset
            
        except ValueError:  # Above failed - probably can't convert string to float 'cause non-numeric input
            reset = True # going to reset
            boxVal = self.cameraParameters['exposureTime'] # Value stays as old value
            
        if reset:
            self.expValueFromBox.set(str(boxVal)) # If reset, set box value back to (reset) temp value
            
        if self.verbose:
            # Print statement for exposure value change
            print("expValue changed to : {}".format(boxVal))

        return
    
    def laserPowerAction(self):
        return
    
    def rotateButtonPush(self, button):
        if (button == 'leftFast'):
            self.scope.spinMotor(self.cameraParameters['spin_bigStep'])
            
        elif (button == 'leftSlow'):
            self.scope.spinMotor(self.cameraParameters['spin_smallStep'])
            
        elif (button == 'rightSlow'):
            self.scope.spinMotor(-self.cameraParameters['spin_smallStep'])    
            
        elif (button == 'rightFast'):
            self.scope.spinMotor(-self.cameraParameters['spin_bigStep'])
        
        return
    
    def lensPushButton(self, button):   
        if (button == 'outFast'):
            self.scope.setFocus(int(self.cameraParameters['lens_bigStep']))
            self.cameraParameters['lensPosition'] += self.cameraParameters['lens_bigStep']
            
        elif (button == 'outSlow'):
            self.scope.setFocus(int(self.cameraParameters['lens_smallStep']))
            self.cameraParameters['lensPosition'] += self.cameraParameters['lens_smallStep']
            
        elif (button == 'inSlow'):
            self.scope.setFocus(int(-self.cameraParameters['lens_smallStep']))
            self.cameraParameters['lensPosition'] += -self.cameraParameters['lens_smallStep']
            
        elif (button == 'inFast'):
            self.scope.setFocus(int(-self.cameraParameters['lens_bigStep']))
            self.cameraParameters['lensPosition'] += -self.cameraParameters['lens_bigStep']
        
        return
        return
    
    def haltAll(self):
        """
        Stop stream and destroy main window
        
        Called if main window closes.  Otherwise camera could continue to stream after GUI is 'closed'
        """
        if self.cameraAcquiring:
            self.stopStream() # Local stopStream method to close out acqusition
            
        if hasattr(self, 'serial'):
            self.serial.close()
            
        self.parent.destroy() # Close main window
        
        return
    
    def doOptions(self):   
        """
        Launch GUI window for recording acquisition options:
            - Save path for recorded movies
            - Exposure auto + time
            - Gain auto + values
            
        Be sure to hit 'SAVE' on exit to write settings. 
        Otherwise 'CANCEL' will not record inputs
        """
        # Launch options page
        self.optWindow = tk.Tk()
        self.optWindow.geometry("400x300")
        self.optWindow.title("Settings")
        
        # Option window frame
        self.optWinfrm = tk.Frame(self.optWindow, height = 50, width = 400, relief = tk.RAISED, borderwidth = 0)
        self.optWinfrm.pack(side = tk.BOTTOM, fill = "x")
        # Save button
        self.saveOptions = ttk.Button(self.optWinfrm, text = 'Save', command = self.saveSettings)
        self.saveOptions.pack(side = tk.RIGHT)
        
        # Cancel button
        self.saveOptions = ttk.Button(self.optWinfrm, text = 'Cancel', command = self.cancelSettings)
        self.saveOptions.pack(side = tk.LEFT)
        
        # Set path button
        self.pathButton = ttk.Button(self.optWindow, text = "Set save path", command = self.savePath)
        self.pathButton.place(x = 10, y = 30)
        
        # Text box for path button
        self.pathEntryString = tk.StringVar(self.optWindow) 
        self.pathEntryString.set("{}".format(self.pathForSaving))
        self.pathTextBox = tk.Entry(self.optWindow, 
                                    textvariable = self.pathEntryString, 
                                    width = 47)
        self.pathTextBox.place(x = 100, y = 33)
        
        '''
        # Exposure auto bool
        self.autoExpBoolVar = tk.BooleanVar(self.optWindow)
        self.autoExpBoolVar.set(self.cameraParameters['autoExposure'])

        self.autoExpCheckbox = tk.Checkbutton(self.optWindow, 
                                               text = 'Auto Exposure', 
                                               command = self.autoExCheckAction, 
                                               variable = self.autoExpBoolVar)
        self.autoExpCheckbox.place(x = 10, y = 80)

        
        # Exposure value set
        self.expValueFromBox = tk.StringVar(self.optWindow)
        self.expValueFromBox.set("{}".format(self.cameraParameters['exposureTime']))
        self.expValueBox = ttk.Entry(self.optWindow, 
                                   width = 10,
                                   textvariable = self.expValueFromBox)
        self.expValueBox.bind('<Key-Return>', self.expValueBoxAction) # Do action on 'Return' button w/ cursor here
        self.expValueBox.place(x = 300, y = 83)
        # Text label for exposure time
        self.expValueText = tk.Label(self.optWindow, text = "Exposure time (ms) :")
        self.expValueText.place(x = 180, y = 83)
        '''
        
        # Gain auto bool
        self.autoGainBoolVar = tk.IntVar(self.optWindow)
        self.autoGainBoolVar.set(self.cameraParameters['autoGain'])
        self.autoGainCheckbox = tk.Checkbutton(self.optWindow, 
                                                text = 'Auto Gain', 
                                                variable = self.autoGainBoolVar, 
                                                command = self.autoGainCheckAction)
        
        self.autoGainCheckbox.place(x = 10, y = 150)
        
        # Gain value set
        self.gainValueFromBox = tk.StringVar(self.optWindow)
        self.gainValueFromBox.set("{}".format(self.cameraParameters['gainValue']))
        self.gainValueBox = ttk.Entry(self.optWindow, 
                                   width = 10,
                                   textvariable = self.gainValueFromBox)
        
        self.gainValueBox.bind('<Key-Return>', self.gainValueBoxAction) # Do action on 'Return'
        self.gainValueBox.place(x = 300, y = 153)
        # Text label for Gain
        self.gainValueText = tk.Label(self.optWindow, text = "Gain (dB) :")
        self.gainValueText.place(x = 180, y = 153)
        
        # Call check actions to init enable/disable status from checkboxes 
        self.autoGainCheckAction()
        self.autoExCheckAction()
        
        self.optWindow.mainloop() # Main loop of options window
        
        if self.verbose:
            # Window launch print statement
            print("options!")
        
        return
    
    def autoGainCheckAction(self):
        """
        If checkbox is enabled, then text box is disabled + ignored
        """
        if self.autoGainBoolVar.get():
            self.gainValueBox.configure(state = tk.DISABLED)
        else:
            self.gainValueBox.configure(state = tk.NORMAL)
        return
    
    def autoExCheckAction(self):
        """
        If checkbox is enabled, then text box is disabled + ignored
        """
        if self.autoExpBoolVar.get():
            self.expValueBox.configure(state = tk.DISABLED)
        else:
            self.expValueBox.configure(state = tk.NORMAL)
        return

    def gainValueBoxAction(self, val):
        """
        Action on 'return' button press in gain value box
        Check that input value is between minGain and maxGain
        If yes, reset to nearest bound
        
        If value is invalid (non-numeric) then reset to previous value
        """
        boxString = self.gainValueFromBox.get() # String in text box
        
        try:
            boxVal = float(boxString) # attempt to convert to float
            reset = False # Init reset need

            if (boxVal > self.cameraParameters['maxGain']): # input above max value
                
                boxVal = self.cameraParameters['maxGain'] # input now = max value
                reset = True # going to reset
                
            elif (boxVal < self.cameraParameters['minGain']): # input below min value
                
                boxVal = self.cameraParameters['minGain'] # input now = min value
                reset = True # going to reset
            
        except ValueError: # Above failed - probably can't convert string to float 'cause non-numeric input
            reset = True # Reset flag
            boxVal = self.cameraParameters['gainValue'] # Value stays as old value
            
        if reset:
            # If reset, set box value back to (reset) temp value
            self.gainValueFromBox.set(str(boxVal))
            
        if self.verbose:
            # Print statement for gain value change
            print("gainValue changed to : {}".format(boxVal))
            
        return
    

    
        
    def cancelSettings(self):
        # Close window and do not overwrite values
        self.optWindow.destroy()
        return
    
    def saveSettings(self):
        # Record settings to relevant locations
        # Called w/ OK button
        # Only function that sets these parameters from options
        
        self.cameraParameters['autoExposure'] = self.autoExpBoolVar.get()
        self.cameraParameters['autoGain'] = self.autoGainBoolVar.get()
        self.cameraParameters['exposureTime'] = float(self.expValueFromBox.get())
        self.cameraParameters['gainValue'] = float(self.gainValueFromBox.get())
        
        # Send values to camera
        if not(self.demoMode):
            self.camera.setParameters(self.cameraParameters)
        
        
        self.pathForSaving = pathlib.Path(self.pathEntryString.get())
        
        self.optWindow.destroy()
        return
        
    def savePath(self):
        # Prompt for path to folder for saving recorded vids
        self.savePathSelect = filedialog.askdirectory()
        
        # Set string in box
        self.pathEntryString.set(self.savePathSelect)
         
        return
    
    def doLive(self, buttonPushed):
        '''
        'Live' button push
        Start/stop stream w/o recording
        Lock out other buttons
        End live w/ same button push
        ''' 
        if not(self.demoMode):
        
            # Disable record and save
            
            if self.liveButtonState:
                # True if 'on'
                # Red border on live and second click stops stream
                buttonPushed.configure(relief = "raised")
                
                self.stopStream()
                
            else:
                # True if off 
                # Start stream and lock out buttons
                buttonPushed.configure(relief = 'sunken')
                self.startStream()
            
            # Record on/off toggle 
            self.liveButtonState = not(self.liveButtonState)
            
            # Start video stream and post to GUI
        if self.verbose:
            print("Live!")
        
        return
    

    def imageResize(self, img):
        '''
        Resize images for display in GUI
        Set so whichever dim is farther away from window
        size is the one to scale arbitrarily.  The 'closer' dim
        is set to window size on that axis. 
        '''
        
        # img is PIL Image object w/ height and width attributes
        
        winWidth = self.imgFrame.winfo_width()
        winHeight = self.imgFrame.winfo_height()
        
        imgHeight = img.height
        imgWidth = img.width
        
        # Make width of image equal width of window
        # Height is whatever is proportional to fit
        
        deltaW = winWidth/imgWidth
        deltaH = winHeight/imgHeight
        
        if deltaW > deltaH:
            # Shrink on height more than width
            newHeight = winHeight
            newWidth = int(imgWidth*deltaH)
        else:
            # Shrink width more than height
            newWidth = winWidth
            newHeight = int(imgHeight*deltaW)

        
        return newWidth, newHeight
        
        

    def showLastFrame(self):
        '''
        Display routine for frame in self.rawFrame
        This is ~last frame in queue
        
        Median filter applied to remove hot pixels
        Img resized 
        Resized image in frame label
        '''
        
        if not(self.rawFrame is None): # Frame exists to show
            # Median blur to remove hot pixels
            cvImg = medianBlur(self.rawFrame, self.cameraParameters['medianFilterSize'])[:,:,::-1]
            
            # Convert to PIL image
            filtImg = Image.fromarray(cvImg)
            
            # Resize to fit in frame window w/ shape preserved
            nW, nH = self.imageResize(filtImg) # Get bounds            
            resizeImg = filtImg.resize((nW, nH)) # Apply bounds
            
            # Convert to TK format
            self.img = ImageTk.PhotoImage(image = resizeImg)
            
            # Display it
            self.label.configure(image = self.img)
            
        else:
            pass

        if self.camera.isStreaming: 
            # If streaming, call this function again in 10 milliseconds
            self.streamAfterID = self.label.after(10, self.showLastFrame)
        
        return
        
    def prepForSaving(self):
        '''
        Set up paths + threads for streaming vid to disk
        
        Pull some parameters from camera
        Generate unique file path
        Initialize saveThread process
        
        '''
        if self.verbose:
            print("Record preparation")
            
        # Pull camera parameters relevant for video display
        self.frameRate = self.camera.queryProperty('fps')
        self.frameWidth = self.camera.queryProperty('width') 
        self.frameHeight = self.camera.queryProperty('height')
      
        # Generate a unique file name for saving
        # Going to be video_0000.avi, with trailing integers incremented until unique
        x = 0
        checkFileName = self.pathForSaving / 'video_{:04d}.avi'.format(x)
        while (checkFileName.exists()):
            # If file with that name exists, increment suffix
            x = x + 1
            checkFileName = self.pathForSaving / 'video_{:04d}.avi'.format(x)
            
        self.saveFileName = checkFileName
        
        if self.verbose:
            print("Saving to : {}".format(self.saveFileName))
        
        # Init saveThread process
        # Calls writeVideo() to write data to disk from saveQueue
        self.saveThreadActive = True
        self.saveThread = multiprocessing.Process(target = writeVideo, args=(self.saveQueue, {'fileName' : str(self.saveFileName),
                                                                                              'frameRate' : self.frameRate, 
                                                                                              'size' : (self.frameHeight, self.frameWidth)}))
        self.saveThread.daemon = True
        self.saveThread.start()
        
        if self.verbose:
            print("Record preparation complete!")
        
        return
    

    
    def pullAndQueue(self):
        '''
        Pull from camera queue, put in display and saveQueue

        '''
        if not(self.camera.frameQueue.empty()):

            # Pull most recent frame from camera queue 
            # self.rawFrame is frame to display in GUI
            # Will be most recent frame acquired unless another frame 
            # arrives between showLastFrame() calls
            self.rawFrame = self.camera.frameQueue.get()
        
            if self.verbose:
                print(self.rawFrame)
                
            if self.isRecording: # If in 'Record' mode
                if not(self.saveQueue.full()): # Queue has space, otherwise error
                    
                    if self.verbose:
                        print("Add to saveQueue")

                    # Apply median filter, as in display, and add to saveQueue
                    # nb - all frames make it here.  Not all make it to GUI display, depending on timing
                    self.saveQueue.put(medianBlur(self.rawFrame.as_opencv_image(), self.cameraParameters['medianFilterSize']))
                else:
                    print('Full queue!')
                    
        if self.camera.isStreaming: # If streaming, call this again in 5 ms
            self.streamAfterID = self.label.after(5, self.pullAndQueue)
                
        return
        
    def startStream(self, record = False):
        '''
        Fire up video stream in camera
        
        Coordinates other function calls to init video streaming.
        record is bool for Record mode (True) or Live mode (False)
        '''
        if self.verbose:
            print("Start stream!")

        self.cameraAcquiring = True # Set flag

        if record: # In 'Record' mode
            if self.verbose:
                print("Recording!")
            
            self.liveButton['state'] = 'disabled' # Lock out other buttons
            self.prepForSaving() # Set up save stream
            self.isRecording = True # Flag

        else:
            
            self.recButton['state'] = 'disabled'# Disable other buttons
            self.isRecording = False # flag
        

        self.camera.startStream() # Call camera's startStream method
        self.pullAndQueue() # Sort incoming frames into local queues
        self.showLastFrame() # Display
        self.optionsButton['state'] = 'disabled' # Lock out other buttons
        self.snapButton['state'] = 'disabled'
        

            
        return
        
    def stopStream(self, record = False):
        '''
        Coordinate end of video stream
        
        Record is bool for Record mode (True) or Live mode (False)
        '''
        
        
        
        if self.verbose:
            print("Stop Stream!")
        
        self.cameraAcquiring = False # Flag
        
        self.camera.stopStream() # Camera's stop video streaming method
        
        self.optionsButton['state'] = 'active' # Reset button
        self.snapButton['state'] = 'active' # Reset button
        
        if record:
            if self.verbose:
                print("Stop recording!")
            
                
            self.saveThreadActive = False # Flag
            self.saveQueue.put(None) # Add None object to signal end of queue


            self.liveButton['state'] = 'active' # Reset button
            
        else:
            
            self.recButton['state'] = 'active' # Reset button

            
        return
    
    def doRecord(self, buttonPushed):
        '''
        Record button pushed
        
        Start/stop stream in Record mode
        
        '''
        
        if not(self.demoMode):

            # Button sunken and sticks
            if self.recButtonState:
                buttonPushed.configure(relief = "raised")
                self.stopStream(record = True)
            else:
                buttonPushed.configure(relief = "sunken")
                self.startStream(record = True)
            
            self.recButtonState = not(self.recButtonState)
        # Start video stream and post to GUI AND save to disk
        if self.verbose:
            print("Record!")
        
        return
    
    def doSnap(self):
        '''
        Snap button pushed
        
        On 'Snap':
            Take a pic
            Prompt + save
            
        newImgOnSnap - bool
            True - call snapImage() to get image from camera
            False - (unimplemented) Use self.rawFrame as last image
            
        saveOnSnap - bool
            True - call file_save() to prompt for path and save image
            False - Do nothing.  File would need to be saved elsewhere (unimplemented)
        '''
        
        
        if not(self.demoMode):
            if self.newImgOnSnap:
                self.snapImage()
            
            if self.saveOnSnap:
                self.file_save()
            else:
                pass
            
        return
    
    def snapImage(self):
        '''Single frame capture
        
        Frame captured from camera goes into camera queue
        Call showLastFrame() to display most recent frame
            nb - stream flag not set so showLastFrame() should not get 
            recall enabled 
        ''' 
        
        self.camera.snap()
        
        self.showLastFrame()        

        return


    def file_save(self):
        '''
        Save last displayed frame
        '''
        
        f = filedialog.asksaveasfile(mode='w', defaultextension=".png") # Prompt file dialog
        if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        # Img to save is last frame from queue through showLastFrame()
        # Convert, do median blur
        img = medianBlur(self.rawFrame.as_opencv_image(), self.cameraParameters['medianFilterSize']) 
        imwrite(f.name, img) # Write to disk
        return
    


if __name__ == "__main__":
    
    root = tk.Tk()
    vidRec = vidRecorder(root)
    root.mainloop()