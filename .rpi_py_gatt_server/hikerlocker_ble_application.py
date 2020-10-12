from ble.lib import *
import dbus

class HikerlockerCheckoutCharacteristic(BLECharacteristic):

  UUID = 'ffffffff-eeee-eeee-eeee-dddd00000003'

  def __init__(self, bus, index, service):
    BLECharacteristic.__init__(
      self, bus, index, self.UUID,
      ['read','write', 'write-without-response', 'notify', 'reliable-write', 'writable-auxiliaries'],
      service)

class HikerlockerCheckinCharacteristic(BLECharacteristic):

  UUID = 'ffffffff-eeee-eeee-eeee-dddd00000002'

  def __init__(self, bus, index, service):
    BLECharacteristic.__init__(
      self, bus, index, self.UUID,
      ['read','write', 'write-without-response', 'notify', 'reliable-write', 'writable-auxiliaries'],
      service)

class HikerlockerUserReadWriteCharacteristic(BLECharacteristic):

  UUID = 'ffffffff-eeee-eeee-eeee-dddd00000001'

  def __init__(self, bus, index, service):
    BLECharacteristic.__init__(
      self, bus, index, self.UUID,
      ['read','write', 'write-without-response', 'notify', 'reliable-write', 'writable-auxiliaries'],
      service)

  def ReadValue(self, options):
    print('HikerlockerUserReadWriteCharacteristic Read: ' + repr(self.GetAll(GATT_CHRC_IFACE)['Value']))
    # val = self.value[0]
    # val = val + 1
    # self.value[0] = val
    #return self.value
    return self.GetAll(GATT_CHRC_IFACE)['Value']
  
  def WriteValue(self, value, options):
    print('HikerlockerUserReadWriteCharacteristic Write: ' + repr(value))
    # self.value = value
    self.emit('value', self, value)
    self.Set(GATT_CHRC_IFACE, 'Value', value)
  
  def set_value(self, value):
    print('HikerlockerUserReadWriteCharacteristic set_value' + repr(value))
    # self.value[0] = value
    # self.WriteValue(value)
    self.Set(GATT_CHRC_IFACE, 'Value', value)
    

class HikerlockerPrimaryService(BLEService):

  UUID = 'ffffffff-eeee-eeee-eeee-dddddddddddd'

  user_readwrite_char = None

  def __init__(self, bus, index):
    BLEService.__init__(self, bus, index, self.UUID, True)
    self.user_readwrite_char = HikerlockerUserReadWriteCharacteristic(bus, 0, self)
    self.user_readwrite_char.on('value', self.handle_char_write)
    self.add_characteristic(self.user_readwrite_char)

    self.checkin_char = HikerlockerCheckinCharacteristic(bus, 1, self)
    self.add_characteristic(self.checkin_char)

    self.checkout_char = HikerlockerCheckoutCharacteristic(bus, 2, self)
    self.add_characteristic(self.checkout_char)
  
  def set_read_char(self, uuid, data):
    pass

  def handle_char_write(self, char, data):
    print('HikerlockerPrimaryService handle_char_write')
    self.emit('char_write', char, data)

  def set_user_data(self, data):
    print('HikerlockerPrimaryService set_user_data')
    self.user_readwrite_char.set_value(data)

class HikerlockerAdvertisement(BLEAdvertisement):
  def __init__(self, bus, index, primary_service):
    BLEAdvertisement.__init__(self, bus, index, 'peripheral')
    # todo: make init arguments
    self.add_service_uuid(primary_service.UUID)
    self.add_local_name('Hikerlocker RPi')
    self.include_tx_power = True

class HikerlockerApplication(BLEApplication):

  primary_service = None

  def __init__(self, server):
    BLEApplication.__init__(self, server.bus)
    self.primary_service = HikerlockerPrimaryService(server.bus, 0)
    self.primary_service.on('char_write', self.handle_char_write)
    self.add_service(self.primary_service)
    self.advertisement = HikerlockerAdvertisement(server.bus, 0, self.primary_service)
  
  def handle_char_write(self, char, data):
    print('HikerlockerApplication handle_char_write')
    self.emit('char_write', char, data)
  
  def set_user_data(self, data):
    print('HikerlockerApplication set_user_data')
    self.primary_service.set_user_data(data)
