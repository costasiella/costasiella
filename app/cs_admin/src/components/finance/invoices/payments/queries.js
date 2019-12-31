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


export const CREATE_INVOICE_ITEM = gql`
  mutation CreateFinanceInvoiceItem($input: CreateFinanceInvoiceItemInput!) {
    createFinanceInvoiceItem(input: $input) {
      financeInvoiceItem {
        id
        productName
        description
        quantity
        price
        financeTaxRate {
          id
          name
        }
      }
    }
  }
`


export const UPDATE_INVOICE_ITEM = gql`
  mutation UpdateFinanceInvoiceItem($input: UpdateFinanceInvoiceItemInput!) {
    updateFinanceInvoiceItem(input: $input) {
      financeInvoiceItem {
        id
        productName
        description
        quantity
        price
        financeTaxRate {
          id
          name
        }
      }
    }
  }
`
