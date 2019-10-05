import gql from "graphql-tag"


export const TOKEN_AUTH = gql`
  mutation TokenAuth($username: String!, $password: String!) {
      tokenAuth(username: $username, password: $password) {
      token
      }
  } 
`


export const TOKEN_VERIFY = gql`
  mutation VerifyToken($token: String!) {
    verifyToken(token: $token) {
      payload
    }
  }
`


export const TOKEN_REFRESH = gql`
  mutation RefreshToken($token: String!) {
    refreshToken(token: $token) {
      token
      payload
    }
  }
`


export const TOKEN_REVOKE = gql`
  mutation RevokeToken($refreshToken: String!) {
    revokeToken(refreshToken: $refreshToken) {
      revoked
    }
  }
`


export const UPDATE_ACCOUNT_PASSWORD = gql`
  mutation UpdateAccountPassword($input: UpdateAccountPasswordInput!) {
    updateAccountPassword(input: $input) {
      ok
    }
  }
`