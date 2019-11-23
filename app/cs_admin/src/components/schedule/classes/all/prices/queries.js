import gql from "graphql-tag"

export const GET_SCHEDULE_ITEM_PRICES_QUERY = gql`
  query ScheduleItemPrices($after: String, $before: String, $scheduleItem: ID!) {
    scheduleItemPrices(first: 15, before: $before, after: $after, scheduleItem: $scheduleItem) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          organizationClasspassDropin {
            id
            name
          }
          organizationClasspassTrial {
            id
            name
          }
          dateStart
          dateEnd       
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

export const GET_SINGLE_SCHEDULE_ITEM_PRICE_QUERY = gql`
query ScheduleItemPrice($before: String, $after: String, $id: ID!) {
  scheduleItemPrice(id: $id) {
    id
    organizationClasspassDropin {
      id
      name
    }
    organizationClasspassTrial {
      id
      name
    }
    dateStart
    dateEnd       
  }
  organizationClasspasses(first: 100, before: $before, after: $after, archived: false) {
    pageInfo {
      startCursor
      endCursor
      hasNextPage
      hasPreviousPage
    }
    edges {
      node {
        id
        name
      }
    }
  }
}
`


export const GET_INPUT_VALUES_QUERY = gql`
  query InputValues($after: String, $before: String) {
    organizationClasspasses(first: 100, before: $before, after: $after, archived: false) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          name
        }
      }
    }
  }
`

export const DELETE_SCHEDULE_ITEM_PRICE = gql`
  mutation DeleteScheduleItemPrice($input: DeleteScheduleItemPriceInput!) {
    deleteScheduleItemPrice(input: $input) {
      ok
    }
  }
`
