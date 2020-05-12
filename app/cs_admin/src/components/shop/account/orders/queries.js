import gql from "graphql-tag"


export const QUERY_ACCOUNT_ORDERS = gql`
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
          message
          status
          total
          totalDisplay
          createdAt
          items(first: 100) {
            pageInfo {
              hasNextPage
              hasPreviousPage
              startCursor
              endCursor
            }
            edges {
              node {
                id
                productName
                description
                quantity
                priceDisplay
                financeTaxRate {
                  id
                  name
                  percentage
                  rateType
                }
                subtotalDisplay
                taxDisplay
                totalDisplay                
              }
            }
          }
        }
      }
    }
  }
`