import React, { useContext, useEffect } from 'react';
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
import Drawer from '@material-ui/core/Drawer';

import DirectionsWalkIcon from '@material-ui/icons/DirectionsWalk';
import SettingsRemoteIcon from '@material-ui/icons/SettingsRemote';
import RecordVoiceOverIcon from '@material-ui/icons/RecordVoiceOver';
import PlaceIcon from '@material-ui/icons/Place';
import HowToRegIcon from '@material-ui/icons/HowToReg';
import CompassCalibrationIcon from '@material-ui/icons/CompassCalibration';
import AssistantPhotoIcon from '@material-ui/icons/AssistantPhoto';

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
      <Drawer 
        anchor={'bottom'}
        open={bleContext.bleDataIn ? true : false} 
        onClose={() => {
          bleContext.clearBleDataIn();
        }}
      >
        {
          bleContext.bleDataIn
          ? <Container>
              <Box>
                <Box>
                  <h3>Log Visit Success.</h3>
                </Box>
                <Box>
                  <h4>User ID: <span style={{fontWeight: 'normal'}}>{bleContext.bleDataIn.userVisits[0]}</span></h4>
                </Box>
                <Box>
                  <h4>Marker ID: <span style={{fontWeight: 'normal'}}>{bleContext.bleDataIn.markerId}</span></h4>
                </Box>
              </Box>
            </Container>
            : (null)
        }
      </Drawer>
    </>
  )
}

const HikerlockerMainScreen = (props) => {

  const bleContext = useContext(BLEContext);

  const onClickScan = (evt) => {
    bleContext.startScan(evt);
  }

  const onClickReadWrite = () => {
    bleContext.executeCommand();
  }

  return (
    <div className="user-interface" style={{}}>
      <Box className="user-interface-upper" style={{
        position: 'relative',
      }}>
        <AppSVGGraphic/>
        <Button 
            onClick={onClickScan}
            style={{
              height: '200px',
              maxWidth: '200px',
              width: '200px',
              position: 'absolute',
              top: '50%',
              left: '0px',
              right: '0px',
              margin: 'auto',
              borderRadius: '100px',
              // backgroundColor: '#ef4335',
              // color: '#fed8c1',
              backgroundColor: '#fed8c1',
              textAlign: 'center',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0px 2px 4px -1px rgba(0,0,0,0.2), 0px 4px 5px 0px rgba(0,0,0,0.14), 0px 1px 10px 0px rgba(0,0,0,0.12)',
            }}
          >
              <span style={{
                display: 'block',
              }}>
                <CompassCalibrationIcon/>
                <span style={{
                  display: 'block',
                }}>
                    Scan Marker
                  </span>
              </span>

          </Button>
      </Box>
      {/*<Container style={{backgroundColor: '#2b102a', color: '#fed8c1'}}>*/}
        <Box className="user-interface-lower" style={{
          backgroundColor: '#2b102a', color: '#fed8c1',
        }}>
        </Box>
      {/*</Container>*/}
    </div>
  )
}


/*
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
*/

const HikerlockerMenuScreen = (props) => {

  const bleContext = useContext(BLEContext);

  const authContext = useContext(AuthContext);

  const MENU_COLORS = [
    '#fc7d48',
    '#ef4335',
    '#c9223e'
  ];

  const MENU_ICONS = {
    [bleContext.BLE_ROUTE_NAMES.LOG_VISIT]: <AssistantPhotoIcon/>,
    [bleContext.BLE_ROUTE_NAMES.CHECK_IN]:  <MobileFriendlyIcon/>,
    [bleContext.BLE_ROUTE_NAMES.CHECK_OUT]: <PhonelinkEraseIcon/>,
  }

  const onClickBack = () => {
    bleContext.disconnect();
  }

  const onSelectChar = (uuid) => (evt) => {
    try {
      const route = bleContext.getCmdRoute(uuid);
      switch (route) {
        case bleContext.BLE_ROUTE_NAMES.LOG_VISIT:
          return bleContext.logVisit(authContext.authUser.uuid);
        default:
          throw 'command not suported';
      }
    } catch (err) {
      console.log(err);
    }
  }

  return (
    <Container>
      <Box>
        <IconButton onClick={onClickBack}><ArrowBackIcon/></IconButton>
      </Box>
      {
      bleContext.connectionState == 2
      ? bleContext.characteristics.map((char, i) => (
        <Card my="auto" style={{backgroundColor: MENU_COLORS[i], color: '#fed8c1', marginBottom: '15px'}} key={char.uuid} onClick={onSelectChar(char.uuid)}>
          <CardContent>
            <div>{MENU_ICONS[bleContext.BLE_CHARACTERISTIC_CMD[char.uuid].route]}</div>
            <div><Typography variant="h5" component="h2">{bleContext.BLE_CHARACTERISTIC_CMD[char.uuid].name }</Typography></div>
          </CardContent>
        </Card>
      ))
      : (null)
      }
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
