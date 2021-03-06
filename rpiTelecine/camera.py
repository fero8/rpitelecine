# RPi Telecine Camera Control
#
# Code to encapsulate the operation of the camera.
#	
# Basically this isolates the fixed settings we use during the
# taking process. Images returned are bgr format Numpy arrays
# that can be used by openCV.
#	
# Prerequisites:
# Uses Python-picamera by Dave Hughes from: 
# https://pypi.python.org/pypi/picamera/
# or use sudo apt-get install python-picamera on your Pi.
#	
# Uses array API of Picamera 1.5+ to return a Numpy array
#
# As of May 2014, it seems to be necessary to set the memory split
# in raspi-config to at least 192M, otherwise we seem to get MMAL 
# out-of-memory errors.
# 
# 
# Copyright (c) 2015, Jason Lane
# 
# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this 
# list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice, 
# this list of conditions and the following disclaimer in the documentation and/or 
# other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its contributors 
# may be used to endorse or promote products derived from this software without 
# specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR 
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON 
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from __future__ import division
import picamera
from picamera import PiCamera
import picamera.array 
import time

# Subclass of PiCamera

class TelecineCamera( PiCamera ):
    
    def __init__(self):
        super(TelecineCamera, self).__init__(sensor_mode=2)
        # Fixed settings
        self.resolution = self.MAX_IMAGE_RESOLUTION # 2592x1944
        self.framerate = 15              # Maximum allowed for full frame stills/preview/video 
        self.iso=100                     # Fix ISO for minimum sensor gain
        self.image_denoise=False         # Switch off image denoise - speeds up capture and retains detail in image
 
    def setup_cam(self,awb_gains,shutter,drc='off',effect='none'):
        """ 
        Settings that can be changed when setting up the job
        Need fixed shutter speed, AWB etc for consistency between frames.
        """
        #time.sleep(0.5)
        self.awb_gains=awb_gains
        self.awb_mode='off'              # Fix the awb_gains
        self.shutter_speed=shutter       # Fix shutter speed
        self.sharpness = -100            # Reduce sharpening to minimum. Too much sharpening introduces artefacts into image
        if effect in self.IMAGE_EFFECTS:
            self.image_effect = effect
        else:
            self.image_effect = 'none'
        self.vflip=True
	
    def take_picture(self):
        """ 
        Returns an openCV compatible colour image 
        """
        with picamera.array.PiRGBArray(self) as output:
            self.capture(output, format='bgr')
            return output.array 

    def take_bracket_pictures(self):
	""" 
	Returns two images in a list
	One with normal exposure, and one with 2 stop longer exposure 
	The aim to to get detail out of shadows/underexposed film
	Resulting images can be combined on a PC with Hugin's enfuse utility
	"""
	old_shutter = self.shutter_speed
	imgs = []
	with picamera.array.PiRGBArray(self) as output:
	    self.capture(output, format='bgr')
	    imgs.append( output.array )
	    self.shutter_speed = old_shutter*4
	    output.truncate(0)
	    self.capture(output, format='bgr')
	    imgs.append( output.array )
	self.shutter_speed = old_shutter
	return imgs
	
