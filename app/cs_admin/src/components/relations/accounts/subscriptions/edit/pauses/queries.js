import gql from "graphql-tag"

export const GET_ACCOUNT_SUBSCRIPTION_PAUSES_QUERY = gql`
query AccountSubscriptionPauses($before: String, $after: String, $accountSubscription: ID!) {
  accountSubscriptionPauses(first: 20, before: $before, after: $after, accountSubscription: $accountSubscription) {
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
        dateStart
        dateEnd
        description
        createdAt
      }
    } 
  }
}
`

export const GET_ACCOUNT_SUBSCRIPTION_PAUSE_QUERY = gql`
query AccountSubscriptionPause($id: ID!) {
  accountSubscriptionPause(id:$id) {
    id
    accountSubscription {
      id
    }
    dateStart
    dateEnd
    description
  }
}
`


export const DELETE_ACCOUNT_SUBSCRIPTION_PAUSE = gql`
  mutation DeleteAccountSubscriptionPause($input: DeleteAccountSubscriptionPauseInput!) {
    deleteAccountSubscriptionPause(input: $input) {
      ok
    }
  }
`
