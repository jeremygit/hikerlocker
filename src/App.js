import React, { useContext } from 'react';
import { BLEContext, BLEContextProvider } from './contexts/BLEContext';
import { AuthContext, AuthContextProvider } from './contexts/AuthContext';

import AppSVGGraphic from './components/AppSVGGraphic';
import AuthAppBar from './components/AuthAppBar';

import { AppBar, IconButton, Toolbar } from '@material-ui/core';
import Container from '@material-ui/core/Container';
import Box from '@material-ui/core/Box';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CardActions from '@material-ui/core/CardActions';
import ArrowBackIcon from '@material-ui/icons/ArrowBack';
import Typography from '@material-ui/core/Typography';
import DirectionsWalkIcon from '@material-ui/icons/DirectionsWalk';
import SettingsRemoteIcon from '@material-ui/icons/SettingsRemote';
import RecordVoiceOverIcon from '@material-ui/icons/RecordVoiceOver';
import PlaceIcon from '@material-ui/icons/Place';
import HowToRegIcon from '@material-ui/icons/HowToReg';

import PhonelinkRingIcon from '@material-ui/icons/PhonelinkRing';
import PhonelinkEraseIcon from '@material-ui/icons/PhonelinkErase';
import MobileFriendlyIcon from '@material-ui/icons/MobileFriendly';
import MobileOffIcon from '@material-ui/icons/MobileOff';

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

  return (
    <>
      <Toolbar/>
      <AuthAppBar/>
      {
        bleContext.connectionState == 2
        ? <HikerlockerMenuScreen/>
        : <HikerlockerMainScreen/>
      }
    </>
  )
}

const HikerlockerMainScreen = (props) => {

  const bleContext = useContext(BLEContext);

  const onClickScan = (evt) => {
    bleContext.startScan(evt);
  }

  const onSelectChar = (uuid) => (evt) => {
    bleContext.executeBLECommand(uuid);
  }

  const onClickReadWrite = () => {
    bleContext.executeCommand();
  }

  return (
    <>
      <Box>
        <AppSVGGraphic/>
      </Box>
      <Container style={{backgroundColor: '#2b102a', color: '#fed8c1'}}>
        <Box>
          <Button variant="contained" color="primary" onClick={onClickScan}>Scan</Button>
          {
            bleContext.connectionState == 2
            ? bleContext.characteristics.map((char) => (
              <div key={char.uuid} onClick={onSelectChar(char.uuid)}>
                { bleContext.BLE_CHARACTERISTIC_CMD[char.uuid].name }
              </div>
            ))
            : <div>Begin by scanning...</div>
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

const HikerlockerMenuScreen = (props) => {
  return (
    <Container>
      <Box>
        <IconButton><ArrowBackIcon/></IconButton>
      </Box>
      <Card my="auto" style={{backgroundColor: '#fc7d48', color: '#fed8c1'}}>
        <CardContent>
          <div><PhonelinkRingIcon/></div>
          <div><Typography variant="h5" component="h2">Log Visit</Typography></div>
        </CardContent>
      </Card>
      <Card style={{backgroundColor: '#ef4335', color: '#fed8c1'}}>
        <CardContent>
          <div><MobileFriendlyIcon/></div>
          <div><Typography variant="h5" component="h2">Check-in</Typography></div>
        </CardContent>
      </Card>
      <Card style={{backgroundColor: '#c9223e', color: '#fed8c1'}}>
        <CardContent>
          <div><PhonelinkEraseIcon/></div>
          <div><Typography variant="h5" component="h2">Check-out</Typography></div>
        </CardContent>
      </Card>
    </Container>
  )
}

const BLEMenuOptions = (props) => {

  const bleContext = useContext(BLEContext);

  return (
    bleContext.smartMarkerCommands.map((cmdObj) => (
      <Box key={cmdObj.code}>
        {cmdObj.displayName}
      </Box>
    ))
  )
}

export default App;
