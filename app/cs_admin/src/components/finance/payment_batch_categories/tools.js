import CSLS from "../../../tools/cs_local_storage"

export function get_list_query_variables() {
  let showArchive = localStorage.getItem(CSLS.FINANCE_PAYMENT_BATCH_CATEGORIES_SHOW_ARCHIVE)
  if (showArchive === null) {
    showArchive = "false"
  }

  let queryVars = {
    archived: (showArchive === "true") ? true : false,
  }

  console.log(queryVars)

  return queryVars
}

