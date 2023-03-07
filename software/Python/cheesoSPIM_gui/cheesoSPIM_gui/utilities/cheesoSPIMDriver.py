# -*- coding: utf-8 -*-
"""
Created on Wed Dec 28 15:12:19 2022

@author: Rusty Nicovich
"""

import time

config = {
    'CMD_NOT_DEFINED': 0x15,
    'DeviceID' : 'cheesoSPIM',
    'ENCODING' : 'utf8',
    'comPort' : 'COM8',
    'baudRate' : 115200,
    'timeout' : 3
    }



def comPortStart(comPort = config['comPort'], baudRate = config['baudRate'], timeOut = config['timeout']):
    
    """
    Helper function to start a serial object
    
    Inputs : comPort - string; com port to use for this object
             baud - int; baud rate for serial port.  NicoLase is set to 115200
             timeOut - int; timeout time for port in seconds.  Default is 1    
             
    Returns : serial port ready to pass to octoDACDriver object
    """
    
    import serial 
    
    ser1 = serial.Serial(comPort, baudRate, timeout = timeOut)
    time.sleep(3)
    ser1.flushInput()
    ser1.reset_input_buffer()
        
    return ser1


class cheesoSPIM_driver():
    """
    Class for communicating with octoDAC Arduino Shield + sketch
    
    """
    def __init__(self, serialDevice, verbose = False):

        # Once connected, check that port actually has octoDAC on the receiving end
        self.serial = serialDevice
        self.verbose = verbose
        devID = self.getIdentification()
        if devID == config['DeviceID']:
            if self.verbose:
                print('Connected to cheesoSPIM on port ' + self.serial.port)
        else:
            print("Device Id returned : {}".format(devID))
            print("Initialization error! Disconnecting!\n")
            self.serial.close()
            
    def numToShortInteger(self, setVal):
        """
        Utility function to convert input value to (two byte?) integer
        """
        if (setVal >= 0) and (setVal < 65536):
            shortVal = str(setVal)
        elif (setVal > 65535):
            shortVal = str(65535)
        else:
            shortVal = str(0)
            
        return shortVal
    
    def writeAndRead(self, sendString, read = True):
        """
        Helper function for sending to serial port, returning line
        """
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()
        sendString = sendString + '\n'
        self.serial.write(sendString.encode(config['ENCODING']))
        
        if read:
            ret = self.serial.readline().decode(config['ENCODING']).strip('\r\n')
            
            if self.verbose:
                print(ret)
                
            return ret
        else:
            return
    
    # D 
    def doDemo(self):
        self.writeAndRead('D', read = False)
        
        return
    
    # V
    def lensAllOut(self):
        self.writeAndRead('V', read = False)
        return
    
    
    # B
    def lensAllIn(self):
        self.writeAndRead('B', read = False)
        return
    
    # E
    def lensIn(self):
        self.writeAndRead('E', read = False)
        return
    
    # Q
    def lensOut(self):
        self.writeAndRead('Q', read = False)
        return
    
    # F
    def setFocus(self, value):
        stringOut = "F {}".format(value)
        print(stringOut)
        self.writeAndRead(stringOut, read = False)
        return
    
    # N
    def laserOn(self):
        self.writeAndRead('N', read = False)
        return
    
    # O
    def laserOff(self):
        self.writeAndRead('O', read = False)
        return
    
    # I
    def laserUp(self):
        self.writeAndRead('I', read = False)
        return
    
    # K
    def laserDown(self):
        self.writeAndRead('K', read = False)
        return
    
    # P
    def setLaserPower(self, value):
        self.writeAndRead('P {}'.format(self.numToShortInteger(value)), read = False)
        return
    
    # M
    def spinMotor(self, steps):
        # Spin as many steps as indicated
        # Negative one way, positive the other

        print("Moving : {}".format(steps))
        self.writeAndRead('M {}'.format(steps) , read = False)

        return
    
    def lensFindLimits(self):
        self.writeAndRead('V', read = False)
        time.sleep(1)
        minVal = self.queryFocus()
        
        self.writeAndRead('B', read = False)
        time.sleep(1)
        maxVal = self.queryFocus()
        
        return [minVal, maxVal]


    # ? F
    def queryFocus(self):
        """ 
        query excitation lens position
        """
        idn = self.writeAndRead('? F')
        return idn 

        
    # ? L
    def queryLaser(self):
        """ 
        query laser power
        """
        idn = self.writeAndRead('? L')
        return idn 
        
    # Y
    def getIdentification(self):
        """ identification query """
        idn = self.writeAndRead('Y')
        return idn
    
if __name__ == '__main__':
    print("Testing octoDAC shield...")
    
    import serial
    
    serPort = serial.Serial('COM4', 115200, timeout = 1)
    oD = cheesoSPIM_driver(serPort)
    
    # Make ramp on CHAN1
    for k in range(0, 65536):
        oD.setChannel(1, k) 
    
    # Blink CHAN1 3 times      
    for k in range(0, 3):
        oD.closeShutter()
        time.sleep(0.5)
        oD.openShutter()
        time.sleep(0.5)
        
    oD.closeShutter()