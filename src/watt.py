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
import csv
import math

CSVHEADER = ['TIME', 'POWER', 'CADENCE', 'DUTYCYCLE']


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
            return int(input("\n\rwatt ------------ Select watt program [0 - "
                             + str(cnt - 1) + "]: "))

        except ValueError:
            print("wattwatt ------------ Invalid input. Please try again!")


def dutycycle_model():

    global factor_a
    global factor_b
    global exponent
    global factor_c
    global conversion
    global reference_cadence
    global dutycycle

    factor_a = 6.4
    factor_b = 70.252
    exponent = -0.571
    factor_c = 50.0
    reference_cadence = 75.0

    conversion = ((factor_c + rpm)/(factor_c + reference_cadence))
    # not sure if the 100 -  is neccessary here, in CSV it is shown correct,
    # but on oscilloscope it is reversed
    dutycycle = 100 - (factor_b * math.pow(watt + offset, exponent)
                       * factor_a * conversion)
    return dutycycle


def module_run(csvfile):
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
    # initiation of CSV file header and writer
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(CSVHEADER)

    # cycle time used for loop control of watt program sequence parsing,
    # MUST BE 1 SECOND BECAUSE OF YAML STRUCTURE
    # !!!! cycle time for loop control of PWM signal is connected to this
    cycle = 1
    # !!!! hardcoded RPM value; has to be changed to RPM GPIO input
    rpm = 75.0
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
        # get date and time for filename
        # open csv file for training session

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
                # run duty cycle model for watt to PWM calculation every 1sec
                dutycycle_model()
                # check for RPM limit
                print("watt ------------ ", watt+offset,
                      "W --- @ ---", rpm, "RPM")
                # write data to csv
                timestr = time.strftime("%Y%m%d-%H%M%S")
                csv_writer.writerow([timestr, watt, rpm, dutycycle])
                csvfile.flush()

                for i in range(1, cycle*100+1):
                    # duty cycle model is calulatedin dev dutycycle_model()
                    # !!!! this must be in central config yaml
                    myergopwm.output(dutycycle)
                    # this sleep is 0.01 second looptime for PWM
                    time.sleep(cycle/100)
            else:
                # # check for RPM limit; pause the sequence of yaml file
                myergopwm.stop()
                # stop GPIO output
                print("watt ------------ stop GPIO output")
                while rpm < rpm_limit:
                    # keep inside while for pausing the sequence of yaml
                    print("watt ------------ 0 Watt will be applied ,"
                          " Training paused")
                    time.sleep(cycle)

    # close training csv file

    # destroy for the automatic loading after finishing the watt program
    myergopwm.destroy()
    # dump for the automatic loading after finishing the watt program
    yaml.dump_all(myyamlload)
