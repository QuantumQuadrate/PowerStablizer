import sys
sys.path.insert(0,'/home/pi/project1/Shield')
sys.path.insert(0,'/home/pi/project1/Rotator')
sys.path.insert(0,'/home/pi/project1/Devicesetup')
import rotator as rt
import ADS1256 as ads
import deviceinfo as di
import RPi.GPIO as GPIO
import math
import time
import serial
import numpy as np
import os
import threading
#System configuration parameters:
#-------------------------------------------------------------------------------
#User-set parameters:

rpinum=0
showalldata=1
enable=[1,1,0,0]
SN=['55000491','55000617','55000392','55000389']

target=[0.53,0.0685,0.266,0.0173]
KP=[70,60,50,50]
KI=[1,1,0,0]
triglist=[0,1,0,0]
delaytime=[0,0,0,0]
readonly=1
tintegral=[0.002,0.002,0.01,0.01]

integralwindow=[10,10,10,10]
enablebuffer=0

mode=[1,1,1,1]
modechange=[1,1,1,1]

#-------------------------------------------------------------------------------
#Default parameters:


datain_high=[0x0,0x2,0x4,0x6]
datain_low=[0x1,0x3,0x5,0x7]
trigmenu=[3,5,7,8]

#------------------------------------------------------------------------------
#Dependent variables and pre-loop setup:
GPIO.setmode(GPIO.BOARD)
GPIO.setup(trigmenu,GPIO.IN)
class opstruct:
    xid=0
    m=rt.K10CR1(serial.Serial())
    trigport=0
    integrallist=[]
    def __init__(self,xidinfo,motorinfo):
        self.xid=xidinfo
        self.m=motorinfo        
        self.trigport=triglist[xidinfo]
        self. integrallist=[]
class trigstruct:
    lent=0
    xlist=[]
    trigpin=0
    def __init__(self,lentinfo,xlistinfo,trigpininfo):
        self.lent=lentinfo
        self.xlist=xlistinfo
        self.trigpin=trigpininfo
        
portaddr=[]
x=[]
totnum=0

for count in range(4):
    if enable[count]==1:
        deviceinfo=di.deviceinfo(SN[count])
        if deviceinfo.deviceexist==0:
            print('Error: Cant find device with serial number:'+SN[count])
            print('Program will continue regardless of this issue')
            time.sleep(5)
        else:
            print('Device with serial number '+SN[count]+' has been successfully set up')
            portaddr.append(deviceinfo.ser.port)
            x.append(opstruct(count,rt.K10CR1(deviceinfo.ser)))
            totnum+=1

trig=[]
for count in range(4):
    xlist=[]
    for i in range(totnum):
        if x[i].trigport==count:
            xlist.append(i)
    trig.append(trigstruct(len(xlist),xlist,trigmenu[count]))
lentrig=len(trig)

ad=ads.ADS1256()
#-----------------------------------------------------------------------------
#main loop:
mainloopflag=1

totangle=[0,0,0,0]
error=0
integral=0
output=0

calcount=0
fullflag=[0,0,0,0]
odata=[0,0,0,0]
ndata=[0,0,0,0]
esign=[1,1,1,1]
error_array=[0,0,0,0]
ad.SetEnableBuffer(enablebuffer)
ad.SelfCalibrate()
data_to_save=[]
thread_list = []

def noiseeater_loop(j):
    if GPIO.event_detected(trig[j].trigpin):
        #print "loop " + str(j+1) + " restarting"
        calcount=0
        data=[]
         
        #if trig[j].lent>0:
          # GPIO.wait_for_edge(trig[j].trigpin,GPIO.RISING,timeout=10000)
	   # if GPIO.event_detected(trig[j].trigpin):
               # continue 
          # time.sleep(1)
       # else:
           # continue
        


        for k in range(trig[j].lent):
            
            i=trig[j].xlist[k]
            
            data0list=[]        
      
            ad.SetInputMux(datain_high[x[i].xid],datain_low[x[i].xid])

            time.sleep(delaytime[j])
            
            t1=time.time()       
            while (time.time()-t1)<tintegral[j]:
                                 
                    data0=ad.ReadADC()

                    data0list.append(float(data0)/float(2000*838.8306))         

            lend0=len(data0list)
            if lend0 >= 2:
                    data0list=data0list[:lend0-1]
                    lend0=lend0-1
            else:
                    print("No measurements done within time limit")
                    continue
            datalist=data0list[1:]
            #lend0=lend0-1
            if showalldata==1:
                    print('List of all measurements in channel '+str(x[i].xid+1)+': ',data0list)
            print('---------------------------------------------------')
            #print str(lend0) + " lendo for " + str(j+1)
            data0ave=float(sum(data0list))/float(lend0)
            data.append(data0ave)
    
        for k in range(trig[j].lent):
            
            i=trig[j].xlist[k]

            data0ave=data[k]
            
            error=data0ave-target[x[i].xid]

            if fullflag[x[i].xid]==0:
                    (x[i].integrallist).append(error)
                    if len(x[i].integrallist)>=integralwindow[x[i].xid]:
                            fullflag[x[i].xid]=1
            else:
                    intcount=0
                    while(intcount<integralwindow[x[i].xid]-1):
                            x[i].integrallist[intcount]=x[i].integrallist[intcount+1]
                            intcount=intcount+1
                    x[i].integrallist[integralwindow[x[i].xid]-1]=error
            integral=float(sum(x[i].integrallist))/float(len(x[i].integrallist))
            #-----------------------------------------------------------------
            #print(x[i].integrallist)
            #-----------------------------------------------------------------
            output=error*KP[x[i].xid]+integral*KI[x[i].xid]
            if data0ave/target[x[i].xid] > 1.05 or data0ave/target[x[i].xid] < 0.95:
                error_array[x[i].xid]=1
            else:
                error_array[x[i].xid]=0
            if np.sum(error_array) > 0:
                os.system('echo 1 > /sys/class/gpio/gpio15/value')
            else:
                os.system('echo 0 > /sys/class/gpio/gpio15/value')

            if mode[x[i].xid]==1:
                if output<0:
                     print('Channel '+str(x[i].xid+1)+': number of measurements received:'+str(lend0))    
                     print('Voltage:'+str(data0ave)+"; Moving:-; Angle="+str(output))
                     if readonly==0:
                             x[i].m.moverel(output)
                             totangle[x[i].xid]=totangle[x[i].xid]+output

                elif output>0:
                     print('Channel '+str(x[i].xid+1)+': number of measurements received:'+str(lend0))    
                     print('Voltage:'+str(data0ave)+"; Moving:+; Angle="+str(output))
                     if readonly==0:
                             x[i].m.moverel(output)
                             totangle[x[i].xid]=totangle[x[i].xid]+output
            
                if totangle[x[i].xid]> 180 or totangle[x[i].xid]<-180:
                     print('Channel '+str(x[i].xid+1)+": Request unattainable: input power too low.")
                     if readonly==0:
                             odata[x[i].xid]=data0ave-0.1
                     if modechange[x[i].xid]==1:
                             mode[x[i].xid]=0

            elif mode[x[i].xid]==0:
                 print('Channel '+str(x[i].xid+1)+': Original request unreachable. Moving to maximum power')
                 if readonly==0:
                     ndata[x[i].xid]=data0ave
                     e=ndata[x[i].xid]-odata[x[i].xid]
                     if e <0:
                         esign[x[i].xid]=esign[x[i].xid]*-1
                     eout=esign[x[i].xid]*abs(KP[x[i].xid]*e)
                     if eout < 1:
                         eout =eout*5
                     print('Channel '+str(x[i].xid+1)+': Voltage= '+str(data0ave))
                     print('Moving with angle: '+str(eout))
                     x[i].m.moverel(eout)
                     odata[x[i].xid]=ndata[x[i].xid]
                 if (ndata[x[i].xid]>target[x[i].xid])&(modechange[x[i].xid]==1):
                     print('back to normal mode')
                     mode[x[i].xid]=1
            calcount=calcount+1
            if calcount >=1000:
                     calcount=0
                     print('self calibrating')
                     ad.SelfCalibrate()
        for k in range(trig[j].lent):
            
            i=trig[j].xlist[k]

            if (readonly==0):
                    x[i].m.rd(20)
       # data_to_save.append(data0ave)
       # np.savetxt("output_array.csv",data_to_save,delimiter= ',')

for j in range(4):
    print j
    if enable[j] == 1:
        GPIO.add_event_detect(trig[j].trigpin, GPIO.RISING)
        print "Making thread " + str(j+1)
        t = threading.Thread(target=noiseeater_loop, args=(j,))
        thread_list.append(t)
for thread in thread_list:
    thread.daemon = True
    thread.start()
    print "start"
#print threading.enumerate()
while True:
   time.sleep(10)
GPIO.cleanup()
