import gql from "graphql-tag"

export const GET_SUBSCRIPTION_PRICES_QUERY = gql`
  query OrganizationSubscriptionPrices($after: String, $before: String, $organizationSubscription: ID!, $archived: Boolean!) {
    organizationSubscriptionPrices(first: 15, before: $before, after: $after, organizationSubscription: $organizationSubscription, archived: $archived) {
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
          financeTaxrate {
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
      financeTaxrate {
        id
        name
      }
      dateStart
      dateEnd
    }
  }
`