import gql from "graphql-tag"


export const GET_INVOICE_PAYMENT_QUERY = gql`
  query FinanceInvoicePayment($id: ID!) {
    financeInvoicePayment(id:$id) {
      id
      date
      amount
      financePaymentMethod {
        id
        name
      }
      note
    }
  }
`
