import gql from "graphql-tag"

export const GET_CLASSPASS_GROUPS_QUERY = gql`
  query SchoolClasspassGroups($after: String, $before: String, $archived: Boolean) {
    schoolClasspassGroups(first: 15, before: $before, after: $after, archived: $archived) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          archived
          name
        }
      }
    }
  }
`

export const GET_CLASSPASS_GROUP_QUERY = gql`
  query SchoolClasspassGroup($id: ID!) {
    schoolClasspassGroup(id:$id) {
      id
      name
      archived
    }
  }
`