import gql from "graphql-tag"

export const GET_APPOINTMENTS_QUERY = gql`
  query OrganizationAppointments($after: String, $before: String, $organizationAppointmentCategory: ID!, $archived: Boolean!) {
    organizationAppointments(first: 15, before: $before, after: $after, organizationAppointmentCategory: $organizationAppointmentCategory, archived: $archived) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          organizationAppointmentCategory {
            id
            name
          }
          archived,
          displayPublic
          name
        }
      }
    }
    organizationAppointmentCategory(id: $organizationAppointmentCategory) {
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