import gql from "graphql-tag"

export const GET_ORGANIZATION_LOCATIONS_QUERY = gql`
  query Organizationlocations($after: String, $before: String) {
    organizationLocations(first: 100, before: $before, after: $after, archived: false) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          name
          organizationlocationroomSet(first: 100, archived: false) {
            edges {
              node {
                id
                name
              }
            }
          }
        }
      }
    }
  }
`
