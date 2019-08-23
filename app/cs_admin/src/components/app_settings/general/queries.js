import gql from "graphql-tag"


export const GET_APP_SETTINGS_QUERY = gql`
  query AppSettings {
    appSettings(id: "QXBwU2V0dGluZ3NOb2RlOjE=") {
      dateFormat
      timeFormat
    }
  }
`