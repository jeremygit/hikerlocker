import React, { createContext, useEffect, useState } from 'react';

export const AuthContext = createContext();

export const AuthContextProvider = ({ children }) => {

  const [state, setState] = useState({
    initialized: false,
  });

  const [authUser, setAuthUser] = useState(null);

  const logout = () => {
    setAuthUser(null);
  }

  const login = () => {
    setAuthUser({
      username: 'Test User',
      uuid: 'b8dfbbd4bed',
    });
  }

  useEffect(() => {

    login();

    setState({initialized: true});

    return () => {}
  }, []);

  return (
    <AuthContext.Provider value={
        {...state, 
          authUser: authUser,
          logout: logout,
          login: login,
        }
      }>
      {children}
    </AuthContext.Provider> 
  );
};