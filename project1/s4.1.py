import sys
sys.path.insert(0,'/home/pi/project1/Shield')
sys.path.insert(0,'/home/pi/project1/Rotator')
sys.path.insert(0,'/home/pi/project1/Devicesetup')
import rotator as rt
import ADS1256 as ads
import deviceinfo as di
import RPi.GPIO as GPIO
import math
import serial
import socket, pickle
from threading import Thread
import time

#System configuration parameters:
#-------------------------------------------------------------------------------
#User-set parameters:

rpinum=0
showalldata=0
enable=[1,1,1,1]
SN=['55000615','55000616','55000392','55000389']
arr = [100, 100, 100, 100]
KP=[10,40,50,50]
KI=[0,0,0,0]
triglist=[0,0,0,0]
delaytime=[0,0,0,0]
readonly=0
tintegral=[0.01,0.01,0.01,0.01]
integralwindow=[10,10,10,10]
enablebuffer=0
#-------------End of setting parameters-------------------------------------------

s = socket.socket()
host = '10.141.157.93' #ip of raspberry pi
port = 12345
s.bind((host, port))
continue_prog = True

def thread1(settings):
    s.listen(5)
    arr = [100, 100, 100, 100]
    global target
    target=[2.23,0.0998,0.266,0.0173]
    initial_target = target
    while continue_prog:
        c, addr = s.accept()
        print ('Got connection from',addr)
        #c.send('Thank you for connecting')
        data_string = c.recv(1024)
        arr = pickle.loads(data_string)
        c.close()
        target = [arr[i]*initial_target[i]*0.01 for i in range(len(arr))]

thread1 = Thread( target = thread1, args = ("Thread-2", ) )
thread1.daemon = True
thread1.start()

   
try:   
#-------------------------MAIN PROGRAM-------------------------------------------------------------------------
    
    datain_high=[0x0,0x2,0x4,0x6]
    datain_low=[0x1,0x3,0x5,0x7]
    trigmenu=[3,5,7,8]
    maxdata=[0,0,0,0]
    acangle=[0,0,0,0]
    mode=[1,1,1,1]

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
    acflag=[0,0,0,0]

    ad.SetEnableBuffer(enablebuffer)
    ad.SelfCalibrate()
    while mainloopflag==1:
        calcount=0
        integrallist=[]
        for j in range(4):
            data=[]
            if trig[j].lent>0:
                GPIO.wait_for_edge(trig[j].trigpin,GPIO.RISING)\
               # time.sleep(1)
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
                datalist=data0list[1:]
                lend0=lend0-1
                if showalldata==1:
                        print('List of all measurements in channel'+str(x[i].xid)+': ',data0list)
                print('----------This is RPi'+str(rpinum)+'------------------------')
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
                output=error*KP[x[i].xid]+integral*KI[x[i].xid]

                totangle[x[i].xid]=totangle[x[i].xid]+output

                acangle[x[i].xid]=acangle[x[i].xid]+output
                if maxdata[x[i].xid]<data0ave:
                        maxdata[x[i].xid]=data0ave
                        if acflag[x[i].xid]==1:
                                acangle[x[i].xid]=output
                        else:
                                acangle[x[i].xid]=0

                if mode[x[i].xid]==1:
                    if output<0:
                         print('Channel '+str(x[i].xid+1)+': number of measurements received:'+str(lend0))    
                         print('Voltage:'+str(data0ave)+"; Moving:-; Angle="+str(output))
                         if readonly==0:
                                 x[i].m.moverel(output)

                    elif output>0:
                         print('Channel '+str(x[i].xid+1)+': number of measurements received:'+str(lend0))    
                         print('Voltage:'+str(data0ave)+"; Moving:+; Angle="+str(output))
                         if readonly==0:
                                 x[i].m.moverel(output)
                
                    if totangle[x[i].xid]> 180 or totangle[x[i].xid]<-180:
                         print('Channel '+str(x[i].xid+1)+": Request unattainable: input power too low.")
                         mode[x[i].xid]=0

                elif mode[x[i].xid]==0:
                    print('Channel '+str(x[i].xid+1)+': Original request unreachable. Moving to maximum')
                    if readonly==0:
                         if acflag[x[i].xid]==0:
                                  x[i].m.moverel(-1*acangle[x[i].xid])
                                  acflag[x[i].xid]=1
                         acangle[x[i].xid]=0
                    if maxdata[x[i].xid]>target[x[i].xid]:
                         print('Channel '+str(x[i].xid+1)+': Input power increased. Returning to normal mode')
                         mode[x[i].xid]=1
                         totangle[x[i].xid]=0
                         acflag[x[i].xid]=0
                calcount=calcount+1
                if calcount >=1000:
                         calcount=0
                         print('self calibrating')
                         ad.SelfCalibrate()
            for k in range(trig[j].lent):
                
                i=trig[j].xlist[k]

                if (mode[x[i].xid]==1)&(readonly==0):
                        x[i].m.rd(20)

    GPIO.cleanup()
#---------------------END OF MAIN PROGRAM----------------------------------------------------------------


except KeyboardInterrupt:
    continue_prog = False
