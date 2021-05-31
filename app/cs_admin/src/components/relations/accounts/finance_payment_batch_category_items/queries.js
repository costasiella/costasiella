import gql from "graphql-tag"

export const GET_ACCOUNT_FINANCE_PAYMENT_BATCH_CATEGORY_ITEMS_QUERY = gql`
  query AccountFinancePaymentBatchCategoryItems($after: String, $before: String, $account: ID!) {
    accountFinancePaymentBatchCategoryItems(first: 15, before: $before, after: $after, account: $account) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          financePaymentBatchCategory {
            id
            name
          }
          year
          month
          amountDisplay
          description
        }
      }
    }
  }
`

export const GET_ACCOUNT_FINANCE_PAYMENT_BATCH_CATEGORY_ITEM_QUERY = gql`
  query AccountFinancePaymentBatchCategoryItem($id: ID!) {
    accountFinancePaymentBatchCategoryItem(id: $id) {
      id
      financePaymentBatchCategory {
        id
        name
      }
      year
      month
      amount
      description
    }
    financePaymentBatchCategories(first: 100, archived: false) {
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
          batchCategoryType
        }
      }
    }
  }
`

export const GET_INPUT_VALUES_QUERY = gql`
  query AccountPaymentBatchCategoryItemInputValues($after: String, $before: String) {
    financePaymentBatchCategories(first: 100, before: $before, after: $after, archived: false) {
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
          batchCategoryType
        }
      }
    }
  }
`

export const CREATE_ACCOUNT_FINANCE_PAYMENT_BATCH_CATEGORY_ITEM = gql`
  mutation CreateAccountFinancePaymentBatchCategoryItem($input: CreateAccountFinancePaymentBatchCategoryItemInput!) {
    createAccountFinancePaymentBatchCategoryItem(input: $input) {
      accountFinancePaymentBatchCategoryItem {
        id
      }
    }
  }
`

export const UPDATE_ACCOUNT_FINANCE_PAYMENT_BATCH_CATEGORY_ITEM = gql`
  mutation UpdateAccountFinancePaymentBatchCategoryItem($input: UpdateAccountFinancePaymentBatchCategoryItemInput!) {
    updateAccountFinancePaymentBatchCategoryItem(input: $input) {
      accountFinancePaymentBatchCategoryItem {
        id
      }
    }
  }
`

export const DELETE_ACCOUNT_FINANCE_PAYMENT_BATCH_CATEGORY_ITEM = gql`
  mutation DeleteAccountFinancePaymentBatchCategoryItem($input: DeleteAccountFinancePaymentBatchCategoryItemInput!) {
    deleteAccountFinancePaymentBatchCategoryItem(input: $input) {
      ok
    }
  }
`
