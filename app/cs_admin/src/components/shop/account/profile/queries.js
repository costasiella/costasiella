import { gql } from '@apollo/client';


export const UPDATE_PROFILE = gql`
  mutation UpdateAccount($input:UpdateAccountInput!) {
    updateAccount(input: $input) {
      account {
        id
        firstName
        lastName
        email
      }
    }
  }
`