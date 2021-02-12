import gql from "graphql-tag"


export const GET_SCHEDULE_CLASS_WEEKLY_OTCS_QUERY = gql`
  query ScheduleClassWeeklyOTCs($scheduleItem: ID!, $date: Date!) {
    scheduleClassWeeklyOtcs(first:1, scheduleItem: $scheduleItem, date:$date) {
      edges {
        node {
          id 
          date
          status
          description
          account {
            id
            fullName
          }
          role
          account2 {
            id
            fullName
          }
          role2
          organizationLocationRoom {
            id
            name
          }
          organizationClasstype {
            id
            name
          }
          organizationLevel {
            id
            name
          }
          timeStart
          timeEnd
          spaces
          walkInSpaces
          infoMailContent
        }
      }
    }
    scheduleItem(id:$scheduleItem) {
      id
      frequencyType
      frequencyInterval
      organizationLocationRoom {
        id
        name
        organizationLocation {
          id
          name
        }
      }
      organizationClasstype {
        id
        name
      }
      organizationLevel {
        id
        name
      }
      dateStart
      dateEnd
      timeStart
      timeEnd
      displayPublic
    }
    accounts(first: 100, isActive: true, teacher: true) {
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
    organizationLocationRooms(first: 100, archived: false) {
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
          organizationLocation {
            id
            name
          }
        }
      }
    }
    organizationClasstypes(first: 100, archived: false) {
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
    organizationLevels(first: 100, archived: false) {
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

export const DELETE_SCHEDULE_CLASS_WEEKLY_OTC = gql`
  mutation DeleteScheduleClassWeeklyOTC($input: DeleteScheduleClassWeeklyOTCInput!) {
    deleteScheduleClassWeeklyOtc(input: $input) {
      ok
    }
  }
`


export const UPDATE_SCHEDULE_CLASS_WEEKLY_OTC = gql`
  mutation UpdateScheduleClassWeeklyOTC($input: UpdateScheduleClassWeeklyOTCInput!) {
    updateScheduleClassWeeklyOtc(input:$input) {
      scheduleClassWeeklyOtc {
        id
      }
    }
  }
`
