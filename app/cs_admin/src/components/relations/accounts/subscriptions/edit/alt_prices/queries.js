import gql from "graphql-tag"

export const GET_ACCOUNT_SUBSCRIPTION_ALT_PRICES_QUERY = gql`
query AccountSubscriptionAltPrices($before:String, $after:String, $accountSubscription: ID!) {
  accountSubscriptionAltPrices(before: $before, after: $after, accountSubscription:$accountSubscription) {
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
        subscriptionYear
        subscriptionMonth
        amount
        amountDisplay
        description
        note
        createdAt
        updatedAt
      }
    }
  }
}
`

export const GET_ACCOUNT_SUBSCRIPTION_ALT_PRICE_QUERY = gql`
query AccountSubscriptionAltPrice($id: ID!) {
  accountSubscriptionAltPrice(id:$id) {
    id
    accountSubscription {
      id
    }
    subscriptionYear
    subscriptionMonth
    amount
    description
    note
  }
}
`


export const DELETE_ACCOUNT_SUBSCRIPTION_ALT_PRICE = gql`
  mutation DeleteAccountSubscriptionAltPrice($input: DeleteAccountSubscriptionAltPriceInput!) {
    deleteAccountSubscriptionAltPrice(input: $input) {
      ok
    }
  }
`
