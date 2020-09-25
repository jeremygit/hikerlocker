import React, { useContext } from 'react';
import logo from './logo.svg';
import './App.css';
import { BLEContext, BLEContextProvider } from './contexts/BLEContext';

function App() {
  return (
    <BLEContextProvider>
      <div className="App">
        <AppMain />
      </div>
    </BLEContextProvider>
  );
}

function AppMain() {

  const bleContext = useContext(BLEContext);

  const onClickScan = (evt) => {
    bleContext.startScan(evt);
  }

  const onSelectChar = (uuid) => (evt) => {
    bleContext.executeCharactersitic(uuid);
  }

  return (
    <main>
      <h2>Hikerlocker {bleContext.connectionState}</h2>
      <button onClick={onClickScan}>Scan</button>
      {
        bleContext.connectionState == 2
        ? bleContext.smartMarkerCommands.map((cmdObj) => (
          <div key={cmdObj.code}>{cmdObj.displayName}</div>
        ))
        : <div>Awaiting Connection...</div>
      }
     {
        bleContext.connectionState == 2
        ? bleContext.characteristics.map((char) => (
          <div key={char.uuid} onClick={onSelectChar(char.uuid)}>{char.uuid}</div>
        ))
        : <div>Awaiting Characterisics...</div>
      }
    </main>
  )
}

export default App;
