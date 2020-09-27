import gql from "graphql-tag"


export const QUERY_ACCOUNT_CLASSPASSES = gql`
  query AccountClasspass($before: String, $after: String, $account: ID!) {
    accountClasspasses(first: 100, before: $before, after: $after, account: $account) {
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
          organizationClasspass {
            name
          }
          dateStart
          dateEnd
          classesRemainingDisplay
        }
      }
    }
    user {
      id
      accountId
      firstName
      lastName
      fullName
      email
      gender
      dateOfBirth
      address
      postcode
      city
      country
      phone
      mobile
      emergency
    }
  }
`