import gql from "graphql-tag"


export const GET_SCHEDULE_EVENT_MEDIAS_QUERY = gql`
  query ScheduleEventMedias($before:String, $after:String, $scheduleEvent:ID!) {
    scheduleEventMedias(first: 100, before:$before, after:$after, scheduleEvent:$scheduleEvent) {
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


export const GET_SCHEDULE_EVENT_MEDIA_QUERY = gql`
  query ScheduleEventMedia($id:ID!) {
    scheduleEventMedia(id: $id) {
      id
      sortOrder
      description
      image
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