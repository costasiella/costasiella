import gql from "graphql-tag"


export const GET_ACCOUNT_TEACHER_PROFILE_QUERY = gql`
  query AccountTeacherQuery($id: ID!) {
    accountTeacherProfile(id:$id) {
      id
      classes
      appointments
      role
      education
      bio
      urlBio
      urlWebsite
    }
  }
`