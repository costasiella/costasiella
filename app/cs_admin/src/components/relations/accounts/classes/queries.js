import gql from "graphql-tag"

export const GET_ACCOUNT_CLASSES_QUERY = gql`
  query ScheduleItemAttendance($account: ID!, $before: String, $after: String) {
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
    account(id:$account) {
      id
      firstName
      lastName
      email
      phone
      mobile
      isActive
    }
  }
`

// export const GET_ACCOUNT_CLASSPASS_QUERY = gql`
//   query AccountClasspass($id: ID!, $accountId: ID!, $after: String, $before: String, $archived: Boolean!) {
//     accountClasspass(id:$id) {
//       id
//       organizationClasspass {
//         id
//         name
//       }
//       dateStart
//       dateEnd
//       note
//       createdAt
//     }
//     organizationClasspasses(first: 100, before: $before, after: $after, archived: $archived) {
//       pageInfo {
//         startCursor
//         endCursor
//         hasNextPage
//         hasPreviousPage
//       }
//       edges {
//         node {
//           id
//           archived
//           name
//         }
//       }
//     }
//     account(id:$accountId) {
//       id
//       firstName
//       lastName
//       email
//       phone
//       mobile
//       isActive
//     }
//   }
// `
