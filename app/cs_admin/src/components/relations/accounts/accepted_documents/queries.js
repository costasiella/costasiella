import gql from "graphql-tag"

export const GET_ACCOUNT_ACCEPTED_DOCUMENTS_QUERY = gql`
  query AccountAcceptedDocuments($after: String, $before: String, $account: ID!) {
    accountAcceptedDocuments(first: 15, before:$before, after:$after, account: $account) {
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
            email
          }
          document {
            id
            documentType
            version
            urlDocument
          }
          dateAccepted
          clientIp
        }
      }
    }
    account(id:$account) {
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
