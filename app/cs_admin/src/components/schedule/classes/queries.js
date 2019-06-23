import gql from "graphql-tag"

export const GET_CLASSES_QUERY = gql`
  query ScheduleClasses($dateFrom: Date!, $dateUntil:Date!, $orderBy: String, $organizationLocation: String) {
    scheduleClasses(dateFrom:$dateFrom, dateUntil: $dateUntil, orderBy: $orderBy, organizationLocation: $organizationLocation) {
      date
      classes {
        scheduleItemId
        frequencyType
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
    organizationLocations(first: 100, archived: false) {
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

export const GET_CLASS_QUERY = gql`
  query ScheduleItem($id: ID!, $before: String, $after: String, $archived: Boolean!) {
    scheduleItem(id:$id) {
      id
      frequencyType
      frequencyInterval
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
      dateStart
      dateEnd
      timeStart
      timeEnd
      displayPublic
    }
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
    organizationLevels(first: 100, before: $before, after: $after, archived: $archived) {
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
    organizationLevels(first: 100, before: $before, after: $after, archived: $archived) {
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