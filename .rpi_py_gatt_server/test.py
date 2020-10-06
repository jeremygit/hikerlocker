from hikerlocker_ble_application import *

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
    self.hl_app.set_user_data('test')


def main():
  hl = HikerlockerTest()

if __name__ == '__main__':
    main()

