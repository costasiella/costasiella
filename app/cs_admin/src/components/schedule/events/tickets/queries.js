import gql from "graphql-tag"

export const GET_SCHEDULE_EVENT_TICKETS_QUERY = gql`
  query ScheduleEventTickets($before:String, $after:String, $scheduleEvent:ID!) {
    scheduleEventTickets(first: 100, before:$before, after:$after, scheduleEvent:$scheduleEvent) {
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
          isSoldOut
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

export const DELETE_SCHEDULE_EVENT_TICKET = gql`
  mutation DeleteScheduleEventTicket($input: DeleteScheduleEventTicketInput!) {
    deleteScheduleEventTicket(input: $input) {
      ok
    }
  }
`


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