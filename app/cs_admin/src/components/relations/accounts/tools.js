import CSLS from "../../../tools/cs_local_storage"

export function get_list_query_variables() {
  let isActive = localStorage.getItem(CSLS.RELATIONS_ACCOUNTS_IS_ACTIVE)
  if (isActive === null) {
    isActive = true
  }

  let search = localStorage.getItem(CSLS.RELATIONS_ACCOUNTS_SEARCH)

  let queryVars = {
    isActive: isActive,
    searchName: search
  }


  console.log(queryVars)

  return queryVars
}

