import gql from "graphql-tag"

export const GET_ACCOUNT_ORDERS_QUERY = gql`
  query FinanceOrders($after: String, $before: String, $status: String, $account: ID!) {
    financeOrders(first: 15, before: $before, after: $after, status: $status, account: $account) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          orderNumber
          account {
            id
            fullName
          }
          status
          createdAt
          total
          totalDisplay
          balanceDisplay
        }
      }
    }
    account(id:$account) {
      id
      firstName
      lastName
      email
      phone
      mobile
      isActive
    }
  }
`
