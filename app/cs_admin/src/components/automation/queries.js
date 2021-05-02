import gql from "graphql-tag"

export const GET_TASK_RESULT_QUERY = gql`
query TaskResults($before: String, $after: String, $taskName:String) {
  djangoCeleryResultTaskResults(first: 100, before: $before, after: $after, taskName: $taskName) {
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    edges {
      node {
        id
        taskId
        taskName
        taskArgs
        taskKwargs
        status
        contentType
        contentEncoding
        result
        dateDone
        traceback
        meta
      }
    }
  }
}
`
