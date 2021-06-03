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
          urlImageThumbnailSmall
          urlImageThumbnailLarge
        }
      }
    }
    tickets(first: 100) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          name
          price
          priceDisplay
          totalPrice
          totalPriceDisplay
          description
          isSoldOut
          isEarlybirdPrice
          ticketScheduleItems(included: true) {
           pageInfo{
            hasNextPage
            hasPreviousPage
            startCursor
            endCursor
            }
            edges {
              node {
                id
                included
                scheduleItem {
                  name
                  dateStart
                  timeStart
                  timeEnd
                  organizationLocationRoom {
                    organizationLocation {
                      name
                    }
                  }
                }
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
