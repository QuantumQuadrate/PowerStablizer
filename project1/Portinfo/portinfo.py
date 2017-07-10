import serial
import serial.tools.list_ports as st

def getport(sn):
    info=st.comports()
    leninfo=len(info)
    count=0
    while count<leninfo:
        if (len(info[count][2])==34) & (info[count][2][26:]==sn):
            return info[count][0]
        else:
            count=count+1
    return 'device not found'
#print(getports('55000425'))
