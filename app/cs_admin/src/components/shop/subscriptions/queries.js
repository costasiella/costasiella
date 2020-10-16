import gql from "graphql-tag"

export const GET_ORGANIZATION_SUBSCRIPTIONS_QUERY = gql`
  query OrganizationSubscriptions($after: String, $before: String) {
    organizationSubscriptions(first: 15, before: $before, after: $after, archived: false) {
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
          priceTodayDisplay
          displayPublic
          displayShop
          name
          description
          sortOrder
          minDuration
          classes
          subscriptionUnit
          subscriptionUnitDisplay
          reconciliationClasses
          creditValidity
          unlimited
          termsAndConditions
          registrationFee
          organizationMembership {
            id
            name
          }
          quickStatsAmount
          financeGlaccount {
            id 
            name
          }
          financeCostcenter {
            id
            name
          }
        }
      }
    }
  }
`