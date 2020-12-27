import gql from "graphql-tag"


export const GET_SCHEDULE_EVENT_MEDIAS_QUERY = gql`
  query ScheduleEventMedias($before:String, $after:String, $schedule_event:ID!) {
    scheduleEventMedias(first: 100, before:$before, after:$after, scheduleEvent:$schedule_event) {
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
          sortOrder
          description
          urlImage
          urlImageThumbnailSmall
          image
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
      organizationLocation {
        id
        name
      }
    }
    account {
      id
      fullName
    }
    account2 {
      id
      fullName
    }
  }
  accounts(first: 100, before: $before, after: $after, isActive:true, teacher: true) {
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
        organizationLocation {
          id 
          name
        }
      }
    }
  }
}
`


export const DELETE_SCHEDULE_EVENT_MEDIA   = gql`
  mutation DeleteScheduleEventMedia($input: DeleteScheduleEventMediaInput!) {
    deleteScheduleEventMedia(input: $input) {
      ok
    }
  }
`


export const GET_INPUT_VALUES_QUERY = gql`
  query ScheduleEventActivityInputValues($after: String, $before: String) {
    accounts(first: 100, before: $before, after: $after, isActive: true, teacher: true) {
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
          organizationLocation {
            id
            name
          }
        }
      }
    }
  }
`