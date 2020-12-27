import CSLS from "../../../../tools/cs_local_storage"

export function get_list_query_variables() {
    let orderBy
    let organizationClasstype
    let organizationLevel
    let organizationLocation
  
    let queryVars = {
      attendanceCountType: "ATTENDING_AND_BOOKED",
      dateFrom: localStorage.getItem(CSLS.SHOP_CLASSES_DATE_FROM), 
      dateUntil: localStorage.getItem(CSLS.SHOP_CLASSES_DATE_UNTIL),
    }
  
    // orderBy = localStorage.getItem(CSLS.SHOP_CLASSES_ORDER_BY)
    // if (orderBy) {
    //   queryVars.orderBy = orderBy
    // }
  
    organizationClasstype = localStorage.getItem(CSLS.SHOP_CLASSES_FILTER_CLASSTYPE)
    if (organizationClasstype) {
      queryVars.organizationClasstype = organizationClasstype
    } else {
      queryVars.organizationClasstype = ""
    }
  
    organizationLevel = localStorage.getItem(CSLS.SHOP_CLASSES_FILTER_LEVEL)
    if (organizationLevel) {
      queryVars.organizationLevel = organizationLevel
    } else {
      queryVars.organizationLevel = ""
    }
  
    organizationLocation = localStorage.getItem(CSLS.SHOP_CLASSES_FILTER_LOCATION)
    if (organizationLocation) {
      queryVars.organizationLocation = organizationLocation
    } else {
      queryVars.organizationLocation = ""
    }
  
    console.log(queryVars)
  
    return queryVars
  }
  