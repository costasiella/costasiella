import gql from "graphql-tag"

export const GET_PAYMENT_BATCH_CATEGORIES_QUERY = gql`
  query FinancePaymentBatchCategories($after: String, $before: String, $archived: Boolean) {
    financePaymentBatchCategories(first: 15, before: $before, after: $after, archived: $archived) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          archived
          description
          batchCategoryType
          name
        }
      }
    }
  }
`

export const GET_PAYMENT_BATCH_CATEGORY_QUERY = gql`
  query FinancePaymentBatchCategory($id: ID!) {
    financePaymentBatchCategory(id:$id) {
      id
      name
      description
      archived
    }
  }
`


export const ARCHIVE_PAYMENT_BATCH_CATEGORY = gql`
  mutation ArchiveFinancePaymentBatchCategory($input: ArchiveFinancePaymentBatchCategoryInput!) {
    archiveFinancePaymentBatchCategory(input: $input) {
      financePaymentBatchCategory {
        id
        archived
      }
    }
  }
`
