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
          percentage
          dateStart
          dateEnd
        }
      }
    }
  }
`


export const GET_SCHEDULE_EVENT_EARLYBIRD_QUERY = gql`
  query ScheduleEventEarlybird($id:ID!) {
    scheduleEventEearlybird(id: $id) {
      id
      percentage
      dateStart
      dateEnd
    }
  }
`


const ADD_SCHEDULE_EVENT_EARLYBIRD = gql`
  mutation CreateScheduleEventEarlybird($input:CreateScheduleEventEarlybirdInput!) {
    createScheduleEventEarlybird(input: $input) {
      scheduleEventEarlybird {
        id
      }
    }
  }
`


const UPDATE_SCHEDULE_EVENT_EARLYBIRD = gql`
  mutation UpdateScheduleEventEarlybird($input:UpdateScheduleEventEarlybirdInput!) {
    updateScheduleEventEarlybird(input: $input) {
      scheduleEventEarlybird {
        id
      }
    }
  }
`


export const DELETE_SCHEDULE_EVENT_EARLYBIRD   = gql`
  mutation DeleteScheduleEventEarlybird$input: DeleteScheduleEventEarlybirdInput!) {
    deleteScheduleEventEarlybird(input: $input) {
      ok
    }
  }
`
