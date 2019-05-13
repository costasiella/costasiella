import gql from "graphql-tag"

export const GET_SUBSCRIPTIONS_QUERY = gql`
  query OrganizationSubscriptions($after: String, $before: String, $archived: Boolean) {
    organizationSubscriptions(first: 15, before: $before, after: $after, archived: $archived) {
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

export const GET_SUBSCRIPTION_QUERY = gql`
  query OrganizationSubscription($id: ID!, $after: String, $before: String, $archived: Boolean!) {
    organizationSubscription(id:$id) {
      id
      archived
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
    organizationMemberships(first: 15, before: $before, after: $after, archived: $archived) {
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
        }
      }
    }
    financeGlaccounts(first: 15, before: $before, after: $after, archived: $archived) {
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
          code
        }
      }
    }
    financeCostcenters(first: 15, before: $before, after: $after, archived: $archived) {
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
          code
        }
      }
    }
  }
`

export const GET_INPUT_VALUES_QUERY = gql`
  query SubscriptionInputValues($after: String, $before: String, $archived: Boolean) {
    organizationMemberships(first: 15, before: $before, after: $after, archived: $archived) {
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
        }
      }
    }
    financeGlaccounts(first: 15, before: $before, after: $after, archived: $archived) {
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
          code
        }
      }
    }
    financeCostcenters(first: 15, before: $before, after: $after, archived: $archived) {
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
          code
        }
      }
    }
  }
`