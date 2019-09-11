import React from 'react'
import { ApolloProvider } from "react-apollo"
import ApolloClient from "apollo-boost"

// Import moment locale
// import moment from 'moment'
// import 'moment/locale/nl'

import CSLS from "./tools/cs_local_storage"
import CSEC from "./tools/cs_error_codes"
import { CSAuth } from './tools/authentication'

// Main app
import AppRoot from "./AppRoot"

// Tabler css 
import "tabler-react/dist/Tabler.css"
// React-datepicker css
import "react-datepicker/dist/react-datepicker.css"
// App css
import './App.css'

// Register "nl" locale for react-datepicker
// https://reactdatepicker.com/#example-17
// import { registerLocale } from "react-datepicker"
// import nl from 'date-fns/locale/nl';
// registerLocale('nl', nl);

// This allows <string>.trunc(x)
String.prototype.trunc = 
  function(n){
      return this.substr(0, n-1) + (this.length > n ? '...' : '')
  }


function processClientError(error) {
  let i
  for (i = 0; i < error.response.errors.length; i++) {
    if (error.response.errors[i].extensions.code == CSEC.USER_NOT_LOGGED_IN) {
      window.location.href = "/#/user/login"
      break
    }
  }  
}

// set up ApolloClient
// TODO: Set up token expiration and auto refresh if possible and redirect to login if refresh token is expired.
const client = new ApolloClient({
  // uri: "http://localhost:8000/graphql/",
  uri: "/graphql/",
  credentials: "same-origin",
  onError: processClientError,
})


function App() {
  // Register "NL" locale for moment
  // moment.locale('en-US')

  return (
    <ApolloProvider client={client}>
      <AppRoot />
    </ApolloProvider>
  )
}

export default App

