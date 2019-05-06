import gql from "graphql-tag"

export const GET_ACCOUNTS_QUERY = gql`
  query Accounts($trashed: Boolean!) {
    accounts(trashed: $trashed) {
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
          trashed
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