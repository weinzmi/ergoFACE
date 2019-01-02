########################################################################
# machine.py is used to handle the state machine
# for ergoFACE, states, triggers, conditions,...
########################################################################
import logging
import os
import sys
import inspect
import io
import watt
import time
from IPython.display import Image, display, display_png
from transitions.extensions import HierarchicalGraphMachine
from IPython.display import Image, display, display_png

# issue#4 - central config and parameters to conf.yaml
# Set up logging; The basic log level will be DEBUG
# Set transitions' log level to INFO; DEBUG messages will be omitted
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('transitions').setLevel(logging.INFO)


cmd_folder = os.path.realpath(
    os.path.dirname(
        os.path.abspath(os.path.split(inspect.getfile
                                      (inspect.currentframe()))[0])))

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


# state machine class
class ergoFACE(object):
    # definition of states
    states = ['ergoFACE loading',
              'program loading',
              'ergoFACE error',
              {'name': 'training',
               'children':
                   ['pedaling',
                    'paused',
                    'finished',
                    'error']
               }
              ]

    def __init__(self, name):

        # Initialize Graph machine
        # put in here twice for easy testing w/o graph
        self.machine = HierarchicalGraphMachine(
            model=self,
            states=ergoFACE.states,
            initial='ergoFACE loading',
            show_auto_transitions=False,
            title="ergoFace state diagram",
            show_conditions=True)

        # Initialize the state machine
        # self.machine = Machine(model=self,
        #                        states=ergoFACE.states,
        #                        initial='ergoFACE loading'
        #                        )

        # Transitions between the states

        # raspberry is started up and ergoFACE can start.
        self.machine.add_transition(
            trigger='AUTOMATIC',
            source='ergoFACE loading',
            dest='program loading',
            before='initialise',
            after='load_program')

        # as soon as there is a RPM signal detected, we are in training
        self.machine.add_transition(
            'LOADED',
            'program loading',
            'training',
            conditions='rpm_OK')

        self.machine.add_transition(
            'RPM',
            ['training_paused', 'training_finished', 'training'],
            'training_pedaling',
            conditions='rpm_OK',
            after='run_program')

        self.machine.add_transition(
            'NO_RPM',
            'training_pedaling',
            'training_paused',
            before='pause_program')

        self.machine.add_transition(
            'RESET',
            ['training', 'training_error'],
            'program loading',
            conditions=['rpm_OK'],
            after='load_program')

        self.machine.add_transition(
            'RESET',
            'ergoFACE error',
            'ergoFACE loading',
            before='restart_ergoFACE')

        self.machine.add_transition(
            'ERROR',
            ['program loading', 'ergoFACE loading', 'training'],
            'ergoFACE error',
            after='restart_ergoFACE')

        self.machine.add_transition(
            'ERROR',
            ['training_paused', 'training_pedaling', 'training_finished'],
            'training_error',
            before='restart_ergoFACE')

        self.machine.add_transition(
            'FINISH',
            'training_pedaling',
            'training_finished')

        self.machine.add_transition(
            'NO_RPM',
            'training',
            'training_paused',
            before='GPIO_PWM_WRITE_0')

        # draw the whole graph
        self.machine.get_graph().draw(
            'ergoFACE_transition_diagram.png', prog='dot'
            )

    # micro programs that are executed depending on the Callback resolution
    # and execution order

    # graph object is created by the machine
    def show_graph(self, **kwargs):
        stream = io.BytesIO()
        self.get_graph(**kwargs).draw(stream, prog='dot', format='png')
        display(Image(stream.getvalue()))

    def initialise(self):
        print(
            "ergoFACE -------- Welcome, Initialising ergoFACE")
        # confirm = str(input("set Trigger to go to Status Program loading : "))

    def load_program(self):
        print(
            "ergoFACE -------- Watt program loader,\n\rplease select your program:")
        watt.module_load()

    def rpm_OK(self):
        print("ergoFACE -------- Check for RPM signal")
        # return transformed GPIO signal in RPM
        print("ergoFACE -------- RPM signal OK; automated set to OK")

        return True

    def run_program(self):
        # if the else with minumim RPM signal for TRUE
        # instantiate a class instance here
        try:
            print("ergoFACE -------- Start the selected watt program")
            watt.module_run()
            Daum8008.FINISH()
            Daum8008.RPM()
        except KeyboardInterrupt:
            Daum8008.ERROR()

    def pause_program(self):
        # stop / halt program
        print("ergoFACE -------- TBD - stop")

    def GPIO_PWM_WRITE_0(self):
        print("ergoFACE -------- NO RPM - 0PWM output")

    def log_data(self):
        # saved logged data
        print("ergoFACE -------- TBD - log_data")

    def restart_ergoFACE(self):
        # restart
        print("ergoFACE -------- TBD - restart")


##################################
# simulation of usecases
##################################
# instantiate the class
Daum8008 = ergoFACE("Daum8008")

# if Graph machine is loaded, uncomment
# Daum8008.show_graph()
# Triggers

print("SIMULATOR ------- trigger AUTOMATIC set")
Daum8008.AUTOMATIC()

print("SIMULATOR ------- trigger LOADED set")
Daum8008.LOADED()

print("SIMULATOR ------- wait for 1 second")
time.sleep(1)

print("SIMULATOR ------- trigger RPM set")
Daum8008.RPM()

# print("SIMULATOR ------- wait for 1 second")
# time.sleep(1)

# Daum8008.NO_RPM()
# print("SIMULATOR ------- trigger noRPM set")

# Daum8008.error()
# Daum8008.noRPM()
