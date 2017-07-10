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


#System configuration parameters:
#-------------------------------------------------------------------------------
#User-set parameters:

#(bool)enable:1 for using,0 for not using the channel
#(string)SN:Serial number for the rotator connected to the channel, if in use
#(int)target:Stablization target for the laser in the channel, if in use
#(float)KP:feedback parameter, if in use
#(float)KI:feedback parameter, if in use
#(int)triglist:Channels for trigger signals
#(float)delaytime:Set the time delay after trigger before measurement
#(tintegral):Set the time duration for measurements. Multiple measurements will be
#            done and the average will be used for feedback
#(bool)readonly:1 for only reading out the signal,0 for running stablization
#(int)integralwindow:Set the length of the integral window in feedback calculation
#(bool):1 for enabling the input buffer(increase input inpedance),0 for disable

enable=[1,1,1,1]
SN=['55000491','55000389','55000392','55000604']
target=[20,50,20,20]
KP=[1,1,1,1]
KI=[0,0,0,0]
triglist=[0,0,0,0]
delaytime=[0,0,0,0]
readonly=0
tintegral=[0.01,0.01,0.01,0.01]
integralwindow=[10,10,10,10]
enablebuffer=0

#-------------------------------------------------------------------------------
#Default parameters:

#(int)trigin:the port on the box that is used for trigger input
#(int)datain:the port on the box that is used for data input

datain_high=[0x0,0x2,0x4,0x6]
datain_low=[0x1,0x3,0x5,0x7]
trigmenu=[3,5,7,8]


#------------------------------------------------------------------------------
#Dependent variables and pre-loop setup:

class opstruct:
    xid=0
    m=rt.K10CR1(serial.Serial())
    trigport=0
    def __init__(self,xidinfo,motorinfo):
        self.xid=xidinfo
        self.m=motorinfo
        self.trigport=triglist[xidinfo]
        
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

totangle=0
error=0
integral=0
output=0

calcount=0

ad.SetEnableBuffer(enablebuffer)
ad.SelfCalibrate()
while mainloopflag==1:
    fullflag=0
    calcount=0
    integrallist=[]
    for j in range(4):
        data=[]
        print(j,' ',trig[j].lent,' ',trig[j].xlist)
        if trig[j].lent>0:
            #GPIO.wait_for_edge(trig[j].trigpin,GPIO.RISING)
            time.sleep(0.1)
        else:
            continue

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
                
            print('List of all measurements in channel'+str(x[i].xid)+': ',data0list)
            
            data0ave=float(sum(data0list))/float(lend0)
            data.append(data0ave)
            
        for k in range(trig[j].lent):
            
            i=trig[j].xlist[k]

            data0ave=data[k]
            
            error=data0ave-target[x[i].xid]
            if fullflag==0:
                    integrallist.append(error)
                    if len(integrallist)>=integralwindow[x[i].xid]:
                            fullflag=1
            else:
                    intcount=integralwindow[x[i].xid]-1
                    while(intcount>0):
                            integrallist[intcount]=integrallist[intcount-1]
                            intcount=intcount-1
                    integrallist[0]=error
            integral=float(sum(integrallist))/float(len(integrallist))
            
            output=error*KP[x[i].xid]+integral*KI[x[i].xid]
            
            totangle=totangle+output
            if output<0:
                    print('number of measurements received:'+str(lend0))    
                    print('Voltage:'+str(data0ave)+"; Moving:-; Angle="+str(output))
                    if readonly==0:
                        x[i].m.moverel(output)

            elif output>0:
                    print('number of measurements received:'+str(lend0))    
                    print('Voltage:'+str(data0ave)+"; Moving:+; Angle="+str(output))
                    if readonly==0:
                        x[i].m.moverel(output)
            
            if totangle> 180 or totangle<-180:
                    print("Request unattainable: input power too low.")
    #                mainloopflag=0

            calcount=calcount+1
            if calcount >=100:
                    calcount=0
                    print('self calibrating')
                    ad.SelfCalibrate()
        for k in range(trig[j].lent):
            
            i=trig[j].xlist[k]

            x[i].m.rd(20)

GPIO.cleanup()
