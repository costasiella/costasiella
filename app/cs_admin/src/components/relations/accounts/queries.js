import gql from "graphql-tag"

export const GET_ACCOUNTS_QUERY = gql`
  query Accounts($after: String, $before: String, $isActive: Boolean!) {
    accounts(first: 15, before: $before, after: $after, isActive: $isActive) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          firstName
          lastName
          email
          isActive
        }
      }
    }
  }
`

export const GET_ACCOUNT_QUERY = gql`
  query Account($id: ID!) {
    account(id:$id) {
      id
      firstName
      lastName
      email
      dateOfBirth
      gender
      address
      postcode
      city
      country
      phone
      mobile
      emergency
      isActive
    }
  }
`