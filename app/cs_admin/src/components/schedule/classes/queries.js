import gql from "graphql-tag"

export const GET_CLASSES_QUERY = gql`
  query ScheduleClasses($dateFrom: Date!, $dateUntil:Date!) {
    scheduleClasses(dateFrom:$dateFrom, dateUntil: $dateUntil) {
      date
      classes {
        scheduleItemId
        date
        organizationLocationRoom {
          id
          name
          organizationLocation {
            id
            name
          }
        }
        timeStart
        timeEnd
      }
    }
  }
`

export const GET_LEVEL_QUERY = gql`
  query SchoolLevel($id: ID!) {
    organizationLevel(id:$id) {
      id
      name
      archived
    }
  }
`