import gql from "graphql-tag"

export const GET_CLASSPASSES_QUERY = gql`
  query SchoolClasspasses($after: String, $before: String, $archived: Boolean) {
    schoolClasspasses(first: 15, before: $before, after: $after, archived: $archived) {
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
          schoolMembership {
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

export const GET_CLASSPASS_QUERY = gql`
  query SchoolClasspass($id: ID!, $after: String, $before: String, $archived: Boolean!) {
    schoolClasspass(id:$id) {
      id
      archived
      displayPublic
      displayShop
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
      schoolMembership {
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
          name
        }
      }
    }
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

export const GET_INPUT_VALUES_QUERY = gql`
  query InputValues($after: String, $before: String, $archived: Boolean) {
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
          name
        }
      }
    }
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