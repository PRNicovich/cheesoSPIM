# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 12:17:34 2022

Acquisition class for Allied Vision camera running through Vimba
Install Vimba w/ python support before executing

Object fires up camera on init. 
Set parameters by passing dict in setParameters method
Acquired frames go into queue.Queue() object where 
they can be accessed elsewhere (eg GUI)

Can be a prototype for other cameras supported with same GUI
Use same object + method names, or rename on import elsewhere

@author: rusty
"""

import cv2
import queue
import threading

class camera():
    
    def __init__(self, camSourceID = 0):
        print('here!')
        # Connect to camera
        self.cam = cv2.VideoCapture(camSourceID)
        print('Connected to cam port {}'.format(camSourceID))

        # Defaults for important parameters        
        self.paramDict = {"exposure" : -2} #-2 = 320 ms
                           # Use cropped ROI

        self.setParameters(self.paramDict)
        
        self.camSource = camSourceID
        self.camName = 'openCV camera'
        self.camID = 'OpenCV camera'
                
        self.isStreaming = False  # Set flag
        self.frameQueue = queue.Queue() # Init empty queue for acquired frames
            
        return
    
    
    def setParameters(self, paramDict):
        """
        Set camera parameters here
        Camera-dependent API, so best to code each call in directly
        
        paramDict is dict w/ supported fields:
            - autoExposure (bool)
            - exposureTime (int, milliseconds, 0.1 - 20000 or so)
            - autoGain (bool)
            - gainValue (int, dB, 0-24)
            - binning (int, pixels to bin)
            - cropROI (bool, should always? be False)
        
     
        if paramDict['autoExposure']:
            c.ExposureAuto.set('Continuous') # On-board autoexposure per frame
        else:
        
        
        
        
        with Vimba.get_instance():
            with self.cams[0] as c:
                
                # Go by fields in paramDict
                # Field names should match a conditional here to get set
                # Non-exhaustive!
                if paramDict['autoExposure']:
                    c.ExposureAuto.set('Continuous') # On-board autoexposure per frame
                else:
                    c.ExposureAuto.set('Off') # No autoexpose - set value in next command
                    c.ExposureTime.set(paramDict['exposureTime']*1000) # milli to microseconds
                    
                if paramDict['autoGain']:
                    c.GainAuto.set('Continuous') # On-board autoGain per frame
                else:
                    c.GainAuto.set('Off') # Fixed gain
                    c.Gain.set(paramDict['gainValue']) # Set gain value in dB
                    
                if (paramDict['binning'] >= 1):
                    # Camera supports binning in two directions independently
                    # Set number of pixels to combine into one on the output
                    c.BinningHorizontal.set(paramDict['binning'])
                    c.BinningVertical.set(paramDict['binning'])

                    # Make sure that regardless of binning setting, the full chip is being used
                    # With pixel count change (such as decreasing binning value) you can 
                    # get camera that sends part of chip instead of chip w/ pixels binned
                    sw = c.SensorWidth.get()
                    sh = c.SensorHeight.get()
                    
                    # Set chip height and width to full size, divided by binning
                    c.Height.set(int(sh/paramDict['binning']))
                    c.Width.set(int(sw/paramDict['binning']))
                    
                    
        """   
        return
        
        
    
    def queryProperty(self, prop):
        '''
        Pass-through function for querying camera properties as class method
        prop is string specifying which property to query.
        Supports:
            - Acquisition frame rate (prop = 'fps' or 'framerate')
            - Width (prop = 'w' or 'width')
            - Height (prop = 'h' or 'height')
            
        Other parameters ToDo as needed
        If unspecified or undefined, method will return None
        
        with Vimba.get_instance():
            with self.cams[0] as c:
            
                if (prop.lower() in {'fps', 'framerate'}):
                    
                    val = c.AcquisitionFrameRate.get() # Frame rate as single value
                    
                elif (prop.lower() in {'width', 'w'}):
                    
                    val = c.Height.get() # Current output image height (pixels)
                    
                elif (prop.lower() in {'height', 'h'}):
                    
                    val = c.Width.get() # Current output image width (pixels)
                    
                else:
                    # All other property queries yield None
                    val = None
                
                
        return val
            
        '''
        return
        
    
    def snap(self):
        '''
        Take a single frame on camera.
        Add this frame to queue        
        '''
        ret, frame = self.cam.read()
                
        # Put images into queue instead of returning directly
        self.frameQueue.put(frame)
        
        return 
    
    def startStream(self):
        '''
        Start camera streaming (Live or Record mode).
        
        Set isStreaming = True
        Start thread daemon of camStream() method
        '''
        
        self.isStreaming = True
        
        threading.Thread(target = self.camStream, daemon = True).start()
        
        return
    
    def stopStream(self):
        '''
        Stop camera streaming (Live or Record mode)
        
        Set isStreaming = False
        Call Vimba class method stop_streaming()
        Clear queue
        Shutdown frameHandler
        '''
        
        
        self.isStreaming = False

        return
    
    
    def camStream(self):
        """
        Class to handle camera acquisition events
        Called in own thread
        """
        # Init frame handler class w/ queue to use

        while self.isStreaming:
            ret, frame = self.cam.read()
            
            if not ret:
                # Error
                print('Cannot receive frame from camera')
            else:
                self.frameQueue.put(frame)

                    
        return
    

        