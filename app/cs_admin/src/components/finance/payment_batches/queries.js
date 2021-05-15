import gql from "graphql-tag"

export const GET_PAYMENT_BATCHES_QUERY = gql`
  query FinancePaymentBatches($after: String, $before: String, $archived: Boolean) {
    financePaymentBatch(first: 15, before: $before, after: $after, archived: $archived) {
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
          status
          financePaymentBatchCategory {
            id
            name
          }
          description
          batchType
          year
          month
          includeZeroAmounts
          organizationLocation {
            id
            name
          }
          note
        }
      }
    }
  }
`

// export const GET_PAYMENT_BATCH_CATEGORY_QUERY = gql`
//   query FinancePaymentBatchCategory($id: ID!) {
//     financePaymentBatchCategory(id:$id) {
//       id
//       name
//       description
//       archived
//     }
//   }
// `


// export const ARCHIVE_PAYMENT_BATCH_CATEGORY = gql`
//   mutation ArchiveFinancePaymentBatchCategory($input: ArchiveFinancePaymentBatchCategoryInput!) {
//     archiveFinancePaymentBatchCategory(input: $input) {
//       financePaymentBatchCategory {
//         id
//         archived
//       }
//     }
//   }
// `
