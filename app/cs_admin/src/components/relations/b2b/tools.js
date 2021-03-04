import CSLS from "../../../tools/cs_local_storage"

export function get_list_query_variables() {
  let queryVars = {}

  let search = localStorage.getItem(CSLS.RELATIONS_BUSINESSES_SEARCH)
  queryVars.searchName = search


  console.log(queryVars)

  return queryVars
}

