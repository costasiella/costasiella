import gql from "graphql-tag"


export const QUERY_ACCOUNT_CLASSPASSES = gql`
  query AccountClasspass($before: String, $after: String) {
    accountClasspasses(first: 100, before: $before, after: $after) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          account {
            id
            fullName
          }
          dateStart
          organizationClasspass {
            name
          }
        }
      }
    }
  }
`