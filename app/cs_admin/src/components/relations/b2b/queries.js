import gql from "graphql-tag"

export const GET_BUSINESSES_QUERY = gql`
  query Businesses($before:String, $after:String, $name:String, $archived: Boolean!) {
    businesses(first:15, before:$before, after:$after, b2b:true, name_Icontains:$name, archived:$archived) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          archived
          b2b
          supplier
          vip
          name
          address
          postcode
          city
          country
          phone
          phone2
          emailContact
          emailBilling
          registration
          taxRegistration
          mollieCustomerId
        }
      }
    }
  }
`

export const GET_BUSINESS_QUERY = gql`
  query Business($id: ID!) {
    business(id:$id) {
      id
      archived
      vip
      name
      address
      postcode
      city
      country
      phone
      phone2
      emailContact
      emailBilling
      registration
      taxRegistration
      mollieCustomerId
    }
  }
`

export const UPDATE_BUSINESS = gql`
  mutation UpdateBusiness($input: UpdateBusinessInput!) {
    updateBusiness(input: $input) {
      business {
        id
        archived
      }
    }
  }
`

