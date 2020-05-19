import gql from "graphql-tag"


export const QUERY_ACCOUNT_ORDERS = gql`
  query FinanceOrders($after: String, $before: String, $account: ID!) {
    financeOrders(first: 15, before: $before, after: $after, account: $account) {
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
    user {
      id
      accountId
      firstName
      lastName
      fullName
      email
      gender
      dateOfBirth
      address
      postcode
      city
      country
      phone
      mobile
      emergency
    }
  }
`


export const UPDATE_ORDER = gql`
  mutation UpdateOrder($input: UpdateFinanceOrderInput!) {
    updateFinanceOrder(input: $input) {
      financeOrder {
        id
        status
      }
    }
  }
`
