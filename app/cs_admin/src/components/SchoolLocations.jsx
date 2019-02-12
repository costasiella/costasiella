import React from 'react'
import { Query } from "react-apollo";
import gql from "graphql-tag";

import SiteWrapper from "./SiteWrapper"

const GET_LOCATIONS = gql`
  {
    schoolLocations {
        id
        name
    }
  }
`


const SchoolLocations = () => (
  <SiteWrapper>
    <Query
      query={GET_LOCATIONS}
    >
      {({ loading, error, data }) => {
        if (loading) return <p>Loading...</p>;
        if (error) return <p>Error loading school locations :(</p>;

        return data.schoolLocations.map(({ id, name }) => (
          <div key={id}>
            <p>{id}: {name}</p>
          </div>
        ));
      }}
    </Query>
  </SiteWrapper>
);

export default SchoolLocations