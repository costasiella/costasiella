import gql from "graphql-tag"

export const GET_LOCATIONS_QUERY = gql`
  query SchoolLocations($archived: Boolean) {
    schoolLocations(first: 1, archived: $archived) {
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
// export const GET_LOCATIONS_QUERY = gql`
//   query SchoolLocations($archived: Boolean!) {
//     schoolLocations(archived:$archived) {
//       id
//       name
//       displayPublic
//       archived
//     }
//   }
// `

export const GET_LOCATION_QUERY = gql`
  query SchoolLocation($id: ID!) {
    schoolLocation(id:$id) {
      id
      name
      displayPublic
      archived
    }
  }
`