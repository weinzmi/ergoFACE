import os
import sys
import yaml


def load_watt_prog():
    # TBD change to automatic directory detection
    global fileName
    global fileList
    global dirName

    dirName = 'C:\\Users\\weikami\\Documents\\GitHub\\ergoFACE\\src\\wattprogram\\'
    items = os.listdir(dirName)

    fileList = []

    for names in items:
        if names.endswith(".yaml"):
            fileList.append(names)

    cnt = 0

    for fileName in fileList:
        sys.stdout.write("[%d] %s\n\r" % (cnt, fileName))
        cnt = cnt + 1
    fileName = int(input("\n\rSelect watt program [0 - " + str(cnt - 1) + "]: "))
    print(fileList[fileName])
    f = open(dirName + fileList[fileName])
    program = yaml.safe_load(f)
    f.close()