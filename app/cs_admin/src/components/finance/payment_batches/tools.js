export function get_list_query_variables(batchType) {
  
  let queryVars = {
    batchType: batchType.toUpperCase()
  }

  console.log(queryVars)

  return queryVars
}
