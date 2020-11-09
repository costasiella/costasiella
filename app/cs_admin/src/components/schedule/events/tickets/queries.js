import gql from "graphql-tag"

export const GET_SCHEDULE_EVENT_TICKETS_QUERY = gql`
query ScheduleEventTickets($before:String, $after:String, $schedule_event:ID!) {
  scheduleEventTickets(first: 100, before:$before, after:$after, scheduleEvent:$schedule_event) {
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    edges {
      node {
        id
        scheduleEvent {
          id
        }
        fullEvent
        deletable
        displayPublic
        name
        description
        price
        priceDisplay
        financeTaxRate {
          id
          name
        }
        financeGlaccount {
          id
          name
        }
        financeCostcenter {
          id
          name
        }
      }
    }
  }
}
`

export const GET_SCHEDULE_EVENT_TICKET_QUERY = gql`
query ScheduleEventTicket($before:String, $after:String, $schedule_event_ticket:ID!) {
  scheduleEventTicket(schedule_event_ticket: $schedule_event_ticket) {
    scheduleEventTicket {
      id
      displayPublic
      name
      description
      price
      financeTaxRate {
        id
        name
      }
      financeGlaccount {
        id
        name
      }
      financeCostcenter {
        id
        name
      }

    }
  }
}
`

// export const GET_ACCOUNT_SUBSCRIPTION_BLOCK_QUERY = gql`
// query AccountSubscriptionBlock($id: ID!) {
//   accountSubscriptionBlock(id:$id) {
//     id
//     accountSubscription {
//       id
//     }
//     dateStart
//     dateEnd
//     description
//   }
// }
// `


// export const DELETE_ACCOUNT_SUBSCRIPTION_BLOCK = gql`
//   mutation DeleteAccountSubscriptionBlock($input: DeleteAccountSubscriptionBlockInput!) {
//     deleteAccountSubscriptionBlock(input: $input) {
//       ok
//     }
//   }
// `


export const GET_INPUT_VALUES_QUERY = gql`
  query ScheduleEventTicketInputValues($after: String, $before: String) {
    financeTaxRates(first: 100, before: $before, after: $after, archived: false) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          name
        }
      }
    }
    financeGlaccounts(first: 100, before: $before, after: $after, archived: false) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          name
        }
      }
    }
    financeCostcenters(first: 100, before: $before, after: $after, archived: false) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          name
        }
      }
    }
  }
`