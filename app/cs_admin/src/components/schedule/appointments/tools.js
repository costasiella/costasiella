import CSLS from "../../../tools/cs_local_storage"

export function get_list_query_variables() {
  let orderBy
  let organizationAppointment
  let organizationLocation

  let queryVars = {
    dateFrom: localStorage.getItem(CSLS.SCHEDULE_APPOINTMENTS_DATE_FROM), 
    dateUntil: localStorage.getItem(CSLS.SCHEDULE_APPOINTMENTS_DATE_UNTIL)
  }

  orderBy = localStorage.getItem(CSLS.SCHEDULE_APPOINTMENTS_ORDER_BY)
  if (orderBy) {
    queryVars.orderBy = orderBy
  }

  organizationAppointment = localStorage.getItem(CSLS.SCHEDULE_APPOINTMENTS_FILTER_CLASSTYPE)
  if (organizationAppointment) {
    queryVars.organizationAppointment = organizationAppointment
  } else {
    queryVars.organizationAppointment = ""
  }

  organizationLocation = localStorage.getItem(CSLS.SCHEDULE_APPOINTMENTS_FILTER_LOCATION)
  if (organizationLocation) {
    queryVars.organizationLocation = organizationLocation
  } else {
    queryVars.organizationLocation = ""
  }

  console.log(queryVars)

  return queryVars
}

