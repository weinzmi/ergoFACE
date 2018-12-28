import os
import sys
import yaml
import time


def module_load():

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
    f.close()


def module_run():
    program = yaml.safe_load(open(dirName + fileList[fileName]))

    for seq_id in program['Prog']:
        duration = program['Prog'][seq_id]['Duration']
        watt = program['Prog'][seq_id]['Watt']
        print(watt, " Watt will be applied for ", duration, "seconds")
        time.sleep(duration)
