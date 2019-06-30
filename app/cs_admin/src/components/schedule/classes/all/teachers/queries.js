import gql from "graphql-tag"

export const GET_LOCATION_ROOMS_QUERY = gql`
  query OrganizationLocationRooms($after: String, $before: String, $organizationLocation: ID!, $archived: Boolean!) {
    organizationLocationRooms(first: 15, before: $before, after: $after, organizationLocation: $organizationLocation, archived: $archived) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          organizationLocation {
            id
            name
          }
          archived,
          displayPublic
          name
        }
      }
    }
    organizationLocation(id: $organizationLocation) {
      id
      name
    }
  }
`

export const GET_LOCATION_ROOM_QUERY = gql`
  query OrganizationLocationRoom($id: ID!) {
    organizationLocationRoom(id:$id) {
      id
      organizationLocation {
        id
        name
      }
      name
      displayPublic
      archived
    }
  }
`