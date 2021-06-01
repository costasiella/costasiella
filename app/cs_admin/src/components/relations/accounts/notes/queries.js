import gql from "graphql-tag"

export const GET_ACCOUNT_NOTES_QUERY = gql`
  query AccountNotes($after: String, $before: String, $account: ID!, $noteType: String!) {
    accountNotes(first: 15, before: $before, after: $after, account: $account, noteType: $noteType ) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          note
          injury
          noteType
          noteBy {
            id
            fullName
          }
          createdAt
        }
      }
    }
  }
`

export const GET_ACCOUNT_NOTE_QUERY = gql`
  query AccountNote($id: ID!) {
    accountNote(id: $id) {
      id
      note
      injury
    }
  }
`


export const CREATE_ACCOUNT_NOTE = gql`
  mutation CreateAccountNote($input: CreateAccountNoteInput!) {
    createAccountNote(input: $input) {
      accountNote {
        id
      }
    }
  }
`

export const UPDATE_ACCOUNT_NOTE = gql`
  mutation UpdateAccountNote($input: UpdateAccountNoteInput!) {
    updateAccountNote(input: $input) {
      accountNote {
        id
      }
    }
  }
`

export const DELETE_ACCOUNT_NOTE = gql`
  mutation DeleteAccountNote($input: DeleteAccountNoteInput!) {
    deleteAccountNote(input: $input) {
      ok
    }
  }
`
