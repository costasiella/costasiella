import gql from "graphql-tag"

export const GET_SUBSCRIPTION_PRICES_QUERY = gql`
  query OrganizationSubscriptionPrices($after: String, $before: String, $organizationLocation: ID!, $archived: Boolean!) {
    organizationSubscriptionPrices(first: 15, before: $before, after: $after, organizationLocation: $organizationLocation, archived: $archived) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          organizationLocation {
            id
            name
          }
          archived,
          displayPublic
          name
        }
      }
    }
    organizationLocation(id: $organizationLocation) {
      id
      name
    }
  }
`

export const GET_SUBSCRIPTION_PRICE_QUERY = gql`
  query OrganizationSubscriptionPrice($id: ID!) {
    organizationSubscriptionPrice(id:$id) {
      id
      organizationLocation {
        id
        name
      }
      name
      displayPublic
      archived
    }
  }
`