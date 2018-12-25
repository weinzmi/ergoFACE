import time


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

time.sleep(2)

# And that state can change...
# forcing the state without a trigger
wattage.pedaling()
# get the status
wattage.state
# >>> 'rpm'

time.sleep(2)

# set the event data for pedaling
# wattage.pedaling(wattage=150, cadence=90)  # keyword args
# wattage.print_cadence()
# >>> 'Current cadence is 90 rpm.'

time.sleep(2)

# set at triger to change the state
wattage.trigger('stoppedaling')
# get the status
wattage.state
# >>> 'norpm'

time.sleep(2)
