from hikerlocker_ble_application import *

def handle_char_write(char, data):
  print('application did write')

def main():
  hlserver = HikerlockerGattServer()
  ta = TestApplication(hlserver)
  ta.on('char_write', handle_char_write)
  hlserver.setApplication(ta)
  hlserver.setAdvertisement(ta.advertisement)
  hlserver.startAdvertising()

if __name__ == '__main__':
    main()

