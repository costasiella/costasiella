import gql from "graphql-tag"


export const GET_ACCOUNT_TEACHER_PROFILE_QUERY = gql`
  query AccountTeacherProfileQuery($id: ID!) {
    accountTeacherProfiles(account:$id) {
      id
      classes
      appointments
      role
      education
      bio
      urlBio
      urlWebsite
    }
    account(id:$id) {
      id
      teacher
      firstName
      lastName
      email
      phone
      mobile
      isActive
    }
  }
`