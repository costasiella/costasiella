import gql from "graphql-tag"

export const GET_CLASSPASS_GROUPS_QUERY = gql`
  query OrganizationClasspassGroups($after: String, $before: String, $archived: Boolean) {
    organizationClasspassGroups(first: 15, before: $before, after: $after, archived: $archived) {
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
  query OrganizationClasspassGroup($id: ID!) {
    organizationClasspassGroup(id:$id) {
      id
      name
      archived
    }
  }
`


export const GET_CLASSPASS_GROUP_PASSES_QUERY = gql`
  query GetPassesAndGroupMembership($after: String, $before: String, $archived: Boolean, $id:ID!) {
    organizationClasspasses(first: 15, before: $before, after: $after, archived: $archived) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          name
        }
      }
    }
    organizationClasspassGroup(id: $id) {
      id
      name
      organizationClasspasses {
        edges {
          node {
            id
            name
          }
        }
      }
    }
  }
`