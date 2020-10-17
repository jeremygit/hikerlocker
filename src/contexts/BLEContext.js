import React, { createContext, useEffect, useState } from 'react';

export const BLEContext = createContext();

const BLE_PRIMARY_SERVICE = 'FFFFFFFF-EEEE-EEEE-EEEE-DDDDDDDDDDDD'.toLowerCase();

const HIKER_BLE_SERVICES = [
  BLE_PRIMARY_SERVICE,
];

const BLE_CHARACTERISTICS = {
  LOG_VISIT: 'ffffffff-eeee-eeee-eeee-dddd00000001',
  CHECK_IN: 'ffffffff-eeee-eeee-eeee-dddd00000002',
  CHECK_OUT: 'ffffffff-eeee-eeee-eeee-dddd00000003',
}

const BLE_ROUTE_NAMES = {
  LOG_VISIT: 'log-visit',
  CHECK_IN: 'check-in',
  CHECK_OUT: 'check-out',
}

const BLE_CONNECTION_STATE = {
  'DISCONNECTED': 0,
  'CONNECTING': 1,
  'CONNECTED': 2,
};

const BLE_CHARACTERISTIC_CMD = {
  [BLE_CHARACTERISTICS.LOG_VISIT]: {
    route: BLE_ROUTE_NAMES.LOG_VISIT,
    name: 'Log Visit',
  },
  [BLE_CHARACTERISTICS.CHECK_IN]: {
    route: BLE_ROUTE_NAMES.CHECK_IN,
    name: 'Check In',
  }, 
  [BLE_CHARACTERISTICS.CHECK_OUT]: {
    route: BLE_ROUTE_NAMES.CHECK_OUT,
    name: 'Check Out',
  },
};

const BLE_TRANSFER_STATUS = {
  READY: 0,
  IN_PROGRESS: 1,
  COMPLETE: 2,
};

export const BLEContextProvider = ({ children }) => {

  const [state, setState] = useState({
    device: null,
    primaryService: null,
    characteristics: null,
    currentCharacteristic: null,
    connectionState: BLE_CONNECTION_STATE.DISCONNECTED,
    transferStatus: BLE_TRANSFER_STATUS.READY,
  });

  const [bleDataIn, setBleDataIn] = useState(null);

  const startScan = async (evt) => {
    setState({...state, connectionState: BLE_CONNECTION_STATE.CONNECTING});
    try {
      // connect device
      const device = await navigator.bluetooth.requestDevice({
        optionalServices: HIKER_BLE_SERVICES,
        acceptAllDevices: true,
      });

      device.addEventListener('gattserverdisconnected', () => {
        setState({...state, 
          connectionState: BLE_CONNECTION_STATE.DISCONNECTED,
          device: null,
        });
      });

      // connect to the gatt server
      const deviceServer = await device.gatt.connect();

      // connect service
      const primaryService = await deviceServer.getPrimaryService(BLE_PRIMARY_SERVICE);

      // get the characterstics
      const characteristics = await primaryService.getCharacteristics();
      console.log(characteristics);

      setState({...state, 
        connectionState: BLE_CONNECTION_STATE.CONNECTED,
        device: device,
        primaryService: primaryService,
        characteristics: characteristics,
      });

    } catch (err) {
      console.log(err);

      setState({...state, connectionState: BLE_CONNECTION_STATE.DISCONNECTED});
      
      handleDeviceScanError();

    } finally {
      //
    }
  }

  const handleDeviceScanError = () => {
    // do soemething
  }

  // OR make them a data structure
  const findCharacteristic = (uuid) => {
    return state.characteristics.find((char) => char.uuid === uuid);
  }

  const executeBLECommand = async (uuid, data) => {
    try {
      const char = findCharacteristic(uuid);
      routeCommand(uuid, char, data);
      // const res_notify = await char.startNotifications();
    } catch (err) {
      console.log(err);
    }
  }

  const routeCommand = async (uuid, char, data) => {
    switch (BLE_CHARACTERISTIC_CMD[uuid].route) {
      case BLE_ROUTE_NAMES.LOG_VISIT: return performLogVisit(char, data);
      default: 
        throw 'command didnt exist';
    }
  }

  const performLogVisit = async (char, data) => {
    setState({...state, transferStatus: BLE_TRANSFER_STATUS.IN_PROGRESS});
    const userId = bleEncodeString(data);
    // const testData = new Uint8Array([1]); // writeValueWithResponse
    const res = await char.writeValue(userId);

    char.oncharacteristicvaluechanged = bleReadValueChanged;
    const res_notify = await char.readValue();
  }

  const bleNotifyValue = async () => {
    try {
      state.currentCharacteristic.oncharacteristicvaluechanged = bleReadValueChanged;
      state.currentCharacteristic.startNotifications();
    } catch (err) {
      console.log(err);
    }
  }

  const bleNotifyValueChanged = (evt, char) => {
    setState({...state, transferStatus: BLE_TRANSFER_STATUS.COMPLETE});
    const decoder = new TextDecoder('utf-8');
    const jsonStr = decoder.decode(evt.target.value);
    const jsonData =  JSON.parse(jsonStr);
    alert(jsonStr);
    setState({...state, transferStatus: BLE_TRANSFER_STATUS.READY});
  }

  const bleWriteValue = async () => {
    try {
      const testData = new Uint8Array([1]); // writeValueWithResponse
      const res = await state.currentCharacteristic.writeValue(testData);
      console.log('res', res);

    } catch (err) {
      // handle write error
      // DOMException: GATT operation failed for unknown reason.
      console.log(err);
    }
  }

  const bleReadSharedValue = async () => {
    try {
      state.currentCharacteristic.addEventListener('characteristicvaluechanged', bleReadValueChanged);
      const res = await state.currentCharacteristic.readValue();
      console.log('res', res);
    } catch (err) {
      console.log(err);
    }
  }

  const bleReadValueChanged = (evt) => {
    setState({...state, transferStatus: BLE_TRANSFER_STATUS.COMPLETE});
    const decoder = new TextDecoder('utf-8');
    const jsonStr = decoder.decode(evt.target.value);
    const jsonData =  JSON.parse(jsonStr);
    console.log(decoder.decode(evt.target.value));
    setBleDataIn(jsonData);
    setState({...state, transferStatus: BLE_TRANSFER_STATUS.READY});
    console.log('bleDataIn', bleDataIn);
    disconnect();
  }

  useEffect(() => {
    // if is set...
    if (state.currentCharacteristic) {
      // if for writing
      // bleWriteValue();

      // if notifying
      // bleNotifyValue();

      // if value for reading
      // bleReadSharedValue();
    }
    return () => {
      // if change
    };
  }, [state.currentCharacteristic]);

  const executeCommand = () => {
    bleWriteValue();
  }

  const disconnect = () => {
    if (state.device) {
      state.device.gatt.disconnect();
    }
  }

  const bleEncodeString = (str) => {
    return new TextEncoder('utf-8').encode(`${str}`);
  }

  const getCmdRoute = (uuid) => {
    if (!BLE_CHARACTERISTIC_CMD[uuid]) {
      throw 'command not a valid';
    }
    return BLE_CHARACTERISTIC_CMD[uuid].route;
  }

  const logVisit = (userUUID) => {
    return executeBLECommand(BLE_CHARACTERISTICS.LOG_VISIT, userUUID);
  }

  const clearBleDataIn = () => {
    setBleDataIn(null);
  }

  return (
    <BLEContext.Provider value={
      {...state, 
        startScan: startScan,
        executeCommand: executeCommand,
        executeBLECommand: executeBLECommand,
        text: 'text',
        disconnect: disconnect,
        getCmdRoute: getCmdRoute,
        logVisit: logVisit,
        BLE_CHARACTERISTIC_CMD: BLE_CHARACTERISTIC_CMD,
        BLE_ROUTE_NAMES: BLE_ROUTE_NAMES,
        bleDataIn: bleDataIn,
        clearBleDataIn: clearBleDataIn,
      }
    }>
    {children}
  </BLEContext.Provider>
  )
}