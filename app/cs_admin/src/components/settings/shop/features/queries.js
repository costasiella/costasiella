import gql from "graphql-tag"


export const GET_SHOP_FEATURES_QUERY = gql`
  query SystemFeatureShop {
    systemFeatureShop(id: "U3lzdGVtRmVhdHVyZVNob3BOb2RlOjE=") {
      memberships
      subscriptions
      classpasses
      classes
      events
    }
  }
`


export const UPDATE_SHOP_FEATURES = gql`
  mutation UpdateSystemFeatureShop($input: UpdateSystemFeatureShopInput!) {
    updateSystemFeatureShop(input: $input) {
      systemFeatureShop {
        id
      }
    }
  }
`