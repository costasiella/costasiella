import gql from "graphql-tag"

export const GET_ACCOUNT_SUBSCRIPTION_BLOCKS_QUERY = gql`
query AccountSubscriptionBlocks($before: String, $after: String, $accountSubscription: ID!) {
  accountSubscriptionBlocks(first: 20, before: $before, after: $after, accountSubscription: $accountSubscription) {
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

export const GET_ACCOUNT_SUBSCRIPTION_BLOCK_QUERY = gql`
query AccountSubscriptionBlock($id: ID!) {
  accountSubscriptionBlock(id:$id) {
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


export const DELETE_ACCOUNT_SUBSCRIPTION_BLOCK = gql`
  mutation DeleteAccountSubscriptionBlock($input: DeleteAccountSubscriptionBlockInput!) {
    deleteAccountSubscriptionBlock(input: $input) {
      ok
    }
  }
`
