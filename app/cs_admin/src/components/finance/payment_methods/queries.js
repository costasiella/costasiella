import gql from "graphql-tag"

export const GET_PAYMENT_METHODS_QUERY = gql`
  query FinancePaymentMethods($after: String, $before: String, $archived: Boolean) {
    financePaymentMethods(first: 15, before: $before, after: $after, archived: $archived) {
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
          systemMethod
          name
          code
        }
      }
    }
  }
`

export const GET_PAYMENT_METHOD_QUERY = gql`
  query FinancePaymentMethod($id: ID!) {
    financePaymentMethod(id:$id) {
      id
      name
      code
      archived
    }
  }
`