
import serial
import time


###############################################################
# setup RS232 and get ergobike adress
###############################################################


def setup():

        print("SUCCESS - Serial Adapter setup, wait 2 seconds ")
        time.sleep(2)  # wait for cockpit to initialize
        try:
            ser.open()
        except Exception as e2:
            print("ERROR - open serial port: ", e2)
        if ser.isOpen():
            try:
                ser.flushInput()  # flush input buffer, discarding all its contents
                ser.flushOutput()  # flush output buffer, aborting current output
                print("SUCCESS - Serial interface is open and ready to get ergobike adress ")
                get_cockadr()  # request cockpit adress
                print("SUCCESS - Ergobike Adress: ", ergobike_adr)
            except Exception as e1:
                print("ERROR - communicating...: ", e1)
        else:
            print("ERROR - cannot open serial port ")

###############################################################
# main program
###############################################################


def main():
    global Power
    global Speed
    global Cadence

    global prev_ms_r
    global prev_ms_p

    # during setup() there should be valid = True, Chick if fails
    if valid:  # if a valid in read_RX_Buff = True; DAUM connected
        print("SUCCESS - Start main program ")
        while valid:  # as long as the DAUM is still connected, get data
            currentMillis = int(round(time.time() * 1000))
            ###############################################################
            # update run data
            ###############################################################
            if (currentMillis - prev_ms_r) >= 1000:
                # if 1s has passed, read values from ergobike
                print("SUCCESS - Ergobike connected and run data ")
                get_RunData()  # request rundata from ergobike
                prev_ms_r = currentMillis
            ###############################################################
            # Print run data
            ###############################################################
            if valid and Speed > 0:
                if (currentMillis - prev_ms_p) >= 1000:
                    prev_ms_p = currentMillis
                    print("SUCCESS - Speed detected and running ")
                    print("Speed [km/h]: ", Speed)
                    print("Power [W]: ", Power)
                    print("Cadence [U/min]: ", Cadence)

    else:
        print("FAILED - Ergobike disconnected ")
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

    cmd = 0x40  # ergobike command for run data

    tx_BuffChar[0] = cmd  # request run data from ergobike
    tx_BuffChar[1] = ergobike_adr  # append ergobike adress to telegram

    clear_RX_Buff()  # clear remining data in RX Buffer
    send_TX_Buff(2)  # RS232 send TX Buffer to ergobike Classic
    printTX_Buff(2)  # print transmitted string
    time.sleep(0.05)

    valid = read_RX_Buff(19)  # pull rx data and store it in rx_buffer

    if (valid):
        printRX_Buff(19)  # print received string
        # parse buffer to get cycling data
        if rx_BuffChar[0] == cmd and rx_BuffChar[1] == ergobike_adr:
            # check cmd and ergobike adress
            if rx_BuffChar[4] > 0:  # check if ergobike is active
                active = True
                Power = rx_BuffChar[5]*5
                Cadence = rx_BuffChar[6]
                Speed = rx_BuffChar[7]
                # Speed=Cadence/2.81
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
    # make sure that the correct command is send to ergobike
    # 001 #
    # cmd = struct.pack('B', 17)  # 0x11(HEX) / 17(INT) is ergobike command for ergobike adress
    # write(data) Write the bytes data to the port.
    # This should be of type bytes (or compatible such as bytearray or memoryview).
    # 002 #
    # cmd = b'\x11'
    # 003 #
    # cmd = B'\x11'
    # https://stackoverflow.com/a/45388986
    # 004 - tested in jupyter; worked#
    cmd = 0x11

    tx_BuffChar[0] = cmd  # assigne request adress of ergobike in tx buffer

    clear_RX_Buff()  # clear remining data in RX Buffer
    send_TX_Buff(1)  # RS232 send TX Telegramm to ergobike Classic
    printTX_Buff(1)  # print TX Telegramm

    valid = read_RX_Buff(2)  # pull rx data and store it in rx_buffer
    if valid:
        printRX_Buff(2)  # print received string
        # parse rx buffer to get data
        if rx_BuffChar[0] == cmd:  # verify if data is valid
            print("SUCCESS - Ergobike cockpit adress read")
            ergobike_adr = rx_BuffChar[1]
        else:
            print("FAILED - Ergobike cockpit adress read")
            ergobike_adr = 0x00

###############################################################
# send SerialD values to ErgoBike-Classic 8008TRS
###############################################################


def send_TX_Buff(tx_BuffLen):
    for i in range(tx_BuffLen):
        # try this or below

        ser.write((tx_BuffChar[i].to_bytes(1, byteorder='little', signed=False)))

        # this can work in 2 ways
        # decode HEX
        # line break at the end

        # ser.write(tx_BuffChar[i].decode('hex') + '\r\n')
    # https://stackoverflow.com/questions/44639741/pyserial-only-reading-one-byte

###############################################################
# reading SerialD values from ErgoBike-Classic 8008TRS
###############################################################


def read_RX_Buff(rx_BuffLen):
    startMillis = int(round(time.time() * 1000))
    currentMillis = 0

    valid = True
    for i in range(rx_BuffLen):
        while valid and ser.inWaiting() == 0:  # delay until byte was received
            time.sleep(0.001)  # Serial.println("*delay*")
            currentMillis = int(round(time.time() * 1000))
            if (currentMillis - startMillis) >= 500:  # 5sec timeout
                valid = False  # data in Buffer is not valid
                print("FAILED - Ergobike not responding!")
                break

        if valid:
            rx_BuffChar[i] = int.from_bytes(ser.read(), byteorder='little')
            # rx_BuffChar[i] = int(ser.read(), 16)  # byte received, add it to buffer

    return valid


###############################################################
# clear SerialD input buffer
###############################################################


def clear_RX_Buff():

    while ser.inWaiting() > 0:
        tmp = ser.read()


###############################################################
# prints serial rx buffer
###############################################################


def printRX_Buff(rx_BuffLen):
    print("RX_byte: ")
    for i in range(rx_BuffLen):
        print(rx_BuffChar[i])
        # print(rx_BuffChar(), sep=', ', end='', flush=True)


###############################################################
# prints serial tx buffer
###############################################################


def printTX_Buff(tx_BuffLen):
    print("TX_byte: ")
    for i in range(tx_BuffLen):
        print(tx_BuffChar[i])
        # print(tx_BuffChar(), sep=', ', end='', flush=True)


if __name__ == "__main__":

    # Constants
    circumference = 2000  # preset circumference(Radumfang) in mm
    valid = True
    # have to be tested, which byt array supports "unsigned char"
    # 001 #
    # rx_BuffChar = array('B', 50) # UART input buffer
    # tx_BuffChar = array('B', 10)# UART output bufer
    # 002 # OK but b'e' in first byte
    # rx_BuffChar = bytearray(50)
    # tx_BuffChar = bytearray(10)
    # 003 #
    # rx_BuffChar = (50)
    # tx_BuffChar = (10)
    # 004 #
    # rx_BuffChar = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    #                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    #                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    #                0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    # tx_BuffChar = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    #                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    #                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    #                0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    # 005 #
    rx_BuffChar = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    tx_BuffChar = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

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

    while True:

        ser = serial.Serial('/dev/ttyUSB0',
                            baudrate=9600,
                            bytesize=8,
                            timeout=0.05)

        print("START - Setup ")
        setup()
        print("START - Main ")
        main()
