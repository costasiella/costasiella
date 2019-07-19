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
  query OrganizationAppointment($id: ID!) {
    organizationAppointment(id:$id) {
      id
      name
      displayPublic
      archived
    }
  }
`