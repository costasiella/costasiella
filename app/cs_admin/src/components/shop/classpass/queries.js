import gql from "graphql-tag"


export const GET_CLASSPASS_QUERY = gql`
  query OrganizationClasspass($id: ID!) {
    organizationClasspass(id:$id) {
      id
      archived
      displayPublic
      displayShop
      trialPass
      trialTimes
      name
      description
      price
      priceDisplay
      financeTaxRate {
        id
        name
      }
      validity
      validityUnit
      validityUnitDisplay
      classes
      unlimited
      organizationMembership {
        id
        name
      }
      quickStatsAmount
      financeGlaccount {
        id 
        name
      }
      financeCostcenter {
        id
        name
      }
    }
  }
`


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