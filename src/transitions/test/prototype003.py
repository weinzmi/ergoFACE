# #######################
# transition section
# #######################
# Import
import time
import yaml


# LOGGING
# Set up logging; The basic log level will be DEBUG
import logging
logging.basicConfig(level=logging.DEBUG)
# Set transitions' log level to INFO; DEBUG messages will be omitted
logging.getLogger('transitions').setLevel(logging.INFO)

# Diagram initialization
import os, sys, inspect, io

cmd_folder = os.path.realpath(
    os.path.dirname(
        os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0])))

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)
    
from transitions import *
from transitions.extensions import GraphMachine
from IPython.display import Image, display, display_png

# Basic initialization
class ergoFACE(object):

    
    # graph object is created by the machine
    def show_graph(self, **kwargs):
        stream = io.BytesIO()
        self.get_graph(**kwargs).draw(stream, prog='dot', format='png')
        display(Image(stream.getvalue()))


    def __init__(self):
        self.wattage = 0
        self.cadence = 0
    # Note that the sole argument is now the EventData instance.
    # This object stores positional arguments passed to the trigger method in the
    # .args property, and stores keywords arguments in the .kwargs dictionary.
    def set_environment(self, event):
        self.wattage = event.kwargs.get('wattage', 0)
        self.cadence = event.kwargs.get('cadence', 0)
    def print_pressure(self): print("Current cadence is %.2f rpm." % self.cadence)
    def print_wattage(self): print("Current wattage is %.2f Watt." % self.wattage)

# ##################################
# select program
# ##################################
....def select_program(self):
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

# ##################################
# apply program
# ##################################

....def apply_program(self):
        f = open(fileList[fileName])
        program = yaml.safe_load(f)
        f.close()

# ##################################
# output PWM via GPIO
# ##################################




training = ergoFACE()


# The states of training
states=['ergoFACE loading', 'program loading', 'pedaling', 'training paused', 'training error', 'ergoFACE error']

# Transitions between states. 
# transitions
transitions = [
    { 'trigger': 'automatic', 'source': 'ergoFACE loading', 'dest': 'program loading' },
    { 'trigger': 'error', 'source': 'ergoFACE loading', 'dest': 'ergoFACE error' },
    { 'trigger': 'RPM', 'source': 'program loading', 'dest': 'pedaling' , 'before':'select_program', 'after':'apply_program'},
    { 'trigger': 'error', 'source': 'program loading', 'dest': 'ergoFACE error' },
    { 'trigger': 'stop reset', 'source': 'pedaling', 'dest': 'program loading' },
    { 'trigger': 'end of sequence reached', 'source': 'pedaling', 'dest': 'program loading' },
    { 'trigger': 'noRPM', 'source': 'pedaling', 'dest': 'training paused' },
    { 'trigger': 'error', 'source': 'pedaling', 'dest': 'training error' },
    { 'trigger': 'RPM', 'source': 'training paused', 'dest': 'pedaling' },
    { 'trigger': 'error', 'source': 'training paused', 'dest': 'training error' },
    { 'trigger': 'timeout', 'source': 'training error', 'dest': 'program loading' }
]

# Initialize
machine = Machine(training, states=states, transitions=transitions, send_event=True, initial='ergoFACE loading')


training.state

training.automatic()

training.state
