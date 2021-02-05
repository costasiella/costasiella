import gql from "graphql-tag"

const GET_USER = gql`
  query {
    user {
      id
      isActive
      email
      firstName
      lastName
      employee
      teacher
      groups {
        edges {
          node {
            id
            name
            permissions {
              edges {
                node {
                  id
                  name
                  codename
                }
              }
            }
          }
        }
      }
    }
  }
`

export default GET_USER