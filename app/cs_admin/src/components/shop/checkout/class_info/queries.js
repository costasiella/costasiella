import gql from "graphql-tag"

export const GET_SCHEDULE_CLASS_QUERY = gql`
  query ScheduleClass($scheduleItemId:ID!, $date:Date!) {
    scheduleClass(scheduleItemId: $scheduleItemId, date:$date) {
      scheduleItemId
      frequencyType
      date
      organizationClasstype {
        name
      }
      organizationLocationRoom {
        organizationLocation {
          name
        }
      }
          timeStart
      timeEnd
      infoMailContent
    }
  }
`



