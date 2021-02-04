import gql from "graphql-tag"

export const GET_SCHEDULE_EVENT_TICKET_SCHEDULE_ITEMS_QUERY = gql`
query ScheduleEventTicketScheduleItem($before:String, $after:String, $scheduleEventTicket:ID!) {
  scheduleEventTicketScheduleItems(first: 100, before: $before, after: $after, scheduleEventTicket:$scheduleEventTicket) {
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    edges {
      node {
        id
        scheduleEventTicket {
          id
          name
          fullEvent
        }
        scheduleItem {
          id
          name
        }
        included
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

