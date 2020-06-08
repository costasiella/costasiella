import gql from "graphql-tag"


export const GET_ACCOUNT_CLASSES_QUERY = gql`
  query ScheduleItemAttendance($before: String, $after: String) {
    scheduleItemAttendances(first: 20, before: $before, after: $after) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          attendanceType
          date
          bookingStatus
          scheduleItem {
            id
            timeStart
            timeEnd
            organizationLocationRoom {
              name
              organizationLocation {
                name
              }
            }
            organizationClasstype {
              name
            }
          }
        }
      } 
    }
    user {
      id
      accountId
      firstName
      lastName
      fullName
      email
      gender
      dateOfBirth
      address
      postcode
      city
      country
      phone
      mobile
      emergency
    }
  }
`