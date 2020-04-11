import gql from "graphql-tag"


export const GET_SYSTEM_SETTINGS_QUERY = gql`
  query SystemSettings {
    systemSettings(setting: "integration_mollie_api_key") {
      edges {
        node {
          id
          setting
          value
        }
      }
    }
  }
`


export const UPDATE_SYSTEM_SETTING = gql`
  mutation UpdateAppSettings($input: UpdateSystemSettingInput!) {
    updateSystemSetting(input: $input) {
      systemSetting {
        id
      }
    }
  }
`