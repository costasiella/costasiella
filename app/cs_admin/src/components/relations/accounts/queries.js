import gql from "graphql-tag"

export const GET_ACCOUNTS_QUERY = gql`
  query Accounts($isActive: Boolean!) {
    accounts(isActive: $isActive) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          firstName
          lastName
          email
          isActive
        }
      }
    }
  }
`

export const GET_ACCOUNT_QUERY = gql`
  query SchoolDiscovery($id: ID!) {
    organizationDiscovery(id:$id) {
      id
      name
      archived
    }
  }
`