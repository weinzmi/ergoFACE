from transitions import Machine
from transitions.extensions import GraphMachine
from IPython.display import Image, display, display_png

import time
import random
import yaml
import logging
import os, sys, inspect, io


# LOGGING
# Set up logging; The basic log level will be DEBUG
logging.basicConfig(level=logging.DEBUG)
# Set transitions' log level to INFO; DEBUG messages will be omitted
logging.getLogger('transitions').setLevel(logging.INFO)



class ergoFACE(object):

    # Define some states for ergoFACE - detail state diagram
....# https://github.com/weinzmi/ergoFACE/blob/prototype-concept/images/wiki/Detailed%20State%20Diagram%20-%20prototype%20002.png
    states=['ergoFACE loading', 'program loading', 'pedaling', 'training paused', 'training error', 'ergoFACE error']


    # graph object is created by the machine
    def show_graph(self, **kwargs):
        stream = io.BytesIO()
        self.get_graph(**kwargs).draw(stream, prog='dot', format='png')
        display(Image(stream.getvalue()))


    def __init__(self, name):

        self.name = name

        # Initiate Daum8008TRS object
        Daum8008TRS = ergoFACE("DAUM Ergobike 8008 TRS")

        # What have we accomplished today?
        self.trainings_completed = 0
        self.trainings_minutes = 0
        self.trainings_distance = 0
        self.trainings_power = 0
        self.actual_wattage = 0
        self.actual_cadence = 0
        self.actual_speed = 0

        # Initialize the state machine
        self.machine = Machine(model=self, states=ergoFACE.states, initial='ergoFACE loading')

        # Add some transitions. We could also define these using a static list of
        # dictionaries, as we did with states above, and then pass the list to
        # the Machine initializer as the transitions= argument.

        # raspberry is started up and ergoFACE can start.
        self.machine.add_transition(trigger='automatic', source='ergoFACE loading', dest='program loading')

        # as soon as there is a RPM signal detected, we are in pedaling
        self.machine.add_transition('RPM', 'program loading', 'pedaling',conditions=['rpm_OK'],
                         before='select_program',
                         after='log_data')

        # stop or reset lead you back to program loading
        self.machine.add_transition('stop_reset', 'pedaling', 'program loading')

        # training Error status can be entered from '*' (all) states
        # in this state, the fallback is to select program
        self.machine.add_transition('error', ['pedaling', 'training paused'], 'training error',
                         before='GPIO_PWM_WRITE_0',
                         after='select_program')

        # ergoFace Error status can be entered from '*' (all) states
        # in this state, the fallback is to select program
        self.machine.add_transition('error', ['program loading', 'ergoFACE loading'], 'ergoFACE error',
                         after='restart_ergoFACE')


        # at the end of every program, when the last sequence is reached, 
        # the training is completed and will restart again
        self.machine.add_transition('program_finished', 'pedaling', 'program loading',
                         after='select_program')

        # when there is noRPM detected, the program will be paused
        self.machine.add_transition('noRPM', 'pedaling', 'training paused',
                         before='GPIO_PWM_WRITE_0')
        self.machine.add_transition('RPM', 'training paused', 'pedaling', conditions=['rpm_OK'])

        # Our NarcolepticSuperhero can fall asleep at pretty much any time.
        self.machine.add_transition('nap', '*', 'asleep')




# show a list of YAML file is specific directory and select
    def select_program(self):
        items = os.listdir("/home/pi/ergoFACE/src/wattprograms")

        fileList = []

        for names in items:
            if names.endswith(".yaml"):
                fileList.append(names)

        cnt = 0
        for fileName in fileList:
            sys.stdout.write( "[%d] %s\n\r" %(cnt, fileName) )
            cnt = cnt + 1


        fileName = int(raw_input("\n\rSelect program [0 - " + str(cnt - 1) + "]: "))
        print(fileList[fileName])


        f = open(fileList[fileName])
        program = yaml.safe_load(f)
        f.close()

        for program_id in program():
        duration = program[program_id]['Duration'] 
        watt = program[program_id]['Watt'] 
        print watt," Watt will be applied for ",duration,"seconds"
        time.sleep(duration)



    def rpm(self):
        
        # return transformed GPIO signal in RPM

    def rpm_OK(self):
        
        # if the else with minumim RPM signal for TRUE

    def log_data(self):
        with open("/home/pi/data_log.csv", "a") as log:
            while True:
                rpm = GPIO.....
                power = 
                distance = 
                speed = 
                log.write("{0},{1},{2},{3}\n".format(strftime("%Y-%m-%d %H:%M:%S"),str(rpm),str(power), str(distance), str(speed)))

    def restart_ergoFACE(self):
        
        # restarting all
