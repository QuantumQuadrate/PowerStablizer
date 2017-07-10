import sys
sys.path.insert(0,'/home/pi/project1/Shield')
sys.path.insert(0,'/home/pi/project1/Rotator')
sys.path.insert(0,'/home/pi/project1/Devicesetup')
import rotator as rt
import ADS1256 as ads
import deviceinfo as di
import time


#System configuration parameters:
#-------------------------------------------------------------------------------
#User-set parameters:

#(bool)INUSE:1 for using,0 for not using the channel
#(bool)MODE:1 for running continously,0 for running with triggering signals
#(string)SN:Serial number for the rotator connected to the channel, if in use
#(int)target:Stablization target for the laser in the channel, if in use
#(float)KP:feedback parameter, if in use
#(float)KI:feedback parameter, if in use

INUSE=[1,1,1,1]
MODE=[0,0,0,0]
SN=['55000491','55000389','55000392','55000604']
target=[0,0,0,0]
KP=[0,0,0,0]
KI=[0,0,0,0]
triglist=[0,0,0,0]
#-------------------------------------------------------------------------------
#Default parameters:

#(int)trigin:the port on the box that is used for trigger input
#(int)datain:the port on the box that is used for data input

datain_high=[0x0,0x2,0x4,0x6]
datain_low=[0x1,0x3,0x5,0x7]


#------------------------------------------------------------------------------
#Dependent variables:

portaddr=[]
motor=[]
totnum=0

for count in range(4):
    datain_high.append(hex(datain[count]*2))
    datain_low.append(hex(datain[count]*2+1))
    trig.append(triglist[trigin[count]])
    if INUSE[count]==1:
        deviceinfo=di.deviceinfo(SN[count])
        if deviceinfo.deviceexist==0:
            print('Error: Cant find device with serial number:'+SN[count])
            print('Program will continue regardless of this issue')
            time.sleep(5)
        else:
            print('Device with serial number '+SN[count]+' has been successfully set up')
            portaddr.append(deviceinfo.ser.port)
            motor.append(rt.K10CR1(deviceinfo.ser))
            #print(motor[count].ser)
            totnum+=1

            
trig=[]
for count in range(4):
    if triglist[count]==0:
        trig[count]=0
    elif triglist[count]==1:
        trig[count]=0
    elif triglist[count]==2:
        trig[count]=0
    elif triglist[count]==3:
        trig[count]=0

for count in range(totnum):
    motor[count].moverel(10+10*count)

