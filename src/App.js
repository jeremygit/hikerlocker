import React, { useContext } from 'react';
import logo from './logo.svg';
import './App.css';
import { BLEContext, BLEContextProvider } from './contexts/BLEContext';
import { AuthContext, AuthContextProvider } from './contexts/AuthContext';

import Container from '@material-ui/core/Container';
import Box from '@material-ui/core/Box';
import Button from '@material-ui/core/Button';
import { AppBar, Toolbar } from '@material-ui/core';

function App() {
  return (
    <AuthContextProvider>
    <BLEContextProvider>
      <div className="App">
        <AppMain />
      </div>
    </BLEContextProvider>
    </AuthContextProvider>
  );
}

function AppMain() {

  const bleContext = useContext(BLEContext);

  const authContext = useContext(AuthContext);

  const onClickScan = (evt) => {
    bleContext.startScan(evt);
  }

  const onSelectChar = (uuid) => (evt) => {
    bleContext.executeCharactersitic(uuid);
  }

  const onClickReadWrite = () => {
    bleContext.executeCommand();
  }

  return (
    <>
      <AppBar position="fixed">
        <Toolbar>
          <h2>Hikerlocker {bleContext.connectionState}</h2>
          <AuthToolbar/>
        </Toolbar>
      </AppBar>
      <Toolbar/>
      <Container>
        <Box my={4}>
        
          <Button variant="contained" color="primary" onClick={onClickScan}>Scan</Button>
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
          {
            bleContext.currentCharacteristic
            ? <Button variant="contained" color="primary" onClick={onClickReadWrite}>Read/Write</Button>
            : null
          }
        </Box>
      </Container>
    </>
  )
}

const AuthToolbar = () => {

  const authContext = useContext(AuthContext);

  const onLogoutClick = () => {
    authContext.logout();
  }

  const onLoginClick = () => {
    authContext.login();
  }

  return (
    authContext.initialized
    ? authContext.authUser
      ? <Button onClick={onLogoutClick}>{authContext.authUser.username} (Logout)</Button>
      : <Button onClick={onLoginClick}>Login</Button>
    : <span>...</span>
  )
}

export default App;
