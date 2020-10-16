import gql from "graphql-tag"


export const QUERY_ACCOUNT_SUBSCRIPTIONS = gql`
  query AccountSubscriptions($before: String, $after: String, $account: ID!) {
    accountSubscriptions(first: 100, before: $before, after: $after, account: $account) {
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
          organizationSubscription {
            name
          }
          dateStart
          dateEnd
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