# read_RPM.py
# 2016-01-20
# Public Domain

import pigpio


class reader:
    """
   A class to read speedometer pulses and calculate the RPM.
   """

    def __init__(self, pi, gpio, pulses_per_rev=1.0, weighting=0.0, min_RPM=5.0):
        """
      Instantiate with the Pi and gpio of the RPM signal
      to monitor.

      Optionally the number of pulses for a complete revolution
      may be specified.  It defaults to 1.

      Optionally a weighting may be specified.  This is a number
      between 0 and 1 and indicates how much the old reading
      affects the new reading.  It defaults to 0 which means
      the old reading has no effect.  This may be used to
      smooth the data.

      Optionally the minimum RPM may be specified.  This is a
      number between 1 and 1000.  It defaults to 5.  An RPM
      less than the minimum RPM returns 0.0.
      """
        self.pi = pi
        self.gpio = gpio
        self.pulses_per_rev = pulses_per_rev

        if min_RPM > 1000.0:
            min_RPM = 1000.0
        elif min_RPM < 1.0:
            min_RPM = 1.0

        self.min_RPM = min_RPM

        self._watchdog = 200  # Milliseconds.

        if weighting < 0.0:
            weighting = 0.0
        elif weighting > 0.99:
            weighting = 0.99

        self._new = 1.0 - weighting  # Weighting for new reading.
        self._old = weighting  # Weighting for old reading.

        self._high_tick = None
        self._period = None

        pi.set_mode(gpio, pigpio.INPUT)

        self._cb = pi.callback(gpio, pigpio.RISING_EDGE, self._cbf)
        pi.set_watchdog(gpio, self._watchdog)

    def _cbf(self, gpio, level, tick):

        if level == 1:  # Rising edge.

            if self._high_tick is not None:
                t = pigpio.tickDiff(self._high_tick, tick)

                if self._period is not None:
                    self._period = (self._old * self._period) + (self._new * t)
                else:
                    self._period = t

            self._high_tick = tick

        elif level == 2:  # Watchdog timeout.

            if self._period is not None:
                if self._period < 2000000000:
                    self._period += (self._watchdog * 1000)

    def RPM(self):
        """
      Returns the RPM.
      """
        RPM = 0.0
        if self._period is not None:
            RPM = 60000000.0 / (self._period * self.pulses_per_rev)
            if RPM < self.min_RPM:
                RPM = 0.0

        return RPM

    def cancel(self):
        """
      Cancels the reader and releases resources.
      """
        self.pi.set_watchdog(self.gpio, 0)  # cancel watchdog
        self._cb.cancel()

# if __name__ == "__main__":

# import time
# import pigpio
# # import read_RPM

# RPM_GPIO = 4
# RUN_TIME = 60.0
# SAMPLE_TIME = 2.0

# pi = pigpio.pi()

# p = self.reader(pi, RPM_GPIO)

# start = time.time()

# while (time.time() - start) < RUN_TIME:

# time.sleep(SAMPLE_TIME)

# RPM = p.RPM()

# print("RPM={}".format(int(RPM+0.5)))

# p.cancel()

# pi.stop()
