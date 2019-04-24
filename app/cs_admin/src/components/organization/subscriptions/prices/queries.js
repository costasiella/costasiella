import gql from "graphql-tag"

export const GET_SUBSCRIPTION_PRICES_QUERY = gql`
  query OrganizationSubscriptionPrices($after: String, $before: String, $organizationSubscription: ID!) {
    organizationSubscriptionPrices(first: 15, before: $before, after: $after, organizationSubscription: $organizationSubscription) {
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
          price
          priceDisplay
          financeTaxRate {
            id
            name
          }
          dateStart
          dateEnd
        }
      }
    }
    organizationSubscription(id: $organizationSubscription) {
      id
      name
    }
  }
`

export const GET_SUBSCRIPTION_PRICE_QUERY = gql`
  query OrganizationSubscriptionPrice($id: ID!) {
    organizationSubscriptionPrice(id:$id) {
      id
      organizationSubscription {
        id
        name
      }
      price
      priceDisplay
      financeTaxRate {
        id
        name
      }
      dateStart
      dateEnd
    }
  }
`


export const GET_INPUT_VALUES_QUERY = gql`
  query InputValues($after: String, $before: String, $archived: Boolean) {
    financeTaxrates(first: 15, before: $before, after: $after, archived: $archived) {
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
          percentage
          rateType
        }
      }
    }
  }
`