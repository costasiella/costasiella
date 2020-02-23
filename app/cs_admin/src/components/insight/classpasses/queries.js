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


export const GET_CLASSPASSES_CURRENT_QUERY = gql`
  query InsightAccountClasspassesCurrent($year: Int!) {
    insightAccountClasspassesCurrent(year: $year) {
      description
      data
      year
    }
  }
`