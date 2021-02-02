import gql from "graphql-tag"

export const GET_ACCOUNT_SCHEDULE_EVENT_TICKETS_QUERY = gql`
  query AccountScheduleEventTickets($after: String, $before: String, $account: ID!) {
    accountScheduleEventTickets(first: 15, before: $before, after: $after, account: $account) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          cancelled
          infoMailSent
          scheduleEventTicket {
            id
            name
            scheduleEvent {
              id
              name
              dateStart
              organizationLocation {
                name
              }
            }
          }
          invoiceItems(first:1) {
            edges {
              node {
                financeInvoice {
                  id
                  invoiceNumber
                  status
                }
              }
            }
          }
        }
        
      }
    }
  }
`

export const GET_ACCOUNT_CLASSPASS_QUERY = gql`
  query AccountClasspass($id: ID!, $accountId: ID!, $after: String, $before: String, $archived: Boolean!) {
    accountClasspass(id:$id) {
      id
      organizationClasspass {
        id
        name
      }
      dateStart
      dateEnd
      note
      createdAt
    }
    organizationClasspasses(first: 100, before: $before, after: $after, archived: $archived) {
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
    account(id:$accountId) {
      id
      firstName
      lastName
      email
      phone
      mobile
      isActive
    }
  }
`

export const GET_INPUT_VALUES_QUERY = gql`
  query ClasspassInputValues($after: String, $before: String, $archived: Boolean!, $accountId: ID!) {
    organizationClasspasses(first: 100, before: $before, after: $after, archived: $archived) {
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
    account(id:$accountId) {
      id
      firstName
      lastName
      email
      phone
      mobile
      isActive
    }
  }
`