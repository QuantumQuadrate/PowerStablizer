
import serial
import math

#---------------------------------------------------------
ser=serial.Serial()
ser.baudrate=115200
ser.timeout=0.1
def setup():
     serportprefix='/dev/ttyUSB'
     serportnum=0;

     while(serportnum<10):
          strnum=str(serportnum)
          serport=serportprefix+strnum
          ser.port=serport
          flag=0
          try:
               x=ser.open()
               flag=1
          except:
               flag=0
          if flag==1:
               return 0
               break
          serportnum=serportnum+1
     return 1
#--------------------------------------------------------

def angle_to_DU(ang):
     return int(ang*24576000/180)

def DU_to_angle(DU):
     return (DU*180/24576000)

def dth(x,bytelen):
     if x>=0:
         hstring=hex(x)
         hstring=hstring[2:]
         while(len(hstring)<2*bytelen):
             hstring='0'+hstring
         count=0
         new=list(hstring)
         while count<bytelen*2:
             tmp=new[count]
             new[count]=new[count+1]
             new[count+1]=tmp
             count=count+2
         hstring=''.join(new)
         hstring=hstring[::-1]
         return hstring
     elif x<0:
         y=abs(x)
         bstring=bin(y)
         bstring=bstring[2:]
         while(len(bstring)<2*bytelen*4):
             bstring='0'+bstring
         #print(bstring)
         count=0
         new=list(bstring)
         while count<2*bytelen*4:
               if new[count]=='1':
                    new[count]='0'
               else:
                    new[count]='1'
          
               count=count+1
         bstring=''.join(new)
         #print(bstring)
         count=2*bytelen*4-1
         add='1'
         while count>-1:
              if new[count]!=add:
                   add='0'
                   new[count]='1'
              else:
                   new[count]='0'
              count=count-1
         bstring=''.join(new)
         #print(bstring)
         hstring=hex(int(bstring,2))
         hstring=hstring[2:]
         while(len(hstring)<2*bytelen):
             hstring='0'+hstring
         count=0
         new=list(hstring)
         while count<bytelen*2:
             tmp=new[count]
             new[count]=new[count+1]
             new[count+1]=tmp
             count=count+2
         hstring=''.join(new)
         hstring=hstring[::-1]
         return hstring
def btd(x):
     bytelen=len(x)
     count=0
     dvalue=0;
     while(count<bytelen):
          dvalue=dvalue+x[count]*(math.pow(256,count))
          count=count+1
     bstring=bin(int(dvalue))
     if len(bstring)<2*bytelen*4+2:
          return int(dvalue)
     elif len(bstring)>2*bytelen*4+2:
          print('Error:Error in byte conversion')
     else:
          bstring=bin(int(dvalue-1))
          bstring=bstring[2:]
          count=0
          new=list(bstring)
          while count<2*bytelen*4:
               if new[count]=='1':
                    new[count]='0'
               else:
                    new[count]='1'          
               count=count+1
          bstring=''.join(new)
          return (int(bstring,2))*(-1)
          
def htb(x):
    return bytearray.fromhex(x)

def rd(bytelen):
    x=ser.readline()
    while(len(x)<bytelen):
         x=x+ser.readline()
    return x

def write(x):
    command=htb(x)
    #print(command)
    return ser.write(command)
#-------------------------------------------------------------
def identify():
     return write('230200005001')

def home():
    write('430401005001')
    return rd(6)
def moverel(x):
    relpos=dth(angle_to_DU(x),4)
    chan='0100'
    header='48040600d001'
    hcmd=header+chan+relpos
    #print(hcmd)
    write(hcmd)
    return rd(20)

def moveabs(x):
     abspos=dth(angle_to_DU(x),4)
     chan='0100'
     header='53040600d001'
     hcmd=header+chan+abspos
     #print(hcmd)
     write(hcmd)
     return rd(20)

def jog():
     write('6a0401015001')
     return rd(20)

def getpos():
     write('110401005001')
     bytedata=rd(12)
     bytedata=bytedata[8:]
     x=DU_to_angle(btd(bytedata))
     return float('%.3f'%x)

