import CSLS from "../../../tools/cs_local_storage"

export function get_list_query_variables() {
  let queryVars = {}

  let status = localStorage.getItem(CSLS.FINANCE_INVOICES_FILTER_STATUS)
  if (status) {
    queryVars.status = status
  } else {
    queryVars.status = undefined
  }
  
  console.log(queryVars)

  return queryVars
}

