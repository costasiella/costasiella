import gql from "graphql-tag"


export const GET_ACCOUNT_CLASSES_QUERY = gql`
  query ScheduleItemAttendance($before: String, $after: String, $account: ID!) {
    scheduleItemAttendances(first: 20, before: $before, after: $after, account: $account, accountScheduleEventTicket_Isnull: true) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          cancellationPossible
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