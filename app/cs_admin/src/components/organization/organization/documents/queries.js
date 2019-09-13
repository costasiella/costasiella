import gql from "graphql-tag"

export const GET_DOCUMENTS_QUERY = gql`
  query OrganizationDocuments($documentType: String!) {
    organizationDocuments(documentType:$documentType) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          documentType
          dateStart
          dateEnd
          document
          urlDocument
        }
      }
    }
  }
`

export const GET_LEVEL_QUERY = gql`
  query SchoolLevel($id: ID!) {
    organizationLevel(id:$id) {
      id
      name
      archived
    }
  }
`