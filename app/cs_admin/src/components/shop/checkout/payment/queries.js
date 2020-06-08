import gql from "graphql-tag"


export const CREATE_PAYMENT_LINK = gql`
mutation CreateFinanceOrderPaymentLink($id: ID!) {
  createFinanceOrderPaymentLink(id: $id) {
    financeOrderPaymentLink {
      paymentLink
    }
  }
}
`