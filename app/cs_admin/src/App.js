import Cookies from 'js-cookie'
import React from 'react'
import { ApolloProvider } from "react-apollo"
import ApolloClient from "apollo-boost"
import { Observable } from 'apollo-link'

import { TOKEN_REFRESH } from "./queries/system/auth"
// Import moment locale
// import moment from 'moment'
// import 'moment/locale/nl'

import CSLS from "./tools/cs_local_storage"
import CSEC from "./tools/cs_error_codes"
import { CSAuth } from './tools/authentication'

// import Cookies from 'js-cookie'

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

function processClientError({ networkError, graphQLErrors, operation, forward, response }) {
  // console.log(Object.keys(error))
  console.log(operation)
  console.log(networkError)
  console.log(graphQLErrors)
  console.log(forward)
  console.log(response)
  // request size check
  if (graphQLErrors[0].message == "Request body exceeded settings.DATA_UPLOAD_MAX_MEMORY_SIZE.") {
    console.error('CHOSEN FILE EXCEEDS SIZE LIMIT')
  }

  // Token refresh / re-auth check
  let i
  for (i = 0; i < response.errors.length; i++) {
    if (response.errors[i].extensions && response.errors[i].extensions.code === CSEC.USER_NOT_LOGGED_IN) {

      let authTokenExpired = false
      const tokenExp = localStorage.getItem(CSLS.AUTH_TOKEN_EXP)
      if ((new Date() / 1000) >= tokenExp) {
        authTokenExpired = true
      }

      console.log('token expired')
      console.log(authTokenExpired)

      if (authTokenExpired) {
        const refreshTokenExp = localStorage.getItem(CSLS.AUTH_TOKEN_REFRESH_EXP)
        if ((new Date() / 1000) >= refreshTokenExp || (refreshTokenExp == null)) {
          // Session expired
          console.log("refresh token expired or not found")
          console.log(new Date() / 1000)
          console.log(refreshTokenExp)

          console.log('HERE')
    
          // window.location.href = "#/user/session/expired"
          // window.location.reload()
        } else {
          // Refresh token... no idea how this observable & subscriber stuff works... but it does :).
          // https://stackoverflow.com/questions/50965347/how-to-execute-an-async-fetch-request-and-then-retry-last-failed-request/51321068#51321068
          console.log("auth token expired")
          console.log(new Date() / 1000)
          console.log(refreshTokenExp)

          console.log("refresh token.... somehow....")

          return new Observable(observer => {
            client.mutate({
              mutation: TOKEN_REFRESH
            })
              .then(({ data }) => { 
                console.log(data)
                CSAuth.updateTokenInfo(data.refreshToken)
              })
              .then(() => {
                const subscriber = {
                  next: observer.next.bind(observer),
                  error: observer.error.bind(observer),
                  complete: observer.complete.bind(observer)
                };

                // Retry last failed request
                forward(operation).subscribe(subscriber);
              })
              .catch(error => {
                // No refresh or client token available, we force user to login
                observer.error(error);
                window.location.href = "/#/user/login"
                window.location.reload()
              })
          })
        }
      } else {
        window.location.href = "/#/user/login"
        window.location.reload()
      }

      // window.location.href = "/#/user/login"
      // window.location.reload()
    }
  }
}

// Fetch CSRF Token 
let csrftoken;
async function getCsrfToken() {
    if (csrftoken) return csrftoken;
    csrftoken = await fetch('/d/csrf/')
        .then(response => response.json())
        .then(data => data.csrfToken)
    return await csrftoken
}

// set up ApolloClient
const client = new ApolloClient({
  // uri: "http://localhost:8000/graphql/",
  uri: "/d/graphql/",
  credentials: "same-origin",
  onError: processClientError,
  request: async (operation) => {
    const csrftoken = await getCsrfToken();
    Cookies.set('csrftoken', csrftoken);
    // set the cookie 'csrftoken'
    operation.setContext({
        // set the 'X-CSRFToken' header to the csrftoken
        headers: {
            'X-CSRFToken': csrftoken,
        },
    });
},
  // request: async operation => {
  //   var csrftoken = Cookies.get('csrftoken');
  //   operation.setContext({
  //     headers: {
  //       "X-CSRFToken": csrftoken ? csrftoken : ''
  //     }
  //   })
  // }
  // request: async operation => {
  //   const token = localStorage.getItem(CSLS.AUTH_TOKEN)
  //   operation.setContext({
  //     headers: {
  //       Authorization: token ? `JWT ${token}`: ''
  //     }
  //   })
  // }
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

