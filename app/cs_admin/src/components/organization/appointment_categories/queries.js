import gql from "graphql-tag"

export const GET_APPOINTMENT_CATEGORIES_QUERY = gql`
  query OrganizationAppointmentCategories($after: String, $before: String, $archived: Boolean) {
    organizationAppointmentCategories(first: 15, before: $before, after: $after, archived: $archived) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id,
          archived,
          displayPublic,
          name
        }
      }
    }
  }
`

export const GET_APPOINTMENT_CATEGORY_QUERY = gql`
  query OrganizationAppointmentCategory($id: ID!) {
    organizationAppointmentCategory(id:$id) {
      id
      name
      displayPublic
      archived
    }
  }
`