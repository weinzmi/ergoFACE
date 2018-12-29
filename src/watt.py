##################################
# watt.py is used to handle the load and run of watt programs
##################################
import os
import sys
import yaml
import time


def module_load():
    # this module is used for listing & seletion of watt programs

    # set variables to "global" for handling in other classes, e.g.: machine.py - class ergoFACE
    global fileName
    global fileList
    global dirName
    # directory for watt program files
    # issue#4 - central config and parameters to conf.yaml
    dirName = 'C:\\Users\\weikami\\Documents\\GitHub\\ergoFACE\\src\\wattprogram\\'
    items = os.listdir(dirName)

    fileList = []
    # get list of yaml files in directory
    for names in items:
        if names.endswith(".yaml"):
            fileList.append(names)

    cnt = 0
    # output the list of yaml files
    for fileName in fileList:
        sys.stdout.write("[%d] %s\n\r" % (cnt, fileName))
        cnt = cnt + 1
    # select per index the watt program
    # issue#5 - error handling in watt.py module load
    fileName = int(input("\n\rSelect watt program [0 - " + str(cnt - 1) + "]: "))
    print(fileList[fileName])
    f = open(dirName + fileList[fileName])
    f.close()


def module_run():
    # this module is used for loading & run of watt programs
    # open the yaml stream of the file selected
    program = yaml.safe_load(open(dirName + fileList[fileName]))
    # cycle time used for loop control of the PWM output
    cycle = 1
    rpm = 0.0
    # run the watt program
    print(fileList[fileName])
    for seq_id in program['Prog']:
        duration = program['Prog'][seq_id]['Duration']
        watt = program['Prog'][seq_id]['Watt']

        # loop for control the PWM output
        # not sure, if break for low RPM is necessary here, or if it could be handled by the state machine itself?
        for cyclecount in range(duration):
            if rpm >= 30.0:  # check for pedaling
                # TBD - has to be changed to GPIO output
                print(watt, " Watt will be applied for ", duration, "seconds")
                rpm = float(input("RPM: "))
                time.sleep(cycle)
            else:  # if there is no pedaling; PRM < 30, then loop for pause; no next sequencing from yaml file
                while rpm < 30:
                    print(" 0 Watt will be applied , Training paused")
                    rpm = float(input("RPM: "))
                    time.sleep(cycle)
