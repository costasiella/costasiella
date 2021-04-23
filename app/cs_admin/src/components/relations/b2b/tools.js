import CSLS from "../../../tools/cs_local_storage"

export function get_list_query_variables() {
  let queryVars = {}

  let search = localStorage.getItem(CSLS.RELATIONS_BUSINESSES_SEARCH)
  let showArchived = localStorage.getItem(CSLS.RELATIONS_BUSINESSES_SHOW_ARCHIVE)
  
  if (search) {
    queryVars.name = search
  }
  if (showArchived === "true") {
    queryVars.archived = true
  } else {
    queryVars.archived = false
  }
  

  console.log(queryVars)

  return queryVars
}

