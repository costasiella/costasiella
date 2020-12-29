import gql from "graphql-tag"


export const GET_SCHEDULE_EVENT_QUERY = gql`
query ScheduleEvent($id: ID!) {
  scheduleEvent(id: $id) {
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
    media(first: 1) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          description
          urlImageThumbnailSmall
          urlImageThumbnailLarge
        }
      }
    }
    tickets {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          name
          price
          description
          scheduleItems {
            pageInfo {
              hasNextPage
              hasPreviousPage
              startCursor
              endCursor
            }
            edges {
              node {
                name
                description
                organizationLocationRoom {
                  name
                  organizationLocation {
                    name
                  }
                }
                dateStart
                timeStart
                timeEnd
              }
            }
          }
        }
      }
    }
    createdAt
    updatedAt
  }
}
`
