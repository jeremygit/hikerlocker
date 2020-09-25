import React, { createContext, useEffect, useState } from 'react';

export const BLEContext = createContext();

const BLE_PRIMARY_SERVICE = 'FFFFFFFF-EEEE-EEEE-EEEE-DDDDDDDDDDDD'.toLowerCase();

const HIKER_BLE_SERVICES = [
  BLE_PRIMARY_SERVICE,
];

const HIKER_SMARTMARKER_CMD = [
  {code: 0, displayName: 'Log Visit'},
  {code: 1, displayName: 'Check-in'},
  {code: 2, displayName: 'Check-out'},
];

const BLE_CONNECTION_STATE = {
  'DISCONNECTED': 0,
  'CONNECTING': 1,
  'CONNECTED': 2,
};

export const BLEContextProvider = ({ children }) => {

  const [state, setState] = useState({
    device: null,
    primaryService: null,
    characteristics: null,
    currentCharacteristic: null,
    connectionState: BLE_CONNECTION_STATE.DISCONNECTED,
  });

  const startScan = async (evt) => {
    setState({...state, connectionState: BLE_CONNECTION_STATE.CONNECTING});
    try {
      // connect device
      const device = await navigator.bluetooth.requestDevice({
        optionalServices: HIKER_BLE_SERVICES,
        acceptAllDevices: true,
      });

      device.addEventListener('gattserverdisconnected', () => {
        alert('disconnected');
        setState({...state, connectionState: BLE_CONNECTION_STATE.DISCONNECTED});
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

  const executeCharactersitic = async (uuid, data) => {
    // set as current char, connect, write/read etc.
    // - visit char = handleLogVisit etc.?
    try {
      const char = findCharacteristic(uuid);
      console.log('char', char);
      setState({...state, currentCharacteristic: char});
    } catch (err) {
      // handle  error
      console.log(err);
    }
  }

  const bleNotifyValue = async () => {
    try {
      state.currentCharacteristic.addEventListener('characteristicvaluechanged', bleNotifyValueChanged);
      state.currentCharacteristic.startNotifications();
    } catch (err) {
      console.log(err);
    }
  }

  const bleNotifyValueChanged = (evt) => {
    const decoder = new TextDecoder('utf-8');
    console.log(decoder.decode(evt.target.value));
  }

  const bleWriteValue = async () => {
    try {
      const testData = new Uint8Array([1]);
      const res = await state.currentCharacteristic.writeValueWithResponse(testData);
      console.log('res', res);
    } catch (err) {
      // handle write error
      // DOMException: GATT operation failed for unknown reason.
      console.log(err);
    }
  }

  const bleReadSharedValue = () => {
    try {
      state.currentCharacteristic.addEventListener('characteristicvaluechanged', bleReadValueChanged);
      state.currentCharacteristic.readValue();
    } catch (err) {
      console.log(err);
    }
  }

  const bleReadValueChanged = (evt) => {
    const decoder = new TextDecoder('utf-8');
    console.log(decoder.decode(evt.target.value));
  }

  useEffect(() => {
    // if is set...
    if (state.currentCharacteristic) {
      // if for writing
      // bleWriteValue();

      // if notifying
      // bleNotifyValue();

      // if value for reading
      bleReadSharedValue();
    }
    return () => {
      // if change
    };
  }, [state.currentCharacteristic])

  return (
    <BLEContext.Provider value={
      {...state, 
        startScan: startScan,
        executeCharactersitic, executeCharactersitic,
        text: 'text',
        smartMarkerCommands: HIKER_SMARTMARKER_CMD,
      }
    }>
    {children}
  </BLEContext.Provider>
  )
}