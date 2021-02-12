import CSLS from "../../../../../tools/cs_local_storage"

export function get_accounts_query_variables() {
  let queryVars = {
    teacher: undefined,
    employee: undefined,
    searchName: undefined
  }

  let search = localStorage.getItem(CSLS.SCHEDULE_EVENTS_TICKETS_CUSTOMERS_SEARCH)
  queryVars.searchName = search

  console.log(queryVars)

  return queryVars
}

// export function get_attendance_list_query_variables(schedule_item_id, date) {
//   return {
//     scheduleItem: schedule_item_id,
//     date: date
//   }
// }
