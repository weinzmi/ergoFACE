import os
import sys
import yaml


def module_load():
    # TBD change to automatic directory detection

    global dirName
    global fileList
    global fileName

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

