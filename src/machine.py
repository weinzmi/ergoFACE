import io
from transitions import *

import logging
import os, sys, inspect, io
import watt
from IPython.display import Image, display, display_png
from transitions import Machine
from transitions.extensions import GraphMachine

# LOGGING
# Set up logging; The basic log level will be DEBUG
logging.basicConfig(level=logging.DEBUG)
# Set transitions' log level to INFO; DEBUG messages will be omitted
logging.getLogger('transitions').setLevel(logging.INFO)

cmd_folder = os.path.realpath(
    os.path.dirname(
        os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0])))

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

class ergoFACE(object):

# Define some states for ergoFACE - detail state diagram
# https://github.com/weinzmi/ergoFACE/blob/prototype-concept/images/wiki/Detailed%20State%20Diagram%20-%20prototype%20002.png
    states=['ergoFACE loading', 'program loading', 'pedaling', 'training paused', 'training error', 'ergoFACE error']


    # graph object is created by the machine
    def show_graph(self, **kwargs):
        stream = io.BytesIO()
        self.get_graph(**kwargs).draw(stream, prog='dot', format='png')
        display(Image(stream.getvalue()))


    def __init__(self, name):




        # What have we accomplished today?
        self.trainings_completed = 0
        self.trainings_minutes = 0
        self.trainings_distance = 0
        self.trainings_power = 0
        self.actual_wattage = 0
        self.actual_cadence = 0
        self.actual_speed = 0

        # Initialize Graph machine
        # self.machine = GraphMachine(model=self,
        #                            states=ergoFACE.states,
        #                            initial='ergoFACE loading',
        #                            show_auto_transitions=False,  # default value is False
        #                            title="ergoFace state diagram",
        #                            show_conditions=True)

        # Initialize the state machine
        self.machine = Machine(model=self,
                               states=ergoFACE.states,
                               initial='ergoFACE loading'
                               )

        # Add some transitions. We could also define these using a static list of
        # dictionaries, as we did with states above, and then pass the list to
        # the Machine initializer as the transitions= argument.

        # raspberry is started up and ergoFACE can start.
        self.machine.add_transition(trigger='automatic', source='ergoFACE loading', dest='program loading',
                                    after='load_program')

        # as soon as there is a RPM signal detected, we are in pedaling
        self.machine.add_transition('RPM', 'program loading', 'pedaling',
                                    before='rpm_OK',
                                    after='run_program')

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

        self.machine.add_transition('RPM', 'training paused', 'pedaling',
                                    conditions=['rpm_OK'])





    def load_program(self):

        print("load watt program")
        watt.load_watt_prog()


    def rpm_OK(self):
        # return transformed GPIO signal in RPM
        print("Check if RPM is ok -> YES")


    def run_program(self):
        # if the else with minumim RPM signal for TRUE
        # instantiate a class instance here

        print("run watt program")
        watt.run_watt_prog()


    def log_data(self):
        # saved logged data
        print("TBD - save done")




Daum8008 = ergoFACE("Daum8008")

Daum8008.state  # get status
Daum8008.automatic()  # trigger
Daum8008.RPM()  # trigger

# if Graph machine is loaded, uncomment
# Daum8008.show_graph()