import gql from "graphql-tag"

export const GET_ACCOUNTS_QUERY = gql`
  query Accounts(
    $after: String, 
    $before: String, 
    $isActive: Boolean!, 
    $searchName: String,
    $customer: Boolean,
    $teacher: Boolean,
    $employee: Boolean
    
  ) {
    accounts(
      first: 15, 
      before: $before, 
      after: $after, 
      isActive: $isActive, 
      fullName_Icontains: $searchName,
      customer: $customer,
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
          customer
          teacher
          employee
          firstName
          lastName
          email
          isActive
        }
      }
    }
  }
`

export const GET_ACCOUNT_QUERY = gql`
  query Account($id: ID!) {
    account(id:$id) {
      id
      customer
      teacher
      employee
      firstName
      lastName
      email
      dateOfBirth
      gender
      address
      postcode
      city
      country
      phone
      mobile
      emergency
      isActive
    }
  }
`