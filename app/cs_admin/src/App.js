// import React, { Component } from 'react';
// import logo from './logo.svg';
// import './App.css';


import React, { Component } from 'react'
import {Route, Switch, HashRouter} from 'react-router-dom'
import { ApolloProvider } from "react-apollo";
import ApolloClient from "apollo-boost";
import gql from "graphql-tag";

import FinanceHome from './components/finance/home/FinanceHome'

import SchoolHome from './components/school/home/SchoolHome'
import SchoolLocations from './components/school/locations/SchoolLocations'
import SchoolLocationAdd from './components/school/locations/SchoolLocationAdd'
import SchoolLocationEdit from './components/school/locations/SchoolLocationEdit'
import SchoolClasstypes from './components/school/classtypes/SchoolClasstypes'
import SchoolClasstypeAdd from './components/school/classtypes/SchoolClasstypeAdd'
import SchoolClasstypeEdit from './components/school/classtypes/SchoolClasstypeEdit'
import SchoolClasstypeEditImage from './components/school/classtypes/SchoolClasstypeEditImage'
import Error404 from "./components/Error404"

// Tabler css 
import "tabler-react/dist/Tabler.css";
// App css
import './App.css'


const client = new ApolloClient({
     uri: "http://localhost:8000/graphql/",
})


const GET_USER = gql`
  query {
    user {
    id
    isActive
    email
    firstName
    lastName
    userPermissions {
      id
    }
    groups {
      id
      name
      permissions {
        id
        name
        codename
      }
    }
  }
}
`


class App extends Component {
  
  componentWillMount() {
    client.query({
      query:GET_USER
    })
  }

  render() {
    return (
      <HashRouter>
        <ApolloProvider client={client}>
          <Switch>
            <Route exact path="/" component={SchoolLocations} />
            <Route exact path="/finance" component={FinanceHome} />
            <Route exact path="/school" component={SchoolHome} />
            <Route exact path="/school/locations" component={SchoolLocations} />
            <Route exact path="/school/locations/add" component={SchoolLocationAdd} />
            <Route exact path="/school/locations/edit/:id" component={SchoolLocationEdit} />
            <Route exact path="/school/classtypes" component={SchoolClasstypes} />
            <Route exact path="/school/classtypes/add" component={SchoolClasstypeAdd} />
            <Route exact path="/school/classtypes/edit/:id" component={SchoolClasstypeEdit} />
            <Route exact path="/school/classtypes/edit_image/:id" component={SchoolClasstypeEditImage} />
            <Route component={Error404} />
          </Switch>
        </ApolloProvider>
      </HashRouter>
    )};
}

export default App

