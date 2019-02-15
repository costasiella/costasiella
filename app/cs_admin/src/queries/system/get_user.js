import gql from "graphql-tag"

const GET_USER = gql`
  query {
    user {
    id
    isActive
    email
    firstName
    lastName
    userPermissions {
      id
    }
    groups {
      id
      name
      permissions {
        id
        name
        codename
      }
    }
  }
  }
`

export default GET_USER