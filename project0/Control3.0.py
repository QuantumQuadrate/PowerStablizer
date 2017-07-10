import sys
sys.path.insert(0,'/home/pi/project0/Shield')
sys.path.insert(0,'/home/pi/project0/Rotator')
import rotator as rt
import ADS1256 as ads

import math
import time
#import matplotlib.pyplot as plt
import RPi.GPIO as GPIO

target=300

KI=0
KP=0.045

rt.setup()
ad=ads.ADS1256()



#----------------------------------------------------------------
mainloopflag=1;
readloopflag=0
commandflag=0;

GPIO.setmode(GPIO.BOARD)

chan=3

GPIO.setup(chan,GPIO.IN)

totangle=0

error=0
integral=0
output=0

fp=open('p00_0601.txt','w+')
ft=open('t00_0601.txt','w+')
timebase=time.time()

while mainloopflag==1:
        datalist=[]
        
        GPIO.wait_for_edge(3,GPIO.RISING)
        t1=time.time()
        
        while (time.time()-t1)<0.001:
                
                ad.SetInputMux(ad.MUX_AIN0,ad.MUX_AINCOM)
                data=ad.ReadADC()
                #sys.stdout.write("AIN_0 value: {:d}\n".format(val))
                #sys.stdout.flush()
                datalist.append(float(data)/float(10000))        
         
        lend=len(datalist)                           
                    
        dataave=float(sum(datalist))/float(lend)
        error=dataave-target
        output=error*KP

        fp.write('%f\n' % (dataave))
        ft.write('%f\n' % (time.time()-timebase))
        
        totangle=totangle+output
        if output<0:
                print('number of measurements received:',lend)    
                print('Power=:',dataave," Moving:-;Angle=",output)
                rt.moverel(output)

        elif output>0:
                print('number of measurements received:',lend)    
                print('Power=:',dataave," Moving:+;Angle=",output)
                rt.moverel(output)
        
        if totangle> 90 or totangle<-90:
                print("Request unattainable: input power too low.")
                mainloopflag=0
      


GPIO.cleanup()
ft.close()
fb.close()
#-----------------------------------------------------------------
                
