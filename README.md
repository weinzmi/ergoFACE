# ergoFACE
Hardware interface for DAUM Ergobike 8008 TRS
change for ATOM

<img src=https://github.com/weinzmi/ergoFACE/blob/master/images/wiki/EF_first_sketsh.jpg width="300">

first idea 22.12.2018; Michael Weinzinger

## Overview
* A hardware + software interface ("ergoFACE") is going to be developed,
which allows a mobile device (smartphone, tablet) to interact with a DAUM Ergobike 8008 TRS ("DAUM").

* The innitial idea is to be able to replace the standard cockpit of the DAUM with this solution (ergoFACE + mobile device).
* This can be achievend by plugging in the ergoFACE with the standard signal cable (4-wire cable) from the cockpit,
or even complete disassembly of the cockpit unit and replace it permanent with a mobild device.

## Aims
* Interaction between mobile device and DAUM
  * Capture the ACTUAL values from the DAUM on a mobile device
  * Send a SET POINT value from the mobile device to the DAUM
* Web server as gateway
* Saving the SET POINT and ACTUAL values as a training session
* Create SET POINT values for workouts
  * manually in an editor
  * convert recorded workouts / ACTUAL 2 SET POINT
* Selection of workouts
  * Manual SET POINT workout
    * WATT
    * Pitch/Climb
    * Heartrate
* Integration of additional external sensors
  * Bluetooth heart rate sensor
* Share the training sessions with social networks

## Usage
### ERG Mode with RS232 using BLE GATT Server to notify speed, cadence and power
* clone repository
* install requirements - see requirements.txt
* copy ergoFACE.service from lib\systemd\system to your local system
'''shell
sudo chmod 644 /lib/systemd/system/ergoFACE.service
'''
* configure
'''shell
sudo systemctl daemon-reload
 sudo systemctl enable ergoFACE.service
 '''
 * reboot
 '''shell
 sudo reboot
 '''
 * check status of service
 '''shell
 sudo systemctl status ergoFACE.service
 '''



more information is documented in the wiki:

https://github.com/weinzmi/ergoFACE/wiki
