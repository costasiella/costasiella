import gql from "graphql-tag"

export const GET_CLASSTYPES_QUERY = gql`
query SchoolClasstypes($archived: Boolean!) {
  schoolClasstypes(archived: $archived) {
    id
    name
    archived
    displayPublic
    description
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
  }
}
`