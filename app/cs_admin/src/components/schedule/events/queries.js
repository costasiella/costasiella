import gql from "graphql-tag"

export const GET_SCHEDULE_EVENTS_QUERY = gql`
  query ScheduleEvents($before:String, $after:String, $archived:Boolean!) {
    scheduleEvents(first: 100, before: $before, after:$after, archived:$archived) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          archived
          displayPublic
          displayShop
          autoSendInfoMail
          organizationLocation {
            id
            name
          }
          name
          tagline
          preview
          description
          organizationLevel {
            id
            name
          }
          teacher {
            id 
            fullName
          }
          teacher2 {
            id
            fullName
          }
          dateStart
          dateEnd
          timeStart
          timeEnd
          infoMailContent
          scheduleItems {
            edges {
              node {
                id
              }
            }
          }
          createdAt
          updatedAt
        }
      }
    }
  }
`

export const GET_EVENT_QUERY = gql`
  query SchoolLevel($id: ID!) {
    organizationLevel(id:$id) {
      id
      name
      archived
    }
  }
`


export const GET_INPUT_VALUES_QUERY = gql`
  query ScheduleEventInputValues($after: String, $before: String) {
    organizationLocations(first: 100, before: $before, after: $after, archived: false) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          archived
          name
        }
      }
    }
    organizationLevels(first: 100, before: $before, after: $after, archived: false) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          archived
          name
        }
      }
    }
  }
`