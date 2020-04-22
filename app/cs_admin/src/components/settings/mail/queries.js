import gql from "graphql-tag"

export const GET_SYSTEM_MAIL_TEMPLATES_QUERY = gql`
  query SystemMailTemplates {
    systemMailTemplates(first:100) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          name
          subject
          title
          description
          content
          comments
        }
      }
    }
  }
`

export const GET_SYSTEM_MAIL_TEMPLATE_QUERY = gql`
  query SystemMailTemplate($id: ID!) {
    systemMailTemplate(id:$id) {
      id
      name
      subject
      title
      description
      content
      comments
    }
  }
`

export const UPDATE_SYSTEM_MAIL_TEMPLATE =  gql`
  mutation UpdateSystemMailTemplate($input: UpdateSystemMailTemplateInput!) {
    updateSystemMailTemplate(input: $input) {
      systemMailTemplate {
        id
        name
        subject
        title
        description
        content
        comments
      }
    }
  }
`