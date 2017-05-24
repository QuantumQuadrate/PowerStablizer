import sys
sys.path.insert(0,'/home/pi/project0/ADserial')
sys.path.insert(0,'/home/pi/project0/Rotator')
import rotator as rt
import ADserial as ADser

import math
import time
import matplotlib.pyplot as plt

target=200

KI=0
KP=0.065

rt.setup()

loopctrl=1

totangle=0

error=0
integral=0
output=0

list_I=[]
list_t=[]
t=0
I=0
plt.ion()

crnttime=time.time()
prvstime=time.time()
dt=0


plt.ion()
while loopctrl==1:        
        ADser.flush()
        data=ADser.rd()
        datanum=ADser.datastoi(data)
        print(datanum)

        I=datanum
        list_I.append(I)

        crnttime=time.time()
        dt=crnttime-prvstime
        prvstime=crnttime
        t=t+dt
        list_t.append(t)
        plt.plot(list_t,list_I,'b-',linewidth=1.0)
        plt.show()
        plt.pause(0.1)
        
        error=datanum-target
        integral=integral+error*dt
        
        outputI=KI*integral
        outputP=KP*error
        output=outputI+outputP
        
        totangle=totangle+output
        if output<0:
            print("Moving:-;Angle=",output,"P=",outputP,"I=",outputI)
            rt.moverel(output)

        elif output>0:
            print("Moving:+;Angle=",output,"P=",outputP,"I=",outputI)
            rt.moverel(output)
        
        if totangle> 360:
            print("Request unattainable: input power too low.")
            loopctrl=0

