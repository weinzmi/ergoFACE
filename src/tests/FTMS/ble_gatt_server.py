#!/usr/bin/env python3

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
import ble_conf
from prettytable import PrettyTable
import numpy as np


try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

mainloop = None

BLUEZ_SERVICE_NAME = 'org.bluez'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'

GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE = 'org.bluez.GattCharacteristic1'
GATT_DESC_IFACE = 'org.bluez.GattDescriptor1'


class InvalidArgsException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.freedesktop.DBus.Error.InvalidArgs'


class NotSupportedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.NotSupported'


class NotPermittedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.NotPermitted'


class InvalidValueLengthException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.InvalidValueLength'


class FailedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.Failed'


class Application(dbus.service.Object):
    """
    org.bluez.GattApplication1 interface implementation
    """

    def __init__(self, bus):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)
        self.add_service(CSCService(bus, 1))
        self.add_service(CyclingPowerService(bus, 2))
        self.add_service(FitnessMachineService(bus, 3))

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        print('BLE GATT - GetManagedObjects')

        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
                descs = chrc.get_descriptors()
                for desc in descs:
                    response[desc.get_path()] = desc.get_properties()

        return response


class Service(dbus.service.Object):
    """
    org.bluez.GattService1 interface implementation
    """
    PATH_BASE = '/org/bluez/example/service'

    def __init__(self, bus, index, uuid, primary):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
                GATT_SERVICE_IFACE: {
                        'UUID': self.uuid,
                        'Primary': self.primary,
                        'Characteristics': dbus.Array(
                                self.get_characteristic_paths(),
                                signature='o')
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_characteristic(self, characteristic):
        self.characteristics.append(characteristic)

    def get_characteristic_paths(self):
        result = []
        for chrc in self.characteristics:
            result.append(chrc.get_path())
        return result

    def get_characteristics(self):
        return self.characteristics

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_SERVICE_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_SERVICE_IFACE]


class Characteristic(dbus.service.Object):
    """
    org.bluez.GattCharacteristic1 interface implementation
    """

    def __init__(self, bus, index, uuid, flags, service):
        self.path = service.path + '/char' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.descriptors = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
                GATT_CHRC_IFACE: {
                        'Service': self.service.get_path(),
                        'UUID': self.uuid,
                        'Flags': self.flags,
                        'Descriptors': dbus.Array(
                                self.get_descriptor_paths(),
                                signature='o')
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_descriptor(self, descriptor):
        self.descriptors.append(descriptor)

    def get_descriptor_paths(self):
        result = []
        for desc in self.descriptors:
            result.append(desc.get_path())
        return result

    def get_descriptors(self):
        return self.descriptors

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_CHRC_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_CHRC_IFACE]

    @dbus.service.method(GATT_CHRC_IFACE,
                         in_signature='a{sv}',
                         out_signature='ay')
    def ReadValue(self, options):
        print('BLE GATT - Default ReadValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print('BLE GATT - Default WriteValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StartNotify(self):
        print('BLE GATT - Default StartNotify called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StopNotify(self):
        print('BLE GATT - Default StopNotify called, returning error')
        raise NotSupportedException()

    @dbus.service.signal(DBUS_PROP_IFACE,
                         signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass


class Descriptor(dbus.service.Object):
    """
    org.bluez.GattDescriptor1 interface implementation
    """

    def __init__(self, bus, index, uuid, flags, characteristic):
        self.path = characteristic.path + '/desc' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.flags = flags
        self.chrc = characteristic
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
                GATT_DESC_IFACE: {
                        'Characteristic': self.chrc.get_path(),
                        'UUID': self.uuid,
                        'Flags': self.flags,
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_DESC_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_DESC_IFACE]

    @dbus.service.method(GATT_DESC_IFACE,
                         in_signature='a{sv}',
                         out_signature='ay')
    def ReadValue(self, options):
        print('BLE GATT - Default ReadValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_DESC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print('BLE GATT - Default WriteValue called, returning error')
        raise NotSupportedException()

###########################################################################
# Start GATT Services
###########################################################################


class FitnessMachineService(Service):
    """
    Abstract:
    This service exposes training-related data in the sports and fitness
    environment, which allows a Server (e.g., a fitness machine) to send
    training-related data to a Client.
    Summary:
    The Fitness Machine Service (FTMS) exposes training-related data in
    the sports and fitness environment, which allows a Client to collect
    training data while a user is exercising with a fitness machine (Server).
    Service Dependencies:
    This service has no dependencies on other GATT-based services.
    """
    FTMS_UUID = '1826'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.FTMS_UUID, True)
        self.add_characteristic(Fitness_Machine_Feature(bus, 0, self))
        self.add_characteristic(Indoor_Bike_Data(bus, 1, self))
        self.add_characteristic(Fitness_Machine_Control_Point(bus, 2, self))
        self.add_characteristic(Fitness_Machine_Status(bus, 3, self))


class Fitness_Machine_Feature(Characteristic):
    """
    The Fitness Machine Feature characteristic is defined
    in the Fitness Machine Service Specification
    """
    FITNESS_MACHINE_FEATURE_UUID = '2ACC'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.FITNESS_MACHINE_FEATURE_UUID,
                ['read'],
                service)
        self.value = [dbus.Byte(0 | (1 << 1)),  # Cadence supported
                      dbus.Byte(0 | (1 << 6)),  # Power mesurement supported
                      dbus.Byte(0), dbus.Byte(0),  # rest of Features
                      dbus.Byte(0 | (1 << 3)),  # Power Target setting supported
                      dbus.Byte(0), dbus.Byte(0), dbus.Byte(0)]  # rest of target setting

    def ReadValue(self, options):
        print('BLE GATT -FTM - Machine Feature Read: ', end="")
        for i, val in enumerate(self.value):
            # zfill(8) because of octets
            print(bin(self.value[i])[2:].zfill(8)[::-1], "| ", end="")
        print(i + 1, "bytes")
        return self.value


class Supported_Power_Range(Characteristic):
    """
    The Supported Power Range characteristic is defined
    in the Fitness Machine Service Specification
    """
    SUPPORTED_POWER_RANGE_UUID = '2AD8'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.SUPPORTED_POWER_RANGE_UUID,
                ['read'],
                service)
        self.value = [dbus.Byte(0), dbus.Byte(0),  # Minimum Power
                      dbus.Byte(0), dbus.Byte(0),  # Maximum Power
                      dbus.Byte(0), dbus.Byte(0)]  # Minimum Increment

        uint_minimum_power = 25 & 0xFFFF
        self.value[1] = (np.int16(uint_minimum_power) & 0xFF00) >> 8
        self.value[0] = (np.int16(uint_minimum_power) & 0xFF)

        uint_maximum_power = 800 & 0xFFFF
        self.value[3] = (np.int16(uint_maximum_power) & 0xFF00) >> 8
        self.value[2] = (np.int16(uint_maximum_power) & 0xFF)

        uint_minimum_increment = 5 & 0xFFFF
        self.value[5] = (np.uint16(uint_minimum_increment) & 0xFF00) >> 8
        self.value[4] = (np.uint16(uint_minimum_increment) & 0xFF)

    def ReadValue(self, options):
        print('BLE GATT -FTM - Supported Power Range Read: ', end="")
        for i, val in enumerate(self.value):
            # zfill(8) because of octets
            print(bin(self.value[i])[2:].zfill(8)[::-1], "| ", end="")
        print(i + 1, "bytes")
        return self.value


class Indoor_Bike_Data(Characteristic):
    """
    The Indoor Bike Data characteristic is used to send training-related
    data to the Client from an indoor bike (Server).
    """
    INDOOR_BIKE_DATA_UUID = '2AD2'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.INDOOR_BIKE_DATA_UUID,
                ['notify'],  # no broadcast
                service)
        self.notifying = False

    def ib_data_cb(self):
        # Flags bit 2,6 set to enable speed, cadence and power data
        value = [dbus.Byte(0 | (1 << 2) | (1 << 6)), dbus.Byte(0),  # 16-bit Flags
                 dbus.Byte(0), dbus.Byte(0),  # Instantaneous Speed
                 dbus.Byte(0), dbus.Byte(0),  # Instantaneous Cadence
                 dbus.Byte(0), dbus.Byte(0),  # Instantaneous Power
                 ]
        ble.ftm_ib()

        # figured out, that in ZWIFT, speed is calculated based on the power,
        # so I skipped speed in the transmission and now power and cadence is
        # shown correct. this might change when riding in sim mode?
        # EDIT: this might happened, because of the wrong bit 0 = more data

        # Build Instantaneous Speed data - little endian
        # convert to uint16
        uint_speed = int(ble.speed) & 0xFFFF
        value[3] = (np.uint16(uint_speed) & 0xFF00) >> 8
        value[2] = (np.uint16(uint_speed) & 0xFF)

        # Build Instantaneous Cadence data - little endian
        # convert to uint16
        # times 2, since in test is was just half the cadence
        uint_cadence = int(ble.cadence * 2) & 0xFFFF
        value[5] = (np.uint16(uint_cadence) & 0xFF00) >> 8
        value[4] = (np.uint16(uint_cadence) & 0xFF)

        # Build Instantaneous Power data - little endian
        # convert to sint16-> do nothing
        # uint_power = int(ble.power)
        value[7] = (np.int16(ble.power) & 0xFF00) >> 8
        value[6] = (np.int16(ble.power) & 0xFF)

        self.PropertiesChanged(GATT_CHRC_IFACE, {'Value': value}, [])
        return self.notifying

    def _update_ib_data_simulation(self):
        print('BLE GATT - FTM - Update Indoor Bike Data')

        if not self.notifying:
            return

        GObject.timeout_add(2000, self.ib_data_cb)

    def StartNotify(self):
        if self.notifying:
            print('BLE GATT - FTM - Already notifying, nothing to do')
            return

        self.notifying = True
        self._update_ib_data_simulation()

    def StopNotify(self):
        if not self.notifying:
            print('BLE GATT - FTM - Not notifying, nothing to do')
            return

        self.notifying = False
        self._update_ib_data_simulation()


class Fitness_Machine_Control_Point(Characteristic):
    """
    The Fitness Machine Control Point characteristic is defined in the
    Fitness Machine Service Specification.
    """
    FITNESS_MACHINE_CONTROL_POINT_UUID = '2AD9'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.FITNESS_MACHINE_CONTROL_POINT_UUID,
                ['write', 'indicate'],
                service)
        self.notifying = False

        self.value = [dbus.Byte(0),  # Op Code
                      dbus.Byte(0), dbus.Byte(0),  # C.4 - Set Target Power
                      dbus.Byte(0),  # Stop / Pause
                      dbus.Byte(0), dbus.Byte(0), dbus.Byte(0), dbus.Byte(0)]  # Response Code

    def ftm_request_control_procedure(self):
        print("Writing values for request - CONTROL, OpCode 0x00")
        self.response_Code = 0x80  # response Op Code
        self.request_Code = 0x00  # request code 0x00 for request control
        self.result_Code = 0x01  # result code 0x01 for success

        # Response Code
        self.value[4] = (np.uint8(self.response_Code) & 0xFF)
        self.value[5] = (np.uint8(self.request_Code) & 0xFF)
        self.value[6] = (np.uint8(self.result_Code) & 0xFF)
        self.value[7] = (np.uint8(self.response_Parameter) & 0xFF)

    def ftm_request_reset_procedure(self):
        print("Writing values for request - RESET, OpCode 0x01")
        self.response_Code = 0x80  # response Op Code
        self.request_Code = 0x01  # request code 0x01 for request reset
        self.result_Code = 0x01  # result code 0x01 for success

        # Response Code
        self.value[4] = (np.uint8(self.response_Code) & 0xFF)
        self.value[5] = (np.uint8(self.request_Code) & 0xFF)
        self.value[6] = (np.uint8(self.result_Code) & 0xFF)
        self.value[7] = (np.uint8(self.response_Parameter) & 0xFF)

    def ftm_request_target_power_procedure(self):
        print("Writing values for request - TARGET POWER, OpCode 0x05")
        self.response_Code = 0x80  # response Op Code
        self.request_Code = 0x05  # request code 0x01 for request reset
        self.result_Code = 0x01  # result code 0x01 for success

        # Response Code
        self.value[4] = (np.uint8(self.response_Code) & 0xFF)
        self.value[5] = (np.uint8(self.request_Code) & 0xFF)
        self.value[6] = (np.uint8(self.result_Code) & 0xFF)
        self.value[7] = (np.uint8(self.response_Parameter) & 0xFF)

    def ftm_request_start_resume_procedure(self):
        print("Writing values for request - START/RESUME, OpCode 0x07")
        self.response_Code = 0x80  # response Op Code
        self.request_Code = 0x07  # request code 0x01 for request reset
        self.result_Code = 0x01  # result code 0x01 for success

        # Response Code
        self.value[4] = (np.uint8(self.response_Code) & 0xFF)
        self.value[5] = (np.uint8(self.request_Code) & 0xFF)
        self.value[6] = (np.uint8(self.result_Code) & 0xFF)
        self.value[7] = (np.uint8(self.response_Parameter) & 0xFF)

    def ftm_request_stop_pause_procedure(self):
        print("Writing values for request - STOP/PAUSE, OpCode 0x08")
        self.response_Code = 0x80  # response Op Code
        self.request_Code = 0x08  # request code 0x01 for request reset
        self.result_Code = 0x01  # result code 0x01 for success

        # Response Code
        self.value[4] = (np.uint8(self.response_Code) & 0xFF)
        self.value[5] = (np.uint8(self.request_Code) & 0xFF)
        self.value[6] = (np.uint8(self.result_Code) & 0xFF)
        self.value[7] = (np.uint8(self.response_Parameter) & 0xFF)

    def ftm_request_response_code_procedure(self):
        print("Writing values for request - RESPONSE CODE, OpCode 0x80")
        self.response_Code = 0x80  # response Op Code
        self.request_Code = 0x80  # request code 0x01 for request reset
        self.result_Code = 0x01  # result code 0x01 for success

        # Response Code
        self.value[4] = (np.uint8(self.response_Code) & 0xFF)
        self.value[5] = (np.uint8(self.request_Code) & 0xFF)
        self.value[6] = (np.uint8(self.result_Code) & 0xFF)
        self.value[7] = (np.uint8(self.response_Parameter) & 0xFF)


###############################################################################
        # Stop / Pause
        self.stop_pause = self.value[3]
###############################################################################
###############################################################################

    def WriteValue(self, value, options):
        print('Fitness Machine Control Point WriteValue called')

        if len(self.value) != 8:
            print("Invalid length Value")
            raise InvalidValueLengthException()

        # Op Code
        op_Code = self.value[0]
        print('Op Code value: ' + repr(op_Code))

        if op_Code == 0x00:
            print("Request for control started")
            self.ftm_request_control_procedure()

        if op_Code == 0x01:
            print("Request for Reset started")
            self.ftm_request_reset_procedure()

        if op_Code == 0x05:
            print("Request for Target Power started")
            self.ftm_request_target_power_procedure()

        if op_Code == 0x07:
            print("Request for Start or Resume started")
            self.ftm_request_start_resume_procedure()

        if op_Code == 0x08:
            print("Request for Stop or Pause started")
            self.ftm_request_stop_pause_procedure()

        if op_Code == 0x80:
            print("Request for Response Code started")
            self.ftm_request_response_code_procedure()

    def power_target(self):
        # C.4 - Set Target Power
        self.target_Power = int.from_bytes(self.value[1, 2], byteorder='little', signed=True)

    def _update_ftm_target_power(self):
        print('Update Target Power values')

        if not self.notifying:
            return

        GObject.timeout_add(1000, self.power_target)

    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
            return

        self.notifying = True
        self._update_hr_msrmt_simulation()

    def StopNotify(self):
        if not self.notifying:
            print('Not notifying, nothing to do')
            return

        self.notifying = False
        self._update_hr_msrmt_simulation()

###############################################################################
###############################################################################
###############################################################################


class Fitness_Machine_Status(Characteristic):
    """
    The Fitness Machine Status characteristic is defined in the
    Fitness Machine Service Specification.
    """
    FITNESS_MACHINE_STATUS_UUID = '2ADA'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.FITNESS_MACHINE_STATUS_UUID,
                ['notify'],  # no broadcast
                service)
        self.notifying = False

    def ftm_status_cb(self):
        self.value = [dbus.Byte(0)]  # The Fitness Machine Status Op Code

        ble.ftm_status()

        # set FTM Status Op Code
        self.value[0] = ble.status
        print('BLE GATT - FTM - Status: ' + repr(self.value))
        self.PropertiesChanged(GATT_CHRC_IFACE, {'Value': self.value}, [])
        return self.notifying

    def _update_ib_data_simulation(self):
        print('BLE GATT - FTM - Update Status')

        if not self.notifying:
            return

        GObject.timeout_add(1000, self.ftm_status_cb)

    def StartNotify(self):
        if self.notifying:
            print('BLE GATT - FTM - Already notifying, nothing to do')
            return

        self.notifying = True
        self._update_ib_data_simulation()

    def StopNotify(self):
        if not self.notifying:
            print('BLE GATT - FTM -Not notifying, nothing to do')
            return

        self.notifying = False
        self._update_ib_data_simulation()

#############################################################################


class CSCService(Service):
    CSC_SERVICE_UUID = '1816'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.CSC_SERVICE_UUID, True)
        self.add_characteristic(CSCMeasurement(bus, 0, self))
        self.add_characteristic(CSCFeatureCharacteristic(bus, 1, self))


class CSCMeasurement(Characteristic):
    CSC_MEASUREMENT_UUID = '2a5b'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CSC_MEASUREMENT_UUID,
                ['notify', 'broadcast'],
                service)
        self.notifying = False

    def csc_msrmt_cb(self):
        # Flags bit 0,1 set to enable wheel and crank revolution data
        value = [dbus.Byte(0 | (1 << 0) | (1 << 1)),  # 8-bit Flags
                 dbus.Byte(0), dbus.Byte(0), dbus.Byte(0), dbus.Byte(0),  # Cumulative wheel revs
                 dbus.Byte(0), dbus.Byte(0),  # Last rev Time
                 dbus.Byte(0), dbus.Byte(0),  # Cumulative Crank
                 dbus.Byte(0), dbus.Byte(0)   # Last Crank Time
                 ]

        ble.Transmit_csc()

        # Build revolution data - little endian
        value[4] = (np.uint32(ble.wheel_revolutions) & 0xFF000000) >> 24
        value[3] = (np.uint32(ble.wheel_revolutions) & 0xFF0000) >> 16
        value[2] = (np.uint32(ble.wheel_revolutions) & 0xFF00) >> 8
        value[1] = (np.uint32(ble.wheel_revolutions) & 0xFF)
        # & 0xFFFF was to convert int to uint, but not to 16 Bits
        # np.uint16 is correct
        time_in_1024_sec = int(ble.rev_time)
        value[6] = (np.uint16(time_in_1024_sec) & 0xFF00) >> 8
        value[5] = (np.uint16(time_in_1024_sec) & 0xFF)
        # Build crank (stroke) data - little endian
        value[8] = (np.uint16(ble.stroke_count) & 0xFF00) >> 8
        value[7] = (np.uint16(ble.stroke_count) & 0xFF)
        # & 0xFFFF was to convert int to uint, but not to 16 Bits
        # np.uint16 is correct
        time_in_1024_sec = int(ble.last_stroke_time)
        value[10] = (np.uint16(time_in_1024_sec) & 0xFF00) >> 8
        value[9] = (np.uint16(time_in_1024_sec) & 0xFF)
        # print("BLE GATT - Stroke time: ", time_in_1024_sec)

        print('BLE GATT - CSC - Measurement: ', end="")
        # for i, val in enumerate(value):
        #     print(hex(value[i]), "| ", end="")
        # print(i + 1, "chars")
        t = PrettyTable(['Wheel revolutions', 'Rev time', 'Cadence', 'stroke time'])
        t.add_row([ble.wheel_revolutions, int(ble.rev_time), ble.stroke_count, int(ble.last_stroke_time)])
        print(t)

        self.PropertiesChanged(GATT_CHRC_IFACE, {'Value': value}, [])
        return self.notifying

    def _update_csc_msrmt_simulation(self):
        print('BLE GATT - CSC - Update CSC Measurement')

        if not self.notifying:
            return
        # set to more than 1000ms to avoid zero cadence, because if cadence is
        # lower than 60 RPM it takes more than one second to increment
        GObject.timeout_add(3000, self.csc_msrmt_cb)

    def StartNotify(self):
        if self.notifying:
            print('BLE GATT - CSC - Already notifying, nothing to do')
            return

        self.notifying = True
        self._update_csc_msrmt_simulation()

    def StopNotify(self):
        if not self.notifying:
            print('BLE GATT - CSC - Not notifying, nothing to do')
            return

        self.notifying = False
        self._update_csc_msrmt_simulation()


class CSCFeatureCharacteristic(Characteristic):

    CSC_FEATURE_UUID = '2a5c'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CSC_FEATURE_UUID,
                ['read'],
                service)
        # Bits 0,1 enable wheel and crank data
        # Value 0x0300
        self.value = [dbus.Byte(0 | (1 << 0) | (1 << 1)), dbus.Byte(0)]

    def ReadValue(self, options):
        print('BLE GATT - CSC - Feature Characteristic Read: ', end="")
        for i, val in enumerate(self.value):
            print(bin(self.value[i])[2:].zfill(8)[::-1], "| ", end="")
        print(i + 1, "bytes")
        return self.value


class CyclingPowerService(Service):
    CYCLING_POWER_SERVICE_UUID = '1818'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.CYCLING_POWER_SERVICE_UUID, True)
        self.add_characteristic(CyclingPowerMeasurement(bus, 0, self))
        self.add_characteristic(CyclingPowerFeatureCharacteristic(bus, 1, self))
        self.add_characteristic(SensorLocation(bus, 2, self))


class CyclingPowerMeasurement(Characteristic):
    CYCLING_POWER_MEASUREMENT_UUID = '2a63'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CYCLING_POWER_MEASUREMENT_UUID,
                ['notify', 'broadcast'],
                service)
        self.notifying = False

    def cp_msrmt_cb(self):
        # Flags bit 4,5 set to enable wheel and crank revolution data
        value = [dbus.Byte(0 | (1 << 4) | (1 << 5)), dbus.Byte(0),  # 16bit Flags
                 dbus.Byte(0), dbus.Byte(0),  # Instantaneous power
                 dbus.Byte(0), dbus.Byte(0), dbus.Byte(0), dbus.Byte(0),  # Cumulative wheel revs
                 dbus.Byte(0), dbus.Byte(0),  # Last rev Time
                 dbus.Byte(0), dbus.Byte(0),  # Cumulative Crank
                 dbus.Byte(0), dbus.Byte(0)   # Last Crank Time
                 ]

        ble.Transmit_cp()

        # Build kcal data - little endian
        value[3] = (np.int16(ble.power) & 0xFF00) >> 8
        value[2] = (np.int16(ble.power) & 0xFF)
        # Build revolution data - little endian
        value[7] = (np.uint32(ble.wheel_revolutions) & 0xFF000000) >> 24
        value[6] = (np.uint32(ble.wheel_revolutions) & 0xFF0000) >> 16
        value[5] = (np.uint32(ble.wheel_revolutions) & 0xFF00) >> 8
        value[4] = (np.uint32(ble.wheel_revolutions) & 0xFF)
        # & 0xFFFF was to convert int to uint, but not to 16 Bits
        # np.uint16 is correct
        # this has a basis of 2048 seconds and is multiplied by two
        time_in_2048_sec = (int(ble.rev_time) * 2)
        value[9] = (np.uint16(time_in_2048_sec) & 0xFF00) >> 8
        value[8] = (np.uint16(time_in_2048_sec) & 0xFF)
        # Build crank (stroke) data - little endian
        value[11] = (np.uint16(ble.stroke_count) & 0xFF00) >> 8
        value[10] = (np.uint16(ble.stroke_count) & 0xFF)
        # & 0xFFFF was to convert int to uint, but not to 16 Bits
        # np.uint16 is correct
        time_in_1024_sec = int(ble.last_stroke_time)
        value[13] = (np.uint16(time_in_1024_sec) & 0xFF00) >> 8
        value[12] = (np.uint16(time_in_1024_sec) & 0xFF)

        print('BLE GATT - CP - Measurement: ', end="")
        for i, val in enumerate(value):
            print(hex(value[i]), "| ", end="")
        print(i + 1, "chars")

        self.PropertiesChanged(GATT_CHRC_IFACE, {'Value': value}, [])
        return self.notifying

    def _update_cp_msrmt_simulation(self):
        print('BLE GATT - CP - Update Power Measurement')
        if not self.notifying:
            return
        # set to more than 1000ms to avoid zero cadence, because if cadence is
        # lower than 60 RPM it takes more than one second to increment
        GObject.timeout_add(3000, self.cp_msrmt_cb)

    def StartNotify(self):
        if self.notifying:
            print('BLE GATT - CP - Already notifying, nothing to do')
            return

        self.notifying = True
        self._update_cp_msrmt_simulation()

    def StopNotify(self):
        if not self.notifying:
            print('BLE GATT - CP - Not notifying, nothing to do')
            return

        self.notifying = False
        self._update_cp_msrmt_simulation()


class CyclingPowerFeatureCharacteristic(Characteristic):

    CYCLING_POWER_FEATURE_UUID = '2a65'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CYCLING_POWER_FEATURE_UUID,
                ['read'],
                service)
        self.value = [dbus.Byte(0), dbus.Byte(0), dbus.Byte(0), dbus.Byte(0)]

    def ReadValue(self, options):
        print('BLE GATT - CP - Feature Characteristic Read: ', end="")
        for i, val in enumerate(self.value):
            print(bin(self.value[i])[2:].zfill(8)[::-1], "| ", end="")
        print(i + 1, "bytes")
        return self.value


class SensorLocation(Characteristic):

    CYCLING_SENSOR_LOCATION_UUID = '2a5d'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CYCLING_SENSOR_LOCATION_UUID,
                ['read'],
                service)
        self.value = [dbus.Byte(0)]
        # 13 == Rear Hub
        self.value[0] = 13

    def ReadValue(self, options):
        print('BLE GATT - CP - Sensor Location Read: ', end="")
        for i, val in enumerate(self.value):
            print(self.value[i], "| ", end="")
        print(i + 1, "enumerates")
        return self.value


def register_app_cb():
    print('BLE GATT - CP - application registered')


def register_app_error_cb(error):
    print('BLE GATT - CP - Failed to register application: ' + str(error))
    mainloop.quit()


def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                               DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if GATT_MANAGER_IFACE in props.keys():
            return o

    return None


ble = ble_conf.bleValue()

###########################################################################
# Start GATT Server
###########################################################################


def main():
    global mainloop

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    adapter = find_adapter(bus)
    if not adapter:
        print('BLE GATT - GattManager1 interface not found')
        return

    service_manager = dbus.Interface(
            bus.get_object(BLUEZ_SERVICE_NAME, adapter),
            GATT_MANAGER_IFACE)

    app = Application(bus)

    mainloop = GObject.MainLoop()

    print('BLE GATT - Registering GATT application...')

    service_manager.RegisterApplication(app.get_path(), {},
                                        reply_handler=register_app_cb,
                                        error_handler=register_app_error_cb)

    mainloop.run()


if __name__ == '__main__':
    main()
