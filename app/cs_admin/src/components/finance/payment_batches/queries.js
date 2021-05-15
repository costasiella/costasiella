import gql from "graphql-tag"

export const GET_PAYMENT_BATCHES_QUERY = gql`
  query FinancePaymentBatches($after: String, $before: String, $batchType: String!) {
    financePaymentBatches(first: 15, before: $before, after: $after, batchType: $batchType) {
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


export const DELETE_PAYMENT_BATCH_CATEGORY = gql`
  mutation DeleteFinancePaymentBatch($input: DeleteFinancePaymentBatchInput!) {
    deleteFinancePaymentBatch(input: $input) {
      financePaymentBatch {
        id
      }
    }
  }
`
