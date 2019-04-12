import serial, time, os, sched, threading, function


class host(object):
    """docstring for host."""
    def __init__(self):
        super(host, self).__init__()
        self.port       =    None
        self.baudrate   =    19200
        self.connected  =    False
        self.printing   =    False
        self.readActiv  =    threading.Event()
        self.printer    =    serial.Serial()
        self.sched      =    sched.scheduler(time.time, time.sleep)
        self.lastMsg    =    None
        self.cTempE     =    0

    def __del__(self):
            if self.connected:
                A.executeGCode("M104 S0\n")
                A.disconect()
            print('class destroed success!')

    def printObject(self, gcode):
        print("PREREAR TO PRINTING..................")
        if not self.connected:
            self.connect()
        self.stopRead()

        x_ = "b'ok\n"
        count = 0
        expectGCode = ''
        len_ = len(gcode)
        print("START PRINTING..................")
        for i in gcode:
            while " \n" in i:
                i = i.replace(" \n", "\n")
            while not("ok" in x_):
                try:
                    time.sleep(0.002)
                    x_ = str(self.printer.readline())
                    print(x_)
                except Exception as e:
                    print(e)
            self.printer.write(i.encode())
            print(i)
            if i[:3] in expectGCode:
                x_ = 'ok'
                print('except!!')
            else:
                x_ = ''
            count += 1
            print("Progress:" + (str(count / len_ * 100)) + "%\n")
        self.startRead()
        # M114 - coordinates
        # M105 - temp

    def printFile(self, fileName):
        print("printFile...")
        self.printObject(function.parsGCode(fileName, 'file'))

    def startRead(self):
        print("startRead")
        self.readActiv = threading.Event()
        self.passiveRead(self.readActiv)

    def  stopRead(self):
        print("stopRead")
        self.readActiv.set()

    def disconect(self):
        if self.connected:
            self.printer = serial.Serial()
            self.stopRead()
            self.connected = False
            print("DISCONECTED!!")
            return(0)
        print("was not connected.")
        return(-1)


    def passiveRead(self, arg):
        if self.detectPort() == -1:
            self.disconect()
        else:
            if not arg.is_set():
                try:
                    self.lastMsg = self.printer.readline()
                    print(self.lastMsg)
                    threading.Timer(0.1, self.passiveRead, [arg]).start()
                except Exception as e:
                    print("Error reading")
                    threading.Timer(2, self.passiveRead, [arg]).start()

    def connect(self):
        if self.connected:
            self.startRead()
            return(0)
        c = 0
        c_ = 5
        while self.detectPort() and c < c_:
            print("Port not detected.. ", c_-c)
            time.sleep(2)
            c += 1
        if self.port == None:
            print("connect error")
            return(-1)
        self.conected = True
        self.printer = serial.Serial(self.port, self.baudrate)
        print("Connecting to ", self.port, " ", self.baudrate)
        self.connected = True
        self.startRead()
        time.sleep(5)
        print("Connecting success!!")

        return(0)

    def executeGCode(self, gCode_):
        print("executeGCode")
        if not(self.connected):
            print("execute GCode error. Connect failed")
            return(-1)
        print("send to printer ", gCode_.encode())
        self.printer.write(gCode_.encode())
        return(0)

    def detectPort(self):
        p_  = ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyACM0", "/dev/ttyACM1"]
        p__ = os.listdir("/dev")
        for i in p_:
            if i[5:] in p__:
                self.port = i
                return(0)
        self.port = None
        return(-1)

    def getTemp(self):
        if not(self.connected):
            print("ERROR: printer not connected")
            return(-1)
        print("getTemp")
        self.printer.write(b'M105\n')
        while not("T:" in str(self.lastMsg)):
            time.sleep(0.01)
        tempStr = str(self.lastMsg)
        tPos = tempStr.find("T:")
        tempStr = tempStr[tPos+2: tPos+8].replace(" ", "")
        self.cTempE = float(tempStr)
        print("Temp:", self.cTempE)

        return(0)

    def getData(self):
        print("Port     :", self.port        )
        print("Baudrate :", self.baudrate    )
        print("conected :", self.connected   )
        print("Temp     :", self.cTempE      )


if __name__ == '__main__':
    A = host()
    A.__init__()
    arg_ = '-h'
    while arg_ != "-e" or  arg_ != "--exit" :

        if arg_ == "-e" or arg_ == "--exit":
            print("exit....")
            # A.__del__()
            A = None
            break
        if arg_ == "-c" or arg_ == "--connect":
            A.connect()
        elif arg_ == "-d" or arg_ == "--disconect":
            A.disconect()
        elif arg_ == "-gd" or arg_ == "--get-data":
            A.getData()
        elif arg_ == "-gt" or arg_ == "--get-temp":
            A.getTemp()
        elif arg_ == "-h" or arg_ == "--help":
            print("usage '--connect' ('-c') to connect printer")
            print("usage '--disconnect' ('-d') to disconnect printer")
            print("usage '--get-data' ('-gd') to get printer data")
            print("usage '--get-temp' ('-gt') to update temp")
            print("usage '-g <Gcode [arg]..>'  to send gCode")

        elif "-g" in arg_:

            A.executeGCode(arg_.replace("-g ", "")+"\n")

        arg_ = input()
    print("success finish!")
