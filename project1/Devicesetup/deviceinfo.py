import serial
import serial.tools.list_ports as st
class searchstruct:
    dvcexist=0
    portstr=''
    def __init__(self,existflag,portinfostr):
        self.dvcexist=existflag
        self.portstr=portinfostr

class serialstruct:
    sersdvcexist=0
    ser=serial.Serial()
    def __init__(self,existinfo,serinfo):
        self.serdvcexist=existinfo
        self.ser=serinfo

class deviceinfo:
    sn=''
    deviceexist=0
    ser=serial.Serial
    serportopened=0
    def __init__(self,SN):
        self.sn=SN
        self.ser=serial.Serial()
        self.ser.baudrate=115200
        self.ser.timeout=0.1
        dvcsearch=devicesearch(SN)
        if dvcsearch.dvcexist==1:
            self.deviceexist=1;
            self.ser.port=dvcsearch.portstr
            try:
                self.ser.open()
            except:
                self.serportopened=self.ser.isOpen()
        else:
            self.deviceexist=0;
def devicesearch(sn):
    info=st.comports()
    leninfo=len(info)
    count=0
    while count<leninfo:
        if (len(info[count][2])==34) & (info[count][2][26:]==sn):
            return searchstruct(1,info[count][0])
        else:
            count=count+1
    return searchstruct(0,'')
