import gql from "graphql-tag"

export const GET_ORDERS_QUERY = gql`
  query FinanceOrders($after: String, $before: String, $status: String) {
    financeOrders(first: 15, before: $before, after: $after, status: $status) {
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
          note
          status
          total
          totalDisplay
          createdAt
        }
      }
    }
  }
`

export const GET_ORDER_QUERY = gql`
  query FinanceOrder($id: ID!, $before: String, $after: String) {
    financeOrder(id:$id) {
      id
      account {
        id
        fullName
      }
      status
    }
  }
`


export const UPDATE_FINANCE_ORDER = gql`
  mutation UpdateFinanceOrder($input: UpdateFinanceOrderInput!) {
    updateFinanceOrder(input: $input) {
      financeOrder {
        id
      }
    }
  }
`

export const DELETE_FINANCE_ORDER = gql`
  mutation DeleteFinanceOrder($input: DeleteFinanceOrderInput!) {
    deleteFinanceOrder(input: $input) {
      ok
    }
  }
`
