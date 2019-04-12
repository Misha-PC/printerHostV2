
from time import sleep

def readFile(fileName):
    f = open(fileName)
    str_ = f.read()
    f.close()
    return(str_)

def parsGCode(str, type="text"):
    if type == "file":
        str = readFile(str)

    str = str.replace("\n\n", "\n")
    currentCode = ''
    currentComment = ''
    write = True
    outArr = []

    for i in str:

        if i == ';':
            write = False
            currentCode += "\n"

        if "\n" in currentCode:
            if currentCode != "\n":
                outArr.append(currentCode)
            currentCode = ''

        if write:
            currentCode += i
        else:
            currentComment += i

        if "\n" in currentComment:
            currentComment = ''
            write = True

    return(outArr)

def request(gCode, object):
    gCode += "\n"
    object.write(gCode.encode())
    sleep(0.2)

def readPort(p):
    try:
        out_ = p.readlines() + '\n'
    except Exception as e:
        out_ = str(e)
    print('readPort', p)
    return(out_)

def makeSlicerCommand(fileName):
    command = "slic3r "
    param = ["--nozzle-diameter", "--temperature", "--first-layer-temperature", "--layer-height", "--first-layer-height", "--retract-length", "--skirts", "--brim-width", "--extrusion-multiplier"]
    default=["0.4",                     "255",                  "255",                  "0.1",                 "0.4",               "3",            "2",           "0",                "2.5",       ]
    for i in param:
        in_ =  input(i + " : ")
        if in_ != '':
            command += " " + i + " " + in_
        else:
            command += " " + i + " " + default[param.index(i)]

    command += " " + fileName

    return (command)

if __name__ == '__main__':
    print(makeSlicerCommand("test.stl"))
