import gql from "graphql-tag"


export const GET_ACCOUNTS_QUERY = gql`
  query Accounts(
    $after: String, 
    $before: String, 
    $searchName: String,
    $teacher: Boolean,
    $employee: Boolean
  ) {
    accounts(
      first: 25, 
      before: $before, 
      after: $after, 
      isActive: true, 
      fullName_Icontains: $searchName,
      customer: true,
      teacher: $teacher,
      employee: $employee
    ) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          firstName
          lastName
          fullName
          email
          isActive
        }
      }
    }
  }
`


export const GET_SCHEDULE_CLASS_ATTENDANCE_QUERY = gql`
  query ScheduleItemAttendances($after: String, $before: String, $scheduleItem: ID!, $date: Date!) {
    scheduleItemAttendances(first: 100, before: $before, after: $after, scheduleItem: $scheduleItem, date: $date) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          account {
            id
            fullName
          }     
          attendanceType
          bookingStatus
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
  }
`

export const GET_SINGLE_SCHEDULE_CLASS_TEACHERS_QUERY = gql`
  query ScheduleItemTeacher($before: String, $after: String, $id: ID!) {
    scheduleItemTeacher(id: $id) {
      id
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
      dateStart
      dateEnd       
    }
    accounts(first: 15, before: $before, after: $after, isActive: true, teacher: true) {
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
  }
`


export const GET_INPUT_VALUES_QUERY = gql`
  query InputValues($after: String, $before: String) {
    accounts(first: 15, before: $before, after: $after, isActive: true, teacher: true) {
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
  }
`