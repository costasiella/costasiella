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

export const GET_APPOINTMENT_PRICE_QUERY = gql`
  query OrganizationAppointment($id: ID!, $after: String, $before: String) {
    organizationAppointmentPrice(id:$id) {
      id
      price
      account {
        id
        fullName
      }
      financeTaxRate {
        id
        name
      }
    }
    financeTaxRates(first: 100, before: $before, after: $after, archived: false) {
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
    accountTeacherProfiles(first: 100, before: $before, after: $after, appointments: true, account_IsActive: true) {
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
        }
      }
    }
  }
`


export const GET_INPUT_VALUES_QUERY = gql`
  query AppointmentInputValues($after: String, $before: String, $archived: Boolean) {
    financeTaxRates(first: 15, before: $before, after: $after, archived: $archived) {
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
    accountTeacherProfiles(first: 100, before: $before, after: $after, appointments: true, account_IsActive: true) {
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
        }
      }
    }
  }
`