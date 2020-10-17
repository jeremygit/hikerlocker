import React, { useContext } from 'react';
import { BLEContext, BLEContextProvider } from '../contexts/BLEContext';
import { AuthContext, AuthContextProvider } from '../contexts/AuthContext';

import { AppBar, Toolbar } from '@material-ui/core';
import Button from '@material-ui/core/Button';
import IconButton from '@material-ui/core/IconButton';
import PermIdentityIcon from '@material-ui/icons/PermIdentity';
import BluetoothDisabledIcon from '@material-ui/icons/BluetoothDisabled';
import BluetoothSearchingIcon from '@material-ui/icons/BluetoothSearching';
import BluetoothIcon from '@material-ui/icons/Bluetooth';
import MenuIcon from '@material-ui/icons/Menu';
import { BluetoothConnected } from '@material-ui/icons';

const AuthAppBar = (props) => {

  const bleContext = useContext(BLEContext);

  const authContext = useContext(AuthContext);

  const style = {
    background: 'none',
    color: '#2b102a',
    flexGrow: 1,
  }

  return (
    <AppBar position="fixed" style={style}>
      <Toolbar style={{display: 'flex'}}>
        <span style={{flexGrow: 1, fontSize: 20, fontWeight: 'bold'}}>Hikerlocker</span>
        <div>
          <ToolBarConnectivity/><AuthToolbar /><IconButton><MenuIcon/></IconButton>
        </div>
      </Toolbar>
    </AppBar>
  )
} 
  
const AuthToolbar = (props) => {

  const authContext = useContext(AuthContext);

  const onLogoutClick = () => {
    authContext.logout();
  }

  const onLoginClick = () => {
    authContext.login();
  }

  // {authContext.authUser.username}

  return (
    authContext.initialized
    ? authContext.authUser
      ? <IconButton onClick={onLogoutClick}><PermIdentityIcon/></IconButton>
      : <Button onClick={onLoginClick}>Login</Button>
    : <span>...</span>
  )
}

const ToolBarConnectivity = (props) => {

  const bleContext = useContext(BLEContext);

  if (bleContext.connectionState == 0) {
    return (<IconButton><BluetoothDisabledIcon style={{color: '#fd3939'}}/></IconButton>)
  } else if (bleContext.connectionState == 1) {
    return (<IconButton><BluetoothSearchingIcon/></IconButton>)
  } else {
    return (<IconButton><BluetoothConnected style={{color: '#00d889'}}/></IconButton>)
  }
}

export default AuthAppBar