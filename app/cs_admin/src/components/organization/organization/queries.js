import gql from "graphql-tag"


export const GET_ORGANIZATION_QUERY = gql`
  query Organization($id: ID!) {
    organization(id:$id) {
      id
      name
      address
      phone
      email
      registration
      taxRegistration
      urlLogoLogin
      urlLogoInvoice
      urlLogoEmail
      urlLogoShopHeader
      urlLogoSelfCheckin
    }
  }
`