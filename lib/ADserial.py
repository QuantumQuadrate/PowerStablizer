import serial

ADportstr='/dev/ttyACM0'


#Prepare the input serial:

ser=serial.Serial()
ser.baudrate=9600

def setup():
     serportprefix='/dev/ttyACM'
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

setup()

print("Serial information:",ser)



#Input Control: Some functions related to data reading from the board

#flush(): flush the excess input stored in the serial
def flush():
    ser.flushInput()
    ser.readline()
    ser.readline()
    ser.readline()
    ser.readline()
    ser.readline()
    return

#rd(): read a line from the input serial(rd() returns a byte string, need to convert the string to number)
def rd():
    return ser.readline()

#seropen():open the serial
def seropen():
    return ser.open()

#serclose():close the serial
def serclose():
    return ser.close()

#datastoi(x): convert the result fron rd() to a normal number
def datastoi(x):
    length=len(x)
    if length ==5:
        return 100*(x[0]-48)+10*(x[1]-48)+x[2]-48
    elif length ==4:
        return 10*(x[0]-48)+x[1]-48
    elif length ==3:
        return x[0]-48
    elif length ==6:
        return 1000*(x[0]-48)+100*(x[1]-48)+10*(x[2]-48)+x[3]-48
