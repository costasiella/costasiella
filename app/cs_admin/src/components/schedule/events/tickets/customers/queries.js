import gql from "graphql-tag"

export const GET_ACCOUNT_SCHEDULE_EVENT_TICKETS_QUERY = gql`
query AccountScheduleEventTickets($before:String, $after:String, $scheduleEventTicket:ID!) {
  accountScheduleEventTickets(first: 100, before: $before, after: $after, scheduleEventTicket:$scheduleEventTicket) {
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    edges {
      node {
        id
        account {
          id
          fullName
        }
        cancelled
        paymentConfirmation
        infoMailSent
      }
    }
  }
}
`

export const GET_SCHEDULE_EVENT_TICKET_SCHEDULE_ITEM_QUERY = gql`
query ScheduleEventTicket($before:String, $after:String, $id:ID!) {
  scheduleEventTicket(id: $id) {
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

export const UPDATE_ACCOUNT_SCHEDULE_EVENT_TICKET = gql`
  mutation UpdateAccountScheduleEventTicket($input:UpdateAccountScheduleEventTicketInput!) {
    updateAccountScheduleEventTicket(input: $input) {
      accountScheduleEventTicket {
        id
      }
    }
  }
`

export const DELETE_SCHEDULE_EVENT_TICKET = gql`
  mutation DeleteScheduleEventTicket($input: DeleteScheduleEventTicketInput!) {
    deleteScheduleEventTicket(input: $input) {
      ok
    }
  }
`

