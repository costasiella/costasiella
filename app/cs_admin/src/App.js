import React from 'react'
// import { ApolloProvider } from "react-apollo"
// import ApolloClient from "apollo-boost"
import { ApolloProvider, ApolloClient, HttpLink, InMemoryCache } from '@apollo/client';


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


function processClientError(error) {
  console.log(Object.keys(error))
  console.log(error.operation)
  console.log(error.networkError)
  console.log(error.graphQLErrors)
  console.log(error.forward)
  // let i
  // for (i = 0; i < error.response.errors.length; i++) {
  //   if (error.response.errors[i].extensions && error.response.errors[i].extensions.code === CSEC.USER_NOT_LOGGED_IN) {
  //     window.location.href = "/#/user/login"
  //     window.location.reload()
  //     break
  //   }
  // }
}

const httpLink = new HttpLink({
  uri: "/d/graphql/",
  fetch: customFetch
})

const customFetch = (uri, options) => {
  // This reference to the refreshingPromise will let us check later on if we are executing getting the refresh token.
  // this.refreshingPromise = null;

  // // Create initial fetch, this is what would normally be executed in the link without the override
  // var initialRequest = fetch(uri, options)

  // // The apolloHttpLink expects that whatever fetch function is used, it returns a promise.
  // // Here we return the initialRequest promise
  // return initialRequest.then((response) => {
  //   return(response.json())
  // }).then((json) => {
  //   // We should now have the JSON from the response of initialRequest
  //   // We check that we do and look for errors from the GraphQL server
  //   // If it has the error 'User is not logged in' (that's our implementation of a 401) we execute the next steps in the re-auth flow
  //   if (json && json.errors && json.errors[0] && json.errors[0].message === 'User is not logged in.') {
  //     if (!this.refreshingPromise) {

  //       // Grab the refresh token from the store

  return fetch(uri, options)
}

// set up ApolloClient
// TODO: Set up token expiration and auto refresh if possible and redirect to login if refresh token is expired.
const client = new ApolloClient({
  // uri: "http://localhost:8000/graphql/",
  link: httpLink,
  credentials: "same-origin",
  onError: processClientError,
  cache: new InMemoryCache()
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

