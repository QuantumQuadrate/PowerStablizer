#Important Constants:

#Stablization setpoint:
target=410
#Feedback constant:
KI=0.0005
KP=0.01
#Time for measurement averaging:
tIntegral=0.001
#Time delay after triggering before measurment
delaytime=0
#Width of the Integral window
Integralwindow=10
#M
readonly=0
#Set the input buffer to change input resistance
enablebuffer=1
#Set data rate:	drate:		datarate/SPS:
#		0		30000
#		1		15000
#		2		7500	
#		3		2.5

drate=0
#--------------------------------------------------------------------

import sys
sys.path.insert(0,'/home/pi/project0/Shield')
sys.path.insert(0,'/home/pi/project0/Rotator')
import rotator as rt
import ADS1256 as ads

import math
import time
#import matplotlib.pyplot as plt
import RPi.GPIO as GPIO



rt.setup()
ad=ads.ADS1256()



#----------------------------------------------------------------
mainloopflag=1;
readloopflag=0
commandflag=0;
autoexitflag=1;
chanflag=0;
fullflag=0

GPIO.setmode(GPIO.BOARD)

chan=3

GPIO.setup(chan,GPIO.IN)

totangle=0

error=0
integral=0
output=0

#fp0=open('p00_0615.txt','w+')
#fp1=open('p01_0615.txt','w+')
#ft=open('t0_0615.txt','w+')
timebase=time.time()
tprvs=time.time()
calcount=0
Integrallist=[]
ad.SetDRate(drate)
ad.SetEnableBuffer(enablebuffer)
ad.SelfCalibrate()
while mainloopflag==1:
        data0list=[]
        
        #data1list=[]
        
        chanflag=GPIO.wait_for_edge(3,GPIO.RISING,timeout=30000)
        if chanflag is None:
                print('Timeout Occured: No rising edge detected in the past 30s.')
                if autoexitflag==1:
                     break
                else:
                     continue	
  
        ad.SetInputMux(ad.MUX_AIN0,ad.MUX_AIN1)
        time.sleep(delaytime)
        t1=time.time()       
        while (time.time()-t1)<tIntegral:
                             
                data0=ad.ReadADC()
                #sys.stdout.write("AIN_0 value: {:d}\n".format(val))
                #sys.stdout.flush()
                data0list.append(float(data0)/float(10000))         

#        print(data0list)
        lend0=len(data0list)
	if lend0>=2:
		data0list=data0list[:lend0-1]
		lend0=lend0-1
	else:
		print("No measurements done within time limit")
		continue
	print("List of all measurements",data0list)                                            
        data0ave=float(sum(data0list))/float(lend0)
       # data0ave=float(ad.ReadADC())/float(10000)

        #ad.SetInputMux(ad.MUX_AIN2,ad.MUX_AIN3)
        #time.sleep(0.001)
        #t1=time.time()       
        #while (time.time()-t1)<0.001:
                             
                #data1=ad.ReadADC()
                #sys.stdout.write("AIN_1 value: {:d}\n".format(val))
                #sys.stdout.flush()
                #data1list.append(float(data1)/float(10000))         

        #lend1=len(data1list)                        
                    
        #data1ave=float(sum(data1list))/float(lend1)

        error=data0ave-target
        if fullflag==0:
                Integrallist.append(error)
                if len(Integrallist)>=Integralwindow:
                        fullflag=1
        else:
                Intcount=Integralwindow-1
                while(Intcount>0):
                        Integrallist[Intcount]=Integrallist[Intcount-1]
                        Intcount=Intcount-1
                Integrallist[0]=error
        integral=float(sum(Integrallist))/float(len(Integrallist))

        #print(error)
        #rint(Integrallist)
        #integral=error*(t1+0.001-tprvs)+integral

        #tprvs=time.time()
        
        output=error*KP+integral*KI
        #output=error*KP
        #print('AIN_0:',data0ave)
        #print('AIN_1:',data1ave)

        #fp0.write('%f\n' % (data0ave))
        #fp1.write('%f\n' % (data1ave))
        #ft.write('%f\n' % (time.time()-timebase))
        
        totangle=totangle+output
        if output<0:
#                print('number of measurements received:',lend0)    
                print('Power=:',data0ave," Moving:-;Angle=",output)
		if readonly==0:
                	rt.moverel(output)

        elif output>0:
#                print('number of measurements received:',lend0)    
                print('Power=:',data0ave," Moving:+;Angle=",output)
                if readonly==0:
		        rt.moverel(output)
        
        if totangle> 180 or totangle<-180:
                print("Request unattainable: input power too low.")
#                mainloopflag=0

        calcount=calcount+1
        if calcount >=100:
                calcount=0
                print('self calibrating')
                ad.SelfCalibrate()


GPIO.cleanup()
#ft.close()
#fp0.close()
#fp1.close()
#-----------------------------------------------------------------
                
