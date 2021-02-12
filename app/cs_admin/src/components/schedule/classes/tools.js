import React from "react"
import CSLS from "../../../tools/cs_local_storage"

import StatusIcon from "../../ui/StatusIcon"


export function get_list_query_variables() {
  let orderBy
  let organizationClasstype
  let organizationLevel
  let organizationLocation

  let queryVars = {
    attendanceCountType: "ATTENDING_AND_BOOKED",
    dateFrom: localStorage.getItem(CSLS.SCHEDULE_CLASSES_DATE_FROM), 
    dateUntil: localStorage.getItem(CSLS.SCHEDULE_CLASSES_DATE_UNTIL)
  }

  orderBy = localStorage.getItem(CSLS.SCHEDULE_CLASSES_ORDER_BY)
  if (orderBy) {
    queryVars.orderBy = orderBy
  }

  organizationClasstype = localStorage.getItem(CSLS.SCHEDULE_CLASSES_FILTER_CLASSTYPE)
  if (organizationClasstype) {
    queryVars.organizationClasstype = organizationClasstype
  } else {
    queryVars.organizationClasstype = ""
  }

  organizationLevel = localStorage.getItem(CSLS.SCHEDULE_CLASSES_FILTER_LEVEL)
  if (organizationLevel) {
    queryVars.organizationLevel = organizationLevel
  } else {
    queryVars.organizationLevel = ""
  }

  organizationLocation = localStorage.getItem(CSLS.SCHEDULE_CLASSES_FILTER_LOCATION)
  if (organizationLocation) {
    queryVars.organizationLocation = organizationLocation
  } else {
    queryVars.organizationLocation = ""
  }

  console.log(queryVars)

  return queryVars
}


export function represent_teacher(name, role) {
  let textColor = false

  switch (role) {
    case "SUB":
      textColor = "text-blue"
      break
    case "ASSISTANT":
      textColor = "text-green"
      break
    case "KARMA":
      textColor = "text-orange"
      break
  }

  if (textColor) {
    return <span className={textColor}>{name}</span>
  } else {
    return name
  }
}


export function represent_class_status(status) {
  let color

  switch (status) {
    case "SUB":
      color = "primary"
      break
    case "CANCELLED":
      color = "warning"
      break
    case "OPEN":
      color = "danger"
      break
    default:
      color = "success"
  }

  return <StatusIcon color={color} />
}
