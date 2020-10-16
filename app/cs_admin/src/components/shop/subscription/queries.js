import gql from "graphql-tag"


export const GET_SUBSCRIPTION_QUERY = gql`
  query OrganizationSubscription($id: ID!) {
    organizationSubscription(id:$id) {
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
`