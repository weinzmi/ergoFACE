import os
import sys
import yaml
import time


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
    test.fileName = int(input("\n\rSelect watt program [0 - " + str(test.cnt - 1) + "]: "))
    print(test.fileList[test.fileName])
    f = open(test.dirName + test.fileList[test.fileName])
    program = yaml.safe_load(f)
    f.close()


def run_watt_prog():
  

    for program_id in load_watt_prog.program['Prog']:
        duration = load_watt_prog.program['Prog'][program_id]['Duration']
        watt = load_watt_prog.program['Prog'][program_id]['Watt']
        print(watt, " Watt will be applied for ", duration, "seconds")
        time.sleep(duration)