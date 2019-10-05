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
