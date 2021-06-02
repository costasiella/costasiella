import gql from "graphql-tag"


export const GET_SCHEDULE_EVENT_EARLYBIRDS_QUERY = gql`
  query ScheduleEventEarlybirds($before:String, $after:String, $scheduleEvent:ID!) {
    scheduleEventEarlybirds(first: 100, before:$before, after:$after, scheduleEvent:$scheduleEvent) {
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
          discountPercentage
          dateStart
          dateEnd
        }
      }
    }
  }
`


export const GET_SCHEDULE_EVENT_EARLYBIRD_QUERY = gql`
  query ScheduleEventEarlybird($id:ID!) {
    scheduleEventEarlybird(id: $id) {
      id
      discountPercentage
      dateStart
      dateEnd
    }
  }
`


export const ADD_SCHEDULE_EVENT_EARLYBIRD = gql`
  mutation CreateScheduleEventEarlybird($input:CreateScheduleEventEarlybirdInput!) {
    createScheduleEventEarlybird(input: $input) {
      scheduleEventEarlybird {
        id
      }
    }
  }
`


export const UPDATE_SCHEDULE_EVENT_EARLYBIRD = gql`
  mutation UpdateScheduleEventEarlybird($input:UpdateScheduleEventEarlybirdInput!) {
    updateScheduleEventEarlybird(input: $input) {
      scheduleEventEarlybird {
        id
      }
    }
  }
`


export const DELETE_SCHEDULE_EVENT_EARLYBIRD   = gql`
  mutation DeleteScheduleEventEarlybird($input: DeleteScheduleEventEarlybirdInput!) {
    deleteScheduleEventEarlybird(input: $input) {
      ok
    }
  }
`
