import RPi.GPIO as GPIO
 
GPIO.setmode(GPIO.BOARD)
 
# Setup GPIO
GPIO.setup(24, GPIO.OUT)
 
# Set PWM instance and frequency
# Frequency [Hz] = 1 / preriod [ms] 
# TBD the Frequency of DAUM cockpit has to be evaluated before setting this
pwm24 = GPIO.PWM(24, 100)

 
# Start PWM with 50% Duty Cycle
# TBD the 50% "could" be 400W, the duty cycle of DAUM cockpit has to be evaluated before setting this
# it might be inverse; 10% = 720W, not 80W
pwm24.start(50)

raw_input('Press return to stop:')	#Wait
 
# Stops the PWM
pwm24.stop()

 
# Cleans the GPIO
GPIO.cleanup()
