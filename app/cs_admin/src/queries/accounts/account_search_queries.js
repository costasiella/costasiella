import gql from "graphql-tag"

export const GET_ACCOUNTS_QUERY = gql`
  query Accounts(
    $after: String, 
    $before: String, 
    $searchName: String,
    $teacher: Boolean,
    $employee: Boolean
  ) {
    accounts(
      first: 25, 
      before: $before, 
      after: $after, 
      isActive: true, 
      fullName_Icontains: $searchName,
      customer: true,
      teacher: $teacher,
      employee: $employee
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
          fullName
          email
          isActive
        }
      }
    }
  }
`