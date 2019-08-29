import React from 'react'
import { ApolloProvider } from "react-apollo"
import ApolloClient from "apollo-boost"

// Import moment locale
// import moment from 'moment'
// import 'moment/locale/nl'

import CSLS from "./tools/cs_local_storage"

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

const token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImVkd2luQG9wZW5zdHVkaW9wcm9qZWN0LmNvbSIsImV4cCI6MTU2NzA3NzE4Miwib3JpZ0lhdCI6MTU2NzA3Njg4Mn0.2x8QJ4SXuHRjTW0sVl5BOq9CJvyE57fDDcQF6rLBni8"

// set up ApolloClient
const client = new ApolloClient({
    uri: "http://localhost:8000/graphql/",
    headers: {
      Authorization: `JWT ${token}`
    }
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

