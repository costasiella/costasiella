import gql from "graphql-tag"


export const GET_BOOKING_OPTIONS_QUERY = gql`
  query ScheduleClassBookingOptions($scheduleItem:ID!, $date:Date!, $listType:String!) {
    scheduleClass(scheduleItemId: $scheduleItem, date:$date) {
      bookingStatus
    }
    scheduleClassBookingOptions(scheduleItem: $scheduleItem, date:$date, listType:$listType) {
      date
      alreadyBooked
      account {
        id
        fullName
      }
      scheduleItem {
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
      }
    	scheduleItemPrices {
        organizationClasspassDropin {
          id
          name
          priceDisplay
        }
        organizationClasspassTrial {
          id
          name
          priceDisplay
        }
      }
      classpasses {
        bookingType 
        allowed
        accountClasspass {
          id
          dateStart
          dateEnd
          classesRemainingDisplay
          organizationClasspass {
            id
            name
          }
        }
      }
      subscriptions {
        bookingType
        allowed
        accountSubscription {
          id
          dateStart
          dateEnd
          organizationSubscription {
            id
            name
          }
          creditTotal
        }
      }
    }
  }
`
