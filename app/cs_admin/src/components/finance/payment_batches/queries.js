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


export const GET_INPUT_VALUES = gql`
  query InputValues($after: String, $before: String) {
    financePaymentBatchCategories(first: 1000, before:$before, after:$after, archived:false) {
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
  }
`


export const ADD_PAYMENT_BATCH = gql`
  mutation CreateFinancePaymentBatch($input:CreateFinancePaymentBatchInput!) {
    createFinancePaymentBatch(input: $input) {
      financePaymentBatch {
        id
      }
    }
  }
`


export const DELETE_PAYMENT_BATCH = gql`
  mutation DeleteFinancePaymentBatch($input: DeleteFinancePaymentBatchInput!) {
    deleteFinancePaymentBatch(input: $input) {
      ok
    }
  }
`
