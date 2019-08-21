import CSLS from "../../../../../tools/cs_local_storage"

export function get_accounts_query_variables() {
  let queryVars = {
    teacher: undefined,
    employee: undefined,
    searchName: undefined
  }

  let search = localStorage.getItem(CSLS.SCHEDULE_CLASSES_CLASS_ATTENDANCE_SEARCH)
  queryVars.searchName = search

  console.log(queryVars)

  return queryVars
}