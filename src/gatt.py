#!/usr/bin/env python3

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
# import array
try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject
# import sys

# from random import randint

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
        # self.add_service(HeartRateService(bus, 0))
        self.add_service(CyclingSpeedCadence(bus, 0))

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        print('GetManagedObjects')

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
        print('Default ReadValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print('Default WriteValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StartNotify(self):
        print('Default StartNotify called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StopNotify(self):
        print('Default StopNotify called, returning error')
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
        print('Default ReadValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_DESC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print('Default WriteValue called, returning error')
        raise NotSupportedException()

##############################################################################
# test of Heart rate service
##############################################################################
#
#
# class HeartRateService(Service):
#     """
#     Fake Heart Rate Service that simulates a fake heart beat and control point
#     behavior.
#
#     """
#     HR_UUID = '180d'
#
#     def __init__(self, bus, index):
#         Service.__init__(self, bus, index, self.HR_UUID, True)
#         self.add_characteristic(HeartRateMeasurementChrc(bus, 0, self))
#         self.add_characteristic(BodySensorLocationChrc(bus, 1, self))
#         self.add_characteristic(HeartRateControlPointChrc(bus, 2, self))
#         self.energy_expended = 0
#
#
# class HeartRateMeasurementChrc(Characteristic):
#     HR_MSRMT_UUID = '2a37'
#
#     def __init__(self, bus, index, service):
#         Characteristic.__init__(
#                 self, bus, index,
#                 self.HR_MSRMT_UUID,
#                 ['notify'],
#                 service)
#         self.notifying = False
#         self.hr_ee_count = 0
#
#     def hr_msrmt_cb(self):
#         '''
#         in APP i can see Value 0x0664
#         06 (hex) = 6 (dec) from above
#         64 (hex) = 100 (dec) from below
#
#         if I comment out value.append(dbus.Byte(0x06)),
#         app that listens on HBM crashes
#
#         0x0664 == 0000 0110 0110 0100
#                 FLAGS 8Bit | Heart Rate Measurement Value (uint8)
#         Bit Field
#         0000 0110 is empty
#
#             Bit 0 = Heart Rate Value Format / Size 1 Bit = "0" = "UINT8"
#             Bit 1 = Sensor Contact Status bits / Size 2 Bits = 00 = "0" = Sensor Contact feature is not supported in the current connection
#             Bit 2 = extension of Bit 1
#             Bit 3 = Energy Expended Status bit / Size 1 Bit = "0" = Energy Expended field is not present
#
#             Bit 4 = RR-Interval bit / Size 1 Bit = "0" = "RR-Interval values are not present."
#             Bit 5 = 	Reserved for future use / Size 3 Bit = "6" = EMPTY
#             Bit 6 = extension of Bit 5
#             Bit 7 = extension of Bit 5
#
#         '''
#         value = []
#         value.append(dbus.Byte(0x00))  # FLAGS 8Bit
#         value.append(dbus.Byte(100))  # Heart Rate Measurement Value (uint8)
#
#         print('Updating value: ' + repr(value))
#
#         self.PropertiesChanged(GATT_CHRC_IFACE, {'Value': value}, [])
#
#         return self.notifying
#
#     def _update_hr_msrmt_simulation(self):
#         print('Update HR Measurement Simulation')
#
#         if not self.notifying:
#             return
#
#         GObject.timeout_add(1000, self.hr_msrmt_cb)
#
#     def StartNotify(self):
#         if self.notifying:
#             print('Already notifying, nothing to do')
#             return
#
#         self.notifying = True
#         self._update_hr_msrmt_simulation()
#
#     def StopNotify(self):
#         if not self.notifying:
#             print('Not notifying, nothing to do')
#             return
#
#         self.notifying = False
#         self._update_hr_msrmt_simulation()
#
#
# class BodySensorLocationChrc(Characteristic):
#     BODY_SNSR_LOC_UUID = '2a38'
#
#     def __init__(self, bus, index, service):
#         Characteristic.__init__(
#                 self, bus, index,
#                 self.BODY_SNSR_LOC_UUID,
#                 ['read'],
#                 service)
#
#     def ReadValue(self, options):
#         # Return 'Chest' as the sensor location.
#         return [0x01]
#         '''
#         Key	Value
#         0	Other
#         1	Chest
#         2	Wrist
#         3	Finger
#         4	Hand
#         5	Ear Lobe
#         6	Foot
#         7 - 255	Reserved for future use
#         '''
#
#
# class HeartRateControlPointChrc(Characteristic):
#     HR_CTRL_PT_UUID = '2a39'
#
#     def __init__(self, bus, index, service):
#         Characteristic.__init__(
#                 self, bus, index,
#                 self.HR_CTRL_PT_UUID,
#                 ['write'],
#                 service)
#
#     def WriteValue(self, value, options):
#         print('Heart Rate Control Point WriteValue called')
#
#         if len(value) != 1:
#             raise InvalidValueLengthException()
#
#         byte = value[0]
#         print('Control Point value: ' + repr(byte))
#
#         if byte != 1:
#             raise FailedException("0x80")
#
#         print('Energy Expended field reset!')
#         self.service.energy_expended = 0
#

##############################################################################
# test of Cycling Speed and Cadence
##############################################################################


class CyclingSpeedCadence(Service):
    """
    Abstract:
    This service exposes speed-related and cadence-related data from a
    Cycling Speed and Cadence sensor intended for fitness applications.

    Summary:
    The Cycling Speed and Cadence (CSC) Service exposes speed-related data
    and/or cadence-related data while using the Cycling Speed and Cadence
    sensor (Server).

    Service Dependencies
    This service is not dependent upon any other services.

    """
    HR_UUID = '1816'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.HR_UUID, True)
        self.add_characteristic(CSCMeasurementChrc(bus, 0, self))
        self.add_characteristic(CSCFeatureChrc(bus, 1, self))
        self.add_characteristic(SensorLocationChrc(bus, 2, self))
        # self.add_characteristic(SCControlPointChrc(bus, 3, self))
        self.energy_expended = 0


class CSCMeasurementChrc(Characteristic):
    HR_MSRMT_UUID = '2A5B'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.HR_MSRMT_UUID,
                ['notify'],
                service)
        self.notifying = False

        '''
        Bit Field / Size 8 Bit
        1100 0000

            Bit 0 = Wheel Revolution Data Present / Size 1 Bit = "1" = "TRUE"
            Bit 1 = Crank Revolution Data Present / Size 1 Bit = 1 = "TRUE"
            Bit 2 = Reserved for future use / Size 6 Bits
            Bit 3 = extension of Bit 2

            Bit 4 = extension of Bit 2
            Bit 5 = extension of Bit 2
            Bit 6 = extension of Bit 2
            Bit 7 = extension of Bit 2
        '''

    def csc_msrmt_cb(self):
        value = []
        # FLAGS; 1100 0000 == 0x0192
        value.append(dbus.Byte(0xC0))
        # C1; Cumulative Wheel Revolutions
        value.append(dbus.Byte(100))
        # C1; Last Wheel Event Time
        value.append(dbus.Byte(150))
        # # # C2; Cumulative Crank Revolutions
        # value.append(dbus.Byte(200))
        # # # C2; Last Crank Event Time
        # value.append(dbus.Byte(250))

        print('Updating value: ' + repr(value))

        self.PropertiesChanged(GATT_CHRC_IFACE, {'Value': value}, [])

        return self.notifying

    def _update_csc_msrmt_simulation(self):
        print('Update CSC Measurement Simulation')

        if not self.notifying:
            return

        GObject.timeout_add(1000, self.csc_msrmt_cb)

    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
            return

        self.notifying = True
        self._update_csc_msrmt_simulation()

    def StopNotify(self):
        if not self.notifying:
            print('Not notifying, nothing to do')
            return

        self.notifying = False
        self._update_csc_msrmt_simulation()


class CSCFeatureChrc(Characteristic):
    BODY_SNSR_LOC_UUID = '2A5C'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.BODY_SNSR_LOC_UUID,
                ['read'],
                service)

    '''
    Bit Field / Size 16 Bit
    1110 0000 0000 0000

        Bit 0 = Wheel Revolution Data Supported / Size 1 Bit = "1" = "TRUE"
        Bit 1 = Crank Revolution Data Supported / Size 1 Bit = 1 = "TRUE"
        Bit 2 = Multiple Sensor Locations Supported	 / Size 1 Bit = 1 = "TRUE"
        Bit 3 = Reserved for future use

        Bit 4 = extension of Bit 3
        Bit 5 = extension of Bit 3
        Bit 6 = extension of Bit 3
        Bit 7 = extension of Bit 3
        ...
    '''

    def ReadValue(self, options):
        # FLAGS; 1110 0000 0000 0000 = 0x57344
        return [0x7]


class SensorLocationChrc(Characteristic):
    BODY_SNSR_LOC_UUID = '2A5D'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.BODY_SNSR_LOC_UUID,
                ['read'],
                service)

    '''
    Bit Field / UINT8

        Enumerations
        Key	Value
        0	Other
        1	Top of shoe
        2	In shoe
        3	Hip
        4	Front Wheel
        ...
    '''

    def ReadValue(self, options):
        # Enumerations; 0xA = 10 = Rear Dropout
        return [0xA]



#############################################################################
def register_app_cb():
    print('GATT application registered')


def register_app_error_cb(error):
    print('Failed to register application: ' + str(error))
    mainloop.quit()


def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                               DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if GATT_MANAGER_IFACE in props.keys():
            return o

    return None


def main():
    global mainloop

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    adapter = find_adapter(bus)
    if not adapter:
        print('GattManager1 interface not found')
        return

    service_manager = dbus.Interface(
            bus.get_object(BLUEZ_SERVICE_NAME, adapter),
            GATT_MANAGER_IFACE)

    app = Application(bus)

    mainloop = GObject.MainLoop()

    print('Registering GATT application...')

    service_manager.RegisterApplication(app.get_path(), {},
                                        reply_handler=register_app_cb,
                                        error_handler=register_app_error_cb)

    mainloop.run()


if __name__ == '__main__':
    main()
