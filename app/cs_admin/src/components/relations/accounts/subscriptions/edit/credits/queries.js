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
