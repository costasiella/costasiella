import gql from "graphql-tag"


export const GET_SUBSCRIPTIONS_SOLD_QUERY = gql`
  query InsightAccountSubscriptionsSold($year: Int!) {
    insightAccountSubscriptionsSold(year: $year) {
      description
      data
      year
    }
  }
`


export const GET_SUBSCRIPTIONS_ACTIVE_QUERY = gql`
  query InsightAccountSubscriptionsActive($year: Int!) {
    insightAccountSubscriptionsActive(year: $year) {
      description
      data
      year
    }
  }
`