// import React, { Component } from 'react';
// import logo from './logo.svg';
// import './App.css';


import React, { Component } from 'react'
import {Route, Switch, HashRouter} from 'react-router-dom'
import { ApolloProvider } from "react-apollo";
import ApolloClient from "apollo-boost";
import gql from "graphql-tag";

import HomeHome from './components/home/home/HomeHome'

import FinanceHome from './components/finance/home/FinanceHome'
import FinanceCostCenters from './components/finance/costcenters/FinanceCostCenters'
import FinanceCostCenterAdd from './components/finance/costcenters/FinanceCostCenterAdd'
import FinanceCostCenterEdit from './components/finance/costcenters/FinanceCostCenterEdit'
import FinanceGLAccounts from './components/finance/glaccounts/FinanceGLAccounts'
import FinanceGLAccountAdd from './components/finance/glaccounts/FinanceGLAccountAdd'
import FinanceGLAccountEdit from './components/finance/glaccounts/FinanceGLAccountEdit'
import FinanceTaxRates from './components/finance/taxrates/FinanceTaxRates'
import FinanceTaxRatesAdd from './components/finance/taxrates/FinanceTaxRateAdd'
import FinanceTaxRatesEdit from './components/finance/taxrates/FinanceTaxRateEdit'

import SchoolHome from './components/school/home/SchoolHome'
import SchoolClasspasses from './components/school/classpasses/SchoolClasspasses'
import SchoolClasspassAdd from './components/school/classpasses/SchoolClasspassAdd'
import SchoolClasspassEdit from './components/school/classpasses/SchoolClasspassEdit'
import SchoolClasstypes from './components/school/classtypes/SchoolClasstypes'
import SchoolClasstypeAdd from './components/school/classtypes/SchoolClasstypeAdd'
import SchoolClasstypeEdit from './components/school/classtypes/SchoolClasstypeEdit'
import SchoolClasstypeEditImage from './components/school/classtypes/SchoolClasstypeEditImage'
import SchoolDiscoveries from './components/school/discovery/SchoolDiscoveries'
import SchoolDiscoveryAdd from './components/school/discovery/SchoolDiscoveryAdd'
import SchoolDiscoveryEdit from './components/school/discovery/SchoolDiscoveryEdit'
import SchoolLocations from './components/school/locations/SchoolLocations'
import SchoolLocationAdd from './components/school/locations/SchoolLocationAdd'
import SchoolLocationEdit from './components/school/locations/SchoolLocationEdit'
import SchoolMemberships from './components/school/memberships/SchoolMemberships'
import SchoolMembershipAdd from './components/school/memberships/SchoolMembershipAdd'
import SchoolMembershipEdit from './components/school/memberships/SchoolMembershipEdit'

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
            <Route exact path="/" component={HomeHome} />
            <Route exact path="/finance" component={FinanceHome} />
            <Route exact path="/finance/costcenters" component={FinanceCostCenters} />
            <Route exact path="/finance/costcenters/add" component={FinanceCostCenterAdd} />
            <Route exact path="/finance/costcenters/edit/:id" component={FinanceCostCenterEdit} />
            <Route exact path="/finance/glaccounts" component={FinanceGLAccounts} />
            <Route exact path="/finance/glaccounts/add" component={FinanceGLAccountAdd} />
            <Route exact path="/finance/glaccounts/edit/:id" component={FinanceGLAccountEdit} />
            <Route exact path="/finance/taxrates" component={FinanceTaxRates} />
            <Route exact path="/finance/taxrates/add" component={FinanceTaxRatesAdd} />
            <Route exact path="/finance/taxrates/edit/:id" component={FinanceTaxRatesEdit} />
            <Route exact path="/school" component={SchoolHome} />
            <Route exact path="/school/classpasses" component={SchoolClasspasses} />
            <Route exact path="/school/classpasses/add" component={SchoolClasspassAdd} />
            <Route exact path="/school/classpasses/edit/:id" component={SchoolClasspassAdd} />
            <Route exact path="/school/classtypes" component={SchoolClasstypes} />
            <Route exact path="/school/classtypes/add" component={SchoolClasstypeAdd} />
            <Route exact path="/school/classtypes/edit/:id" component={SchoolClasstypeEdit} />
            <Route exact path="/school/classtypes/edit_image/:id" component={SchoolClasstypeEditImage} />
            <Route exact path="/school/discoveries" component={SchoolDiscoveries} />
            <Route exact path="/school/discoveries/add" component={SchoolDiscoveryAdd} /> 
            <Route exact path="/school/discoveries/edit/:id" component={SchoolDiscoveryEdit} /> 
            <Route exact path="/school/locations" component={SchoolLocations} />
            <Route exact path="/school/locations/add" component={SchoolLocationAdd} />
            <Route exact path="/school/locations/edit/:id" component={SchoolLocationEdit} />
            <Route exact path="/school/memberships" component={SchoolMemberships} />
            <Route exact path="/school/memberships/add" component={SchoolMembershipAdd} />
            <Route exact path="/school/memberships/edit/:id" component={SchoolMembershipEdit} />

            <Route component={Error404} />
          </Switch>
        </ApolloProvider>
      </HashRouter>
    )};
}

export default App

