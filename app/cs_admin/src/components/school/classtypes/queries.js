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

// export const GET_LOCATION_QUERY = gql`
//   query SchoolLocation($id: ID!) {
//     schoolLocation(id:$id) {
//       id
//       name
//       displayPublic
//       archived
//     }
//   }
// `