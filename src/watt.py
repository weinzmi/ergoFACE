#!/usr/bin/env python3
########################################################################
# watt.py is used to handle the load and run of watt programs
########################################################################
import os
import sys
import yaml
import time
import pwm
import yamlordereddictloader


def module_load():
    # this module is used for listing & seletion of watt programs
    # set variables to "global" for handling in other classes,
    # e.g.: machine.py - class ergoFACE
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
    print("watt ------------ installed programs")
    for fileName in fileList:
        sys.stdout.write("[%d] %s\n\r" % (cnt, fileName))
        cnt = cnt + 1

    # select per index the watt program
    # issue#5 - error handling in watt.py module load
    fileName = get_user_input()
    print("watt ------------ selected File:\n\r", fileList[fileName])
    f = open(dirName + fileList[fileName])
    f.close()


def get_user_input():

    while True:
        try:
            return int(input("\n\rwatt ------------ Select watt program [0 - " + str(cnt - 1) + "]: "))

        except ValueError:
            print("wattwatt ------------ Invalid input. Please try again!")


def module_run():
    # this module is used for loading & run of watt programs

    global cycle
    global rpm
    global rpm_limit
    global offset
    global rawwatt
    global watt
    global duration
    global cyclecount

    # create instance of class; open the yaml stream of the file selected
    myyamlload = yaml.load(open(dirName + fileList[fileName]),
                           Loader=yamlordereddictloader.Loader)
    # create instance of class
    myergopwm = pwm.Ergopwm()
    # cycle time used for loop control of watt program sequence parsing,
    # MUST BE 1 SECOND BECAUSE OF YAML STRUCTURE
    # !!!! cycle time for loop control of PWM signal is connected to this
    cycle = 1
    # !!!! hardcoded RPM value; has to be changed to RPM GPIO input
    rpm = 33.3
    # !!!! RPM limit has to be in central config file
    rpm_limit = 30.0
    # setup the GPIOs
    offset = 0.0
    # manual watt offset
    myergopwm.setup()
    # Output the name and description of yaml file
    prog = myyamlload['Prog']['Seq1']['Name']
    description = myyamlload['Prog']['Seq1']['Description']
    print("watt ------------ Name: ", prog)
    print("watt ------------ Description: ", description)
    # run the watt program
    for seq_id in myyamlload['Prog']:
        # get the duration and watt from yaml file
        duration = myyamlload['Prog'][seq_id]['Duration']
        watt = myyamlload['Prog'][seq_id]['Watt']
        print("watt ------------ ", watt+offset,
              "Watt will be applied for", duration, "seconds")
        # GPIO output loop of PWM signal
        for cyclecount in range(duration):
            # loop for seq in yaml file, later if/else is used for running and
            # pausing the sequence count
            if rpm >= rpm_limit:
                # check for RPM limit
                print("watt ------------ ", watt+offset,
                      "W --- @ ---", rpm, "RPM")
                for i in range(1, cycle*100+1):
                    # write the GPOIs; convert 800w to 100%
                    # !!!! this must be in central config yaml
                    myergopwm.output((watt+offset)/800*100)
                    # this sleep is 0.01 second looptime for PWM
                    time.sleep(cycle/100)
            else:
                # # check for RPM limit; pause the sequence of yaml file
                myergopwm.stop()
                # stop GPIO output
                print("watt ------------ stop GPIO output")
                while rpm < rpm_limit:
                    # keep inside while for pausing the sequence of yaml
                    print("watt ------------ 0 Watt will be applied , Training paused")
                    time.sleep(cycle)

    # destroy for the automatic loading after finishing the watt program
    myergopwm.destroy()
    # dump for the automatic loading after finishing the watt program
    yaml.dump_all(myyamlload)
