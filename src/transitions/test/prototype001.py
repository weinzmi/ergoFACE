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

    def is_valid(self):
        return True
    
    def is_not_valid(self):
        return False
    
    def is_also_valid(self):
        return True

    def __init__(self):
        self.wattage = 0
        self.cadence = 0
    
    # graph object is created by the machine
    def show_graph(self, **kwargs):
        stream = io.BytesIO()
        self.get_graph(**kwargs).draw(stream, prog='dot', format='png')
        display(Image(stream.getvalue()))

    # Note that the sole argument is now the EventData instance.
    # This object stores positional arguments passed to the trigger method in the
    # .args property, and stores keywords arguments in the .kwargs dictionary.
    def set_environment(self, event):
        self.wattage = event.kwargs.get('wattage', 0)
        self.cadence = event.kwargs.get('cadence', 0)

    def print_pressure(self): print("Current cadence is %.2f rpm." % self.cadence)

wattage = ergoFACE()

from transitions import Machine


# The states of wattage
# norpm - there is no rotation of the pedals
# rpm - there is at least a noticable RPM signal detected
# toolowcadence - the cadence is to low for the assigned power output (wattage)
# toohighcadence - the cadence is to high for the assigned power output (wattage)
states=['norpm', 'rpm', 'toolowcadence', 'toohighcadence']

# Transitions between states. 
transitions = [
    { 'trigger': 'pedaling', 'source': 'norpm', 'dest': 'rpm' },
    { 'trigger': 'pedalinglow', 'source': 'rpm', 'dest': 'toolowcadence' },
    { 'trigger': 'pedalinghigh', 'source': 'rpm', 'dest': 'toohighcadence' },
    { 'trigger': 'pedaling', 'source': 'toolowcadence', 'dest': 'rpm' },
    { 'trigger': 'pedaling', 'source': 'toohighcadence', 'dest': 'rpm' },
    { 'trigger': 'stoppedaling', 'source': 'rpm', 'dest': 'norpm' },
    { 'trigger': 'stoppedaling', 'source': 'toolowcadence', 'dest': 'norpm' },
    { 'trigger': 'stoppedaling', 'source': 'toohighcadence', 'dest': 'norpm' }
]

# LOGGING
# Set up logging; The basic log level will be DEBUG
import logging
logging.basicConfig(level=logging.DEBUG)
# Set transitions' log level to INFO; DEBUG messages will be omitted
logging.getLogger('transitions').setLevel(logging.INFO)


# Initialize
machine = Machine(wattage, states=states, transitions=transitions, send_event=True, initial='norpm')
machine.add_transition('norpm', 'rpm', 'toolowcadence', 'toohighcadence', before='set_environment')


# Now wattage maintains state...
wattage.state
# >>> 'norpm'

sleep(2)

# And that state can change...
# forcing the state without a trigger
wattage.pedaling()
# get the status
wattage.state
# >>> 'rpm'

sleep(2)

# set the event data for pedaling
wattage.pedaling(wattage=150, cadence=90)  # keyword args
wattage.print_cadence()
# >>> 'Current cadence is 90 rpm.'

sleep(2)

# set at triger to change the state
lump.trigger('stoppedaling')
# get the status
lump.state
# >>> 'norpm'

sleep(2)

# Generating diagram of model ergoFACE
model = ergoFACE()
machine = GraphMachine(model=model, 
                       states=states, 
                       transitions=transitions,
                       initial='norpm',
                       show_auto_transitions=True, # default value is False
                       title="ergoFACE transition diagram",
                       show_conditions=True)
model.show_graph()
