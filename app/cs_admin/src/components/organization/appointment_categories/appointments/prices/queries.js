import gql from "graphql-tag"

export const GET_APPOINTMENT_PRICES_QUERY = gql`
  query OrganizationAppointmentPrices($after: String, $before: String, $organizationAppointment: ID!) {
    organizationAppointmentPrices(first: 15, before: $before, after: $after, organizationAppointment: $organizationAppointment) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          account {
            id
            fullName
          }
          price
          priceDisplay
          financeTaxRate {
            id
            name
          }
        }
      }
    }
    organizationAppointment(id: $organizationAppointment) {
      id
      name
    }
  }
`

export const GET_APPOINTMENT_QUERY = gql`
  query OrganizationAppointment($id: ID!, $after: String, $before: String) {
    organizationAppointment(id:$id) {
      id
      name
      displayPublic
      archived
      financeGlaccount {
        id 
        name
      }
      financeCostcenter {
        id
        name
      }
    }
    financeGlaccounts(first: 15, before: $before, after: $after, archived: false) {
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
    financeCostcenters(first: 15, before: $before, after: $after, archived: false) {
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
  query AppointmentInputValues($after: String, $before: String, $archived: Boolean) {
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
          code
        }
      }
    }
    accounts(first: 100, before: $before, after: $after, isActive: true, teacher: true) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          fullName
        }
      }
    }
  }
`