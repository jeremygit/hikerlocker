import sys
from pyee import BaseEventEmitter
import dbus
import dbus.mainloop.glib
import dbus.service
import dbus.exceptions
from gi.repository import GLib
import time

DBUS_OM_IFACE =                 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE =               'org.freedesktop.DBus.Properties'
BLUEZ_SERVICE_NAME =            'org.bluez'
ADAPTER_IFACE =                 'org.bluez.Adapter1'
LE_ADVERTISING_MANAGER_IFACE =  'org.bluez.LEAdvertisingManager1'
LE_ADVERTISEMENT_IFACE =        'org.bluez.LEAdvertisement1'
GATT_SERVICE_IFACE =            'org.bluez.GattService1'
GATT_MANAGER_IFACE =            'org.bluez.GattManager1'
GATT_CHRC_IFACE =               'org.bluez.GattCharacteristic1'

MAINLOOP = None

def BLEStringToBytes(str):
    return dbus.Array([dbus.Byte(ord(letter)) for letter in str], 'y')

class InvalidArgsException(dbus.exceptions.DBusException):
  _dbus_error_name = 'org.freedesktop.DBus.Error.InvalidArgs'

class NotSupportedException(dbus.exceptions.DBusException):
  _dbus_error_name = 'org.bluez.Error.NotSupported'

class BLECharacteristic(dbus.service.Object, BaseEventEmitter):

  def __init__(self, bus, index, uuid, flags, service):
    BaseEventEmitter.__init__(self)
    self.path = service.path + '/char' + str(index)
    self.bus = bus
    self.uuid = uuid
    self.service = service
    self.flags = flags
    self.descriptors = []
    self.value = [0]
    self.notifying = False
    dbus.service.Object.__init__(self, bus, self.path)
  
  def get_properties(self):
    return {
      GATT_CHRC_IFACE: {
        'UUID': self.uuid,
        'Service': self.service.get_path(),
        'Flags': self.flags,
        'Value': self.value,
        'Notifying': self.notifying,
        'Descriptors': dbus.Array(self.get_descriptors(), signature='o')
      }
    }
  
  def get_path(self):
    return dbus.ObjectPath(self.path)
  
  def add_descriptor(self, descriptor):
    self.descriptors.append(descriptor)

  def get_descriptor_paths(self):
    result = []
    for desc in self.descriptors:
      print('should be 0 descriptors')
      # result.append(desc.get_path())
    return result
  
  def get_descriptors(self):
    return self.descriptors

  @dbus.service.method(DBUS_PROP_IFACE,
    in_signature='s', out_signature='a{sv}')
  def GetAll(self, interface):
    if interface != GATT_CHRC_IFACE:
      raise InvalidArgsException()
    return self.get_properties()[GATT_CHRC_IFACE]

  @dbus.service.method(DBUS_PROP_IFACE,
    in_signature='ssv', out_signature='')
  def Set(self, interface, prop, value, *args, **kwargs):
    if interface != GATT_CHRC_IFACE:
      raise InvalidArgsException()
    # if prop no in self properties
    if (prop == 'Value'):
      self.value = value
    
    if (prop == 'Notifying'):
      self.notifying = value

    return self.PropertiesChanged(GATT_CHRC_IFACE,
      self.bus, dbus.Dictionary({prop: value}, signature='sv'),
      dbus.Array([], signature='s'))
  
  @dbus.service.method(DBUS_PROP_IFACE,
    signature='sa{sv}as')
  def PropertiesChanged(self, interface, changed, invalidated):
    print('change event emitted by dbus')


  @dbus.service.method(GATT_CHRC_IFACE,
    in_signature='a{sv}', out_signature='ay')
  def ReadValue(self, options):
    # raise NotSupportedException()
    # default
    return self.GetAll(GATT_CHRC_IFACE)['Value']

    #in sig was 'ay'
  @dbus.service.method(GATT_CHRC_IFACE,
    in_signature='aya{sv}')
  def WriteValue(self, value, options):
    # raise NotSupportedException()
    # default
    self.Set(GATT_CHRC_IFACE, 'Value', [value])

  @dbus.service.method(GATT_CHRC_IFACE)
  def StartNotify(self):
    print('StartNotify')
    self.Set(GATT_CHRC_IFACE, 'Notifying', dbus.Boolean(True))
    # raise NotSupportedException()

  @dbus.service.method(GATT_CHRC_IFACE)
  def StopNotify(self):
    print('StopNotify')
    self.Set(GATT_CHRC_IFACE, 'Notifying', dbus.Boolean(False))
    # raise NotSupportedException()

  @dbus.service.signal(DBUS_PROP_IFACE,
    signature='sa{sv}as')
  def PropertiesChanged(self, interface, changed, invalidated):
    pass


class BLEService(dbus.service.Object, BaseEventEmitter):

  PATH_BASE = '/org/bluez/hikerlocker/service'

  def __init__(self, bus, index, uuid, primary):
    BaseEventEmitter.__init__(self)
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
        'Characteristics': dbus.Array(self.get_characteristic_paths(), signature='o')
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
    in_signature='s', out_signature='a{sv}')
  def GetAll(self, interface):
    if interface != GATT_SERVICE_IFACE:
      raise InvalidArgsException()
    return self.get_properties[GATT_SERVICE_IFACE]
  
  @dbus.service.method(DBUS_OM_IFACE,
    out_signature='a{oa{sa{sv}}}')
  def GetManagedObjects(self):
    response = {}
    print('GetManagedObjects')

    reponse[self.get_path()] = self.get_properties()
    chrcs = self.get_characteristics()
    for chrc in chrcs:
        reponse[chrc.get_path()] = chrc.get_properties()
        # Ignoring descriptors
    return response


class BLEApplication(dbus.service.Object, BaseEventEmitter):
  ''' org.bluez.GattApplication1 '''
  def __init__(self, bus):
    BaseEventEmitter.__init__(self)
    self.path = '/'
    self.services = []
    dbus.service.Object.__init__(self, bus, self.path)

  def get_path(self):
    return dbus.ObjectPath(self.path)
  
  def add_service(self, service):
    self.services.append(service)

  @dbus.service.method(DBUS_OM_IFACE,
    out_signature='a{oa{sa{sv}}}')
  def GetManagedObjects(self):
    response = {}
    print('GetManagedObjects')

    for service in self.services:
      print('service')
      print(service)
      response[service.get_path()] = service.get_properties()
      print('got path')
      chrcs = service.get_characteristics()
      print('got chrcs')
      for chrc in chrcs:
        response[chrc.get_path()] = chrc.get_properties()
        #ignore descriptors
    print('response')
    print(response)
    return response


class BLEAdvertisement(dbus.service.Object, BaseEventEmitter):

  PATH_BASE = '/org/bluez/hikerlocker/advertisement'

  def __init__(self, bus, index, advertising_type):
    BaseEventEmitter.__init__(self)
    self.path = self.PATH_BASE + str(index)
    self.bus = bus
    self.adv_type = advertising_type
    self.service_uuids = None
    self.manufacturer_data = None
    self.solicit_uuids = None
    self.service_data = None
    self.local_name = None
    self.include_tx_power = None
    dbus.service.Object.__init__(self, bus, self.path)

  def get_properties(self):
    properties = dict()
    properties['Type'] = self.adv_type
    if self.service_uuids != None:
      properties['ServiceUUIDs'] = dbus.Array(self.service_uuids, signature='s')
    if self.solicit_uuids != None:
      properties['SolicitUUIDs'] = dbus.Array(self.solicit_uuids, signature='s')
    if self.manufacturer_data != None:
      properties['ManufacturerData'] = dbus.Dictionary(self.manufacturer_data, signature='qv')
    if self.service_data != None:
      properties['ServiceData'] = dbus.Dictionary(self.service_data, signature='sv')
    if self.include_tx_power != None:
      properties['IncludeTxPower'] = dbus.Boolean(self.include_tx_power)
    if self.local_name != None:
      properties['LocalName'] = dbus.String(self.local_name)
    return {LE_ADVERTISEMENT_IFACE: properties}
  
  def get_path(self):
    return dbus.ObjectPath(self.path)
  
  def add_service_uuid(self, uuid):
    if self.service_uuids == None:
      self.service_uuids = []
    self.service_uuids.append(uuid)
  
  def add_solicit_uuid(self, uuid):
    if self.solicit_uuids == None:
      self.solicit_uuids = []
    self.solicit_uuids.append(uuid)
  
  def add_manufacturer_data(self, manuf_code, data):
    if self.manufacturer_data == None:
      self.manufacturer_data = dbus.Dictionary({}, signature='qv')
    self.manufacturer_data[manuf_code] = dbus.Array(data, signature='y')
  
  def add_service_data(self, uuid, data):
    if self.service_data == None:
      self.service_data = dbus.Dictionary({}, signature='sv')
    self.service_data[uuid] = dbus.Array(data, signature='y')
  
  def add_local_name(self, name):
    if self.local_name == None:
      self.local_name = ''
    self.local_name = dbus.String(name)
  
  @dbus.service.method(DBUS_PROP_IFACE,
    in_signature='s', out_signature='a{sv}')
  def GetAll(self, interface):
    print('GetAll')
    print(interface)
    if interface != LE_ADVERTISEMENT_IFACE:
      raise InvalidArgsException()
    print('returning props')
    return self.get_properties()[LE_ADVERTISEMENT_IFACE]
  
  @dbus.service.method(LE_ADVERTISEMENT_IFACE,
    in_signature='', out_signature='')
  def Release(self):
    print('%s: Released!' % self.path)

class BLEGattServer(BaseEventEmitter):
  def __init__(self):
    BaseEventEmitter.__init__(self)

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    self.mainloop = GLib.MainLoop()

    self.bus = dbus.SystemBus()

    self.adapter = self.find_adapter()

    self.advertisement = None
    self.application = None

    if (self.adapter == None):
      raise Exception('No adapter found')

    self.app_service_manager = dbus.Interface(
      self.bus.get_object(BLUEZ_SERVICE_NAME, self.adapter), GATT_MANAGER_IFACE)

    self.advertisement_manager = dbus.Interface(
      self.bus.get_object(BLUEZ_SERVICE_NAME, self.adapter), LE_ADVERTISING_MANAGER_IFACE)
  
  def startAdvertising(self):
    # Power on BLE
    adapter_props = dbus.Interface(
      self.bus.get_object(BLUEZ_SERVICE_NAME, self.adapter), DBUS_PROP_IFACE)
    adapter_props.Set(ADAPTER_IFACE, 'Powered', dbus.Boolean(1))

    try:
      print('mainloop.run')
      self.mainloop.run()
    except KeyboardInterrupt:
      if (self.advertisement):
        self.advertisement.Release()
      self.mainloop.quit()

  def testExec(self):
    self.emit('ready')

  def handle_advertisement_success(self):
    print('handle_advertisement_success')

  def handle_advertisement_error(self):
    print('handle_advertisement_error')
  
  def handle_application_success(self):
    print('handle_application_success')
  
  def handle_application_error(self):
    print('handle_application_error')

  def find_adapter(self):
    remote_om = dbus.Interface(
      self.bus.get_object(BLUEZ_SERVICE_NAME, '/'), DBUS_OM_IFACE)

    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
      if LE_ADVERTISING_MANAGER_IFACE in props and GATT_MANAGER_IFACE in props:
        return o
      print('Skip adapter:', o)
    return None
  
  def setAdvertisement(self, advertisement):
    self.advertisement = advertisement
    self.advertisement_manager.RegisterAdvertisement(advertisement.get_path(), {},
      reply_handler=self.handle_advertisement_success,
      error_handler=self.handle_advertisement_error)

  def setApplication(self, application):
    self.application = application
    self.app_service_manager.RegisterApplication(application.get_path(), {},
      reply_handler=self.handle_application_success,
      error_handler=self.handle_application_error)
