import moment from 'moment'

import CSLS from "../../../../tools/cs_local_storage"


export function class_subtitle({t, location, locationRoom, classtype, timeStart, date}) {
  return t('general.class') + ': ' + 
         location + ' (' + locationRoom + ') - ' + 
         classtype + ' @ ' + 
         moment(date).format('LL') + ' ' + moment(timeStart).format('LT')
}

export function get_accounts_query_variables() {
  let queryVars = {
    teacher: undefined,
    employee: undefined
  }

  let search = localStorage.getItem(CSLS.SCHEDULE_CLASSES_CLASS_ATTENDANCE_SEARCH)
  queryVars.searchName = search

  console.log(queryVars)

  return queryVars
}