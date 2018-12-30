##################################
# machine.py is used to handle the state machine for ergoFACE, states, triggers, conditions,...
##################################
import logging
import os, sys, inspect, io
import watt
import time
import pygraphviz
from IPython.display import Image, display, display_png
from transitions import Machine
from transitions.extensions import GraphMachine

# issue#4 - central config and parameters to conf.yaml
# Set up logging; The basic log level will be DEBUG
# Set transitions' log level to INFO; DEBUG messages will be omitted
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('transitions').setLevel(logging.INFO)

cmd_folder = os.path.realpath(
    os.path.dirname(
        os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0])))

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

# state machine class
class ergoFACE(object):

    # definition of states
    states=['ergoFACE loading', 'program loading', 'pedaling', 'training paused', 'training error', 'ergoFACE error']

    def show_graph(self, **kwargs):
        stream = io.BytesIO()
        self.get_graph(**kwargs).draw(stream, prog='dot', format='png')
        display(Image(stream.getvalue()))

    def __init__(self, name):

        # Initialize Graph machine - put in here twice for easy testing w/o graph
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

        # Transitions between the states

        # raspberry is started up and ergoFACE can start.
        self.machine.add_transition(trigger='automatic', source='ergoFACE loading', dest='program loading',
                                    before='initialise',
                                    after='load_program')

        # as soon as there is a RPM signal detected, we are in pedaling
        self.machine.add_transition('RPM', 'program loading', 'pedaling',
                                    before='rpm_OK',
                                    after='run_program')

        # stop or reset lead you back to program loading
        self.machine.add_transition('stop_reset', 'pedaling', 'program loading')

        # RPM OK sub state (not sure if it has to be nested)
        # this came up during trigger testing, so for failsafe we need this status?
        #self.machine.add_transition('RPM', 'pedaling', 'PRM OK')


        # training Error status can be entered from '*' (all) states
        # in this state, the fallback is to select program
        self.machine.add_transition('error', ['pedaling', 'training paused', 'RPM', 'noRPM'], 'training error',
                                    before='GPIO_PWM_WRITE_0',
                                    after='load_program')

        # ergoFace Error status can be entered from '*' (all) states
        # in this state, the fallback is to select program
        self.machine.add_transition('error', ['program loading', 'ergoFACE loading'], 'ergoFACE error',
                                    after='restart_ergoFACE')

        # at the end of every program, when the last sequence is reached, 
        # the training is completed and will restart again
        self.machine.add_transition('program_finished', 'pedaling', 'pedaling',
                                    after='run_program')

        # when there is noRPM detected, the program will be paused
        self.machine.add_transition('noRPM', 'pedaling', 'training paused',
                                    before='GPIO_PWM_WRITE_0')

        self.machine.add_transition('RPM', 'training paused', 'pedaling',
                                    conditions=['rpm_OK'])

    # micro programs that are executed depending on the Callback resolution and execution order
    # https://github.com/pytransitions/transitions#callback-resolution-and-execution-order

    def initialise(self):
         print("Initialising ergoFACE, user confirmation required:")
         # confirm = str(input("set Trigger to go to Status Program loading : "))

    def load_program(self):
        print("load watt program")
        watt.module_load()

    def rpm_OK(self):
        # return transformed GPIO signal in RPM
        print("Check for RPM signal; RPM signal OK")

    def run_program(self):
        # if the else with minumim RPM signal for TRUE
        # instantiate a class instance here
        try:
            print("Start the selected watt program")
            watt.module_run()
            Daum8008.program_finished()
        except KeyboardInterrupt:
            Daum8008.error()

    def GPIO_PWM_WRITE_0(self):
        print("NO RPM - 0PWM output")


    def log_data(self):
        # saved logged data
        print("TBD - log_data")

##################################
# simulation of usecases
##################################

Daum8008 = ergoFACE("Daum8008")
# Triggers
print("SIMULATOR:trigger automatic set")
Daum8008.automatic()
print("SIMULATOR:wait for 5 seconds")
time.sleep(5)
print("SIMULATOR:trigger RPM set")
Daum8008.RPM()
time.sleep(10)
print("SIMULATOR:trigger noRPM set")
Daum8008.noRPM()
# Daum8008.error()
# Daum8008.noRPM()


# if Graph machine is loaded, uncomment
# Daum8008.show_graph()
