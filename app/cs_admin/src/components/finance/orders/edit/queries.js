import gql from "graphql-tag"

export const GET_FINANCE_ORDER_QUERY = gql`
  query FinanceOrder($id: ID!) {
    financeOrder(id: $id) {
      id
      account {
        id
        fullName
      }
      status
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


export const UPDATE_FINANCE_ORDER = gql`
  mutation UpdateAccountClasspass($input: UpdateAccountClasspassInput!) {
    updateAccountClasspass(input: $input) {
      accountClasspass {
        id
        account {
          id
          firstName
          lastName
          email
        }
        organizationClasspass {
          id
          name
        }
        dateStart
        dateEnd
        note
      }
    }
  }
`