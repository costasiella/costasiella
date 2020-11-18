import gql from "graphql-tag"

export const GET_SCHEDULE_EVENT_ACTIVITIES_QUERY = gql`
query ScheduleItem($before:String, $after:String, $schedule_event:ID!) {
  scheduleItems(first:100, before:$before, after:$after, scheduleEvent:$schedule_event) {
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    edges {
      node {
        id
        displayPublic
        scheduleEvent {
          id
          name
        }
      	scheduleItemType
        frequencyType
        scheduleItemType
        organizationLocationRoom {
          id
          name
        }
        name
        spaces
        dateStart
        timeStart
        timeEnd
      	description
      }
    }
  }
}
`

// export const GET_SCHEDULE_EVENT_TICKET_QUERY = gql`
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


export const DELETE_SCHEDULE_EVENT_ACTIVITY = gql`
  mutation DeleteScheduleEventActivity($input: DeleteScheduleEventActivityInput!) {
    deleteScheduleEventActivity(input: $input) {
      ok
    }
  }
`


// export const GET_INPUT_VALUES_QUERY = gql`
//   query ScheduleEventTicketInputValues($after: String, $before: String) {
//     financeTaxRates(first: 100, before: $before, after: $after, archived: false) {
//       pageInfo {
//         startCursor
//         endCursor
//         hasNextPage
//         hasPreviousPage
//       }
//       edges {
//         node {
//           id
//           name
//         }
//       }
//     }
//     financeGlaccounts(first: 100, before: $before, after: $after, archived: false) {
//       pageInfo {
//         startCursor
//         endCursor
//         hasNextPage
//         hasPreviousPage
//       }
//       edges {
//         node {
//           id
//           name
//         }
//       }
//     }
//     financeCostcenters(first: 100, before: $before, after: $after, archived: false) {
//       pageInfo {
//         startCursor
//         endCursor
//         hasNextPage
//         hasPreviousPage
//       }
//       edges {
//         node {
//           id
//           name
//         }
//       }
//     }
//   }
// `