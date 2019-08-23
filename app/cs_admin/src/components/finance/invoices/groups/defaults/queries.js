import gql from "graphql-tag"

export const GET_INVOICE_GROUPS_DEFAULTS_QUERY = gql`
query FinanceInvoiceGroupDefaults {
  financeInvoiceGroupDefaults(first: 100) {
    edges {
      node {
        id
        itemType
        financeInvoiceGroup {
          id
          name
        }
      }
    }
  }
}
`

export const GET_INVOICE_GROUP_QUERY = gql`
  query FinanceInvoiceGroup($id: ID!) {
    financeInvoiceGroup(id:$id) {
      id
      archived
      displayPublic
      name
      nextId
      dueAfterDays
      prefix
      prefixYear
      autoResetPrefixYear
      terms
      footer
      code
    }
  }
`