import CSLS from "../../../tools/cs_local_storage"

export function get_list_query_variables() {
    return {
      dateFrom: localStorage.getItem(CSLS.SCHEDULE_CLASSES_DATE_FROM), 
      dateUntil: localStorage.getItem(CSLS.SCHEDULE_CLASSES_DATE_UNTIL)
    }
  }

