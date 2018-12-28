import time
import pigpio
import rpm

RPM_GPIO = 4
RUN_TIME = 60.0
SAMPLE_TIME = 2.0

pi = pigpio.pi()

p = rpm.reader(pi, RPM_GPIO)

start = time.time()

while (time.time() - start) < RUN_TIME:
    time.sleep(SAMPLE_TIME)
    RPM = p.RPM()
    print("RPM={}".format(int(RPM + 0.5)))

p.cancel()

pi.stop()
