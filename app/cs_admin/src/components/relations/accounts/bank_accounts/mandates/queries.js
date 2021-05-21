import gql from "graphql-tag"


export const CREATE_ACCOUNT_BANK_ACCOUNT_MANDATE = gql`
  mutation CreateAccountBankAccountMandate($input:CreateAccountBankAccountMandateInput!) {
    createAccountBankAccountMandate(input: $input) {
      accountBankAccountMandate {
        id
      }
    }
  }
`
