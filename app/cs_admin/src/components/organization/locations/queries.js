import gql from "graphql-tag"

export const GET_LOCATIONS_QUERY = gql`
  query OrganizationLocations($after: String, $before: String, $archived: Boolean) {
    organizationLocations(first: 15, before: $before, after: $after, archived: $archived) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id,
          archived,
          displayPublic,
          name
        }
      }
    }
  }
`

export const GET_LOCATION_QUERY = gql`
  query OrganizationLocation($id: ID!) {
    organizationLocation(id:$id) {
      id
      name
      displayPublic
      archived
    }
  }
`