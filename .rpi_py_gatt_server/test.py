from hikerlocker_ble_application import *
import time
import json

class HikerlockerTest():

  hl_server = None
  hl_app = None

  def __init__(self):
    self.hl_server = BLEGattServer()
    self.hl_app = HikerlockerApplication(self.hl_server)
    self.hl_app.on('char_write', self.handle_char_in)

    self.hl_server.setApplication(self.hl_app)
    self.hl_server.setAdvertisement(self.hl_app.advertisement)
    self.hl_server.startAdvertising()

  def handle_char_in(self, char, data):
    print('application did write')
    print('data')
    data = bytes(data).decode()
    print(data)
    print('setting data...')
    outgoing_data = {
      'markerId': 'xxxxxxxxxxx',
      'userVisits': [data, '00000000000']
    }
    print(outgoing_data)
    outgoing_data = json.dumps(outgoing_data)
    print(outgoing_data)
    self.hl_app.set_user_data( BLEStringToBytes(outgoing_data) )
    # time.sleep(1)


def main():
  hl = HikerlockerTest()

if __name__ == '__main__':
    main()

