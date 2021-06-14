import gql from "graphql-tag"

export const GET_CLASSPASS_GROUPS_QUERY = gql`
  query OrganizationClasspassGroups($after: String, $before: String) {
    organizationClasspassGroups(first: 15, before: $before, after: $after) {
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
          description
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
      description
    }
  }
`


export const GET_CLASSPASS_GROUP_PASSES_QUERY = gql`
  query GetPassesAndGroupMembership($after: String, $before: String, id:ID!) {
    organizationClasspasses(first: 15, before: $before, after: $after) {
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
            discription
          }
        }
      }
    }
  }
`