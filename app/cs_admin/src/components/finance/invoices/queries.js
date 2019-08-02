import gql from "graphql-tag"

export const GET_INVOICES_QUERY = gql`
  query FinanceInvoices($after: String, $before: String, $status: String) {
    financeInvoices(first: 15, before: $before, after: $after, status: $status) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          account {
            id
            fullName
          }
          invoiceNumber
          status
          summary
          relationCompany
          relationContactName
          dateSent
          dateDue
          total
          totalDisplay
          balance
          balanceDisplay
        }
      }
    }
  }
`

export const GET_INVOICE_QUERY = gql`
  query FinanceInvoice($id: ID!) {
    financeInvoice(id:$id) {
      id
      account {
        id
        fullName
      }
      financePaymentMethod {
        id
        name
      }
      relationCompany
      relationCompanyRegistration
      relationCompanyTaxRegistration
      relationContactName
      relationAddress
      relationPostcode
      relationCity
      relationCountry
      status
      summary
      invoiceNumber
      dateSent
      dateDue
      terms
      footer
      note
      subtotalDisplay
      taxDisplay
      totalDisplay
      paidDisplay
      balanceDisplay
      items {
        edges {
          node {
            id
            lineNumber
            productName
            description
            quantity
            price
            financeTaxRate {
              id
              name
              percentage
              rateType
            }
            subtotal
            tax
            total
            financeGlaccount {
              id
              name
            }
            financeCostcenter {
              id
              name
            }
          }
        }
      }
    }
  }
`


export const UPDATE_INVOICE = gql`
  mutation UpdateFinanceInvoice($input: UpdateFinanceInvoiceInput!) {
    updateFinanceInvoice(input: $input) {
      financeInvoice {
        id
      }
    }
  }
`