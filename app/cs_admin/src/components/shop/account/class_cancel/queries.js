import gql from "graphql-tag"


export const GET_ACCOUNT_CLASS_QUERY = gql`
  query ScheduleItemAttendance($scheduleItemId:ID!, $date:Date!, $id: ID!) {
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
    scheduleItemAttendance(id: $id) {
      id
      cancellationPossible
      attendanceType
      date
      bookingStatus
      scheduleItem {
        id
        timeStart
        timeEnd
        organizationLocationRoom {
          name
          organizationLocation {
            name
          }
        }
        organizationClasstype {
          name
        }
      }
    }
    user {
      id
      accountId
      firstName
      lastName
      fullName
      email
      gender
      dateOfBirth
      address
      postcode
      city
      country
      phone
      mobile
      emergency
    }
  }
`