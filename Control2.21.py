import sys
sys.path.insert(0,'/home/pi/project0/ADserial')
sys.path.insert(0,'/home/pi/project0/Rotator')
import rotator as rt
import ADserial as ADser

import math
import time
import matplotlib.pyplot as plt
import RPi.GPIO as GPIO

target=200

KI=0
KP=0.065

rt.setup()


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

while mainloopflag==1:
        datalist=[]
        ADser.flush()
        
        GPIO.wait_for_edge(3,GPIO.RISING)
        t1=time.time()
        
        while (time.time()-t1)<0.001:
                
                data=ADser.rd()
                datalist.append(data)        
         
        idatalist=[]
        lend=len(datalist)
        print('number of measurements received:',lend)
                                
        i=0;
        while(i<lend):
                idatalist.append(ADser.datastoi(datalist[i]))
                i+=1
                    
        dataave=float(sum(idatalist))/float(len(idatalist))
        error=dataave-target
        output=error*KP

        totangle=totangle+output
        if output<0:
                print('Power=:',dataave," Moving:-;Angle=",output)
                rt.moverel(output)

        elif output>0:
                print('Power=:',dataave," Moving:+;Angle=",output)
                rt.moverel(output)
        
        if totangle> 90 or totangle<-90:
                print("Request unattainable: input power too low.")
                mainloopflag=0
      


GPIO.cleanup()
#-----------------------------------------------------------------
                
