import gql from "graphql-tag"

export const GET_ORGANIZATION_CLASSPASSES_QUERY = gql`
  query OrganizationClasspasses($after: String, $before: String) {
    organizationClasspasses(first: 15, before: $before, after: $after, archived: false, displayShop: true) {
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
          displayPublic
          displayShop
          trialPass
          name
          description
          price
          priceDisplay
          financeTaxRate {
            id
            name
          }
          validity
          validityUnit
          validityUnitDisplay
          classes
          unlimited
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
