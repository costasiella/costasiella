import gql from "graphql-tag"

export const GET_ACCOUNT_SUBSCRIPTION_CREDITS_QUERY = gql`
query AccountSubscriptionCredits($before: String, $after: String, $accountSubscription: ID!) {
  accountSubscriptionCredits(first: 20, before: $before, after: $after, accountSubscription: $accountSubscription) {
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    edges {
      node {
        id
        accountSubscription {
          id
        }
        mutationType
        mutationAmount
        description
        createdAt
      }
    } 
  }
}
`

export const GET_ACCOUNT_SUBSCRIPTION_CREDIT_QUERY = gql`
query AccountSubscriptionCredit($id: ID!) {
  accountSubscriptionCredit(id:$id) {
    id
    accountSubscription {
      id
    }
    mutationType
    mutationAmount
    description
    createdAt
  }
}
`


export const DELETE_ACCOUNT_SUBSCRIPTION_CREDIT = gql`
  mutation DeleteAccountSubscriptionCredit($input: DeleteAccountSubscriptionCreditInput!) {
    deleteAccountSubscriptionCredit(input: $input) {
      ok
    }
  }
`
