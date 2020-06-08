import gql from "graphql-tag"


export const GET_CLASS_QUERY = gql`
  query ScheduleClass($scheduleItemId: ID!, $date: Date!) {
    scheduleClass(scheduleItemId: $scheduleItemId, date:$date) {
      scheduleItemId 
      date
      organizationLocationRoom {
        organizationLocation {
          name
        }
      }
      organizationClasstype {
        name
      }
      timeStart
      timeEnd
    }
  }
`


export const CREATE_ORDER = gql`
  mutation CreateFinanceOrder($input: CreateFinanceOrderInput!) {
    createFinanceOrder(input: $input) {
      financeOrder {
        id
      }
    }
  }
`
