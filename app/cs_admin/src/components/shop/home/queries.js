import gql from "graphql-tag"

export const GET_SHOP_ANNOUNCEMENTS_QUERY = gql`
  query OrganizationAnnouncements($after: String, $before: String) {
    organizationAnnouncements(first: 100, before: $before, after: $after, displayPublic: true, displayShop: true) {
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