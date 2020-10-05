from ble.lib import *
import dbus

class TestCharacteristic(BLECharacteristic):

  UUID = '12345678-1234-5678-1234-56789abcdef1'

  def __init__(self, bus, index, service):
    BLECharacteristic.__init__(
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
    self.emit('value', self, self.value)
    self.value = value

class TestPrimaryService(BLEService):

  UUID = 'ffffffff-eeee-eeee-eeee-dddddddddddd'

  def __init__(self, bus, index):
    BLEService.__init__(self, bus, index, self.UUID, True)
    test_char = TestCharacteristic(bus, 0, self)
    test_char.on('value', self.handle_char_write)
    self.add_characteristic(test_char)
  
  def set_read_char(self, uuid, data):
    pass

  def handle_char_write(self, char, data):
    print('TestPrimaryService handle_char_write')
    self.emit('char_write', char, data)

class TestAdvert(BLEAdvertisement):
  def __init__(self, bus, index):
    BLEAdvertisement.__init__(self, bus, index, 'peripheral')
    # todo: make init arguments
    self.add_service_uuid('ffffffff-eeee-eeee-eeee-dddddddddddd')
    self.add_local_name('Test RPi')
    self.include_tx_power = True

class TestApplication(BLEApplication):
  def __init__(self, server):
    BLEApplication.__init__(self, server.bus)
    self.primary_service = TestPrimaryService(server.bus, 0)
    self.primary_service.on('char_write', self.handle_char_write)
    self.add_service(self.primary_service)
    self.advertisement = TestAdvert(server.bus, 0)
  
  def handle_char_write(self, char, data):
    print('TestApplication handle_char_write')
    self.emit('char_write', char, data)