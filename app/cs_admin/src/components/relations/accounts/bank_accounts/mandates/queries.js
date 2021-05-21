import gql from "graphql-tag"


export const CREATE_ACCOUNT_BANK_ACCOUNT_MANDATE = gql`
  mutation CreateAccountBanKAccountMandate($input:CreateAccountBankAccountMandateInput!) {
    createAccountBankAccountMandate(input: $input) {
      accountBankAccountManddate {
        id
      }
    }
  }
`
