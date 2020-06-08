import gql from "graphql-tag"

export const GET_FINANCE_ORDER_QUERY = gql`
  query FinanceOrder($id: ID!) {
    financeOrder(id: $id) {
      id
      account {
        id
        fullName
      }
      orderNumber
      status
      message
      createdAt
      total
      totalDisplay
      balanceDisplay
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
            organizationClasspass {
              id
              name
            }
            productName 
            description
            quantity
            price
            priceDisplay
            financeTaxRate {
              name
            }
            subtotalDisplay
            taxDisplay
            totalDisplay
            financeGlaccount {
              name
            }
          	financeCostcenter {
              name
            }
          }
        }
      }
    }
  }
`


export const UPDATE_ORDER = gql`
  mutation UpdateFinanceOrder($input: UpdateFinanceOrderInput!) {
    updateFinanceOrder(input: $input) {
      financeOrder {
        id
      }
    }
  }
`