import gql from "graphql-tag"

const GET_USER_PROFILE = gql`
  query User {
    user {
      id
      firstName
      lastName
      fullName
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

export default GET_USER_PROFILE