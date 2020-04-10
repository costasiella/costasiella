import gql from "graphql-tag"


export const GET_ORDER_QUERY = gql`
  query FinanceOrder($id: ID!) {
    financeOrder(id: $id) {
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
      items {
        edges {
          node {
            id
            productName
            description
            quantity
            totalDisplay
          }
        }
      }
      
    }
  }
`