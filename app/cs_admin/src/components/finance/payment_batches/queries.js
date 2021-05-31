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
          note
        }
      }
    }
  }
`

export const GET_PAYMENT_BATCH_QUERY = gql`
  query FinancePaymentBatch($id: ID!) {
    financePaymentBatch(id:$id) {
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
      note
      totalDisplay
      countItems
      items {
        pageInfo {
          startCursor
          endCursor
          hasNextPage
          hasPreviousPage
        }
        edges {
          node {
            id
            account {
              id
              fullName
            }
            financeInvoice {
              id
              invoiceNumber
            }
            accountHolder
            accountNumber
            accountBic
            mandateReference
            mandateSignatureDate
            amount
            amountDisplay
            currency
            description
          }
        }
      }
      exports {
        pageInfo {
          startCursor
          endCursor
          hasNextPage
          hasPreviousPage
        }
        edges {
          node {
            id
            account {
              id
              fullName
            }
            createdAt
          }
        }
      }
    }
  }
`


export const GET_INPUT_VALUES = gql`
  query InputValues($after: String, $before: String, $batchCategoryType: String!) {
    financePaymentBatchCategories(first: 1000, before:$before, after:$after, archived:false, batchCategoryType: $batchCategoryType) {
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


export const UPDATE_PAYMENT_BATCH = gql`
  mutation UpdateFinancePaymentBatch($input:UpdateFinancePaymentBatchInput!) {
    updateFinancePaymentBatch(input: $input) {
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
