import gql from "graphql-tag"

export const GET_SCHEDULE_CLASS_TEACHERS_QUERY = gql`
  query ScheduleItemTeachers($after: String, $before: String, $scheduleItem: ID!) {
    scheduleItemTeachers(first: 15, before: $before, after: $after, scheduleItem: $scheduleItem) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          account {
            id
            fullName
          }
          role
          account2 {
            id
            fullName
          }
          role2
          dateStart
          dateEnd       
        }
      }
    }
  }
`

export const GET_LOCATION_ROOM_QUERY = gql`
  query OrganizationLocationRoom($id: ID!) {
    organizationLocationRoom(id:$id) {
      id
      organizationLocation {
        id
        name
      }
      name
      displayPublic
      archived
    }
  }
`