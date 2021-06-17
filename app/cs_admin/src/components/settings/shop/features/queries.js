import gql from "graphql-tag"


export const GET_SHOP_FEATURES_QUERY = gql`
  query ShopFeatures {
    systemShopFeature(id: "U3lzdGVtU2hvcEZlYXR1cmVOb2RlOjE=") {
      memberships
      subscriptions
      classpasses
      classes
      events
    }
  }
`


export const UPDATE_SHOP_FEATURES = gql`
  mutation UpdateSystemShopFeature($input: UpdateSystemShopFeatureInput!) {
    updateSystemShopFeature(input: $input) {
      systemShopFeature {
        id
      }
    }
  }
`