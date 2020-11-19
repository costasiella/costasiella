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
        organizationLocationRoom {
          id
          name
        }
        name
        spaces
        dateStart
        timeStart
        timeEnd
        account {
          id
          fullName
        }
        account2 {
          id
          fullName
        }
      }
    }
  }
}
`


export const GET_SCHEDULE_EVENT_ACTIVITY_QUERY = gql`
query ScheduleEventActivity($before:String, $after:String, $id:ID!) {
  scheduleItem(id: $id) {
    id
    displayPublic
    name
    spaces
    dateStart
    timeStart
    timeEnd
    organizationLocationRoom {
      id
      name
    }
    account {
      id
      name
    }
    account2 {
      id
      name
    }
  }
  accounts(first: 100, before: $before, after: $after, teacher: true) {
    pageInfo {
      startCursor
      endCursor
      hasNextPage
      hasPreviousPage
    }
    edges {
      node {
        id
        fullName
      }
    }
  }
  organizationLocationRooms(first: 100, before: $before, after: $after, archived: false) {
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


export const DELETE_SCHEDULE_EVENT_ACTIVITY = gql`
  mutation DeleteScheduleEventActivity($input: DeleteScheduleEventActivityInput!) {
    deleteScheduleEventActivity(input: $input) {
      ok
    }
  }
`


export const GET_INPUT_VALUES_QUERY = gql`
  query ScheduleEventActivityInputValues($after: String, $before: String) {
    accounts(first: 100, before: $before, after: $after, teacher: true) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          fullName
        }
      }
    }
    organizationLocationRooms(first: 100, before: $before, after: $after, archived: false) {
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