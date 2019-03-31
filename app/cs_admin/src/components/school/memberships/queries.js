import gql from "graphql-tag"

export const GET_MEMBERSHIPS_QUERY = gql`
  query SchoolMemberships($after: String, $before: String, $archived: Boolean) {
    schoolMemberships(first: 15, before: $before, after: $after, archived: $archived) {
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
          name
          description
          price
          financeTaxRate {
            id
            name
          }
          validity
          validityUnit
          termsAndConditions
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

export const GET_MEMBERSHIP_QUERY = gql`
  query SchoolMembership($id: ID!) {
    schoolMembership(id:$id) {
      id
      archived
      displayPublic
      displayShop
      name
      description
      price
      financeTaxRate {
        id
        name
      }
      validity
      validityUnit
      termsAndConditions
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

export const GET_INPUT_VALUES_QUERY = gql`
  query FinanceInputValues($after: String, $before: String, $archived: Boolean) {
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