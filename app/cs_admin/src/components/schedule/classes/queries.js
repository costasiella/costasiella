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
        displayPublic
      }
    }
    user {
      id
      isActive
      email
      firstName
      lastName
      groups {
        edges {
          node {
            id
            name
            permissions {
              edges {
                node {
                  id
                  name
                  codename
                }
              }
            }
          }
        }
      }
    }
  }
`

export const GET_CLASS_QUERY = gql`
  query SchoolLevel($id: ID!) {
    organizationLevel(id:$id) {
      id
      name
      archived
    }
  }
`

export const GET_INPUT_VALUES_QUERY = gql`
  query ScheduleClassInputValues($after: String, $before: String, $archived: Boolean) {
    organizationLocationRooms(first: 100, before: $before, after: $after, archived: $archived) {
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
    organizationClasstypes(first: 100, before: $before, after: $after, archived: $archived) {
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
    financePaymentMethods(first: 100, before: $before, after: $after, archived: $archived) {
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