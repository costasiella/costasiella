import gql from "graphql-tag"

export const GET_BACKEND_ANNOUNCEMENTS_QUERY = gql`
  query OrganizationAnnouncements($after: String, $before: String) {
    organizationAnnouncements(first: 100, before: $before, after: $after, displayPublic: true, displayBackend: true) {
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