#!/usr/bin/env python3

import serial
import time


circumference = 2000  # preset circumference(Radumfang) in mm
valid = True
rx_BuffChar = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
tx_BuffChar = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# Variables
ergobike_adr = 0x00  # ergobike adress; commented to avoid wrong initiation
Power = 0  # actual cycling power
Cadence = 0.0  # actual cycling cadence
Speed = 0.0  # actual cycling speed
# active = False  # someone is cycling on ergobike
dT_c = 0.0  # delta time cadence
dT_s = 0.0  # delta time speed

prev_ms_p = 0  # last time power has been updated, in ms
prev_ms_r = 0  # last time of Ergobike update, in ms
prev_ms_s = 0  # last time speed was checked, in ms
prev_ms_c = 0  # last time cadence was checked, in ms

prev_ms_t = 0


ser = serial.Serial('/dev/ttyUSB0',
                    baudrate=9600,
                    bytesize=8,
                    timeout=0.05)

###############################################################
# setup RS232 and get ergobike adress
###############################################################


def setup():

        print("RS232 - SUCCESS - Serial Adapter setup, wait 2 seconds ")
        time.sleep(2)  # wait for cockpit to initialize
        try:
            ser.open()
        except Exception as e2:
            print("RS232 - ERROR - open serial port: ", e2)
        if ser.isOpen():
            try:
                ser.flushInput()  # flush input buffer
                ser.flushOutput()  # flush output buffer
                print("RS232 - SUCCESS - Serial interface is ",
                      "open and ready to get ergobike adress ")
                get_cockadr()  # request cockpit adress
                print("RS232 - SUCCESS - Ergobike Adress: ", ergobike_adr)
            except Exception as e1:
                print("RS232 - ERROR - communicating...: ", e1)
        else:
            print("RS232 - ERROR - cannot open serial port ")

###############################################################
# main program
###############################################################


def loop():
    global Power
    global Speed
    global Cadence

    global prev_ms_p
    global prev_ms_r
    global prev_ms_s
    global prev_ms_c

    global Wheel_Rev
    global Crank_Rev
    global Crank_LastEvTime
    global Wheel_LastEvTime
    global dT_c
    global dT_s
    global T_s
    global gear

    Wheel_Rev = 1  # Wheel revolutions since last update
    Crank_Rev = 1  # Crank revolutions since last update
    Crank_LastEvTime = 1  # last event time when crank was detected
    Wheel_LastEvTime = 1  # last event time when wheel was detected
    gear = 15  # prerequisite for gearshifting
    dT_c = 0
    dT_s = 0
    T_s = 1

    prev_ms_p = 0  # last time power has been updated, in ms
    prev_ms_r = 0  # last time of Ergobike update, in ms
    prev_ms_s = 0  # last time speed was checked, in ms
    prev_ms_c = 0  # last time cadence was checked, in ms

    # during setup() there should be valid = True, Chick if fails
    print("RS232 - SUCCESS - Ergobike connected and run data ")
    if valid:  # if a valid in read_RX_Buff = True; DAUM connected
        print("RS232 - SUCCESS - Start loop program ")
        while valid:  # as long as the DAUM is still connected, get data
            currentMillis = int(round(time.time() * 1024))
            ###############################################################
            # update run data
            ###############################################################
            if (currentMillis - prev_ms_r) >= 1000:
                # if 1s has passed, read values from ergobike
                # print("SUCCESS - Ergobike connected and run data ")
                get_RunData()  # request rundata from ergobike
                prev_ms_r = currentMillis
            ###############################################################
            # Print run data
            ###############################################################
            if valid and Speed > 0:
                if (currentMillis - prev_ms_c) >= dT_c:
                    prev_ms_c = currentMillis
                    Crank_Rev = Crank_Rev + 1
                    Crank_LastEvTime = Crank_LastEvTime + dT_c

                if (currentMillis - prev_ms_s) >= dT_s:
                    prev_ms_s = currentMillis
                    Wheel_Rev = Wheel_Rev + gear
                    T_s = T_s + dT_s
                    Wheel_LastEvTime = round(T_s)

                # if (currentMillis - prev_ms_p) >= 1000:
                #     prev_ms_p = currentMillis
                #     # print("SUCCESS - Speed detected and running ")
                #     # print("Speed [km/h]: ", Speed)
                #     # print("Power [W]: ", Power)
                #     # print("Cadence [U/min]: ", Cadence)

    else:
        print("RS232 - FAILED - Ergobike disconnected ")
        Power = 0
        Speed = 0.0
        Cadence = 0.0

###############################################################
# requesting run data from eErgoBike-Classic 8008TRS
###############################################################


def get_RunData():
    global active
    global Power
    global Speed
    global Cadence
    global dT_c
    global dT_s

    cmd = 0x40  # ergobike command for run data

    tx_BuffChar[0] = cmd  # request run data from ergobike
    tx_BuffChar[1] = ergobike_adr  # append ergobike adress to telegram

    clear_RX_Buff()  # clear remining data in RX Buffer
    send_TX_Buff(2)  # RS232 send TX Buffer to ergobike Classic
    # printTX_Buff(2)  # print transmitted string
    time.sleep(0.05)

    valid = read_RX_Buff(19)  # pull rx data and store it in rx_buffer

    if (valid):
        # printRX_Buff(19)  # print received string
        # parse buffer to get cycling data
        if rx_BuffChar[0] == cmd and rx_BuffChar[1] == ergobike_adr:
            # check cmd and ergobike adress
            if rx_BuffChar[4] > 0:  # check if ergobike is active
                active = True
                Power = rx_BuffChar[5]*5
                Cadence = rx_BuffChar[6]
                Speed = rx_BuffChar[7]
                # Speed=Cadence/2.81
                if Speed == 0 or Cadence == 0:
                    dT_s = 100000
                    dT_c = 100000
                else:
                    dT_s = (3.6 / Speed) * circumference
                    dT_s = 15 * dT_s
                    dT_c = (60000 / Cadence) / 0.974
            else:  # ergobike is not active set values to zero
                active = False
                Speed = 0
                Cadence = 0
                Power = 0
                dT_s = 100000
                dT_c = 100000

###############################################################
# requesting cockpit adress from ErgoBike-Classic 8008TRS
###############################################################


def get_cockadr():

    global ergobike_adr

    cmd = 0x11
    tx_BuffChar[0] = cmd  # assigne request adress of ergobike in tx buffer

    clear_RX_Buff()  # clear remining data in RX Buffer
    send_TX_Buff(1)  # RS232 send TX Telegramm to ergobike Classic
    # printTX_Buff(1)  # print TX Telegramm

    valid = read_RX_Buff(2)  # pull rx data and store it in rx_buffer
    if valid:
        # printRX_Buff(2)  # print received string
        # parse rx buffer to get data
        if rx_BuffChar[0] == cmd:  # verify if data is valid
            print("RS232 - SUCCESS - Ergobike cockpit adress read")
            ergobike_adr = rx_BuffChar[1]
        else:
            print("RS232 - FAILED - Ergobike cockpit adress read")
            ergobike_adr = 0x00

###############################################################
# send SerialD values to ErgoBike-Classic 8008TRS
###############################################################


def send_TX_Buff(tx_BuffLen):
    for i in range(tx_BuffLen):
        ser.write((tx_BuffChar[i].to_bytes(1, byteorder='little',
                                           signed=False)))

###############################################################
# reading SerialD values from ErgoBike-Classic 8008TRS
###############################################################


def read_RX_Buff(rx_BuffLen):
    startMillis = int(round(time.time() * 1024))
    currentMillis = 0

    valid = True
    for i in range(rx_BuffLen):
        while valid and ser.inWaiting() == 0:  # delay until byte was received
            time.sleep(0.001)  # Serial.println("*delay*")
            currentMillis = int(round(time.time() * 1024))
            if (currentMillis - startMillis) >= 500:  # 5sec timeout
                valid = False  # data in Buffer is not valid
                print("RS232 - FAILED - Ergobike not responding!")
                break

        if valid:
            rx_BuffChar[i] = int.from_bytes(ser.read(), byteorder='little')

    return valid


###############################################################
# clear SerialD input buffer
###############################################################


def clear_RX_Buff():

    while ser.inWaiting() > 0:
        ser.read()


###############################################################
# prints serial rx buffer
###############################################################


# def printRX_Buff(rx_BuffLen):
#     print("RX_byte: ")
#     # for i in range(rx_BuffLen):
#     #     print(rx_BuffChar[i])
#     #     # print(rx_BuffChar(), sep=', ', end='', flush=True)


###############################################################
# prints serial tx buffer
###############################################################


# def printTX_Buff(tx_BuffLen):
#     print("TX_byte: ")
#     # for i in range(tx_BuffLen):
#     #     print(tx_BuffChar[i])
#     #     # print(tx_BuffChar(), sep=', ', end='', flush=True)


def main():
    # Constants
    while True:
        print("RS232 - START - Setup ")
        setup()
        print("RS232 - START - Loop ")
        loop()


if __name__ == "__main__":
    main()
