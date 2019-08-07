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
  query FinanceInvoice($id: ID!, $before: String, $after: String) {
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
      updatedAt
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
            subtotalDisplay
            tax
            taxDisplay
            total
            totalDisplay
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
    financePaymentMethods(first: 100, before: $before, after: $after, archived: false) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          name
        }
      }
    }
    financeTaxRates(first: 100, before: $before, after: $after, archived: false) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          name
        }
      }
    }
    organization(id:"T3JnYW5pemF0aW9uTm9kZToxMDA=") {
      id
      name
      address
      phone
      email
      registration
      taxRegistration
    }
  }
`


export const UPDATE_INVOICE = gql`
  mutation UpdateFinanceInvoice($input: UpdateFinanceInvoiceInput!) {
    updateFinanceInvoice(input: $input) {
      financeInvoice {
        id
        summary
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


export const DELETE_INVOICE_ITEM = gql`
  mutation DeleteFinanceInvoiceItem($input: DeleteFinanceInvoiceItemInput!) {
    deleteFinanceInvoiceItem(input: $input) {
      ok
    }
  }
`