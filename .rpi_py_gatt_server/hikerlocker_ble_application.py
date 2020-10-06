from ble.lib import *
import dbus

class HikerlockerUserReadWriteCharacteristic(BLECharacteristic):

  UUID = 'ffffffff-eeee-eeee-eeee-dddd00000001'

  def __init__(self, bus, index, service):
    BLECharacteristic.__init__(
      self, bus, index, self.UUID,
      ['read', 'write', 'write-without-response', 'reliable-write', 'writable-auxiliaries'],
      service)
    self.value = []

  def ReadValue(self, options):
    print('TestCharacteristic Read: ' + repr(self.value))
    # val = self.value[0]
    # val = val + 1
    # self.value[0] = val
    return self.value
  
  def WriteValue(self, value, options):
    print('TestCharacteristic Write: ' + repr(value))
    self.emit('value', self, self.value)
    self.value = value
  
  def set_value(self, value):
    self.value = [value]
    

class HikerlockerPrimaryService(BLEService):

  UUID = 'ffffffff-eeee-eeee-eeee-dddddddddddd'

  user_readwrite_char = None

  def __init__(self, bus, index):
    BLEService.__init__(self, bus, index, self.UUID, True)
    self.user_readwrite_char = HikerlockerUserReadWriteCharacteristic(bus, 0, self)
    self.user_readwrite_char.on('value', self.handle_char_write)
    self.add_characteristic(self.user_readwrite_char)
  
  def set_read_char(self, uuid, data):
    pass

  def handle_char_write(self, char, data):
    print('TestPrimaryService handle_char_write')
    self.emit('char_write', char, data)

  def set_user_data(self, data):
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
    print('TestApplication handle_char_write')
    self.emit('char_write', char, data)
  
  def set_user_data(self, data):
    self.primary_service.set_user_data(data)
