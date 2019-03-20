import gql from "graphql-tag"

export const GET_GLACCOUNTS_QUERY = gql`
  query FinanceGLAccounts($after: String, $before: String, $archived: Boolean) {
    financeGlaccounts(first: 15, before: $before, after: $after, archived: $archived) {
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
          name,
          code
        }
      }
    }
  }
`

export const GET_GLACCOUNT_QUERY = gql`
  query FinanceGLAccount($id: ID!) {
    financeGlaccount(id:$id) {
      id
      name
      code
      archived
    }
  }
`