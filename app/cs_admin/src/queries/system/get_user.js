import gql from "graphql-tag"

const GET_USER = gql`
  query User($permissionsBefore:String, $permissionsAfter:String)  {
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
            permissions(first: 100, before: $permissionsBefore, after: $permissionsAfter) {
              pageInfo {
                hasNextPage
                hasPreviousPage
                startCursor
                endCursor                
              }
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