import gql from "graphql-tag"


export const GET_ACCOUNT_QUERY = gql`
  query User {
    user {
      id
      firstName
      lastName
      email
      gender
      dateOfBirth
      address
      postcode
      city
      country
      phone
      mobile
      emergency
    }
  }
`