import gql from "graphql-tag"


export const GET_ACCOUNT_BANK_ACCOUNTS_QUERY = gql`
  query AccountBankAccounts($after: String, $before: String, $account: ID!) {
    accountBankAccounts(
      first: 1, 
      before: $before, 
      after: $after, 
      account: $account
    ) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          number
          holder
          bic
          mandates(first: 100) {
            pageInfo {
              hasNextPage
              hasPreviousPage
              startCursor
              endCursor
            }
            edges {
              node {
                id
                reference
                content
                signatureDate
              }
            }
          }
        }
      }
    }
  }
`

// export const GET_ACCOUNT_QUERY = gql`
//   query Account($id: ID!) {
//     account(id:$id) {
//       id
//       customer
//       teacher
//       employee
//       firstName
//       lastName
//       email
//       dateOfBirth
//       gender
//       address
//       postcode
//       city
//       country
//       phone
//       mobile
//       emergency
//       isActive
//     }
//   }
// `

export const UPDATE_ACCOUNT_BANK_ACCOUNT = gql`
  mutation UpdateAccountBanKAccount($input:UpdateAccountBankAccountInput!) {
    updateAccountBankAccount(input: $input) {
      accountBankAccount {
        id
        number
        holder
        bic
      }
    }
  }
`
