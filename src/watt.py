#!/usr/bin/env python3
##################################
# watt.py is used to handle the load and run of watt programs
##################################
import os
import sys
import yaml
import time
import pwm
import yamlordereddictloader


def get_user_input():

    while True:
        try:
            return int(input("\n\rSelect watt program [0 - " + str(cnt - 1) + "]: "))

        except ValueError:
            print("Invalid input. Please try again!")


def module_load():
    # this module is used for listing & seletion of watt programs
    # set variables to "global" for handling in other classes, e.g.: machine.py - class ergoFACE
    global fileName
    global fileList
    global dirName
    global cnt
    # directory for watt program files
    # issue#4 - central config and parameters to conf.yaml
    dirName = "/home/pi/ergoFACE/src/wattprogram/"
    items = sorted(os.listdir(dirName))

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
    fileName = get_user_input()
    print(fileList[fileName])
    f = open(dirName + fileList[fileName])
    f.close()


def module_run():
    # this module is used for loading & run of watt programs
    # set variables to "global" for handling in other classes, e.g.: machine.py - class ergoFACE
    global cycle
    global rpm
    global watt
    global duration
    global cyclecount
    # myergopwm = pwm.Ergopwm('watt', 12, GPIO.BOARD)  # watt is used as name of __init__ in Ergopwm

    # open the yaml stream of the file selected
    myyamlload = yaml.load(open(dirName + fileList[fileName]), Loader=yamlordereddictloader.Loader)
    myergopwm = pwm.Ergopwm()
    # cycle time used for loop control of the PWM output
    cycle = 1
    rpm = 33.3
    myergopwm.setup()
    # run the watt program
    # print(fileList[fileName])
    prog = myyamlload['Prog']['Seq1']['Name']
    description = myyamlload['Prog']['Seq1']['Description']
    print("Name: ", prog)
    print("Description: ", description)

    for seq_id in myyamlload['Prog']:

        duration = myyamlload['Prog'][seq_id]['Duration']
        watt = myyamlload['Prog'][seq_id]['Watt']

        print(watt, " Watt will be applied for ", duration, "seconds")
        # loop for control the PWM output
        # not sure, if break for low RPM is necessary here, or if it could be handled by the state machine itself?
        for cyclecount in range(duration):
            if rpm >= 30.0:  # check for pedaling
                # TBD - has to be changed to GPIO output
                print(watt, " Watt will be applied for ", duration, "seconds")
                for i in range(1, cycle*100+1):
                    myergopwm.output(watt/800*100)
                    # rpm = float(input("RPM: "))
                    time.sleep(cycle/100)

            else:  # if there is no pedaling; PRM < 30, then loop for pause; no next sequencing from yaml file
                myergopwm.stop()
                while rpm < 30.0:
                    print(" 0 Watt will be applied , Training paused")
                    # rpm = float(input("RPM: "))
                    time.sleep(cycle)

    myergopwm.destroy()  # destroy for the automatic loading after finishing the watt program
    yaml.dump_all(myyamlload)
