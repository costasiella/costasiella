import gql from "graphql-tag"

export const GET_ACCOUNT_CLASSPASSES_QUERY = gql`
  query AccountClasspasses($after: String, $before: String, $accountId: ID!) {
    accountClasspasses(first: 15, before: $before, after: $after, account: $accountId) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          organizationClasspass {
            id
            name
          }
          dateStart
          dateEnd
          classesRemainingDisplay
          createdAt
        }
      }
    }
    account(id:$accountId) {
      id
      firstName
      lastName
      email
      phone
      mobile
      isActive
    }
  }
`

export const GET_ACCOUNT_CLASSPASS_QUERY = gql`
  query AccountClasspass($id: ID!, $accountId: ID!, $after: String, $before: String, $archived: Boolean!) {
    accountClasspass(id:$id) {
      id
      organizationClasspass {
        id
        name
      }
      dateStart
      dateEnd
      note
      createdAt
    }
    organizationClasspasses(first: 100, before: $before, after: $after, archived: $archived) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          archived
          name
        }
      }
    }
    account(id:$accountId) {
      id
      firstName
      lastName
      email
      phone
      mobile
      isActive
    }
  }
`

export const GET_INPUT_VALUES_QUERY = gql`
  query ClasspassInputValues($after: String, $before: String, $archived: Boolean!, $accountId: ID!) {
    organizationClasspasses(first: 100, before: $before, after: $after, archived: $archived) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          archived
          name
        }
      }
    }
    account(id:$accountId) {
      id
      firstName
      lastName
      email
      phone
      mobile
      isActive
    }
  }
`