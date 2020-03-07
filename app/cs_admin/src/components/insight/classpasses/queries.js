import gql from "graphql-tag"


export const GET_CLASSPASSES_SOLD_QUERY = gql`
  query InsightAccountClasspassesSold($year: Int!) {
    insightAccountClasspassesSold(year: $year) {
      description
      data
      year
    }
  }
`


export const GET_CLASSPASSES_ACTIVE_QUERY = gql`
  query InsightAccountClasspassesActive($year: Int!) {
    insightAccountClasspassesActive(year: $year) {
      description
      data
      year
    }
  }
`