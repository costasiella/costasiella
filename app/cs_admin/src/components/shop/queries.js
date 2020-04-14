import gql from "graphql-tag"


export const CREATE_ORDER = gql`
  mutation CreateFinanceOrder($input: CreateFinanceOrderInput!) {
    createFinanceOrder(input: $input) {
      financeOrder {
        id
      }
    }
  }
`