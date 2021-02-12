import gql from "graphql-tag"

export const GET_SCHEDULE_ITEM_ATTENDANCES_QUERY = gql`
query ScheduleItemAttendances($before:String, $after:String, $schedule_item:ID!) {
  scheduleItemAttendances(first: 100, before: $before, after: $after, scheduleItem:$schedule_item) {
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    edges {
      node {
        id
        bookingStatus
        account {
          id
          fullName
        }
        accountScheduleEventTicket {
          id
          scheduleEventTicket {
            name
          }
          cancelled
        }
      }
    }
  }
}
`

// export const GET_SCHEDULE_EVENT_TICKET_SCHEDULE_ITEM_QUERY = gql`
// query ScheduleEventTicket($before:String, $after:String, $id:ID!) {
//   scheduleEventTicket(id: $id) {
//     id
//     displayPublic
//     name
//     description
//     price
//     financeTaxRate {
//       id
//       name
//     }
//     financeGlaccount {
//       id
//       name
//     }
//     financeCostcenter {
//       id
//       name
//     }
//   }
//   financeTaxRates(first: 100, before: $before, after: $after, archived: false) {
//     pageInfo {
//       startCursor
//       endCursor
//       hasNextPage
//       hasPreviousPage
//     }
//     edges {
//       node {
//         id
//         name
//       }
//     }
//   }
//   financeGlaccounts(first: 100, before: $before, after: $after, archived: false) {
//     pageInfo {
//       startCursor
//       endCursor
//       hasNextPage
//       hasPreviousPage
//     }
//     edges {
//       node {
//         id
//         name
//       }
//     }
//   }
//   financeCostcenters(first: 100, before: $before, after: $after, archived: false) {
//     pageInfo {
//       startCursor
//       endCursor
//       hasNextPage
//       hasPreviousPage
//     }
//     edges {
//       node {
//         id
//         name
//       }
//     }
//   }
// }
// `

