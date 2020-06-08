import gql from "graphql-tag"


export const GET_SYSTEM_SETTINGS_QUERY = gql`
  query SystemSettings($setting: String!) {
    systemSettings(setting: $setting) {
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
  mutation UpdateSystemSetting($input: UpdateSystemSettingInput!) {
    updateSystemSetting(input: $input) {
      systemSetting {
        id
      }
    }
  }
`