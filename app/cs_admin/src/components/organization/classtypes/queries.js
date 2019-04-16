import gql from "graphql-tag"

export const GET_CLASSTYPES_QUERY = gql`
query SchoolClasstypes($after: String, $before: String, $archived: Boolean) {
  schoolClasstypes(first: 15, before: $before, after: $after, archived: $archived) {
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
        displayPublic
        name
        description
        urlWebsite
        urlImage
        urlImageThumbnailSmall
      }
    }
  }
}
`

export const GET_CLASSTYPE_QUERY = gql`
query getSchoolClasstype($id: ID!) {
  schoolClasstype(id:$id) {
    id
    archived
    name
    description
    displayPublic
    urlWebsite
    urlImage
  }
}
`