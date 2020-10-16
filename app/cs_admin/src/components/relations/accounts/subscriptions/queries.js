import gql from "graphql-tag"

export const GET_ACCOUNT_SUBSCRIPTIONS_QUERY = gql`
  query AccountSubscriptions($after: String, $before: String, $accountId: ID!) {
    accountSubscriptions(first: 15, before: $before, after: $after, account: $accountId) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          organizationSubscription {
            id
            name
          }
          financePaymentMethod {
            id
            name
          }
          dateStart
          dateEnd
          creditTotal
          registrationFeePaid
          createdAt
        }
      }
    }
    account(id:$accountId) {
      id
      firstName
      lastName
      email
      phone
      mobile
      isActive
    }
  }
`

export const GET_ACCOUNT_SUBSCRIPTION_QUERY = gql`
  query AccountSubscription($id: ID!, $accountId: ID!, $after: String, $before: String) {
    accountSubscription(id:$id) {
      id
      organizationSubscription {
        id
        name
      }
      financePaymentMethod {
        id
        name
      }
      dateStart
      dateEnd
      note
      creditTotal
      registrationFeePaid
      createdAt
    }
    organizationSubscriptions(first: 100, before: $before, after: $after, archived: false) {
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
          name
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
          archived
          name
          code
        }
      }
    }
    account(id:$accountId) {
      id
      firstName
      lastName
      email
      phone
      mobile
      isActive
    }
  }
`

export const GET_INPUT_VALUES_QUERY = gql`
  query SubscriptionInputValues($after: String, $before: String, $archived: Boolean!, $accountId: ID!) {
    organizationSubscriptions(first: 100, before: $before, after: $after, archived: $archived) {
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
          name
        }
      }
    }
    financePaymentMethods(first: 100, before: $before, after: $after, archived: $archived) {
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
          name
          code
        }
      }
    }
    account(id:$accountId) {
      id
      firstName
      lastName
      email
      phone
      mobile
      isActive
    }
  }
`


export const GET_ACCOUNT_QUERY = gql`
  query Account($accountId: ID!) {
    account(id:$accountId) {
      id
      firstName
      lastName
      email
      phone
      mobile
      isActive
    }
  }
`