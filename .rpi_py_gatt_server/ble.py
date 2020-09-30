# run on RaspberryPi
# $ sudo python3 ble.py
# ---------------------
# https://kernel.googlesource.com/pub/scm/bluetooth/bluez/+/5.36/test/example-gatt-server
# https://github.com/RadiusNetworks/bluez/blob/master/test/example-advertisement
# https://scribles.net/creating-ble-gatt-server-uart-service-on-raspberry-pi/
import sys
import dbus
import dbus.mainloop.glib
import dbus.service
import dbus.exceptions
from gi.repository import GLib

DBUS_OM_IFACE =                 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE =               'org.freedesktop.DBus.Properties'
BLUEZ_SERVICE_NAME =            'org.bluez'
ADAPTER_IFACE =                 'org.bluez.Adapter1'
LE_ADVERTISING_MANAGER_IFACE =  'org.bluez.LEAdvertisingManager1'
LE_ADVERTISEMENT_IFACE =        'org.bluez.LEAdvertisement1'
GATT_SERVICE_IFACE =            'org.bluez.GattService1'
GATT_MANAGER_IFACE =            'org.bluez.GattManager1'
GATT_CHRC_IFACE =               'org.bluez.GattCharacteristic1'
# Services
LOCAL_NAME =                    'rpi-gatt-server'
mainloop = None

class InvalidArgsException(dbus.exceptions.DBusException):
  _dbus_error_name = 'org.freedesktop.DBus.Error.InvalidArgs'

class NotSupportedException(dbus.exceptions.DBusException):
  _dbus_error_name = 'org.bluez.Error.NotSupported'

# https://github.com/luetzel/bluez/blob/master/test/example-advertisement worked
# https://github.com/hadess/bluez/blob/master/test/example-advertisement promising
# https://github.com/RadiusNetworks/bluez/blob/master/test/example-advertisement didnt work
class Advertisement(dbus.service.Object):

  PATH_BASE = '/org/bluez/test/advertisement'

  def __init__(self, bus, index, advertising_type):
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


class Service(dbus.service.Object):
  PATH_BASE = '/org/bluez/test/service'

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

class Characteristic(dbus.service.Object):
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
  
  @dbus.service.method(GATT_CHRC_IFACE,
    in_signature='a{sv}', out_signature='ay')
  def ReadValue(self, options):
    raise NotSupportedException()

    #in sig was 'ay'
  @dbus.service.method(GATT_CHRC_IFACE,
    in_signature='aya{sv}')
  def WriteValue(self, value, options):
    raise NotSupportedException()

  @dbus.service.method(GATT_CHRC_IFACE)
  def StartNotify(self):
    raise NotSupportedException()

  @dbus.service.method(GATT_CHRC_IFACE)
  def StopNotify(self):
    raise NotSupportedException()

  @dbus.service.signal(DBUS_PROP_IFACE,
    signature='sa{sv}as')
  def PropertiesChanged(self, interface, changed, invalidated):
    pass

class TestCharacteristic(Characteristic):
  UUID = '12345678-1234-5678-1234-56789abcdef1'
  def __init__(self, bus, index, service):
    Characteristic.__init__(
      self, bus, index, self.UUID,
      ['read', 'write', 'write-without-response', 'reliable-write', 'writable-auxiliaries'],
      service)
    self.value = [0]

  def ReadValue(self, options):
    print('TestCharacteristic Read: ' + repr(self.value))
    val = self.value[0]
    val = val + 1
    self.value[0] = val
    return self.value
  
  def WriteValue(self, value, options):
    print('TestCharacteristic Write: ' + repr(value))
    self.value = value

class TestService(Service):
  UUID = 'ffffffff-eeee-eeee-eeee-dddddddddddd'
  def __init__(self, bus, index):
    Service.__init__(self, bus, index, self.UUID, True)
    self.add_characteristic(TestCharacteristic(bus, 0, self))


class TestAdvertisement(Advertisement):
  def __init__(self, bus, index):
    Advertisement.__init__(self, bus, index, 'peripheral')
    self.add_service_uuid('ffffffff-eeee-eeee-eeee-dddddddddddd')
    # self.add_service_uuid('180F')
    # self.add_manufacturer_data(0xffff, [0x00, 0x01, 0x02, 0x03, 0x04])
    # self.add_service_data('9999', [0x00, 0x01, 0x02, 0x03, 0x04])
    self.add_local_name('Test RPi')
    self.include_tx_power = True

class Application(dbus.service.Object):
  ''' org.bluez.GattApplication1 '''
  def __init__(self, bus):
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

class TestApplication(Application):
  def __init__(self, bus):
    Application.__init__(self, bus)
    # add service

def register_service_cb():
  print('register_service_cb')

def register_service_error_cb(error):
  print('register_service_error_cb')
  mainloop.quit()

def register_app_cb():
  print('register_app_cb')

def register_app_error_cb(error):
  print('register_app_error_cb: ' + str(error))
  mainloop.quit()

def register_ad_cb():
  print('register_ad_cb')

def register_ad_error_cb(error):
  print('register_ad_error_cb: ' + str(error))
  mainloop.quit()

def find_adapter(bus):
  remote_om = dbus.Interface(
    bus.get_object(BLUEZ_SERVICE_NAME, '/'), DBUS_OM_IFACE)
  objects = remote_om.GetManagedObjects()
  print(objects)
  for o, props in objects.items():
    if LE_ADVERTISING_MANAGER_IFACE in props and GATT_MANAGER_IFACE in props:
      return o
    print('Skip adapter:', o)
  return None

def main():
  global mainloop
  dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
  bus = dbus.SystemBus()
  adapter = find_adapter(bus)

  if not adapter:
    return 

  adapter_props = dbus.Interface(
    bus.get_object(BLUEZ_SERVICE_NAME, adapter), DBUS_PROP_IFACE)
  adapter_props.Set(ADAPTER_IFACE, 'Powered', dbus.Boolean(1))

  # service
  service = dbus.Interface(
    bus.get_object(BLUEZ_SERVICE_NAME, adapter), GATT_MANAGER_IFACE)

  # advertisement
  advertisement = dbus.Interface(
    bus.get_object(BLUEZ_SERVICE_NAME, adapter), LE_ADVERTISING_MANAGER_IFACE)

  # app
  app = TestApplication(bus)

  test_service = TestService(bus, 0)
  app.add_service(test_service)


  
  # adv
  adv = TestAdvertisement(bus, 1)

  mainloop = GLib.MainLoop()

  # service - register app
  service.RegisterApplication(app.get_path(), {},
    reply_handler=register_app_cb,
    error_handler=register_app_error_cb)
  # service.RegisterService(test_service.get_path(), {},
  #   reply_handler=register_service_cb,
  #   error_handler=register_service_error_cb)

  # advertisement - register advertisement
  advertisement.RegisterAdvertisement(adv.get_path(), {},
    reply_handler=register_ad_cb,
    error_handler=register_ad_error_cb)

  try:
    print('mainloop.run')
    mainloop.run()
  except KeyboardInterrupt:
    adv.Release()
    mainloop.quit()

if __name__ == '__main__':
    main()