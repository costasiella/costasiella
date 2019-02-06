import React from 'react'
import { Query } from "react-apollo";
import gql from "graphql-tag";

const SchoolLocations = () => (
  <Query
    query={gql`
      {
        schoolLocations {
            id
            name
        }
      }
    `}
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
);

export default SchoolLocations