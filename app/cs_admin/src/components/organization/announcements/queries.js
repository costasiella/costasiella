import gql from "graphql-tag"

export const GET_ANNOUNCEMENTS_QUERY = gql`
  query OrganizationAnnouncements($after: String, $before: String) {
    organizationAnnouncements(first: 15, before: $before, after: $after) {
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
          title
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
      title
      content
      dateStart
      dateEnd
      priority
    }
  }
`

export const ADD_ANNOUNCEMENT = gql`
  mutation CreateOrganizationAnnouncement($input:CreateOrganizationAnnouncementInput!) {
    createOrganizationAnnouncement(input: $input) {
      organizationAnnouncement {
        id
      }
    }
  }
`

export const UPDATE_ANNOUNCEMENT = gql`
  mutation UpdateOrganizationAnnouncement($input: UpdateOrganizationAnnouncementInput!) {
    updateOrganizationAnnouncement(input: $input) {
      organizationAnnouncement {
        id
      }
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
