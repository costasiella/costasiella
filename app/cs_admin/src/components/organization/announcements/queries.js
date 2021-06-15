import gql from "graphql-tag"

export const GET_ANNOUNCEMENTS_QUERY = gql`
  query OrganizationAnnouncements($after: String, $before: String) {
    organizationLevels(first: 15, before: $before, after: $after) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          displayPublic
          displayShop
          displayBackend
          name
          content
          dateStart
          dateEnd
          priority
        }
      }
    }
  }
`

export const GET_ANNOUNCEMENT_QUERY = gql`
  query OrganizationAnnouncement($id: ID!) {
    organizationAnnouncement(id:$id) {
      id
      displayPublic
      displayShop
      displayBackend
      name
      content
      dateStart
      dateEnd
      priority
    }
  }
`

export const DELETE_ANNOUNCEMENT = gql`
mutation DeleteOrganizationAnnouncement($input: DeleteOrganizationAnnouncementInput!) {
  deleteOrganizationAnnouncement(input: $input) {
    ok
  }
}
`
