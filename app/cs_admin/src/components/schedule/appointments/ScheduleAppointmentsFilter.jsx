// @flow

import React from 'react'
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"


import CSLS from "../../../tools/cs_local_storage"
import { get_list_query_variables } from './tools'


function getDefaultValue(value) {
  let defaultValue = localStorage.getItem(value)
  if (defaultValue) {
    return defaultValue
  } else {
    return ""
  }
}


function updateLocalStorageAndRefetch(key, value, refetch) {
  localStorage.setItem(key, value)
  refetch(get_list_query_variables())
}

const selectClass = "form-control mb-2"


const ScheduleAppointmentsFilter = ({ t, history, data, refetch }) => (
  <div>
    {/* Locations */}
    <select 
      className={selectClass}
      defaultValue={getDefaultValue(CSLS.SCHEDULE_APPOINTMENTS_FILTER_LOCATION)}
      onChange={ (event) => {
        updateLocalStorageAndRefetch(
          CSLS.SCHEDULE_APPOINTMENTS_FILTER_LOCATION,
          event.target.value,
          refetch
        )
      }}
    >
      <option value="" key={v4()}>{t("schedule.appointments.filter_all_locations")}</option>
      {data.organizationLocations.edges.map(({ node }) =>
        <option value={node.id} key={v4()}>{node.name}</option>
      )}
    </select>
    {/* Appointments */}
    {/* <select 
      className={selectClass}
      defaultValue={getDefaultValue(CSLS.SCHEDULE_APPOINTMENTS_FILTER_CLASSTYPE)}
      onChange={ (event) => {
        updateLocalStorageAndRefetch(
          CSLS.SCHEDULE_APPOINTMENTS_FILTER_CLASSTYPE,
          event.target.value,
          refetch
        )
      }}
    >
      <option value="" key={v4()}>{t("schedule.appointments.filter_all_appointments")}</option>
      {data.organizationAppointments.edges.map(({ node }) =>
        <option value={node.id} key={v4()}>{node.name}</option>
      )}
    </select> */}
  </div>
);

export default withTranslation()(withRouter(ScheduleAppointmentsFilter))