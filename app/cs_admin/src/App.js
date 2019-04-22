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

import OrganizationHome from './components/organization/home/OrganizationHome'
import OrganizationClasspasses from './components/organization/classpasses/OrganizationClasspasses'
import OrganizationClasspassAdd from './components/organization/classpasses/OrganizationClasspassAdd'
import OrganizationClasspassEdit from './components/organization/classpasses/OrganizationClasspassEdit'
import OrganizationClasspassesGroups from './components/organization/classpassesgroups/OrganizationClasspassesGroups'
import OrganizationClasspassesGroupAdd from './components/organization/classpassesgroups/OrganizationClasspassesGroupAdd'
import OrganizationClasspassesGroupEdit from './components/organization/classpassesgroups/OrganizationClasspassesGroupEdit'
import OrganizationClasspassesGroupEditPasses from './components/organization/classpassesgroups/OrganizationClasspassesGroupEditPasses'
import OrganizationClasstypes from './components/organization/classtypes/OrganizationClasstypes'
import OrganizationClasstypeAdd from './components/organization/classtypes/OrganizationClasstypeAdd'
import OrganizationClasstypeEdit from './components/organization/classtypes/OrganizationClasstypeEdit'
import OrganizationClasstypeEditImage from './components/organization/classtypes/OrganizationClasstypeEditImage'
import OrganizationDiscoveries from './components/organization/discovery/OrganizationDiscoveries'
import OrganizationDiscoveryAdd from './components/organization/discovery/OrganizationDiscoveryAdd'
import OrganizationDiscoveryEdit from './components/organization/discovery/OrganizationDiscoveryEdit'
import OrganizationLocations from './components/organization/locations/OrganizationLocations'
import OrganizationLocationAdd from './components/organization/locations/OrganizationLocationAdd'
import OrganizationLocationEdit from './components/organization/locations/OrganizationLocationEdit'
import OrganizationLocationRooms from './components/organization/locations/rooms/OrganizationLocationRooms'
import OrganizationLocationRoomAdd from './components/organization/locations/rooms/OrganizationLocationRoomAdd'
import OrganizationLocationRoomEdit from './components/organization/locations/rooms/OrganizationLocationRoomEdit'
import OrganizationLevels from './components/organization/levels/OrganizationLevels'
import OrganizationLevelAdd from './components/organization/levels/OrganizationLevelAdd'
import OrganizationLevelEdit from './components/organization/levels/OrganizationLevelEdit'
import OrganizationMemberships from './components/organization/memberships/OrganizationMemberships'
import OrganizationMembershipAdd from './components/organization/memberships/OrganizationMembershipAdd'
import OrganizationMembershipEdit from './components/organization/memberships/OrganizationMembershipEdit'
import OrganizationSubscriptions from './components/organization/subscriptions/OrganizationSubscriptions'
import OrganizationSubscriptionAdd from './components/organization/subscriptions/OrganizationSubscriptionAdd'


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
            <Route exact path="/organization" component={OrganizationHome} />
            <Route exact path="/organization/classpasses" component={OrganizationClasspasses} />
            <Route exact path="/organization/classpasses/add" component={OrganizationClasspassAdd} />
            <Route exact path="/organization/classpasses/edit/:id" component={OrganizationClasspassEdit} />    
            <Route exact path="/organization/classpasses/groups" component={OrganizationClasspassesGroups} />
            <Route exact path="/organization/classpasses/groups/add" component={OrganizationClasspassesGroupAdd} />
            <Route exact path="/organization/classpasses/groups/edit/:id" component={OrganizationClasspassesGroupEdit} />
            <Route exact path="/organization/classpasses/groups/edit/passes/:id" component={OrganizationClasspassesGroupEditPasses} />
            <Route exact path="/organization/classtypes" component={OrganizationClasstypes} />
            <Route exact path="/organization/classtypes/add" component={OrganizationClasstypeAdd} />
            <Route exact path="/organization/classtypes/edit/:id" component={OrganizationClasstypeEdit} />
            <Route exact path="/organization/classtypes/edit_image/:id" component={OrganizationClasstypeEditImage} />
            <Route exact path="/organization/discoveries" component={OrganizationDiscoveries} />
            <Route exact path="/organization/discoveries/add" component={OrganizationDiscoveryAdd} /> 
            <Route exact path="/organization/discoveries/edit/:id" component={OrganizationDiscoveryEdit} /> 
            <Route exact path="/organization/levels" component={OrganizationLevels} />
            <Route exact path="/organization/levels/add" component={OrganizationLevelAdd} />
            <Route exact path="/organization/levels/edit/:id" component={OrganizationLevelEdit} />
            <Route exact path="/organization/locations" component={OrganizationLocations} />
            <Route exact path="/organization/locations/add" component={OrganizationLocationAdd} />
            <Route exact path="/organization/locations/edit/:id" component={OrganizationLocationEdit} />
            <Route exact path="/organization/locations/rooms/:location_id" component={OrganizationLocationRooms} />
            <Route exact path="/organization/locations/rooms/add/:location_id" component={OrganizationLocationRoomAdd} />
            <Route exact path="/organization/locations/rooms/edit/:location_id/:id" component={OrganizationLocationRoomEdit} />
            <Route exact path="/organization/memberships" component={OrganizationMemberships} />
            <Route exact path="/organization/memberships/add" component={OrganizationMembershipAdd} />
            <Route exact path="/organization/memberships/edit/:id" component={OrganizationMembershipEdit} /> 
            <Route exact path="/organization/subscriptions" component={OrganizationSubscriptions} />
            <Route exact path="/organization/subscriptions/add" component={OrganizationSubscriptionAdd} />

            <Route component={Error404} />
          </Switch>
        </ApolloProvider>
      </HashRouter>
    )};
}

export default App

