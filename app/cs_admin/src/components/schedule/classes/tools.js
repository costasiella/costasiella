import CSLS from "../../../tools/cs_local_storage"

export function get_list_query_variables() {
  let orderBy
  let organizationLocation

  let queryVars = {
    dateFrom: localStorage.getItem(CSLS.SCHEDULE_CLASSES_DATE_FROM), 
    dateUntil: localStorage.getItem(CSLS.SCHEDULE_CLASSES_DATE_UNTIL)
  }

  orderBy = localStorage.getItem(CSLS.SCHEDULE_CLASSES_ORDER_BY)
  if (orderBy) {
    queryVars.orderBy = orderBy
  }

  organizationLocation = localStorage.getItem(CSLS.SCHEDULE_CLASSES_FILTER_LOCATION)
  if (organizationLocation) {
    queryVars.organizationLocation = organizationLocation
  }

  console.log(queryVars)

  return queryVars
}

