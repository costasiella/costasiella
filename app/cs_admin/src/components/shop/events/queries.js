import gql from "graphql-tag"

export const GET_SCHEDULE_EVENTS_QUERY = gql`
  query ScheduleEvents($before:String, $after:String) {
    scheduleEvents(first: 100, before: $before, after:$after, archived:false, displayShop:true) {
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
          media(first: 1) {
            pageInfo {
              hasNextPage
              hasPreviousPage
              startCursor
              endCursor
            }
            edges {
              node {
                urlImageThumbnailSmall
                urlImageThumbnailLarge
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
