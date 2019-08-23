import gql from "graphql-tag"

export const GET_INVOICE_GROUPS_QUERY = gql`
  query FinanceInvoiceGroupsQuery($archived: Boolean!) {
    financeInvoiceGroups(archived: $archived) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
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