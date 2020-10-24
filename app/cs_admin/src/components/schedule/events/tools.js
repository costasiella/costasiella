import CSLS from "../../../tools/cs_local_storage"

export function get_list_query_variables() {
  let isActive = localStorage.getItem(CSLS.SCHEDULE_EVENTS_IS_ACTIVE)
  if (isActive === null) {
    isActive = true
  }

  let queryVars = {
    isActive: (isActive === "true") ? true : false,
  }

  console.log(queryVars)

  return queryVars
}
